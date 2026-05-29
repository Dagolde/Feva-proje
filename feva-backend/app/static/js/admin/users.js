/**
 * Admin User Management JavaScript module
 * Handles user CRUD interactions on /admin/users
 * Requirements: 17.2, 4.1-4.5
 */

let currentPage = 1;
const PAGE_SIZE = 50;
let allUsers = [];
let roles = [];

// Load roles for dropdowns
async function loadRoles() {
    const response = await apiRequest('/api/v1/admin/roles');
    if (!response || !response.ok) return;
    roles = await response.json();

    ['createRole', 'editRole'].forEach(id => {
        const select = document.getElementById(id);
        if (!select) return;
        roles.forEach(role => {
            const opt = document.createElement('option');
            opt.value = role.id;
            opt.textContent = role.name;
            select.appendChild(opt);
        });
    });
}

// Load users with pagination
async function loadUsers() {
    const response = await apiRequest(`/api/v1/admin/users?page=${currentPage}&page_size=${PAGE_SIZE}`);
    if (!response || !response.ok) {
        showNotification('Failed to load users', 'error');
        return;
    }
    const data = await response.json();
    allUsers = data.items;
    renderUsers(allUsers);
    renderPagination(data.total, data.page, data.page_size, changePage);
    updateUserStats(data.items);
}

// Render users table body
function renderUsers(users) {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;

    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:40px;color:#666;">No users found</td></tr>';
        return;
    }

    tbody.innerHTML = users.map(user => {
        const roleName = roles.find(r => r.id === user.role_id)?.name || 'Unknown';
        const statusClass = user.locked_at ? 'badge-danger' : 'badge-success';
        const statusText = user.locked_at ? 'Locked' : 'Active';
        const lgaDisplay = user.lga_assignment?.length ? user.lga_assignment.join(', ') : '-';
        const createdDate = new Date(user.created_at).toLocaleDateString();

        return `
            <tr>
                <td>${escapeHtml(user.username)}</td>
                <td>${escapeHtml(user.email)}</td>
                <td>${escapeHtml(roleName)}</td>
                <td>${escapeHtml(lgaDisplay)}</td>
                <td><span class="badge ${statusClass}">${statusText}</span></td>
                <td>${createdDate}</td>
                <td>
                    <div class="user-actions">
                        <button class="btn btn-secondary btn-icon" onclick="openEditUserModal('${user.id}')">Edit</button>
                        <button class="btn btn-secondary btn-icon" onclick="openResetPasswordModal('${user.id}', '${escapeHtml(user.username)}')">Reset</button>
                        ${!user.locked_at ? `<button class="btn btn-danger btn-icon" onclick="openDeactivateUserModal('${user.id}', '${escapeHtml(user.username)}')">Deactivate</button>` : ''}
                    </div>
                </td>
            </tr>`;
    }).join('');
}

// Update stat cards
function updateUserStats(users) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('totalUsers', users.length);
    set('activeUsers', users.filter(u => !u.locked_at).length);
    set('lockedUsers', users.filter(u => u.locked_at).length);
}

// Filter users by search term
function filterUsers(term) {
    const filtered = allUsers.filter(u =>
        u.username.toLowerCase().includes(term.toLowerCase()) ||
        u.email.toLowerCase().includes(term.toLowerCase())
    );
    renderUsers(filtered);
}

// Pagination helper
function renderPagination(total, page, pageSize, onChangePage) {
    const totalPages = Math.ceil(total / pageSize);
    const el = document.getElementById('pagination');
    if (!el || totalPages <= 1) { if (el) el.innerHTML = ''; return; }

    let html = `<button ${page === 1 ? 'disabled' : ''} onclick="${onChangePage.name}(${page - 1})">Previous</button>`;
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= page - 2 && i <= page + 2)) {
            html += `<button class="${i === page ? 'active' : ''}" onclick="${onChangePage.name}(${i})">${i}</button>`;
        } else if (i === page - 3 || i === page + 3) {
            html += '<span>...</span>';
        }
    }
    html += `<button ${page === totalPages ? 'disabled' : ''} onclick="${onChangePage.name}(${page + 1})">Next</button>`;
    el.innerHTML = html;
}

async function changePage(page) {
    currentPage = page;
    await loadUsers();
}

// Create user
function openCreateUserModal() {
    document.getElementById('createUserModal').style.display = 'flex';
    document.getElementById('createUserForm').reset();
}

function closeCreateUserModal() {
    document.getElementById('createUserModal').style.display = 'none';
}

async function submitCreateUser() {
    const form = document.getElementById('createUserForm');
    const fd = new FormData(form);
    const lgaRaw = fd.get('lga_assignment');
    const data = {
        username: fd.get('username'),
        email: fd.get('email'),
        password: fd.get('password'),
        role_id: parseInt(fd.get('role_id')),
        lga_assignment: lgaRaw ? lgaRaw.split(',').map(s => s.trim()).filter(Boolean) : null,
    };

    const resp = await apiRequest('/api/v1/admin/users', { method: 'POST', body: JSON.stringify(data) });
    if (resp && resp.ok) {
        showNotification('User created successfully', 'success');
        closeCreateUserModal();
        await loadUsers();
    } else {
        const err = await resp.json();
        showNotification(err.detail || 'Failed to create user', 'error');
    }
}

// Edit user
function openEditUserModal(userId) {
    const user = allUsers.find(u => u.id === userId);
    if (!user) return;
    document.getElementById('editUserId').value = user.id;
    document.getElementById('editUsername').value = user.username;
    document.getElementById('editEmail').value = user.email;
    document.getElementById('editRole').value = user.role_id;
    document.getElementById('editLgaAssignment').value = user.lga_assignment?.join(', ') || '';
    document.getElementById('editUserModal').style.display = 'flex';
}

function closeEditUserModal() {
    document.getElementById('editUserModal').style.display = 'none';
}

async function submitEditUser() {
    const userId = document.getElementById('editUserId').value;
    const lgaRaw = document.getElementById('editLgaAssignment').value;
    const data = {
        role_id: parseInt(document.getElementById('editRole').value),
        lga_assignment: lgaRaw ? lgaRaw.split(',').map(s => s.trim()).filter(Boolean) : null,
    };

    const resp = await apiRequest(`/api/v1/admin/users/${userId}`, { method: 'PATCH', body: JSON.stringify(data) });
    if (resp && resp.ok) {
        showNotification('User updated successfully', 'success');
        closeEditUserModal();
        await loadUsers();
    } else {
        const err = await resp.json();
        showNotification(err.detail || 'Failed to update user', 'error');
    }
}

// Reset password
function openResetPasswordModal(userId, username) {
    document.getElementById('resetUserId').value = userId;
    document.getElementById('resetUsername').textContent = username;
    document.getElementById('resetPasswordForm').reset();
    document.getElementById('resetPasswordModal').style.display = 'flex';
}

function closeResetPasswordModal() {
    document.getElementById('resetPasswordModal').style.display = 'none';
}

async function submitResetPassword() {
    const userId = document.getElementById('resetUserId').value;
    const resp = await apiRequest(`/api/v1/admin/users/${userId}/reset-password`, {
        method: 'POST',
        body: JSON.stringify({ new_password: document.getElementById('newPassword').value }),
    });
    if (resp && resp.ok) {
        showNotification('Password reset successfully', 'success');
        closeResetPasswordModal();
    } else {
        const err = await resp.json();
        showNotification(err.detail || 'Failed to reset password', 'error');
    }
}

// Deactivate user
function openDeactivateUserModal(userId, username) {
    document.getElementById('deactivateUserId').value = userId;
    document.getElementById('deactivateUsername').textContent = username;
    document.getElementById('deactivateUserModal').style.display = 'flex';
}

function closeDeactivateUserModal() {
    document.getElementById('deactivateUserModal').style.display = 'none';
}

async function submitDeactivateUser() {
    const userId = document.getElementById('deactivateUserId').value;
    const resp = await apiRequest(`/api/v1/admin/users/${userId}`, { method: 'DELETE' });
    if (resp && resp.ok) {
        showNotification('User deactivated successfully', 'success');
        closeDeactivateUserModal();
        await loadUsers();
    } else {
        const err = await resp.json();
        showNotification(err.detail || 'Failed to deactivate user', 'error');
    }
}
