/**
 * Control Panel - Mobile Module
 * Handles all NPC Mobile CRUD operations with Attributes
 */

var MobileModule = (function() {
    'use strict';

    // State
    let currentPage = 1;
    let mobilesPerPage = 10;
    let searchQuery = '';
    let editingMobile = null;
    let currentMobileAttributes = {};

    /**
     * Initialize the Mobile module
     */
    function init() {
        console.log('Initializing Mobile module...');
        renderListView();
    }

    // ========================================================================
    // List View
    // ========================================================================

    /**
     * Render the list view
     */
    function renderListView() {
        let html = `
            <div class="row mb-3">
                <div class="col">
                    <h2><i class="bi bi-person-bounding-box"></i> NPC Mobiles</h2>
                </div>
                <div class="col-auto">
                    <button class="btn btn-primary" id="create-mobile-btn">
                        <i class="bi bi-plus-circle"></i> Create NPC
                    </button>
                </div>
            </div>

            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-search"></i></span>
                        <input
                            type="text"
                            class="form-control"
                            id="mobile-search-input"
                            placeholder="Search by name..."
                            value="${App.escapeHtml(searchQuery)}"
                        >
                        <button class="btn btn-primary" type="button" id="search-btn">
                            Search
                        </button>
                        <button class="btn btn-outline-secondary" type="button" id="clear-search-btn">
                            Clear
                        </button>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="input-group">
                        <span class="input-group-text">Per Page:</span>
                        <select class="form-select" id="mobiles-per-page-select">
                            <option value="5" ${mobilesPerPage === 5 ? 'selected' : ''}>5</option>
                            <option value="10" ${mobilesPerPage === 10 ? 'selected' : ''}>10</option>
                            <option value="20" ${mobilesPerPage === 20 ? 'selected' : ''}>20</option>
                            <option value="50" ${mobilesPerPage === 50 ? 'selected' : ''}>50</option>
                            <option value="100" ${mobilesPerPage === 100 ? 'selected' : ''}>100</option>
                        </select>
                    </div>
                </div>
            </div>

            <div id="mobiles-table-container">
                <!-- Table will be rendered here -->
            </div>

            <div id="pagination-container" class="mt-3">
                <!-- Pagination will be rendered here -->
            </div>
        `;

        $('#content').html(html);

        // Set up event handlers
        $('#create-mobile-btn').on('click', function() {
            editingMobile = null;
            renderFormView();
        });

        $('#search-btn').on('click', function() {
            searchQuery = $('#mobile-search-input').val();
            currentPage = 1;
            loadMobiles();
        });

        $('#mobile-search-input').on('keyup', function(e) {
            if (e.key === 'Enter') {
                searchQuery = $(this).val();
                currentPage = 1;
                loadMobiles();
            }
        });

        $('#clear-search-btn').on('click', function() {
            searchQuery = '';
            $('#mobile-search-input').val('');
            currentPage = 1;
            loadMobiles();
        });

        $('#mobiles-per-page-select').on('change', function() {
            mobilesPerPage = parseInt($(this).val());
            currentPage = 1;
            loadMobiles();
        });

        // Load mobiles
        loadMobiles();
    }

    /**
     * Load mobiles from the server
     */
    function loadMobiles() {
        App.showLoading();

        $.ajax({
            url: '/api/mobiles',
            method: 'GET',
            data: {
                page: currentPage - 1,
                per_page: mobilesPerPage,
                search: searchQuery,
            },
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    renderMobilesTable(response.mobiles, response.total_count);
                } else {
                    App.showError('Failed to load mobiles: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load mobiles: ' + error);
            },
        });
    }

    /**
     * Render the mobiles table
     */
    function renderMobilesTable(mobiles, totalCount) {
        let html = '';

        if (mobiles.length === 0) {
            html = '<div class="alert alert-info">No NPC mobiles found.</div>';
        } else {
            html = `
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Type</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            mobiles.forEach(function(mobile) {
                html += `
                    <tr>
                        <td>${mobile.id || 'N/A'}</td>
                        <td><strong>${App.escapeHtml(mobile.what_we_call_you)}</strong></td>
                        <td><span class="badge bg-info">NPC</span></td>
                        <td>
                            <button class="btn btn-sm btn-primary show-mobile-btn" data-mobile-id="${mobile.id}">
                                <i class="bi bi-eye"></i> Show
                            </button>
                            <button class="btn btn-sm btn-outline-primary edit-mobile-btn" data-mobile-id="${mobile.id}">
                                <i class="bi bi-pencil"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-mobile-btn" data-mobile-id="${mobile.id}">
                                <i class="bi bi-trash"></i> Delete
                            </button>
                        </td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                    </table>
                </div>
            `;
        }

        $('#mobiles-table-container').html(html);

        // Set up action button handlers
        $('.show-mobile-btn').on('click', function() {
            let mobileId = $(this).data('mobile-id');
            loadMobileForShow(mobileId);
        });

        $('.edit-mobile-btn').on('click', function() {
            let mobileId = $(this).data('mobile-id');
            loadMobileForEdit(mobileId);
        });

        $('.delete-mobile-btn').on('click', function() {
            let mobileId = $(this).data('mobile-id');
            deleteMobile(mobileId);
        });

        // Render pagination
        renderPagination(totalCount);
    }

    /**
     * Render pagination controls
     */
    function renderPagination(totalCount) {
        let totalPages = Math.ceil(totalCount / mobilesPerPage);

        if (totalPages <= 1) {
            $('#pagination-container').html('');
            return;
        }

        let html = '<nav><ul class="pagination justify-content-center">';

        // Previous button
        html += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>
            </li>
        `;

        // Page numbers
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, currentPage + 2);

        if (startPage > 1) {
            html += '<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>';
            if (startPage > 2) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }

        // Next button
        html += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>
            </li>
        `;

        html += '</ul></nav>';

        $('#pagination-container').html(html);

        // Set up pagination handlers
        $('.page-link').on('click', function(e) {
            e.preventDefault();
            let page = $(this).data('page');
            if (page && page !== currentPage) {
                currentPage = page;
                loadMobiles();
            }
        });
    }

    // ========================================================================
    // Form View (Create/Edit)
    // ========================================================================

    /**
     * Render the create/edit form
     */
    function renderFormView() {
        let isEdit = editingMobile !== null;
        let title = isEdit ? 'Edit NPC Mobile' : 'Create NPC Mobile';
        let mobile = editingMobile || {};

        // Initialize mobile attributes from editing mobile
        if (isEdit && mobile.attributes) {
            currentMobileAttributes = App.clone(mobile.attributes);
        } else {
            currentMobileAttributes = {};
        }

        let html = `
            <div class="row mb-3">
                <div class="col">
                    <h2><i class="bi bi-${isEdit ? 'pencil' : 'plus-circle'}"></i> ${title}</h2>
                </div>
                <div class="col-auto">
                    <button class="btn btn-secondary" id="cancel-form-btn">
                        <i class="bi bi-x-circle"></i> Cancel
                    </button>
                </div>
            </div>

            <form id="mobile-form">
                <!-- Hidden ID field -->
                <input type="hidden" id="mobile-id" value="${mobile.id || ''}">

                <!-- Mobile Information Card -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5><i class="bi bi-person-badge"></i> NPC Information</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="mobile-name" class="form-label">NPC Name *</label>
                                <input
                                    type="text"
                                    class="form-control"
                                    id="mobile-name"
                                    required
                                    value="${App.escapeHtml(mobile.what_we_call_you || '')}"
                                >
                                <div class="form-text">The name of this NPC (Fantasy or Sci-fi style)</div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Mobile Type</label>
                                <div class="mt-2">
                                    <span class="badge bg-info">NPC (Non-Player Character)</span>
                                </div>
                                <div class="form-text">Type is automatically set to NPC</div>
                            </div>
                        </div>

                        <hr>

                        <h6>Character Attributes</h6>
                        <button type="button" class="btn btn-success mb-3" id="add-attribute-btn">
                            <i class="bi bi-plus"></i> Add Attribute
                        </button>
                        <div id="attributes-container">
                            <!-- Attributes table will be rendered here -->
                        </div>
                    </div>
                </div>

                <!-- Submit Button -->
                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                    <button type="button" class="btn btn-secondary me-md-2" id="cancel-form-btn-bottom">
                        Cancel
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-save"></i> ${isEdit ? 'Update' : 'Create'} NPC
                    </button>
                </div>
            </form>
        `;

        $('#content').html(html);

        // Render attributes
        renderMobileAttributesTable();

        // Set up event handlers
        setupFormHandlers();
    }

    /**
     * Set up form event handlers
     */
    function setupFormHandlers() {
        // Cancel buttons
        $('#cancel-form-btn, #cancel-form-btn-bottom').on('click', function() {
            renderListView();
        });

        // Form submission
        $('#mobile-form').on('submit', function(e) {
            e.preventDefault();
            saveMobile();
        });

        // Add attribute button
        $('#add-attribute-btn').on('click', function() {
            addMobileAttribute();
        });
    }

    // ========================================================================
    // Mobile Attributes Management
    // ========================================================================

    /**
     * Render the mobile attributes table
     */
    function renderMobileAttributesTable() {
        let html = '';

        if (Object.keys(currentMobileAttributes).length === 0) {
            html = '<div class="alert alert-info">No attributes added yet.</div>';
        } else {
            html = `
                <div class="table-responsive">
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Internal Name</th>
                                <th>Visible</th>
                                <th>Value</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            for (let attrTypeKey in currentMobileAttributes) {
                let attr = currentMobileAttributes[attrTypeKey];
                let attrTypeName = App.getEnumName('AttributeType', attr.attribute_type);
                let valueDisplay = getAttributeValueDisplay(attr.value);

                html += `
                    <tr>
                        <td><span class="badge bg-secondary">${attrTypeName}</span></td>
                        <td>${App.escapeHtml(attr.internal_name)}</td>
                        <td>${attr.visible ? 'Yes' : 'No'}</td>
                        <td>${valueDisplay}</td>
                        <td>
                            <button
                                type="button"
                                class="btn btn-sm btn-outline-danger remove-attr-btn"
                                data-attr-type="${attrTypeKey}"
                            >
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            }

            html += `
                        </tbody>
                    </table>
                </div>
            `;
        }

        $('#attributes-container').html(html);

        // Set up handlers
        $('.remove-attr-btn').on('click', function() {
            let attrType = $(this).data('attr-type');
            delete currentMobileAttributes[attrType];
            renderMobileAttributesTable();
        });
    }

    /**
     * Get display string for an attribute value
     */
    function getAttributeValueDisplay(value) {
        if (!value) return 'N/A';

        if (value.bool_value !== undefined) {
            return value.bool_value ? 'true' : 'false';
        } else if (value.double_value !== undefined) {
            return value.double_value.toString();
        } else if (value.vector3 !== undefined) {
            let v = value.vector3;
            return `(${v.x}, ${v.y}, ${v.z})`;
        } else if (value.asset_id !== undefined) {
            return `Asset ID: ${value.asset_id}`;
        }

        return 'N/A';
    }

    /**
     * Add a new mobile attribute
     */
    function addMobileAttribute() {
        // Create a simple form inline
        let enums = App.getEnums();
        let attrTypeOptions = '';

        for (let name in enums.AttributeType) {
            let value = enums.AttributeType[name];
            attrTypeOptions += `<option value="${value}">${name}</option>`;
        }

        let html = `
            <div class="card mb-2" id="new-attribute-form">
                <div class="card-body">
                    <h6>New Attribute</h6>
                    <div class="row g-2">
                        <div class="col-md-3">
                            <label class="form-label">Type</label>
                            <select class="form-select form-select-sm" id="new-attr-type">
                                ${attrTypeOptions}
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">Internal Name</label>
                            <input type="text" class="form-control form-control-sm" id="new-attr-internal-name">
                        </div>
                        <div class="col-md-2">
                            <label class="form-label">Visible</label>
                            <select class="form-select form-select-sm" id="new-attr-visible">
                                <option value="true">Yes</option>
                                <option value="false">No</option>
                            </select>
                        </div>
                        <div class="col-md-2">
                            <label class="form-label">Value Type</label>
                            <select class="form-select form-select-sm" id="new-attr-value-type">
                                <option value="bool">Bool</option>
                                <option value="double" selected>Double</option>
                                <option value="vector3">Vector3</option>
                                <option value="asset_id">Asset ID</option>
                            </select>
                        </div>
                        <div class="col-md-2">
                            <label class="form-label">Value</label>
                            <input type="text" class="form-control form-control-sm" id="new-attr-value" placeholder="Enter value">
                        </div>
                    </div>
                    <div class="mt-2">
                        <button type="button" class="btn btn-sm btn-primary" id="save-new-attr-btn">Save</button>
                        <button type="button" class="btn btn-sm btn-secondary" id="cancel-new-attr-btn">Cancel</button>
                    </div>
                </div>
            </div>
        `;

        $('#attributes-container').prepend(html);

        $('#save-new-attr-btn').on('click', function() {
            saveMobileAttribute();
        });

        $('#cancel-new-attr-btn').on('click', function() {
            $('#new-attribute-form').remove();
        });
    }

    /**
     * Save the new mobile attribute
     */
    function saveMobileAttribute() {
        let attrType = parseInt($('#new-attr-type').val());
        let internalName = $('#new-attr-internal-name').val();
        let visible = $('#new-attr-visible').val() === 'true';
        let valueType = $('#new-attr-value-type').val();
        let valueInput = $('#new-attr-value').val();

        if (!internalName) {
            App.showError('Please enter an internal name');
            return;
        }

        // Build attribute value
        let attrValue = {};

        if (valueType === 'bool') {
            attrValue.bool_value = valueInput.toLowerCase() === 'true';
        } else if (valueType === 'double') {
            attrValue.double_value = parseFloat(valueInput) || 0;
        } else if (valueType === 'vector3') {
            // Expect format: "x,y,z"
            let parts = valueInput.split(',');
            attrValue.vector3 = {
                x: parseFloat(parts[0]) || 0,
                y: parseFloat(parts[1]) || 0,
                z: parseFloat(parts[2]) || 0,
            };
        } else if (valueType === 'asset_id') {
            attrValue.asset_id = parseInt(valueInput) || 0;
        }

        // Create attribute object
        let attr = {
            internal_name: internalName,
            visible: visible,
            value: attrValue,
            attribute_type: attrType,
            owner: { mobile_id: editingMobile && editingMobile.id ? editingMobile.id : 0 },
        };

        // Add to current attributes
        currentMobileAttributes[attrType] = attr;

        // Remove form and re-render
        $('#new-attribute-form').remove();
        renderMobileAttributesTable();

        App.showSuccess('Attribute added');
    }

    // ========================================================================
    // Save Mobile
    // ========================================================================

    /**
     * Save the mobile (create or update)
     */
    function saveMobile() {
        // Gather form data
        let mobileId = $('#mobile-id').val();
        let mobileName = $('#mobile-name').val();

        if (!mobileName) {
            App.showError('Please enter an NPC name');
            return;
        }

        // Build mobile object
        let mobileData = {
            what_we_call_you: mobileName,
            mobile_type: 2, // MobileType.NPC
            attributes: currentMobileAttributes,
        };

        if (mobileId) {
            mobileData.id = parseInt(mobileId);
        }

        // Determine if create or update
        let isUpdate = !!mobileId;
        let url = isUpdate ? '/api/mobiles/' + mobileId : '/api/mobiles';
        let method = isUpdate ? 'PUT' : 'POST';

        App.showLoading();

        $.ajax({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(mobileData),
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    App.showSuccess(isUpdate ? 'NPC mobile updated successfully' : 'NPC mobile created successfully');
                    renderListView();
                } else {
                    App.showError('Failed to save mobile: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to save mobile: ' + error);
            },
        });
    }

    // ========================================================================
    // Show View
    // ========================================================================

    /**
     * Render the show/detail view for a mobile
     */
    function renderShowView(mobile) {
        let html = `
            <div class="row mb-3">
                <div class="col">
                    <h2><i class="bi bi-eye"></i> NPC Mobile Details</h2>
                </div>
                <div class="col-auto">
                    <button class="btn btn-outline-secondary" id="back-to-list-btn">
                        <i class="bi bi-arrow-left"></i> Back to List
                    </button>
                </div>
            </div>

            <div class="card mb-3">
                <div class="card-header">
                    <h5>NPC Information</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>ID:</strong> ${mobile.id || 'N/A'}</p>
                            <p><strong>Name:</strong> ${App.escapeHtml(mobile.what_we_call_you)}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Type:</strong> <span class="badge bg-info">NPC</span></p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Show mobile attributes if they exist
        if (mobile.attributes && Object.keys(mobile.attributes).length > 0) {
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h5>Character Attributes</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Type</th>
                                        <th>Internal Name</th>
                                        <th>Visible</th>
                                        <th>Value</th>
                                    </tr>
                                </thead>
                                <tbody>
            `;

            for (let attrTypeKey in mobile.attributes) {
                let attr = mobile.attributes[attrTypeKey];
                let attrTypeName = App.getEnumName('AttributeType', attr.attribute_type);
                let valueDisplay = getAttributeValueDisplay(attr.value);

                html += `
                    <tr>
                        <td><span class="badge bg-secondary">${attrTypeName}</span></td>
                        <td>${App.escapeHtml(attr.internal_name)}</td>
                        <td>${attr.visible ? 'Yes' : 'No'}</td>
                        <td>${valueDisplay}</td>
                    </tr>
                `;
            }

            html += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div class="card mb-3">
                    <div class="card-body">
                        <p class="text-muted">No character attributes.</p>
                    </div>
                </div>
            `;
        }

        $('#content').html(html);

        // Set up back button handler
        $('#back-to-list-btn').on('click', function() {
            renderListView();
        });
    }

    // ========================================================================
    // Helper Functions
    // ========================================================================

    /**
     * Load a mobile for display
     */
    function loadMobileForShow(mobileId) {
        App.showLoading();

        $.ajax({
            url: '/api/mobiles/' + mobileId,
            method: 'GET',
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    renderShowView(response.mobile);
                } else {
                    App.showError('Failed to load mobile: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load mobile: ' + error);
            },
        });
    }

    /**
     * Load a mobile for editing
     */
    function loadMobileForEdit(mobileId) {
        App.showLoading();

        $.ajax({
            url: '/api/mobiles/' + mobileId,
            method: 'GET',
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    editingMobile = response.mobile;
                    renderFormView();
                } else {
                    App.showError('Failed to load mobile: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load mobile: ' + error);
            },
        });
    }

    /**
     * Delete a mobile
     */
    function deleteMobile(mobileId) {
        if (!confirm('Are you sure you want to delete this NPC mobile? This will also delete all associated attributes.')) {
            return;
        }

        App.showLoading();

        $.ajax({
            url: '/api/mobiles/' + mobileId,
            method: 'DELETE',
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    App.showSuccess('NPC mobile deleted successfully');
                    loadMobiles(); // Reload the list
                } else {
                    App.showError('Failed to delete mobile: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to delete mobile: ' + error);
            },
        });
    }

    // Public API
    return {
        init: init,
    };
})();
