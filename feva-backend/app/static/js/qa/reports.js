/**
 * QA Reports JavaScript module
 * Handles report generation and statistics display on /qa/reports
 * Requirements: 17.1, 13.1-13.6
 */

let reportFilters = {};

// Apply report filters
function applyReportFilters() {
    reportFilters = {};
    const lga = document.getElementById('filterLga')?.value.trim();
    const ward = document.getElementById('filterWard')?.value.trim();
    const startDate = document.getElementById('filterStartDate')?.value;
    const endDate = document.getElementById('filterEndDate')?.value;

    if (lga) reportFilters.lga = lga;
    if (ward) reportFilters.ward = ward;
    if (startDate) reportFilters.start_date = startDate;
    if (endDate) reportFilters.end_date = endDate;

    loadReportData();
}

// Clear report filters
function clearReportFilters() {
    ['filterLga', 'filterWard', 'filterStartDate', 'filterEndDate'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    reportFilters = {};
    loadReportData();
}

// Load statistics from API
async function loadReportData() {
    const params = new URLSearchParams(reportFilters);
    const resp = await apiRequest(`/api/v1/qa/statistics?${params}`);
    if (!resp || !resp.ok) {
        showNotification('Failed to load report data', 'error');
        return;
    }
    const data = await resp.json();
    renderReportSummary(data);
    renderEnumeratorRates(data.approval_rate_by_enumerator);
    renderDailyVolumes(data.daily_volumes);
    updateLastRefreshTime();
}

// Render summary stat cards
function renderReportSummary(data) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('totalRecords', data.total_records ?? '--');
    set('pendingRecords', data.pending_records ?? '--');
    set('approvedRecords', data.approved_records ?? '--');
    set('rejectedRecords', data.rejected_records ?? '--');

    const reviewed = (data.approved_records || 0) + (data.rejected_records || 0);
    const rate = reviewed > 0 ? Math.round((data.approved_records / reviewed) * 100) : null;
    set('overallApprovalRate', rate !== null ? `${rate}%` : 'N/A');

    const avgSecs = data.average_review_time_seconds;
    set('avgReviewTime', avgSecs != null ? formatReviewDuration(avgSecs) : 'N/A');
}

// Render enumerator approval rate table
function renderEnumeratorRates(rateByEnumerator) {
    const tbody = document.getElementById('enumeratorTableBody');
    if (!tbody) return;

    const entries = Object.entries(rateByEnumerator || {});
    if (entries.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;padding:24px;color:#666;">No enumerator data available</td></tr>';
        return;
    }

    entries.sort((a, b) => b[1] - a[1]);
    tbody.innerHTML = entries.map(([username, rate]) => {
        const pct = Math.round(rate * 100);
        const color = pct >= 80 ? '#27ae60' : pct >= 50 ? '#f39c12' : '#c0392b';
        return `
            <tr>
                <td style="font-size:13px;">${escapeHtml(username)}</td>
                <td style="font-weight:600;color:${color};">${pct}%</td>
                <td>
                    <div style="background:#f0f0f0;border-radius:4px;height:14px;overflow:hidden;">
                        <div style="width:${pct}%;height:100%;background:${color};border-radius:4px;transition:width 0.4s;"></div>
                    </div>
                </td>
            </tr>`;
    }).join('');
}

// Render daily volume chart
function renderDailyVolumes(dailyVolumes) {
    const container = document.getElementById('dailyVolumeChart');
    if (!container) return;

    if (!dailyVolumes || dailyVolumes.length === 0) {
        container.innerHTML = '<p style="color:#666;text-align:center;padding:40px 0;">No daily volume data available</p>';
        return;
    }

    const volumes = dailyVolumes.slice(-14);
    const maxVal = Math.max(...volumes.map(v => Math.max(v.submitted, v.reviewed)), 1);

    const legend = `
        <div style="display:flex;gap:16px;margin-bottom:12px;font-size:12px;">
            <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#2980b9;margin-right:4px;"></span>Submitted</span>
            <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#27ae60;margin-right:4px;"></span>Reviewed</span>
        </div>`;

    const rows = volumes.map(v => {
        const sPct = Math.round((v.submitted / maxVal) * 100);
        const rPct = Math.round((v.reviewed / maxVal) * 100);
        const label = formatShortDate(v.date);
        return `
            <div style="margin-bottom:10px;">
                <div style="font-size:11px;color:#888;margin-bottom:3px;">${escapeHtml(label)}</div>
                <div style="display:flex;align-items:center;gap:8px;font-size:12px;">
                    <div style="flex:1;background:#f0f0f0;border-radius:4px;height:16px;overflow:hidden;">
                        <div style="width:${sPct}%;height:100%;background:#2980b9;border-radius:4px;transition:width 0.4s;"></div>
                    </div>
                    <span style="width:36px;color:#2980b9;font-weight:500;">${v.submitted}</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px;font-size:12px;margin-top:3px;">
                    <div style="flex:1;background:#f0f0f0;border-radius:4px;height:16px;overflow:hidden;">
                        <div style="width:${rPct}%;height:100%;background:#27ae60;border-radius:4px;transition:width 0.4s;"></div>
                    </div>
                    <span style="width:36px;color:#27ae60;font-weight:500;">${v.reviewed}</span>
                </div>
            </div>`;
    }).join('');

    container.innerHTML = legend + rows;
}

// Format seconds to human-readable duration
function formatReviewDuration(seconds) {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${(seconds / 3600).toFixed(1)}h`;
}

// Format ISO date to short label
function formatShortDate(dateStr) {
    try {
        return new Date(dateStr).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
    } catch { return dateStr; }
}
