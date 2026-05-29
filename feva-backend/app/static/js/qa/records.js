/**
 * QA Records JavaScript module
 * Handles record list filtering and pagination on /qa/records
 * Requirements: 17.1, 10.1-10.8
 */

let currentPage = 1;
let pageSize = 50;
let currentFilters = {};

// Apply filters from form inputs
function applyFilters() {
    currentFilters = {};
    const fields = {
        status: 'filterStatus',
        entity_type: 'filterEntityType',
        lga: 'filterLga',
        ward: 'filterWard',
        enumerator: 'filterEnumerator',
        start_date: 'filterStartDate',
        end_date: 'filterEndDate',
    };

    Object.entries(fields).forEach(([key, id]) => {
        const el = document.getElementById(id);
        if (el && el.value) currentFilters[key] = el.value;
    });

    currentPage = 1;
    updateQueryParams({ ...currentFilters, page: currentPage, page_size: pageSize });
    loadRecords();
}

// Clear all filters
function clearFilters() {
    ['filterStatus', 'filterEntityType', 'filterLga', 'filterWard', 'filterEnumerator', 'filterStartDate', 'filterEndDate'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    currentFilters = {};
    currentPage = 1;
    updateQueryParams({ page: currentPage, page_size: pageSize });
    loadRecords();
}

// Load records from API
async function loadRecords() {
    const params = new URLSearchParams({ page: currentPage, page_size: pageSize, ...currentFilters });
    const resp = await apiRequest(`/api/v1/qa/records?${params}`);
    if (!resp || !resp.ok) {
        showNotification('Failed to load records', 'error');
        return;
    }
    const data = await resp.json();
    renderRecords(data.items);
    renderRecordsPagination(data.total, data.page, data.page_size);
    updateRecordCount(data.total, data.page, data.page_size);
    updateLastRefreshTime();
}

// Render records table
function renderRecords(records) {
    const tbody = document.getElementById('recordsTableBody');
    if (!tbody) return;

    if (records.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:40px;color:#666;">No records found matching the current filters</td></tr>';
        return;
    }

    tbody.innerHTML = records.map(r => {
        const typeClass = r.entity_type === 'building' ? 'badge-building' : 'badge-street';
        const typeLabel = r.entity_type === 'building' ? 'Building' : 'Street';
        return `
            <tr class="record-row" onclick="viewRecordDetail('${r.id}', '${r.entity_type}')">
                <td><span class="${typeClass}">${typeLabel}</span></td>
                <td>${escapeHtml(r.record_id)}</td>
                <td>${escapeHtml(r.lga)}</td>
                <td>${escapeHtml(r.ward || '-')}</td>
                <td>${escapeHtml(r.enumerator_username)}</td>
                <td>${formatDateTime(r.submitted_at)}</td>
                <td>${getStatusBadge(r.status)}</td>
                <td>
                    <button class="btn btn-secondary btn-icon"
                        onclick="event.stopPropagation(); viewRecordDetail('${r.id}', '${r.entity_type}')">
                        View
                    </button>
                </td>
            </tr>`;
    }).join('');
}

// Render pagination controls
function renderRecordsPagination(total, page, ps) {
    const totalPages = Math.ceil(total / ps);
    const el = document.getElementById('pagination');
    if (!el) return;
    if (totalPages <= 1) { el.innerHTML = ''; return; }

    let html = `<button ${page === 1 ? 'disabled' : ''} onclick="changePage(${page - 1})">Previous</button>`;
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= page - 2 && i <= page + 2)) {
            html += `<button class="${i === page ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
        } else if (i === page - 3 || i === page + 3) {
            html += '<span>...</span>';
        }
    }
    html += `<button ${page === totalPages ? 'disabled' : ''} onclick="changePage(${page + 1})">Next</button>`;
    el.innerHTML = html;
}

function updateRecordCount(total, page, ps) {
    const el = document.getElementById('recordCount');
    if (!el) return;
    const start = (page - 1) * ps + 1;
    const end = Math.min(page * ps, total);
    el.textContent = total > 0 ? `Showing ${start}-${end} of ${total} records` : 'No records found';
}

async function changePage(page) {
    currentPage = page;
    updateQueryParams({ ...currentFilters, page: currentPage, page_size: pageSize });
    await loadRecords();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function changePageSize() {
    const el = document.getElementById('pageSize');
    if (el) pageSize = parseInt(el.value);
    currentPage = 1;
    updateQueryParams({ ...currentFilters, page: currentPage, page_size: pageSize });
    await loadRecords();
}

function viewRecordDetail(id, entityType) {
    window.location.href = `/qa/records/${id}?entity_type=${entityType}`;
}
