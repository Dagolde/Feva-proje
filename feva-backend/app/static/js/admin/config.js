/**
 * Admin System Configuration JavaScript module
 * Handles dropdown configuration editor on /admin/config
 * Requirements: 17.2, 6.1-6.4
 */

let dropdownItems = [];
let currentCategory = '';

// Load dropdown config for a given category
async function loadDropdownConfig(category) {
    currentCategory = category;
    const params = category ? `?category=${encodeURIComponent(category)}` : '';
    const resp = await apiRequest(`/api/v1/admin/dropdown-config${params}`);
    if (!resp || !resp.ok) {
        showNotification('Failed to load dropdown configuration', 'error');
        return;
    }
    dropdownItems = await resp.json();
    renderDropdownTable(dropdownItems);
}

// Render dropdown config table
function renderDropdownTable(items) {
    const tbody = document.getElementById('dropdownTableBody');
    if (!tbody) return;

    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:32px;color:#666;">No dropdown options found</td></tr>';
        return;
    }

    tbody.innerHTML = items.map(item => `
        <tr>
            <td>${escapeHtml(item.category)}</td>
            <td>${escapeHtml(item.value)}</td>
            <td>${escapeHtml(item.label)}</td>
            <td>${item.sort_order ?? '-'}</td>
            <td>
                <div style="display:flex;gap:8px;">
                    <button class="btn btn-secondary btn-icon" onclick="openEditDropdownModal(${item.id})">Edit</button>
                    <button class="btn btn-danger btn-icon" onclick="deleteDropdownOption(${item.id}, '${escapeHtml(item.label)}')">Delete</button>
                </div>
            </td>
        </tr>`).join('');
}

// Create dropdown option
function openCreateDropdownModal() {
    document.getElementById('createDropdownForm')?.reset();
    document.getElementById('createDropdownModal').style.display = 'flex';
}

function closeCreateDropdownModal() {
    document.getElementById('createDropdownModal').style.display = 'none';
}

async function submitCreateDropdown() {
    const form = document.getElementById('createDropdownForm');
    const fd = new FormData(form);
    const data = {
        category: fd.get('category'),
        value: fd.get('value'),
        label: fd.get('label'),
        sort_order: fd.get('sort_order') ? parseInt(fd.get('sort_order')) : 0,
    };

    const resp = await apiRequest('/api/v1/admin/dropdown-config', { method: 'POST', body: JSON.stringify(data) });
    if (resp && resp.ok) {
        showNotification('Dropdown option created', 'success');
        closeCreateDropdownModal();
        await loadDropdownConfig(currentCategory);
    } else {
        const err = await resp.json();
        showNotification(err.detail || 'Failed to create option', 'error');
    }
}

// Edit dropdown option
function openEditDropdownModal(id) {
    const item = dropdownItems.find(i => i.id === id);
    if (!item) return;
    document.getElementById('editDropdownId').value = item.id;
    document.getElementById('editDropdownLabel').value = item.label;
    document.getElementById('editDropdownSortOrder').value = item.sort_order ?? 0;
    document.getElementById('editDropdownModal').style.display = 'flex';
}

function closeEditDropdownModal() {
    document.getElementById('editDropdownModal').style.display = 'none';
}

async function submitEditDropdown() {
    const id = document.getElementById('editDropdownId').value;
    const data = {
        label: document.getElementById('editDropdownLabel').value,
        sort_order: parseInt(document.getElementById('editDropdownSortOrder').value) || 0,
    };

    const resp = await apiRequest(`/api/v1/admin/dropdown-config/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
    if (resp && resp.ok) {
        showNotification('Dropdown option updated', 'success');
        closeEditDropdownModal();
        await loadDropdownConfig(currentCategory);
    } else {
        const err = await resp.json();
        showNotification(err.detail || 'Failed to update option', 'error');
    }
}

// Delete dropdown option
async function deleteDropdownOption(id, label) {
    if (!confirm(`Delete dropdown option "${label}"?`)) return;
    const resp = await apiRequest(`/api/v1/admin/dropdown-config/${id}`, { method: 'DELETE' });
    if (resp && resp.ok) {
        showNotification('Dropdown option deleted', 'success');
        await loadDropdownConfig(currentCategory);
    } else {
        const err = await resp.json();
        showNotification(err.detail || 'Failed to delete option', 'error');
    }
}
