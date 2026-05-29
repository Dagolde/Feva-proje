/**
 * Admin Export Task Management JavaScript module
 * Handles export creation and status polling on /admin/export
 * Requirements: 17.2, 8.1-8.6
 */

let exportTasks = [];
let exportRefreshInterval = null;

// Load export tasks
async function loadExportTasks() {
    const resp = await apiRequest('/api/v1/admin/export/tasks');
    if (!resp || !resp.ok) {
        showNotification('Failed to load export tasks', 'error');
        return;
    }
    const data = await resp.json();
    exportTasks = data.items || [];
    renderExportTasks(exportTasks);
    updateLastRefreshTime();
}

// Render export tasks table
function renderExportTasks(tasks) {
    const tbody = document.getElementById('exportTasksTableBody');
    if (!tbody) return;

    if (tasks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:40px;color:#666;">No export tasks found. Create your first export above.</td></tr>';
        return;
    }

    const sorted = [...tasks].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    tbody.innerHTML = sorted.map(task => {
        const statusClass = `status-${task.status}`;
        const filterSummary = formatFilterSummary(task.filters);
        let actions = '';

        if (task.status === 'completed') {
            actions = `<button class="btn btn-download" onclick="downloadExport('${task.id}')">Download</button>`;
        } else if (task.status === 'failed') {
            actions = `<span style="color:#c0392b;font-size:12px;" title="${escapeHtml(task.error_message || '')}">Failed</span>`;
        } else {
            actions = '<span class="spinner" style="width:20px;height:20px;"></span>';
        }

        return `
            <tr>
                <td>${escapeHtml(task.entity_type)}</td>
                <td>${task.format.toUpperCase()}</td>
                <td><div class="filter-summary">${filterSummary}</div></td>
                <td><span class="status-badge ${statusClass}">${task.status}</span></td>
                <td>${formatDateTime(task.created_at)}</td>
                <td>${task.completed_at ? formatDateTime(task.completed_at) : '-'}</td>
                <td>${actions}</td>
            </tr>`;
    }).join('');
}

// Format filter summary badges
function formatFilterSummary(filters) {
    if (!filters || !Object.keys(filters).length) return '<span style="color:#999;">No filters</span>';
    const items = [];
    if (filters.lga) items.push(`<span class="filter-item">LGA: ${escapeHtml(filters.lga)}</span>`);
    if (filters.ward) items.push(`<span class="filter-item">Ward: ${escapeHtml(filters.ward)}</span>`);
    if (filters.status) items.push(`<span class="filter-item">Status: ${escapeHtml(filters.status)}</span>`);
    if (filters.date_from) items.push(`<span class="filter-item">From: ${filters.date_from}</span>`);
    if (filters.date_to) items.push(`<span class="filter-item">To: ${filters.date_to}</span>`);
    return items.join('') || '<span style="color:#999;">No filters</span>';
}

// Handle export form submission
async function handleExportSubmit(event) {
    event.preventDefault();
    const fd = new FormData(event.target);
    const entityType = fd.get('entity_type');
    const format = fd.get('format');

    if (!entityType || !format) {
        showNotification('Please select export type and format', 'error');
        return;
    }

    const filters = {};
    if (entityType !== 'audit_log') {
        ['lga', 'ward', 'status', 'date_from', 'date_to'].forEach(k => {
            if (fd.get(k)) filters[k] = fd.get(k);
        });
    }

    const resp = await apiRequest('/api/v1/admin/export', {
        method: 'POST',
        body: JSON.stringify({ format, entity_type: entityType, filters }),
    });

    if (resp && resp.ok) {
        showNotification('Export task created', 'success');
        event.target.reset();
        document.getElementById('filterSection').style.display = 'none';
        await loadExportTasks();
    } else {
        const err = await resp.json();
        showNotification(err.detail || 'Failed to create export', 'error');
    }
}

// Download a completed export
function downloadExport(taskId) {
    window.location.href = `/api/v1/admin/export/download/${taskId}`;
    showNotification('Download started', 'success');
}

// Start auto-refresh (10s for export status polling)
function startExportAutoRefresh() {
    if (exportRefreshInterval) clearInterval(exportRefreshInterval);
    exportRefreshInterval = setInterval(loadExportTasks, 10000);
}

function stopExportAutoRefresh() {
    if (exportRefreshInterval) { clearInterval(exportRefreshInterval); exportRefreshInterval = null; }
}
