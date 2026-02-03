// ========================================
// MAIN JAVASCRIPT FILE - Utilities and Helpers
// ========================================
// This file contains JavaScript functions used throughout the application
// It provides form validation, AJAX helpers, and utility functions

// ===== FORM VALIDATION =====
/**
 * Initialize Bootstrap form validation
 * Adds validation feedback to all forms with 'needs-validation' class
 */
function initializeFormValidation() {
    // Get all forms with validation class
    const forms = document.querySelectorAll('.needs-validation');
    
    // Add validation to each form
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            // Check if form is valid
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            // Add validation class to show feedback
            form.classList.add('was-validated');
        });
    });
}

// ===== ALERT/NOTIFICATION HELPERS =====
/**
 * Show a success notification
 * @param {string} message - The message to display
 * @param {number} duration - How long to show the alert (milliseconds)
 */
function showSuccess(message, duration = 3000) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
        <i class="fas fa-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add alert to top of page
    document.body.insertBefore(alert, document.body.firstChild);
    
    // Auto-dismiss after duration
    if (duration > 0) {
        setTimeout(() => {
            alert.remove();
        }, duration);
    }
}

/**
 * Show an error notification
 * @param {string} message - The error message to display
 * @param {number} duration - How long to show the alert (milliseconds)
 */
function showError(message, duration = 5000) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
        <i class="fas fa-exclamation-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add alert to top of page
    document.body.insertBefore(alert, document.body.firstChild);
    
    // Auto-dismiss after duration
    if (duration > 0) {
        setTimeout(() => {
            alert.remove();
        }, duration);
    }
}

/**
 * Show an info notification
 * @param {string} message - The message to display
 */
function showInfo(message) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = 'alert alert-info alert-dismissible fade show';
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
        <i class="fas fa-info-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add alert to page
    document.body.insertBefore(alert, document.body.firstChild);
}

// ===== AJAX HELPERS =====
/**
 * Make an AJAX POST request
 * @param {string} url - The URL to post to
 * @param {object} data - The data to send
 * @param {function} successCallback - Function to call on success
 * @param {function} errorCallback - Function to call on error
 */
function postRequest(url, data, successCallback, errorCallback) {
    // Make the AJAX request using jQuery
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        dataType: 'json',
        success: function(response) {
            // Call success callback with response
            if (successCallback) {
                successCallback(response);
            }
        },
        error: function(xhr, status, error) {
            // Call error callback with error info
            if (errorCallback) {
                errorCallback(error);
            } else {
                // Show default error message
                showError('An error occurred. Please try again.');
            }
        }
    });
}

/**
 * Make an AJAX GET request
 * @param {string} url - The URL to get from
 * @param {function} successCallback - Function to call on success
 * @param {function} errorCallback - Function to call on error
 */
function getRequest(url, successCallback, errorCallback) {
    // Make the AJAX request
    $.ajax({
        type: 'GET',
        url: url,
        dataType: 'json',
        success: function(response) {
            if (successCallback) {
                successCallback(response);
            }
        },
        error: function(xhr, status, error) {
            if (errorCallback) {
                errorCallback(error);
            } else {
                showError('An error occurred. Please try again.');
            }
        }
    });
}

// ===== CONFIRMATION DIALOGS =====
/**
 * Show a confirmation dialog before performing an action
 * @param {string} message - The confirmation message
 * @param {function} onConfirm - Function to call if user confirms
 * @param {function} onCancel - Function to call if user cancels
 */
function confirmAction(message, onConfirm, onCancel) {
    // Use Bootstrap modal for confirmation
    const modalHtml = `
        <div class="modal fade" id="confirmModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Action</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirmBtn">Confirm</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
    modal.show();
    
    // Handle confirm button
    document.getElementById('confirmBtn').addEventListener('click', function() {
        modal.hide();
        if (onConfirm) onConfirm();
        // Remove modal
        document.getElementById('confirmModal').remove();
    });
    
    // Handle cancel
    document.getElementById('confirmModal').addEventListener('hidden.bs.modal', function() {
        if (onCancel) onCancel();
        this.remove();
    });
}

// ===== TABLE UTILITIES =====
/**
 * Make a table row highlight on hover
 * @param {element} table - The table element
 */
function initializeTableHover(table) {
    // Get all rows in table body
    const rows = table.querySelectorAll('tbody tr');
    
    // Add hover effect to each row
    rows.forEach(row => {
        row.style.cursor = 'pointer';
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fc';
        });
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
        });
    });
}

// ===== LOADING SPINNER =====
/**
 * Show a loading spinner
 * Useful for AJAX requests
 */
function showLoadingSpinner() {
    // Create spinner HTML
    const spinner = document.createElement('div');
    spinner.id = 'loadingSpinner';
    spinner.className = 'spinner-border';
    spinner.setAttribute('role', 'status');
    spinner.innerHTML = '<span class="visually-hidden">Loading...</span>';
    
    // Add to page
    document.body.appendChild(spinner);
}

/**
 * Hide the loading spinner
 */
function hideLoadingSpinner() {
    // Find and remove spinner
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.remove();
    }
}

// ===== DATE FORMATTING =====
/**
 * Format a date to readable format
 * @param {string} dateString - The date string to format
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    // Create date object from string
    const date = new Date(dateString);
    
    // Format options
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    // Return formatted date
    return date.toLocaleDateString('en-US', options);
}

// ===== COPY TO CLIPBOARD =====
/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 */
function copyToClipboard(text) {
    // Create temporary input element
    const input = document.createElement('input');
    input.value = text;
    document.body.appendChild(input);
    
    // Select and copy text
    input.select();
    document.execCommand('copy');
    
    // Remove temporary input
    document.body.removeChild(input);
    
    // Show success message
    showSuccess('Copied to clipboard!', 2000);
}

// ===== INITIALIZATION =====
/**
 * Run initialization functions when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        // Initialize all tooltips on page
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// ===== EXPORT FUNCTIONS FOR EXTERNAL USE =====
// These functions can be called from other files

// Make functions globally available
window.showSuccess = showSuccess;
window.showError = showError;
window.showInfo = showInfo;
window.postRequest = postRequest;
window.getRequest = getRequest;
window.confirmAction = confirmAction;
window.copyToClipboard = copyToClipboard;
window.formatDate = formatDate;
