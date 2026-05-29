/**
 * QA Record Detail JavaScript module
 * Handles record detail view, approval/rejection, and audit trail on /qa/records/{id}
 * Requirements: 17.1, 11.1-11.7, 12.1-12.7, 14.1-14.4
 */

// Load complete record detail
async function loadRecordDetail(recordId, entityType) {
    const resp = await apiRequest(`/api/v1/qa/records/${recordId}?entity_type=${entityType}`);
    if (!resp || !resp.ok) {
        showNotification('Failed to load record details', 'error');
        return null;
    }
    return resp.json();
}

// Load audit trail for a record
async function loadAuditTrail(recordId, entityType) {
    const resp = await apiRequest(`/api/v1/qa/records/${recordId}/audit?entity_type=${entityType}`);
    if (!resp || !resp.ok) return null;
    return resp.json();
}

// Approve a record
async function approveRecord(recordId, entityType) {
    if (!confirm('Approve this record?')) return false;
    const resp = await apiRequest(`/api/v1/qa/records/${recordId}/approve?entity_type=${entityType}`, { method: 'POST' });
    if (resp && resp.ok) {
        showNotification('Record approved successfully', 'success');
        return true;
    }
    const err = await resp.json();
    showNotification(err.detail || 'Failed to approve record', 'error');
    return false;
}

// Reject a record with a reason
async function rejectRecord(recordId, entityType, reason) {
    if (!reason || !reason.trim()) {
        showNotification('Rejection reason is required', 'error');
        return false;
    }
    const resp = await apiRequest(`/api/v1/qa/records/${recordId}/reject?entity_type=${entityType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rejection_reason: reason.trim() }),
    });
    if (resp && resp.ok) {
        showNotification('Record rejected', 'success');
        return true;
    }
    const err = await resp.json();
    showNotification(err.detail || 'Failed to reject record', 'error');
    return false;
}

// Render field data as a definition list
function renderFieldData(data) {
    if (!data || typeof data !== 'object') return '<p style="color:#666;">No field data available</p>';
    return Object.entries(data).map(([key, val]) => {
        const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        const display = val == null ? '<em style="color:#999;">—</em>' : escapeHtml(String(val));
        return `<div style="display:flex;gap:16px;padding:8px 0;border-bottom:1px solid #f0f0f0;">
            <dt style="width:200px;flex-shrink:0;font-weight:500;color:#555;">${label}</dt>
            <dd style="margin:0;color:#333;">${display}</dd>
        </div>`;
    }).join('');
}

// Render audit trail entries
function renderAuditTrail(entries) {
    if (!entries || entries.length === 0) {
        return '<p style="color:#666;padding:16px 0;">No audit trail entries</p>';
    }
    return entries.map(e => {
        const action = e.action.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        return `
            <div style="padding:12px 0;border-bottom:1px solid #eee;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <strong style="font-size:14px;">${action}</strong>
                    <span style="font-size:12px;color:#999;">${formatDateTime(e.timestamp)}</span>
                </div>
                <div style="font-size:13px;color:#555;">by ${escapeHtml(e.user)}</div>
                ${e.detail && Object.keys(e.detail).length ? `<div style="font-size:12px;color:#888;margin-top:4px;">${escapeHtml(JSON.stringify(e.detail))}</div>` : ''}
            </div>`;
    }).join('');
}
