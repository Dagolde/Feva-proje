/**
 * Admin Monitoring JavaScript module
 * Handles real-time monitoring updates on /admin/monitoring
 * Requirements: 17.2, 9.1-9.4, 9.6
 */

// Load system health metrics
async function loadHealthMetrics() {
    const resp = await apiRequest('/api/v1/admin/monitoring/health');
    if (!resp || !resp.ok) return;
    const data = await resp.json();

    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('dbStatus', data.database || '--');
    set('diskSpace', data.disk_space_gb != null ? `${data.disk_space_gb.toFixed(1)} GB` : '--');
    set('uptime', data.uptime_seconds != null ? formatUptime(data.uptime_seconds) : '--');
}

// Load record statistics
async function loadRecordStatistics() {
    const resp = await apiRequest('/api/v1/admin/monitoring/statistics');
    if (!resp || !resp.ok) return;
    const data = await resp.json();

    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    const byStatus = data.records_by_status || {};
    set('statPending', byStatus.pending ?? 0);
    set('statApproved', byStatus.approved ?? 0);
    set('statRejected', byStatus.rejected ?? 0);

    const byRole = data.users_by_role || {};
    set('statAdmins', byRole.admin ?? 0);
    set('statEnumerators', byRole.enumerator ?? 0);
    set('statSupervisors', byRole.supervisor ?? 0);
    set('statQaOfficers', byRole.qa_officer ?? 0);
}

// Load sync sessions
async function loadSyncSessions(page = 1, pageSize = 50, statusFilter = '') {
    const params = new URLSearchParams({ page, page_size: pageSize });
    if (statusFilter) params.set('status', statusFilter);

    const resp = await apiRequest(`/api/v1/admin/monitoring/sync-sessions?${params}`);
    if (!resp || !resp.ok) {
        showNotification('Failed to load sync sessions', 'error');
        return;
    }
    const data = await resp.json();
    renderSyncSessions(data.items || []);
    updateLastRefreshTime();
}

// Render sync sessions table
function renderSyncSessions(sessions) {
    const tbody = document.getElementById('syncSessionsTableBody');
    if (!tbody) return;

    if (sessions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:32px;color:#666;">No sync sessions found</td></tr>';
        return;
    }

    tbody.innerHTML = sessions.map(s => {
        const statusClass = s.status === 'completed' ? 'badge-success' : s.status === 'failed' ? 'badge-danger' : 'badge-warning';
        return `
            <tr>
                <td>${escapeHtml(s.device_id || '--')}</td>
                <td>${escapeHtml(s.username || '--')}</td>
                <td>${formatDateTime(s.started_at)}</td>
                <td>${s.completed_at ? formatDateTime(s.completed_at) : '--'}</td>
                <td><span class="badge ${statusClass}">${s.status}</span></td>
                <td>${s.records_synced ?? '--'}</td>
            </tr>`;
    }).join('');
}

// Refresh all monitoring data
async function refreshMonitoring() {
    await Promise.all([loadHealthMetrics(), loadRecordStatistics(), loadSyncSessions()]);
    updateLastRefreshTime();
}

// Format uptime seconds to human-readable
function formatUptime(seconds) {
    const d = Math.floor(seconds / 86400);
    const h = Math.floor((seconds % 86400) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (d > 0) return `${d}d ${h}h ${m}m`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
}
