/**
 * Control Panel - Item Module
 * Handles all Item CRUD operations
 */

var ItemModule = (function() {
    'use strict';

    // State
    let currentPage = 1;
    let itemsPerPage = 10;
    let searchQuery = '';
    let editingItem = null;
    let currentAttributes = {};
    let currentBlueprintComponents = {};

    /**
     * Initialize the Item module
     */
    function init() {
        console.log('Initializing Item module...');
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
                    <h2><i class="bi bi-box"></i> Items</h2>
                </div>
                <div class="col-auto">
                    <button class="btn btn-primary" id="create-item-btn">
                        <i class="bi bi-plus-circle"></i> Create Item
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
                            id="item-search-input"
                            placeholder="Search by internal name..."
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
                        <select class="form-select" id="items-per-page-select">
                            <option value="5" ${itemsPerPage === 5 ? 'selected' : ''}>5</option>
                            <option value="10" ${itemsPerPage === 10 ? 'selected' : ''}>10</option>
                            <option value="20" ${itemsPerPage === 20 ? 'selected' : ''}>20</option>
                            <option value="50" ${itemsPerPage === 50 ? 'selected' : ''}>50</option>
                            <option value="100" ${itemsPerPage === 100 ? 'selected' : ''}>100</option>
                        </select>
                    </div>
                </div>
            </div>

            <div id="items-table-container">
                <!-- Table will be rendered here -->
            </div>

            <div id="pagination-container" class="mt-3">
                <!-- Pagination will be rendered here -->
            </div>
        `;

        $('#content').html(html);

        // Set up event handlers
        $('#create-item-btn').on('click', function() {
            editingItem = null;
            renderFormView();
        });

        $('#search-btn').on('click', function() {
            searchQuery = $('#item-search-input').val();
            currentPage = 1;
            loadItems();
        });

        $('#item-search-input').on('keyup', function(e) {
            if (e.key === 'Enter') {
                searchQuery = $(this).val();
                currentPage = 1;
                loadItems();
            }
        });

        $('#clear-search-btn').on('click', function() {
            searchQuery = '';
            $('#item-search-input').val('');
            currentPage = 1;
            loadItems();
        });

        $('#items-per-page-select').on('change', function() {
            itemsPerPage = parseInt($(this).val());
            currentPage = 1;
            loadItems();
        });

        // Load items
        loadItems();
    }

    /**
     * Load items from the server
     */
    function loadItems() {
        App.showLoading();

        $.ajax({
            url: '/api/items',
            method: 'GET',
            data: {
                page: currentPage,
                per_page: itemsPerPage,
                search: searchQuery,
            },
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    renderItemsTable(response.items, response.total_count);
                } else {
                    App.showError('Failed to load items: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load items: ' + error);
            },
        });
    }

    /**
     * Render the items table
     */
    function renderItemsTable(items, totalCount) {
        let enums = App.getEnums();
        let html = '';

        if (items.length === 0) {
            html = '<div class="alert alert-info">No items found.</div>';
        } else {
            html = `
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Internal Name</th>
                                <th>Type</th>
                                <th>Max Stack Size</th>
                                <th>Attributes</th>
                                <th>Blueprint</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            items.forEach(function(item) {
                let itemType = App.getEnumName('ItemType', item.item_type);
                let attrCount = item.attributes ? Object.keys(item.attributes).length : 0;
                let hasBlueprint = item.blueprint ? 'Yes' : 'No';

                html += `
                    <tr>
                        <td>${item.id || 'N/A'}</td>
                        <td><strong>${App.escapeHtml(item.internal_name)}</strong></td>
                        <td><span class="badge bg-secondary">${itemType}</span></td>
                        <td>${item.max_stack_size || 'N/A'}</td>
                        <td><span class="badge bg-info">${attrCount}</span></td>
                        <td>${hasBlueprint}</td>
                        <td>
                            <button class="btn btn-sm btn-primary show-item-btn" data-item-id="${item.id}">
                                <i class="bi bi-eye"></i> Show
                            </button>
                            <button class="btn btn-sm btn-outline-primary edit-item-btn" data-item-id="${item.id}">
                                <i class="bi bi-pencil"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-item-btn" data-item-id="${item.id}">
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

        $('#items-table-container').html(html);

        // Set up action button handlers
        $('.show-item-btn').on('click', function() {
            let itemId = $(this).data('item-id');
            loadItemForShow(itemId);
        });

        $('.edit-item-btn').on('click', function() {
            let itemId = $(this).data('item-id');
            loadItemForEdit(itemId);
        });

        $('.delete-item-btn').on('click', function() {
            let itemId = $(this).data('item-id');
            deleteItem(itemId);
        });

        // Render pagination
        renderPagination(totalCount);
    }

    /**
     * Render pagination controls
     */
    function renderPagination(totalCount) {
        let totalPages = Math.ceil(totalCount / itemsPerPage);

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
                loadItems();
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
        let isEdit = editingItem !== null;
        let title = isEdit ? 'Edit Item' : 'Create Item';
        let item = editingItem || {};

        // Initialize attributes and blueprint from editing item
        if (isEdit && item.attributes) {
            currentAttributes = App.clone(item.attributes);
        } else {
            currentAttributes = {};
        }

        if (isEdit && item.blueprint && item.blueprint.components) {
            currentBlueprintComponents = App.clone(item.blueprint.components);
        } else {
            currentBlueprintComponents = {};
        }

        let enums = App.getEnums();

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

            <form id="item-form">
                <!-- Hidden ID field -->
                <input type="hidden" id="item-id" value="${item.id || ''}">

                <!-- Basic Fields -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5><i class="bi bi-info-circle"></i> Basic Information</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="internal-name" class="form-label">Internal Name *</label>
                                <input
                                    type="text"
                                    class="form-control"
                                    id="internal-name"
                                    required
                                    value="${App.escapeHtml(item.internal_name || '')}"
                                >
                                <div class="form-text">Non-localized identifier</div>
                            </div>

                            <div class="col-md-6 mb-3">
                                <label for="max-stack-size" class="form-label">Max Stack Size</label>
                                <input
                                    type="number"
                                    class="form-control"
                                    id="max-stack-size"
                                    min="1"
                                    value="${item.max_stack_size || ''}"
                                >
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="item-type" class="form-label">Item Type *</label>
                                <select class="form-select" id="item-type" required>
                                    ${generateEnumOptions('ItemType', item.item_type)}
                                </select>
                            </div>

                            <div class="col-md-6 mb-3">
                                <label for="backing-table" class="form-label">Backing Table</label>
                                <select class="form-select" id="backing-table">
                                    <option value="">-- Select --</option>
                                    ${generateEnumOptions('BackingTable', item.backing_table)}
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Attributes Section -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5><i class="bi bi-tags"></i> Attributes</h5>
                    </div>
                    <div class="card-body">
                        <button type="button" class="btn btn-success mb-3" id="add-attribute-btn">
                            <i class="bi bi-plus"></i> Add Attribute
                        </button>
                        <div id="attributes-container">
                            <!-- Attributes table will be rendered here -->
                        </div>
                    </div>
                </div>

                <!-- Blueprint Section -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5><i class="bi bi-diagram-3"></i> Blueprint</h5>
                    </div>
                    <div class="card-body">
                        <div class="form-check mb-3">
                            <input
                                class="form-check-input"
                                type="checkbox"
                                id="has-blueprint"
                                ${item.blueprint ? 'checked' : ''}
                            >
                            <label class="form-check-label" for="has-blueprint">
                                This item has a blueprint
                            </label>
                        </div>

                        <div id="blueprint-section" style="display: ${item.blueprint ? 'block' : 'none'};">
                            <div class="mb-3">
                                <label for="bake-time-ms" class="form-label">Bake Time (ms)</label>
                                <input
                                    type="number"
                                    class="form-control"
                                    id="bake-time-ms"
                                    min="0"
                                    value="${item.blueprint ? item.blueprint.bake_time_ms : 0}"
                                >
                            </div>

                            <button type="button" class="btn btn-success mb-3" id="add-component-btn-trigger">
                                <i class="bi bi-plus"></i> Add Component
                            </button>

                            <div id="components-container">
                                <!-- Components table will be rendered here -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Submit Button -->
                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                    <button type="button" class="btn btn-secondary me-md-2" id="cancel-form-btn-bottom">
                        Cancel
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-save"></i> ${isEdit ? 'Update' : 'Create'} Item
                    </button>
                </div>
            </form>
        `;

        $('#content').html(html);

        // Render attributes and components
        renderAttributesTable();
        renderComponentsTable();

        // Set up event handlers
        setupFormHandlers();
    }

    /**
     * Generate enum options for a select
     */
    function generateEnumOptions(enumType, selectedValue) {
        let enums = App.getEnums();
        let html = '';

        if (!enums[enumType]) return html;

        for (let name in enums[enumType]) {
            let value = enums[enumType][name];
            let selected = (value === selectedValue) ? 'selected' : '';
            html += `<option value="${value}" ${selected}>${name}</option>`;
        }

        return html;
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
        $('#item-form').on('submit', function(e) {
            e.preventDefault();
            saveItem();
        });

        // Blueprint checkbox
        $('#has-blueprint').on('change', function() {
            if ($(this).is(':checked')) {
                $('#blueprint-section').show();
            } else {
                $('#blueprint-section').hide();
            }
        });

        // Add attribute button
        $('#add-attribute-btn').on('click', function() {
            addAttribute();
        });

        // Add component button
        $('#add-component-btn-trigger').on('click', function() {
            openComponentSearchModal();
        });
    }

    // ========================================================================
    // Attributes Management
    // ========================================================================

    /**
     * Render the attributes table
     */
    function renderAttributesTable() {
        let html = '';

        if (Object.keys(currentAttributes).length === 0) {
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

            for (let attrTypeKey in currentAttributes) {
                let attr = currentAttributes[attrTypeKey];
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
                                class="btn btn-sm btn-outline-primary edit-attr-btn"
                                data-attr-type="${attrTypeKey}"
                            >
                                <i class="bi bi-pencil"></i>
                            </button>
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
            delete currentAttributes[attrType];
            renderAttributesTable();
        });

        $('.edit-attr-btn').on('click', function() {
            let attrType = $(this).data('attr-type');
            editAttribute(attrType);
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
     * Add a new attribute
     */
    function addAttribute() {
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
                                <option value="double">Double</option>
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
            saveNewAttribute();
        });

        $('#cancel-new-attr-btn').on('click', function() {
            $('#new-attribute-form').remove();
        });
    }

    /**
     * Save the new attribute
     */
    function saveNewAttribute() {
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
            owner: { item_id: editingItem ? editingItem.id : 0 },
        };

        // Add to current attributes
        currentAttributes[attrType] = attr;

        // Remove form and re-render
        $('#new-attribute-form').remove();
        renderAttributesTable();

        App.showSuccess('Attribute added');
    }

    /**
     * Edit an existing attribute (simplified - just allow removal for now)
     */
    function editAttribute(attrType) {
        // For simplicity, we'll just show an alert
        App.showInfo('To edit an attribute, remove it and add a new one.');
    }

    // ========================================================================
    // Blueprint Components Management
    // ========================================================================

    /**
     * Render the blueprint components table
     */
    function renderComponentsTable() {
        let html = '';

        if (Object.keys(currentBlueprintComponents).length === 0) {
            html = '<div class="alert alert-info">No components added yet.</div>';
        } else {
            html = `
                <div class="table-responsive">
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Item ID</th>
                                <th>Item Name</th>
                                <th>Ratio</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            for (let itemIdKey in currentBlueprintComponents) {
                let comp = currentBlueprintComponents[itemIdKey];

                html += `
                    <tr>
                        <td>${comp.item_id}</td>
                        <td><span class="component-name" data-item-id="${comp.item_id}">Loading...</span></td>
                        <td>${comp.ratio}</td>
                        <td>
                            <button
                                type="button"
                                class="btn btn-sm btn-outline-danger remove-component-btn"
                                data-item-id="${itemIdKey}"
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

        $('#components-container').html(html);

        // Load item names for components
        $('.component-name').each(function() {
            let itemId = $(this).data('item-id');
            let $elem = $(this);
            loadItemName(itemId, function(name) {
                $elem.text(name);
            });
        });

        // Set up remove handlers
        $('.remove-component-btn').on('click', function() {
            let itemId = $(this).data('item-id');
            delete currentBlueprintComponents[itemId];
            renderComponentsTable();
        });
    }

    /**
     * Open the component search modal
     */
    function openComponentSearchModal() {
        $('#componentSearchModal').modal('show');

        // Clear previous state
        $('#component-search-input').val('');
        $('#component-search-results').html('');
        $('#selected-component-info').hide();
        $('#selected-component-id').val('');
        $('#component-ratio-input').val('1.0');
        $('#add-component-btn').prop('disabled', true);

        // Set up search handler
        $('#component-search-input').off('input').on('input', function() {
            let query = $(this).val();
            if (query.length >= 2) {
                searchItemsForComponent(query);
            } else {
                $('#component-search-results').html('');
            }
        });

        // Set up add button
        $('#add-component-btn').off('click').on('click', function() {
            addComponentFromModal();
        });
    }

    /**
     * Search for items (autocomplete)
     */
    function searchItemsForComponent(query) {
        $.ajax({
            url: '/api/items/autocomplete',
            method: 'GET',
            data: {
                search: query,
                max_results: 10,
            },
            success: function(response) {
                if (response.success) {
                    renderComponentSearchResults(response.results);
                } else {
                    App.showError('Search failed: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.showError('Search failed: ' + error);
            },
        });
    }

    /**
     * Render component search results
     */
    function renderComponentSearchResults(results) {
        let html = '';

        if (results.length === 0) {
            html = '<div class="list-group-item">No items found</div>';
        } else {
            results.forEach(function(item) {
                html += `
                    <button
                        type="button"
                        class="list-group-item list-group-item-action component-result-item"
                        data-item-id="${item.id}"
                        data-item-name="${App.escapeHtml(item.internal_name)}"
                    >
                        <strong>${App.escapeHtml(item.internal_name)}</strong> <small class="text-muted">(ID: ${item.id})</small>
                    </button>
                `;
            });
        }

        $('#component-search-results').html(html);

        // Set up click handlers
        $('.component-result-item').on('click', function() {
            let itemId = $(this).data('item-id');
            let itemName = $(this).data('item-name');

            $('#selected-component-id').val(itemId);
            $('#selected-component-name').text(itemName + ' (ID: ' + itemId + ')');
            $('#selected-component-info').show();
            $('#add-component-btn').prop('disabled', false);

            // Clear search
            $('#component-search-input').val('');
            $('#component-search-results').html('');
        });
    }

    /**
     * Add component from modal
     */
    function addComponentFromModal() {
        let itemId = parseInt($('#selected-component-id').val());
        let ratio = parseFloat($('#component-ratio-input').val());

        if (!itemId) {
            App.showError('Please select an item');
            return;
        }

        if (ratio < 0.1 || ratio > 1.0) {
            App.showError('Ratio must be between 0.1 and 1.0');
            return;
        }

        // Add to components
        currentBlueprintComponents[itemId] = {
            item_id: itemId,
            ratio: ratio,
        };

        // Close modal and re-render
        $('#componentSearchModal').modal('hide');
        renderComponentsTable();

        App.showSuccess('Component added');
    }

    // ========================================================================
    // Helper Functions
    // ========================================================================

    /**
     * Format a number with thousand separators
     * @param {Number} num - The number to format
     * @returns {String} Formatted number string (e.g., "1,234.56")
     */
    function formatNumber(num) {
        if (num === null || num === undefined) return 'N/A';

        // Handle whole numbers vs decimals
        let parts = num.toString().split('.');
        let intPart = parts[0];
        let decPart = parts.length > 1 ? parts[1] : null;

        // Add thousand separators to integer part
        intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');

        // Reconstruct with decimal part if it exists
        if (decPart !== null) {
            // Limit to 2 decimal places if it's not already
            if (decPart.length > 2) {
                decPart = parseFloat('0.' + decPart).toFixed(2).split('.')[1];
            }
            return intPart + '.' + decPart;
        }

        return intPart;
    }

    /**
     * Load an item's name by ID
     */
    function loadItemName(itemId, callback) {
        $.ajax({
            url: '/api/items/' + itemId,
            method: 'GET',
            success: function(response) {
                if (response.success && response.item) {
                    callback(response.item.internal_name);
                } else {
                    callback('Unknown');
                }
            },
            error: function() {
                callback('Unknown');
            },
        });
    }

    /**
     * Load an item for editing
     */
    function loadItemForEdit(itemId) {
        App.showLoading();

        $.ajax({
            url: '/api/items/' + itemId,
            method: 'GET',
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    editingItem = response.item;
                    renderFormView();
                } else {
                    App.showError('Failed to load item: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load item: ' + error);
            },
        });
    }

    /**
     * Load an item for display with blueprint tree
     */
    function loadItemForShow(itemId) {
        App.showLoading();

        // Load both the item and its blueprint tree in parallel
        $.when(
            $.ajax({
                url: '/api/items/' + itemId,
                method: 'GET',
            }),
            $.ajax({
                url: '/api/items/' + itemId + '/blueprint_tree',
                method: 'GET',
            }),
        ).done(function(itemResponse, treeResponse) {
            App.hideLoading();

            let itemData = itemResponse[0];
            let treeData = treeResponse[0];

            if (itemData.success && treeData.success) {
                renderShowView(itemData.item, treeData.tree);
            } else {
                App.showError('Failed to load item: ' + (itemData.error || treeData.error));
            }
        }).fail(function(xhr, status, error) {
            App.hideLoading();
            App.showError('Failed to load item: ' + error);
        });
    }

    /**
     * Render the show/detail view for an item
     */
    function renderShowView(item, tree) {
        let enums = App.getEnums();
        let itemType = App.getEnumName('ItemType', item.item_type);

        let html = `
            <div class="row mb-3">
                <div class="col">
                    <h2><i class="bi bi-eye"></i> Item Details</h2>
                </div>
                <div class="col-auto">
                    <button class="btn btn-outline-secondary" id="back-to-list-btn">
                        <i class="bi bi-arrow-left"></i> Back to List
                    </button>
                </div>
            </div>

            <div class="card mb-3">
                <div class="card-header">
                    <h5>Basic Information</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>ID:</strong> ${item.id || 'N/A'}</p>
                            <p><strong>Internal Name:</strong> ${App.escapeHtml(item.internal_name)}</p>
                            <p><strong>Item Type:</strong> <span class="badge bg-secondary">${itemType}</span></p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Max Stack Size:</strong> ${item.max_stack_size || 'N/A'}</p>
                            <p><strong>Backing Table:</strong> ${item.backing_table ? App.getEnumName('BackingTable', item.backing_table) : 'N/A'}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Attributes section
        if (item.attributes && Object.keys(item.attributes).length > 0) {
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h5>Attributes (${Object.keys(item.attributes).length})</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Type</th>
                                        <th>Internal Name</th>
                                        <th>Value</th>
                                        <th>Visible</th>
                                    </tr>
                                </thead>
                                <tbody>
            `;

            for (let attrTypeKey in item.attributes) {
                let attr = item.attributes[attrTypeKey];
                let attrTypeName = App.getEnumName('AttributeType', attr.attribute_type);
                let value = formatAttributeValue(attr.value);

                html += `
                    <tr>
                        <td><span class="badge bg-info">${attrTypeName}</span></td>
                        <td>${App.escapeHtml(attr.internal_name)}</td>
                        <td>${value}</td>
                        <td>${attr.visible ? 'Yes' : 'No'}</td>
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
        }

        // Blueprint tree section with tabs
        if (tree.blueprint) {
            let rootBakeTime = tree.blueprint.bake_time_ms;
            let totalBakeTime = tree.total_bake_time_ms;

            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h5>Blueprint Information</h5>
                        <p class="mb-0 text-muted">
                            <strong>Bake Time:</strong> ${rootBakeTime}ms |
                            <strong>Total Bake Time:</strong> ${totalBakeTime}ms
                            (bake: ${rootBakeTime}ms + components: ${totalBakeTime - rootBakeTime}ms)
                        </p>
                    </div>
                    <div class="card-body">
                        <!-- Nav tabs -->
                        <ul class="nav nav-tabs" id="blueprintTabs" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="tree-tab" data-bs-toggle="tab" data-bs-target="#tree-pane" type="button" role="tab" aria-controls="tree-pane" aria-selected="true">
                                    <i class="bi bi-diagram-3"></i> Blueprint Tree
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="materials-tab" data-bs-toggle="tab" data-bs-target="#materials-pane" type="button" role="tab" aria-controls="materials-pane" aria-selected="false">
                                    <i class="bi bi-list-check"></i> Materials List
                                </button>
                            </li>
                        </ul>

                        <!-- Tab content -->
                        <div class="tab-content pt-3" id="blueprintTabContent">
                            <!-- Blueprint Tree Tab -->
                            <div class="tab-pane fade show active" id="tree-pane" role="tabpanel" aria-labelledby="tree-tab">
                                ${renderBlueprintTree(tree, 0)}
                            </div>

                            <!-- Materials List Tab -->
                            <div class="tab-pane fade" id="materials-pane" role="tabpanel" aria-labelledby="materials-tab">
                                <div class="mb-3">
                                    <label for="quantity-input" class="form-label">Quantity to Make:</label>
                                    <input type="number" class="form-control" id="quantity-input" value="1" min="1" step="1" style="max-width: 200px;">
                                </div>
                                <div id="materials-table-container">
                                    <!-- Materials table will be rendered here -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> This item does not have a blueprint.
                </div>
            `;
        }

        $('#content').html(html);

        // Store tree for materials calculation
        if (tree.blueprint) {
            $('#content').data('blueprintTree', tree);

            // Initial materials list render
            renderMaterialsList(tree, 1);

            // Set up quantity input handler
            $('#quantity-input').on('input', function() {
                let quantity = parseFloat($(this).val()) || 1;
                if (quantity < 1) {
                    quantity = 1;
                    $(this).val(1);
                }
                renderMaterialsList(tree, quantity);
            });
        }

        // Set up back button handler
        $('#back-to-list-btn').on('click', function() {
            // Restore the list view with preserved state
            renderListView();
        });
    }

    /**
     * Format an attribute value for display
     */
    function formatAttributeValue(value) {
        if (!value) return 'N/A';

        if (value.bool_value !== undefined) {
            return value.bool_value ? 'True' : 'False';
        } else if (value.double_value !== undefined) {
            return value.double_value.toString();
        } else if (value.vector3) {
            let v = value.vector3;
            return `(${v.x}, ${v.y}, ${v.z})`;
        } else if (value.asset_id !== undefined) {
            return value.asset_id.toString();
        }

        return 'N/A';
    }

    /**
     * Recursively render a blueprint tree
     */
    function renderBlueprintTree(node, depth) {
        let indent = '&nbsp;'.repeat(depth * 4);
        let html = '';

        // Render current node
        let itemInfo = `<strong>${App.escapeHtml(node.item.internal_name)}</strong> (ID: ${node.item.id})`;
        let bakeInfo = '';

        if (node.blueprint) {
            bakeInfo = ` - Bake: ${node.blueprint.bake_time_ms}ms, Total: ${node.total_bake_time_ms}ms`;
        }

        html += `<div class="mb-2" style="padding-left: ${depth * 20}px;">`;
        html += `<i class="bi bi-box"></i> ${itemInfo}${bakeInfo}`;

        if (node.max_depth_reached) {
            html += ` <span class="badge bg-warning">Max Depth Reached</span>`;
        }
        if (node.cycle_detected) {
            html += ` <span class="badge bg-danger">Cycle Detected</span>`;
        }

        html += '</div>';

        // Render component nodes recursively
        if (node.component_nodes && node.component_nodes.length > 0) {
            for (let i = 0; i < node.component_nodes.length; i++) {
                let componentNode = node.component_nodes[i];
                let ratio = node.component_ratios[i];

                html += `<div class="mb-1" style="padding-left: ${(depth + 1) * 20}px;">`;
                html += `<i class="bi bi-arrow-return-right"></i> <span class="badge bg-secondary">Ratio: ${ratio}</span>`;
                html += '</div>';

                html += renderBlueprintTree(componentNode, depth + 1);
            }
        }

        return html;
    }

    /**
     * Calculate materials needed from a blueprint tree
     * @param {Object} node - The current tree node
     * @param {Number} multiplier - The quantity multiplier from parent nodes
     * @param {Object} materials - Map of item_id -> {item_id, internal_name, item_type, quantity}
     */
    function calculateMaterialsFromTree(node, multiplier, materials) {
        // If this node has components
        if (node.component_nodes && node.component_nodes.length > 0) {
            for (let i = 0; i < node.component_nodes.length; i++) {
                let componentNode = node.component_nodes[i];
                let ratio = node.component_ratios[i];

                // Calculate how many of this component we need
                // ratio is "parts of component per parent", so 1.0/ratio gives us units needed
                let componentMultiplier = multiplier * (1.0 / ratio);

                // Add to materials map
                let itemId = componentNode.item.id;
                if (!materials[itemId]) {
                    materials[itemId] = {
                        item_id: itemId,
                        internal_name: componentNode.item.internal_name,
                        item_type: componentNode.item.item_type,
                        quantity: 0,
                    };
                }
                materials[itemId].quantity += componentMultiplier;

                // Recurse into this component's blueprint
                calculateMaterialsFromTree(componentNode, componentMultiplier, materials);
            }
        }
    }

    /**
     * Render the materials list table
     * @param {Object} tree - The blueprint tree
     * @param {Number} quantity - The quantity to make
     */
    function renderMaterialsList(tree, quantity) {
        // Calculate materials
        let materials = {};
        calculateMaterialsFromTree(tree, quantity, materials);

        // Convert to array
        let materialsList = Object.values(materials);

        // Get current sort state (or default to name ascending)
        let sortColumn = $('#materials-table-container').data('sortColumn') || 'internal_name';
        let sortAsc = $('#materials-table-container').data('sortAsc');
        if (sortAsc === undefined) sortAsc = true;

        // Get current filter
        let filterValue = $('#materials-name-filter').val() || '';

        // Render table
        let html = '';

        if (materialsList.length === 0) {
            html = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> This item has no components.
                </div>
            `;
        } else {
            // Add filter input
            html += `
                <div class="mb-3">
                    <label for="materials-name-filter" class="form-label">Filter by Name:</label>
                    <input
                        type="text"
                        class="form-control"
                        id="materials-name-filter"
                        placeholder="Type to filter..."
                        value="${App.escapeHtml(filterValue)}"
                        style="max-width: 300px;"
                    >
                </div>
            `;

            // Sort materials
            materialsList.sort((a, b) => {
                let valA, valB;

                if (sortColumn === 'item_id') {
                    valA = a.item_id;
                    valB = b.item_id;
                } else if (sortColumn === 'internal_name') {
                    valA = a.internal_name.toLowerCase();
                    valB = b.internal_name.toLowerCase();
                    return sortAsc
                        ? valA.localeCompare(valB)
                        : valB.localeCompare(valA);
                } else if (sortColumn === 'item_type') {
                    valA = App.getEnumName('ItemType', a.item_type);
                    valB = App.getEnumName('ItemType', b.item_type);
                    return sortAsc
                        ? valA.localeCompare(valB)
                        : valB.localeCompare(valA);
                } else if (sortColumn === 'quantity') {
                    valA = a.quantity;
                    valB = b.quantity;
                }

                if (sortAsc) {
                    return valA < valB ? -1 : (valA > valB ? 1 : 0);
                } else {
                    return valA > valB ? -1 : (valA < valB ? 1 : 0);
                }
            });

            // Filter materials by name
            if (filterValue) {
                let filterLower = filterValue.toLowerCase();
                materialsList = materialsList.filter(m =>
                    m.internal_name.toLowerCase().includes(filterLower)
                );
            }

            // Helper function to render sort indicator
            function getSortIcon(column) {
                if (sortColumn !== column) {
                    return '<i class="bi bi-arrow-down-up text-muted"></i>';
                }
                return sortAsc
                    ? '<i class="bi bi-arrow-up"></i>'
                    : '<i class="bi bi-arrow-down"></i>';
            }

            html += `
                <div class="table-responsive">
                    <table class="table table-striped table-hover" id="materials-table">
                        <thead>
                            <tr>
                                <th class="sortable" data-column="item_id" style="cursor: pointer;">
                                    Item ID ${getSortIcon('item_id')}
                                </th>
                                <th class="sortable" data-column="internal_name" style="cursor: pointer;">
                                    Internal Name ${getSortIcon('internal_name')}
                                </th>
                                <th class="sortable" data-column="item_type" style="cursor: pointer;">
                                    Item Type ${getSortIcon('item_type')}
                                </th>
                                <th class="sortable" data-column="quantity" style="cursor: pointer;">
                                    Quantity Needed ${getSortIcon('quantity')}
                                </th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            for (let material of materialsList) {
                let itemType = App.getEnumName('ItemType', material.item_type);

                // Format quantity with thousand separators
                let qtyDisplay;
                if (material.quantity % 1 === 0) {
                    qtyDisplay = formatNumber(material.quantity);
                } else {
                    qtyDisplay = formatNumber(parseFloat(material.quantity.toFixed(2)));
                }

                html += `
                    <tr>
                        <td>${formatNumber(material.item_id)}</td>
                        <td><strong>${App.escapeHtml(material.internal_name)}</strong></td>
                        <td><span class="badge bg-secondary">${itemType}</span></td>
                        <td>${qtyDisplay}</td>
                    </tr>
                `;
            }

            html += `
                        </tbody>
                    </table>
                </div>
            `;

            // Show count
            html += `
                <p class="text-muted">
                    Showing ${materialsList.length} material${materialsList.length !== 1 ? 's' : ''}
                    ${filterValue ? ' (filtered)' : ''}
                </p>
            `;
        }

        $('#materials-table-container').html(html);

        // Set up filter handler
        $('#materials-name-filter').on('input', function() {
            renderMaterialsList(tree, quantity);
        });

        // Set up sort handlers
        $('.sortable').on('click', function() {
            let column = $(this).data('column');
            let currentSort = $('#materials-table-container').data('sortColumn');
            let currentAsc = $('#materials-table-container').data('sortAsc');

            // Toggle sort direction if clicking the same column
            if (currentSort === column) {
                $('#materials-table-container').data('sortAsc', !currentAsc);
            } else {
                // Default to ascending for new column
                $('#materials-table-container').data('sortColumn', column);
                $('#materials-table-container').data('sortAsc', true);
            }

            renderMaterialsList(tree, quantity);
        });
    }

    /**
     * Save the item (create or update)
     */
    function saveItem() {
        // Gather form data
        let itemId = $('#item-id').val();
        let internalName = $('#internal-name').val();
        let maxStackSize = $('#max-stack-size').val();
        let itemType = parseInt($('#item-type').val());
        let backingTable = $('#backing-table').val();

        if (!internalName) {
            App.showError('Please enter an internal name');
            return;
        }

        // Build item object
        let itemData = {
            internal_name: internalName,
            item_type: itemType,
            attributes: currentAttributes,
        };

        if (itemId) {
            itemData.id = parseInt(itemId);
        }

        if (maxStackSize) {
            itemData.max_stack_size = parseInt(maxStackSize);
        }

        if (backingTable) {
            itemData.backing_table = parseInt(backingTable);
        }

        // Blueprint
        if ($('#has-blueprint').is(':checked')) {
            let bakeTime = parseInt($('#bake-time-ms').val()) || 0;

            itemData.blueprint = {
                bake_time_ms: bakeTime,
                components: currentBlueprintComponents,
            };

            if (editingItem && editingItem.blueprint && editingItem.blueprint.id) {
                itemData.blueprint.id = editingItem.blueprint.id;
            }
        }

        // Determine if create or update
        let isUpdate = !!itemId;
        let url = isUpdate ? '/api/items/' + itemId : '/api/items';
        let method = isUpdate ? 'PUT' : 'POST';

        App.showLoading();

        $.ajax({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(itemData),
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    App.showSuccess(isUpdate ? 'Item updated successfully' : 'Item created successfully');
                    renderListView();
                } else {
                    App.showError('Failed to save item: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to save item: ' + error);
            },
        });
    }

    /**
     * Delete an item
     */
    function deleteItem(itemId) {
        App.confirm('Are you sure you want to delete this item?', function() {
            App.showLoading();

            $.ajax({
                url: '/api/items/' + itemId,
                method: 'DELETE',
                success: function(response) {
                    App.hideLoading();

                    if (response.success) {
                        App.showSuccess('Item deleted successfully');
                        loadItems();
                    } else {
                        App.showError('Failed to delete item: ' + response.error);
                    }
                },
                error: function(xhr, status, error) {
                    App.hideLoading();
                    App.showError('Failed to delete item: ' + error);
                },
            });
        });
    }

    // Public API
    return {
        init: init,
    };
})();
