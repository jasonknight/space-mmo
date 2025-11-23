/**
 * Control Panel - Main App Module
 * Handles routing, notifications, and shared utilities
 */

var App = (function() {
    'use strict';

    // Current view state
    let currentView = 'items';

    // Enum cache
    let enums = {};

    /**
     * Initialize the app
     */
    function init() {
        console.log('Initializing Control Panel...');

        // Load enums
        loadEnums();

        // Set up navigation
        setupNavigation();

        // Load initial view
        loadView('items');
    }

    /**
     * Load enum definitions from the server
     */
    function loadEnums() {
        $.ajax({
            url: '/api/enums',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    enums = response.enums;
                    console.log('Enums loaded:', enums);
                } else {
                    showError('Failed to load enum definitions');
                }
            },
            error: function(xhr, status, error) {
                showError('Failed to load enum definitions: ' + error);
            },
        });
    }

    /**
     * Get enum definitions
     */
    function getEnums() {
        return enums;
    }

    /**
     * Get enum name from value
     */
    function getEnumName(enumType, value) {
        if (!enums[enumType]) return value;
        for (let name in enums[enumType]) {
            if (enums[enumType][name] === value) {
                return name;
            }
        }
        return value;
    }

    /**
     * Set up navigation click handlers
     */
    function setupNavigation() {
        $('.navbar-nav .nav-link').on('click', function(e) {
            e.preventDefault();

            // Don't handle disabled links
            if ($(this).hasClass('disabled')) {
                return;
            }

            let view = $(this).data('view');

            // Update active nav item
            $('.navbar-nav .nav-link').removeClass('active');
            $(this).addClass('active');

            // Load the view
            loadView(view);
        });
    }

    /**
     * Load a specific view
     */
    function loadView(view) {
        currentView = view;
        console.log('Loading view:', view);

        // Clear content
        $('#content').html('');

        // Load the appropriate view
        switch(view) {
            case 'items':
                if (typeof ItemModule !== 'undefined') {
                    ItemModule.init();
                }
                break;
            case 'inventories':
                if (typeof InventoryModule !== 'undefined') {
                    InventoryModule.init();
                } else {
                    $('#content').html('<div class="alert alert-danger">Inventory module not loaded</div>');
                }
                break;
            case 'players':
                // TODO: Load players view
                $('#content').html('<div class="alert alert-info">Player management coming soon...</div>');
                break;
            default:
                $('#content').html('<div class="alert alert-warning">Unknown view</div>');
        }
    }

    /**
     * Show loading overlay
     */
    function showLoading() {
        $('#loading-overlay').show();
    }

    /**
     * Hide loading overlay
     */
    function hideLoading() {
        $('#loading-overlay').hide();
    }

    /**
     * Show a success notification
     */
    function showSuccess(message) {
        showNotification(message, 'success');
    }

    /**
     * Show an error notification
     */
    function showError(message) {
        showNotification(message, 'danger');
    }

    /**
     * Show an info notification
     */
    function showInfo(message) {
        showNotification(message, 'info');
    }

    /**
     * Show a notification toast
     */
    function showNotification(message, type) {
        let toast = $('#notification-toast');
        let toastBody = toast.find('.toast-body');
        let toastHeader = toast.find('.toast-header');

        // Update icon based on type
        let icon = 'bi-info-circle-fill';
        if (type === 'success') {
            icon = 'bi-check-circle-fill text-success';
        } else if (type === 'danger') {
            icon = 'bi-exclamation-triangle-fill text-danger';
        } else if (type === 'warning') {
            icon = 'bi-exclamation-circle-fill text-warning';
        }

        toastHeader.find('i').attr('class', icon + ' me-2');
        toastBody.text(message);

        // Show the toast
        let bsToast = new bootstrap.Toast(toast[0]);
        bsToast.show();
    }

    /**
     * Confirm an action with a Bootstrap modal
     */
    function confirm(message, callback) {
        if (window.confirm(message)) {
            callback();
        }
    }

    /**
     * Format a date string
     */
    function formatDate(dateStr) {
        if (!dateStr) return '';
        let date = new Date(dateStr);
        return date.toLocaleString();
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        if (text == null) return '';
        let map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;',
        };
        return String(text).replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    /**
     * Truncate text to a maximum length
     */
    function truncate(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    /**
     * Deep clone an object
     */
    function clone(obj) {
        return JSON.parse(JSON.stringify(obj));
    }

    /**
     * Check if an object is empty
     */
    function isEmpty(obj) {
        if (obj == null) return true;
        if (Array.isArray(obj) || typeof obj === 'string') {
            return obj.length === 0;
        }
        return Object.keys(obj).length === 0;
    }

    // Public API
    return {
        init: init,
        loadView: loadView,
        showLoading: showLoading,
        hideLoading: hideLoading,
        showSuccess: showSuccess,
        showError: showError,
        showInfo: showInfo,
        confirm: confirm,
        formatDate: formatDate,
        escapeHtml: escapeHtml,
        truncate: truncate,
        clone: clone,
        isEmpty: isEmpty,
        getEnums: getEnums,
        getEnumName: getEnumName,
    };
})();
