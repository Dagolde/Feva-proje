/**
 * Common JavaScript utilities for Admin and QA Dashboards
 * Provides AJAX helpers, notification system, and error handling
 * 
 * Requirements: 17.3, 17.4
 */

/**
 * Make an API request with automatic authentication and error handling
 * @param {string} url - The API endpoint URL
 * @param {Object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise<Response>} - The fetch response
 */
async function apiRequest(url, options = {}) {
    // Support both cookie-based auth and localStorage token auth
    const token = localStorage.getItem('access_token');
    
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        credentials: 'include', // Include cookies for JWT authentication
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        // Handle authentication errors
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            showNotification('Session expired. Please log in again.', 'error');
            setTimeout(() => {
                window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
            }, 2000);
            return null;
        }
        
        // Handle authorization errors
        if (response.status === 403) {
            showNotification('You do not have permission to perform this action.', 'error');
            return response;
        }
        
        return response;
    } catch (error) {
        console.error('API request error:', error);
        showNotification('Network error. Please check your connection.', 'error');
        throw error;
    }
}

/**
 * Show a notification toast message
 * @param {string} message - The message to display
 * @param {string} type - The notification type (success, error, warning, info)
 * @param {number} duration - How long to show the notification in milliseconds (default: 5000)
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Remove any existing notifications
    const existingNotification = document.getElementById('notification-toast');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'notification-toast';
    notification.className = `notification-toast notification-${type}`;
    notification.textContent = message;
    
    // Add styles if not already present
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification-toast {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 16px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 10000;
                font-size: 14px;
                font-weight: 500;
                max-width: 400px;
                animation: slideIn 0.3s ease-out;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
            
            .notification-toast.hiding {
                animation: slideOut 0.3s ease-out;
            }
            
            .notification-success {
                background: #e8f5e9;
                color: #1a6b3c;
                border-left: 4px solid #27ae60;
            }
            
            .notification-error {
                background: #fde8e8;
                color: #c0392b;
                border-left: 4px solid #c0392b;
            }
            
            .notification-warning {
                background: #fff3cd;
                color: #856404;
                border-left: 4px solid #ffc107;
            }
            
            .notification-info {
                background: #e3f2fd;
                color: #0d47a1;
                border-left: 4px solid #2196f3;
            }
            
            @media (max-width: 768px) {
                .notification-toast {
                    top: 10px;
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Add to document
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        notification.classList.add('hiding');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

/**
 * Format a date string to a readable format
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
}

/**
 * Format a datetime string to a readable format
 * @param {string} dateString - ISO datetime string
 * @returns {string} - Formatted datetime string
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

/**
 * Debounce function to limit how often a function is called
 * @param {Function} func - The function to debounce
 * @param {number} wait - The debounce delay in milliseconds
 * @returns {Function} - The debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} text - The text to escape
 * @returns {string} - The escaped HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Parse query parameters from URL
 * @returns {Object} - Object containing query parameters
 */
function getQueryParams() {
    const params = {};
    const queryString = window.location.search.substring(1);
    const pairs = queryString.split('&');
    
    for (const pair of pairs) {
        const [key, value] = pair.split('=');
        if (key) {
            params[decodeURIComponent(key)] = decodeURIComponent(value || '');
        }
    }
    
    return params;
}

/**
 * Update URL query parameters without page reload
 * @param {Object} params - Object containing query parameters to set
 */
function updateQueryParams(params) {
    const url = new URL(window.location);
    
    for (const [key, value] of Object.entries(params)) {
        if (value === null || value === undefined || value === '') {
            url.searchParams.delete(key);
        } else {
            url.searchParams.set(key, value);
        }
    }
    
    window.history.pushState({}, '', url);
}

/**
 * Confirm action with user
 * @param {string} message - The confirmation message
 * @returns {boolean} - True if user confirmed, false otherwise
 */
function confirmAction(message) {
    return confirm(message);
}

/**
 * Download a file from a blob
 * @param {Blob} blob - The blob to download
 * @param {string} filename - The filename for the download
 */
function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

/**
 * Copy text to clipboard
 * @param {string} text - The text to copy
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard', 'success', 2000);
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        showNotification('Failed to copy to clipboard', 'error');
    }
}

/**
 * Validate email format
 * @param {string} email - The email to validate
 * @returns {boolean} - True if valid, false otherwise
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate password complexity
 * @param {string} password - The password to validate
 * @returns {Object} - Object with isValid boolean and message string
 */
function validatePassword(password) {
    if (password.length < 8) {
        return {
            isValid: false,
            message: 'Password must be at least 8 characters long',
        };
    }
    
    if (!/[A-Z]/.test(password)) {
        return {
            isValid: false,
            message: 'Password must contain at least one uppercase letter',
        };
    }
    
    if (!/[a-z]/.test(password)) {
        return {
            isValid: false,
            message: 'Password must contain at least one lowercase letter',
        };
    }
    
    if (!/[0-9]/.test(password)) {
        return {
            isValid: false,
            message: 'Password must contain at least one number',
        };
    }
    
    return {
        isValid: true,
        message: 'Password is valid',
    };
}

/**
 * Format file size in human-readable format
 * @param {number} bytes - The file size in bytes
 * @returns {string} - Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Get status badge HTML
 * @param {string} status - The status value
 * @returns {string} - HTML for status badge
 */
function getStatusBadge(status) {
    const statusMap = {
        'pending': { class: 'badge-warning', text: 'Pending' },
        'approved': { class: 'badge-success', text: 'Approved' },
        'rejected': { class: 'badge-danger', text: 'Rejected' },
        'flagged': { class: 'badge-info', text: 'Flagged' },
        'active': { class: 'badge-success', text: 'Active' },
        'inactive': { class: 'badge-danger', text: 'Inactive' },
        'locked': { class: 'badge-danger', text: 'Locked' },
    };
    
    const statusInfo = statusMap[status.toLowerCase()] || { class: 'badge-info', text: status };
    return `<span class="badge ${statusInfo.class}">${statusInfo.text}</span>`;
}

/**
 * Start auto-refresh for a function at specified interval
 * @param {Function} refreshFunction - The function to call on each refresh
 * @param {number} intervalSeconds - The refresh interval in seconds
 * @returns {number} - The interval ID (can be used with clearInterval)
 */
function startAutoRefresh(refreshFunction, intervalSeconds) {
    const intervalMs = intervalSeconds * 1000;
    return setInterval(refreshFunction, intervalMs);
}

/**
 * Update last refresh time display
 * Updates an element with id 'lastRefreshTime' if it exists
 */
function updateLastRefreshTime() {
    const element = document.getElementById('lastRefreshTime');
    if (element) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
        element.textContent = `Last updated: ${timeString}`;
    }
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        apiRequest,
        showNotification,
        formatDate,
        formatDateTime,
        debounce,
        escapeHtml,
        getQueryParams,
        updateQueryParams,
        confirmAction,
        downloadBlob,
        copyToClipboard,
        isValidEmail,
        validatePassword,
        formatFileSize,
        getStatusBadge,
        startAutoRefresh,
        updateLastRefreshTime,
    };
}
