/**
 * Admin Shapefile Management JavaScript module
 * Handles shapefile upload and version management on /admin/shapefiles
 * Requirements: 17.2, 7.1-7.5
 */

let shapefileVersions = [];

// Load shapefile versions
async function loadShapefileVersions() {
    const resp = await apiRequest('/api/v1/admin/shapefiles');
    if (!resp || !resp.ok) {
        showNotification('Failed to load shapefile versions', 'error');
        return;
    }
    shapefileVersions = await resp.json();
    renderShapefileTable(shapefileVersions);
}

// Render shapefile versions table
function renderShapefileTable(versions) {
    const tbody = document.getElementById('shapefileTableBody');
    if (!tbody) return;

    if (versions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:32px;color:#666;">No shapefile versions uploaded yet</td></tr>';
        return;
    }

    tbody.innerHTML = versions.map(v => {
        const uploadedDate = formatDateTime(v.uploaded_at);
        const activeClass = v.active ? 'badge-success' : 'badge-info';
        const activeText = v.active ? 'Active' : 'Inactive';

        return `
            <tr>
                <td>${escapeHtml(v.layer || v.layer_name || '--')}</td>
                <td>${escapeHtml(v.version || v.version_tag || '--')}</td>
                <td>${uploadedDate}</td>
                <td>${v.features_written ?? '--'}</td>
                <td><span class="badge ${activeClass}">${activeText}</span></td>
                <td>
                    ${!v.active ? `<button class="btn btn-secondary btn-icon" onclick="activateShapefile(${v.id})">Activate</button>` : '<span style="color:#999;font-size:12px;">Current</span>'}
                </td>
            </tr>`;
    }).join('');
}

// Handle shapefile upload form submission
async function handleShapefileUpload(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Uploading...'; }

    try {
        const resp = await fetch('/api/v1/admin/shapefiles', {
            method: 'POST',
            credentials: 'include',
            body: formData,  // multipart/form-data — do NOT set Content-Type header
        });

        if (resp.ok) {
            const data = await resp.json();
            showNotification(`Shapefile uploaded: ${data.features_written ?? 0} features written`, 'success');
            form.reset();
            await loadShapefileVersions();
        } else {
            const err = await resp.json();
            showNotification(err.detail || 'Upload failed', 'error');
        }
    } catch (err) {
        console.error('Shapefile upload error:', err);
        showNotification('Upload failed — network error', 'error');
    } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Upload Shapefile'; }
    }
}

// Activate a shapefile version
async function activateShapefile(id) {
    const resp = await apiRequest(`/api/v1/admin/shapefiles/${id}/activate`, { method: 'PATCH' });
    if (resp && resp.ok) {
        showNotification('Shapefile version activated', 'success');
        await loadShapefileVersions();
    } else {
        const err = await resp.json();
        showNotification(err.detail || 'Failed to activate shapefile', 'error');
    }
}
