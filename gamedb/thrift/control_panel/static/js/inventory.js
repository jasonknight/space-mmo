/**
 * Control Panel - Inventory Module
 * Handles all Inventory CRUD operations
 */

var InventoryModule = (function() {
    'use strict';

    // State
    let currentPage = 1;
    let inventoriesPerPage = 10;
    let searchQuery = '';
    let editingInventory = null;
    let currentEntries = [];

    /**
     * Initialize the Inventory module
     */
    function init() {
        console.log('Initializing Inventory module...');
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
                    <h2><i class="bi bi-backpack"></i> Inventories</h2>
                </div>
                <div class="col-auto">
                    <button class="btn btn-primary" id="create-inventory-btn">
                        <i class="bi bi-plus-circle"></i> Create Inventory
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
                            id="inventory-search-input"
                            placeholder="Search inventories..."
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
                        <select class="form-select" id="inventories-per-page-select">
                            <option value="5" ${inventoriesPerPage === 5 ? 'selected' : ''}>5</option>
                            <option value="10" ${inventoriesPerPage === 10 ? 'selected' : ''}>10</option>
                            <option value="20" ${inventoriesPerPage === 20 ? 'selected' : ''}>20</option>
                            <option value="50" ${inventoriesPerPage === 50 ? 'selected' : ''}>50</option>
                            <option value="100" ${inventoriesPerPage === 100 ? 'selected' : ''}>100</option>
                        </select>
                    </div>
                </div>
            </div>

            <div id="inventories-table-container">
                <!-- Table will be rendered here -->
            </div>

            <div id="pagination-container" class="mt-3">
                <!-- Pagination will be rendered here -->
            </div>
        `;

        $('#content').html(html);

        // Set up event handlers
        $('#create-inventory-btn').on('click', function() {
            editingInventory = null;
            renderFormView();
        });

        $('#search-btn').on('click', function() {
            searchQuery = $('#inventory-search-input').val();
            currentPage = 1;
            loadInventories();
        });

        $('#inventory-search-input').on('keyup', function(e) {
            if (e.key === 'Enter') {
                searchQuery = $(this).val();
                currentPage = 1;
                loadInventories();
            }
        });

        $('#clear-search-btn').on('click', function() {
            searchQuery = '';
            $('#inventory-search-input').val('');
            currentPage = 1;
            loadInventories();
        });

        $('#inventories-per-page-select').on('change', function() {
            inventoriesPerPage = parseInt($(this).val());
            currentPage = 1;
            loadInventories();
        });

        // Load inventories
        loadInventories();
    }

    /**
     * Load inventories from the server
     */
    function loadInventories() {
        App.showLoading();

        $.ajax({
            url: '/api/inventories',
            method: 'GET',
            data: {
                page: currentPage - 1,
                per_page: inventoriesPerPage,
                search: searchQuery,
            },
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    renderInventoriesTable(response.inventories, response.total_count);
                } else {
                    App.showError('Failed to load inventories: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load inventories: ' + error);
            },
        });
    }

    /**
     * Render the inventories table
     */
    function renderInventoriesTable(inventories, totalCount) {
        let html = '';

        if (inventories.length === 0) {
            html = '<div class="alert alert-info">No inventories found.</div>';
        } else {
            html = `
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Owner</th>
                                <th>Max Entries</th>
                                <th>Max Volume</th>
                                <th>Current Entries</th>
                                <th>Last Calc Volume</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            inventories.forEach(function(inventory) {
                let ownerDisplay = getOwnerDisplay(inventory.owner);
                let entriesCount = inventory.entries ? inventory.entries.length : 0;

                html += `
                    <tr>
                        <td>${inventory.id || 'N/A'}</td>
                        <td>${ownerDisplay}</td>
                        <td>${inventory.max_entries || 'N/A'}</td>
                        <td>${inventory.max_volume || 'N/A'}</td>
                        <td><span class="badge bg-info">${entriesCount}</span></td>
                        <td>${inventory.last_calculated_volume || 0}</td>
                        <td>
                            <button class="btn btn-sm btn-primary show-inventory-btn" data-inventory-id="${inventory.id}">
                                <i class="bi bi-eye"></i> Show
                            </button>
                            <button class="btn btn-sm btn-outline-primary edit-inventory-btn" data-inventory-id="${inventory.id}">
                                <i class="bi bi-pencil"></i> Edit
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

        $('#inventories-table-container').html(html);

        // Set up action button handlers
        $('.show-inventory-btn').on('click', function() {
            let inventoryId = $(this).data('inventory-id');
            loadInventoryForShow(inventoryId);
        });

        $('.edit-inventory-btn').on('click', function() {
            let inventoryId = $(this).data('inventory-id');
            loadInventoryForEdit(inventoryId);
        });

        // Render pagination
        renderPagination(totalCount);
    }

    /**
     * Get display string for an owner
     */
    function getOwnerDisplay(owner) {
        if (!owner) return 'N/A';

        if (owner.mobile_id) {
            return `Mobile #${owner.mobile_id}`;
        } else if (owner.item_id) {
            return `Item #${owner.item_id}`;
        } else if (owner.asset_id) {
            return `Asset #${owner.asset_id}`;
        } else if (owner.player_id) {
            return `Player #${owner.player_id}`;
        }

        return 'N/A';
    }

    /**
     * Render pagination controls
     */
    function renderPagination(totalCount) {
        let totalPages = Math.ceil(totalCount / inventoriesPerPage);

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
                loadInventories();
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
        let isEdit = editingInventory !== null;
        let title = isEdit ? 'Edit Inventory' : 'Create Inventory';
        let inventory = editingInventory || {};

        // Initialize entries from editing inventory
        if (isEdit && inventory.entries) {
            currentEntries = App.clone(inventory.entries);
        } else {
            currentEntries = [];
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

            <form id="inventory-form">
                <!-- Hidden ID field -->
                <input type="hidden" id="inventory-id" value="${inventory.id || ''}">

                <!-- Basic Fields -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5><i class="bi bi-info-circle"></i> Basic Information</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <label for="max-entries" class="form-label">Max Entries *</label>
                                <input
                                    type="number"
                                    class="form-control"
                                    id="max-entries"
                                    required
                                    min="0"
                                    value="${inventory.max_entries || ''}"
                                >
                                <div class="form-text">Maximum number of item stacks</div>
                            </div>

                            <div class="col-md-4 mb-3">
                                <label for="max-volume" class="form-label">Max Volume *</label>
                                <input
                                    type="number"
                                    class="form-control"
                                    id="max-volume"
                                    required
                                    min="0"
                                    step="0.01"
                                    value="${inventory.max_volume || ''}"
                                >
                                <div class="form-text">Maximum volume capacity</div>
                            </div>

                            <div class="col-md-4 mb-3">
                                <label for="last-calculated-volume" class="form-label">Last Calculated Volume</label>
                                <input
                                    type="number"
                                    class="form-control"
                                    id="last-calculated-volume"
                                    min="0"
                                    step="0.01"
                                    value="${inventory.last_calculated_volume || 0}"
                                >
                                <div class="form-text">Current volume (calculated)</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Owner Section -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5><i class="bi bi-person"></i> Owner</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="owner-type" class="form-label">Owner Type *</label>
                                <div class="input-group">
                                    <select class="form-select" id="owner-type" required>
                                        <option value="">-- Select Owner Type --</option>
                                        <option value="mobile_id" ${getOwnerType(inventory.owner) === 'mobile_id' ? 'selected' : ''}>Mobile</option>
                                        <option value="item_id" ${getOwnerType(inventory.owner) === 'item_id' ? 'selected' : ''}>Item</option>
                                        <option value="asset_id" ${getOwnerType(inventory.owner) === 'asset_id' ? 'selected' : ''}>Asset</option>
                                        <option value="player_id" ${getOwnerType(inventory.owner) === 'player_id' ? 'selected' : ''}>Player</option>
                                    </select>
                                    <button class="btn btn-outline-secondary" type="button" id="owner-search-trigger-btn" disabled>
                                        <i class="bi bi-search"></i>
                                    </button>
                                </div>
                            </div>

                            <div class="col-md-6 mb-3">
                                <label for="owner-id" class="form-label">Owner *</label>
                                <div id="owner-display-container">
                                    <!-- Owner info will be loaded here -->
                                    <div class="text-muted">Select an owner type to begin...</div>
                                </div>
                                <input type="hidden" id="owner-id" value="${getOwnerId(inventory.owner)}">
                                <input type="hidden" id="owner-type-hidden" value="${getOwnerType(inventory.owner)}">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Entries Section -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5><i class="bi bi-box-seam"></i> Inventory Entries</h5>
                    </div>
                    <div class="card-body">
                        <button type="button" class="btn btn-success mb-3" id="add-entry-btn">
                            <i class="bi bi-plus"></i> Add Entry
                        </button>
                        <div id="entries-container">
                            <!-- Entries table will be rendered here -->
                        </div>
                    </div>
                </div>

                <!-- Submit Button -->
                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                    <button type="button" class="btn btn-secondary me-md-2" id="cancel-form-btn-bottom">
                        Cancel
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-save"></i> ${isEdit ? 'Update' : 'Create'} Inventory
                    </button>
                </div>
            </form>
        `;

        $('#content').html(html);

        // Render entries
        renderEntriesTable();

        // Set up event handlers
        setupFormHandlers();
    }

    /**
     * Get owner type from owner object
     */
    function getOwnerType(owner) {
        if (!owner) return '';
        if (owner.mobile_id) return 'mobile_id';
        if (owner.item_id) return 'item_id';
        if (owner.asset_id) return 'asset_id';
        if (owner.player_id) return 'player_id';
        return '';
    }

    /**
     * Get owner ID from owner object
     */
    function getOwnerId(owner) {
        if (!owner) return '';
        if (owner.mobile_id) return owner.mobile_id;
        if (owner.item_id) return owner.item_id;
        if (owner.asset_id) return owner.asset_id;
        if (owner.player_id) return owner.player_id;
        return '';
    }

    /**
     * Get owner display for form (shows name if available, otherwise just ID)
     */
    function getOwnerDisplayForForm(owner) {
        if (!owner) return '';

        // For editing, we'll just show the ID for now
        // The search modal will populate the display name
        let ownerId = getOwnerId(owner);
        if (ownerId) {
            return `ID: ${ownerId}`;
        }
        return '';
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
        $('#inventory-form').on('submit', function(e) {
            e.preventDefault();
            saveInventory();
        });

        // Add entry button
        $('#add-entry-btn').on('click', function() {
            openEntrySearchModal();
        });

        // Owner type change handler - auto-trigger modal
        $('#owner-type').on('change', function() {
            let ownerType = $(this).val();

            if (ownerType) {
                // Enable search button
                $('#owner-search-trigger-btn').prop('disabled', false);

                // Clear current owner
                $('#owner-id').val('');
                updateOwnerDisplay(null, null);

                // Automatically open the selection flow
                openOwnerSelectionFlow(ownerType);
            } else {
                // Disable search button
                $('#owner-search-trigger-btn').prop('disabled', true);
                $('#owner-id').val('');
                updateOwnerDisplay(null, null);
            }
        });

        // Owner search button click handler
        $('#owner-search-trigger-btn').on('click', function() {
            let ownerType = $('#owner-type').val();
            if (ownerType) {
                openOwnerSelectionFlow(ownerType);
            }
        });

        // Load existing owner info if editing
        loadExistingOwnerInfo();
    }

    /**
     * Load and display existing owner info when editing
     */
    function loadExistingOwnerInfo() {
        let ownerId = $('#owner-id').val();
        let ownerType = $('#owner-type-hidden').val();

        if (ownerId && ownerType) {
            // Enable the search button since we have an owner type
            $('#owner-search-trigger-btn').prop('disabled', false);

            // Fetch owner info from backend
            $.ajax({
                url: `/api/owners/${ownerType}/${ownerId}`,
                method: 'GET',
                success: function(response) {
                    if (response.success) {
                        updateOwnerDisplay(response.owner, ownerType);
                    } else {
                        // Fallback to just showing ID
                        updateOwnerDisplay({id: ownerId, name: `ID: ${ownerId}`}, ownerType);
                    }
                },
                error: function() {
                    // Fallback to just showing ID
                    updateOwnerDisplay({id: ownerId, name: `ID: ${ownerId}`}, ownerType);
                },
            });
        }
    }

    /**
     * Update the owner display container
     */
    function updateOwnerDisplay(owner, ownerType) {
        let html = '';

        if (!owner) {
            html = '<div class="text-muted">Select an owner type to begin...</div>';
        } else {
            html = `
                <div class="card">
                    <div class="card-body p-2">
                        <div class="row g-2">
                            <div class="col-4">
                                <small class="text-muted">ID</small>
                                <div><strong>${owner.id}</strong></div>
                            </div>
                            <div class="col-8">
                                <small class="text-muted">Name</small>
                                <div><strong>${App.escapeHtml(owner.name)}</strong></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        $('#owner-display-container').html(html);
    }

    // ========================================================================
    // Entries Management
    // ========================================================================

    /**
     * Render the entries table
     */
    function renderEntriesTable() {
        let html = '';

        if (currentEntries.length === 0) {
            html = '<div class="alert alert-info">No entries added yet.</div>';
        } else {
            html = `
                <div class="table-responsive">
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Item ID</th>
                                <th>Item Name</th>
                                <th>Quantity</th>
                                <th>Max Stacked</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            currentEntries.forEach(function(entry, index) {
                html += `
                    <tr>
                        <td>${entry.item_id}</td>
                        <td><span class="entry-item-name" data-item-id="${entry.item_id}">Loading...</span></td>
                        <td>${entry.quantity}</td>
                        <td>${entry.is_max_stacked ? 'Yes' : 'No'}</td>
                        <td>
                            <button
                                type="button"
                                class="btn btn-sm btn-outline-danger remove-entry-btn"
                                data-index="${index}"
                            >
                                <i class="bi bi-trash"></i>
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

        $('#entries-container').html(html);

        // Load item names for entries
        $('.entry-item-name').each(function() {
            let itemId = $(this).data('item-id');
            let $elem = $(this);
            loadItemName(itemId, function(name) {
                $elem.text(name);
            });
        });

        // Set up remove handlers
        $('.remove-entry-btn').on('click', function() {
            let index = $(this).data('index');
            currentEntries.splice(index, 1);
            renderEntriesTable();
        });
    }

    /**
     * Open the entry search modal (reuse item search modal)
     */
    function openEntrySearchModal() {
        $('#componentSearchModal').modal('show');
        $('.modal-title').text('Add Inventory Entry');

        // Clear previous state
        $('#component-search-input').val('');
        $('#component-search-results').html('');
        $('#selected-component-info').hide();
        $('#selected-component-id').val('');
        $('#component-ratio-input').val('1');
        $('#add-component-btn').prop('disabled', true);

        // Update label for quantity
        $('label[for="component-ratio-input"]').text('Quantity');
        $('#component-ratio-input').attr({
            min: 0.1,
            max: 999999,
            step: 0.1,
        });
        $('.form-text').text('How many units of this item');

        // Set up search handler
        $('#component-search-input').off('input').on('input', function() {
            let query = $(this).val();
            if (query.length >= 2) {
                searchItemsForEntry(query);
            } else {
                $('#component-search-results').html('');
            }
        });

        // Set up add button
        $('#add-component-btn').off('click').on('click', function() {
            addEntryFromModal();
        });
    }

    /**
     * Search for items (autocomplete)
     */
    function searchItemsForEntry(query) {
        $.ajax({
            url: '/api/items/autocomplete',
            method: 'GET',
            data: {
                search: query,
                max_results: 10,
            },
            success: function(response) {
                if (response.success) {
                    renderEntrySearchResults(response.results);
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
     * Render entry search results
     */
    function renderEntrySearchResults(results) {
        let html = '';

        if (results.length === 0) {
            html = '<div class="list-group-item">No items found</div>';
        } else {
            results.forEach(function(item) {
                html += `
                    <button
                        type="button"
                        class="list-group-item list-group-item-action entry-result-item"
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
        $('.entry-result-item').on('click', function() {
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
     * Add entry from modal
     */
    function addEntryFromModal() {
        let itemId = parseInt($('#selected-component-id').val());
        let quantity = parseFloat($('#component-ratio-input').val());

        if (!itemId) {
            App.showError('Please select an item');
            return;
        }

        if (quantity <= 0) {
            App.showError('Quantity must be greater than 0');
            return;
        }

        // Check if item already exists in entries
        let existingEntry = currentEntries.find(e => e.item_id === itemId);
        if (existingEntry) {
            App.showError('This item is already in the inventory. Remove it first if you want to change it.');
            return;
        }

        // Add to entries
        currentEntries.push({
            item_id: itemId,
            quantity: quantity,
            is_max_stacked: false,
        });

        // Close modal and re-render
        $('#componentSearchModal').modal('hide');
        renderEntriesTable();

        App.showSuccess('Entry added');
    }

    // ========================================================================
    // Owner Selection Flow
    // ========================================================================

    /**
     * Open the appropriate owner selection flow based on type
     */
    function openOwnerSelectionFlow(ownerType) {
        if (ownerType === 'asset_id') {
            // Show prompt for manual asset ID entry
            openAssetIdPrompt();
        } else {
            // Open search modal for other types
            openOwnerSearchModal(ownerType);
        }
    }

    /**
     * Open prompt for manual asset ID entry
     */
    function openAssetIdPrompt() {
        let assetId = prompt('Please enter the Asset ID:');

        if (assetId !== null && assetId.trim() !== '') {
            assetId = parseInt(assetId.trim());

            if (isNaN(assetId) || assetId <= 0) {
                App.showError('Please enter a valid Asset ID (positive number)');
                return;
            }

            // Set the owner
            $('#owner-id').val(assetId);
            updateOwnerDisplay({id: assetId, name: `Asset #${assetId}`}, 'asset_id');
            App.showSuccess('Asset owner set');
        }
    }

    // ========================================================================
    // Owner Search Modal
    // ========================================================================

    /**
     * Open the owner search modal
     */
    function openOwnerSearchModal(ownerType) {
        if (!ownerType) {
            ownerType = $('#owner-type').val();
        }

        if (!ownerType) {
            App.showError('Please select an owner type first');
            return;
        }

        console.log('openOwnerSearchModal called with ownerType:', ownerType);

        // Show modal
        $('#ownerSearchModal').modal('show');

        // Clear previous state
        $('#owner-search-input').val('');
        $('#owner-search-results').html('');
        $('#selected-owner-info').hide();
        $('#selected-owner-id').val('');
        $('#select-owner-btn').prop('disabled', true);
        $('#owner-manual-entry-notice').hide();

        // Update modal title
        let ownerTypeLabel = $('#owner-type option:selected').text();
        $('#ownerSearchModal .modal-title').text(`Select ${ownerTypeLabel} Owner`);

        // Enable search
        $('#owner-search-input').prop('disabled', false);

        // Set up search handler based on owner type
        $('#owner-search-input').off('input').on('input', function() {
            let query = $(this).val();
            console.log('Search input triggered. Query:', query, 'OwnerType:', ownerType);
            if (query.length >= 2) {
                if (ownerType === 'item_id') {
                    console.log('Calling searchItemsForOwner');
                    searchItemsForOwner(query);
                } else if (ownerType === 'player_id') {
                    console.log('Calling searchPlayersForOwner');
                    searchPlayersForOwner(query);
                } else if (ownerType === 'mobile_id') {
                    console.log('Calling searchMobilesForOwner');
                    searchMobilesForOwner(query);
                } else {
                    console.log('WARNING: Unknown ownerType:', ownerType);
                }
            } else {
                $('#owner-search-results').html('');
            }
        });

        // Set up select button
        $('#select-owner-btn').off('click').on('click', function() {
            selectOwnerFromModal();
        });
    }

    /**
     * Search for items (for owner selection)
     */
    function searchItemsForOwner(query) {
        $.ajax({
            url: '/api/items/autocomplete',
            method: 'GET',
            data: {
                search: query,
                max_results: 10,
            },
            success: function(response) {
                if (response.success) {
                    renderOwnerSearchResults(response.results, 'item');
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
     * Search for players (for owner selection)
     */
    function searchPlayersForOwner(query) {
        console.log('searchPlayersForOwner called with query:', query);
        $.ajax({
            url: '/api/players/search',
            method: 'GET',
            data: {
                search: query,
                max_results: 10,
            },
            success: function(response) {
                console.log('Player search response:', response);
                if (response.success) {
                    renderOwnerSearchResults(response.results, 'player');
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
     * Search for mobiles (for owner selection)
     */
    function searchMobilesForOwner(query) {
        console.log('searchMobilesForOwner called with query:', query);
        $.ajax({
            url: '/api/mobiles/search',
            method: 'GET',
            data: {
                search: query,
                max_results: 10,
            },
            success: function(response) {
                console.log('Mobile search response:', response);
                if (response.success) {
                    renderOwnerSearchResults(response.results, 'mobile');
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
     * Render owner search results
     */
    function renderOwnerSearchResults(results, ownerType) {
        console.log('renderOwnerSearchResults called. Type:', ownerType, 'Results:', results);
        let html = '';

        if (results.length === 0) {
            html = '<div class="list-group-item">No results found</div>';
        } else {
            results.forEach(function(result) {
                let displayName = '';
                let subtitle = '';

                if (ownerType === 'item') {
                    displayName = result.internal_name;
                    subtitle = `ID: ${result.id}`;
                } else if (ownerType === 'player') {
                    displayName = result.what_we_call_you;
                    subtitle = `ID: ${result.id} - ${result.email || 'No email'}`;
                } else if (ownerType === 'mobile') {
                    displayName = result.what_we_call_you;
                    subtitle = `ID: ${result.id} - Type: ${result.mobile_type}`;
                }

                html += `
                    <button
                        type="button"
                        class="list-group-item list-group-item-action owner-result-item"
                        data-owner-id="${result.id}"
                        data-owner-name="${App.escapeHtml(displayName)}"
                    >
                        <strong>${App.escapeHtml(displayName)}</strong>
                        <br><small class="text-muted">${subtitle}</small>
                    </button>
                `;
            });
        }

        $('#owner-search-results').html(html);

        // Set up click handlers
        $('.owner-result-item').on('click', function() {
            let ownerId = $(this).data('owner-id');
            let ownerName = $(this).data('owner-name');

            $('#selected-owner-id').val(ownerId);
            $('#selected-owner-name').text(ownerName + ' (ID: ' + ownerId + ')');
            $('#selected-owner-info').show();
            $('#select-owner-btn').prop('disabled', false);

            // Clear search
            $('#owner-search-input').val('');
            $('#owner-search-results').html('');
        });
    }

    /**
     * Select owner from modal and close
     */
    function selectOwnerFromModal() {
        let ownerId = $('#selected-owner-id').val();
        let ownerName = $('#selected-owner-name').text();
        let ownerType = $('#owner-type').val();

        if (!ownerId) {
            App.showError('Please select an owner');
            return;
        }

        // Extract just the name (remove the " (ID: X)" part if present)
        let displayName = ownerName.replace(/\s*\(ID:\s*\d+\)\s*$/, '');

        // Update form fields
        $('#owner-id').val(ownerId);
        updateOwnerDisplay({id: ownerId, name: displayName}, ownerType);

        // Close modal
        $('#ownerSearchModal').modal('hide');

        App.showSuccess('Owner selected');
    }

    // ========================================================================
    // Show View
    // ========================================================================

    /**
     * Render the show/detail view for an inventory
     */
    function renderShowView(inventory) {
        let html = `
            <div class="row mb-3">
                <div class="col">
                    <h2><i class="bi bi-eye"></i> Inventory Details</h2>
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
                            <p><strong>ID:</strong> ${inventory.id || 'N/A'}</p>
                            <p><strong>Owner:</strong> <span id="show-owner-display">Loading...</span></p>
                            <p><strong>Max Entries:</strong> ${inventory.max_entries || 'N/A'}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Max Volume:</strong> ${inventory.max_volume || 'N/A'}</p>
                            <p><strong>Last Calculated Volume:</strong> ${inventory.last_calculated_volume || 0}</p>
                            <p><strong>Current Entries:</strong> ${inventory.entries ? inventory.entries.length : 0}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Entries section
        if (inventory.entries && inventory.entries.length > 0) {
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h5>Inventory Entries (${inventory.entries.length})</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Item ID</th>
                                        <th>Item Name</th>
                                        <th>Quantity</th>
                                        <th>Max Stacked</th>
                                    </tr>
                                </thead>
                                <tbody>
            `;

            inventory.entries.forEach(function(entry) {
                html += `
                    <tr>
                        <td>${entry.item_id}</td>
                        <td><span class="show-item-name" data-item-id="${entry.item_id}">Loading...</span></td>
                        <td>${entry.quantity}</td>
                        <td>${entry.is_max_stacked ? 'Yes' : 'No'}</td>
                    </tr>
                `;
            });

            html += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> This inventory has no entries.
                </div>
            `;
        }

        $('#content').html(html);

        // Load item names
        $('.show-item-name').each(function() {
            let itemId = $(this).data('item-id');
            let $elem = $(this);
            loadItemName(itemId, function(name) {
                $elem.text(name);
            });
        });

        // Load owner info
        loadOwnerDisplayForShow(inventory.owner);

        // Set up back button handler
        $('#back-to-list-btn').on('click', function() {
            renderListView();
        });
    }

    /**
     * Load and display owner info for show view
     */
    function loadOwnerDisplayForShow(owner) {
        if (!owner) {
            $('#show-owner-display').text('N/A');
            return;
        }

        let ownerId = getOwnerId(owner);
        let ownerType = getOwnerType(owner);

        if (!ownerId || !ownerType) {
            $('#show-owner-display').text('N/A');
            return;
        }

        // Fetch owner info
        $.ajax({
            url: `/api/owners/${ownerType}/${ownerId}`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    $('#show-owner-display').html(`
                        <strong>${App.escapeHtml(response.owner.name)}</strong>
                        <small class="text-muted"> (ID: ${response.owner.id})</small>
                    `);
                } else {
                    $('#show-owner-display').text(getOwnerDisplay(owner));
                }
            },
            error: function() {
                $('#show-owner-display').text(getOwnerDisplay(owner));
            },
        });
    }

    // ========================================================================
    // Helper Functions
    // ========================================================================

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
     * Load an inventory for editing
     */
    function loadInventoryForEdit(inventoryId) {
        App.showLoading();

        $.ajax({
            url: '/api/inventories/' + inventoryId,
            method: 'GET',
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    editingInventory = response.inventory;
                    renderFormView();
                } else {
                    App.showError('Failed to load inventory: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load inventory: ' + error);
            },
        });
    }

    /**
     * Load an inventory for display
     */
    function loadInventoryForShow(inventoryId) {
        App.showLoading();

        $.ajax({
            url: '/api/inventories/' + inventoryId,
            method: 'GET',
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    renderShowView(response.inventory);
                } else {
                    App.showError('Failed to load inventory: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load inventory: ' + error);
            },
        });
    }

    /**
     * Save the inventory (create or update)
     */
    function saveInventory() {
        // Gather form data
        let inventoryId = $('#inventory-id').val();
        let maxEntries = $('#max-entries').val();
        let maxVolume = $('#max-volume').val();
        let lastCalculatedVolume = $('#last-calculated-volume').val();
        let ownerType = $('#owner-type').val();
        let ownerId = $('#owner-id').val();

        if (!maxEntries || !maxVolume || !ownerType || !ownerId) {
            App.showError('Please fill in all required fields');
            return;
        }

        // Build owner object
        let owner = {};
        owner[ownerType] = parseInt(ownerId);

        // Build inventory object
        let inventoryData = {
            max_entries: parseInt(maxEntries),
            max_volume: parseFloat(maxVolume),
            last_calculated_volume: parseFloat(lastCalculatedVolume) || 0,
            owner: owner,
            entries: currentEntries,
        };

        if (inventoryId) {
            inventoryData.id = parseInt(inventoryId);
        }

        // Determine if create or update
        let isUpdate = !!inventoryId;
        let url = isUpdate ? '/api/inventories/' + inventoryId : '/api/inventories';
        let method = isUpdate ? 'PUT' : 'POST';

        App.showLoading();

        $.ajax({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(inventoryData),
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    App.showSuccess(isUpdate ? 'Inventory updated successfully' : 'Inventory created successfully');
                    renderListView();
                } else {
                    App.showError('Failed to save inventory: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to save inventory: ' + error);
            },
        });
    }

    // Public API
    return {
        init: init,
    };
})();
