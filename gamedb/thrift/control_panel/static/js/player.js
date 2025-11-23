/**
 * Control Panel - Player Module
 * Handles all Player CRUD operations with Mobile and Attributes
 */

var PlayerModule = (function() {
    'use strict';

    // State
    let currentPage = 1;
    let playersPerPage = 10;
    let searchQuery = '';
    let editingPlayer = null;
    let currentMobileAttributes = {};

    /**
     * Initialize the Player module
     */
    function init() {
        console.log('Initializing Player module...');
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
                    <h2><i class="bi bi-people"></i> Players</h2>
                </div>
                <div class="col-auto">
                    <button class="btn btn-primary" id="create-player-btn">
                        <i class="bi bi-plus-circle"></i> Create Player
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
                            id="player-search-input"
                            placeholder="Search by nickname, name, or email..."
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
                        <select class="form-select" id="players-per-page-select">
                            <option value="5" ${playersPerPage === 5 ? 'selected' : ''}>5</option>
                            <option value="10" ${playersPerPage === 10 ? 'selected' : ''}>10</option>
                            <option value="20" ${playersPerPage === 20 ? 'selected' : ''}>20</option>
                            <option value="50" ${playersPerPage === 50 ? 'selected' : ''}>50</option>
                            <option value="100" ${playersPerPage === 100 ? 'selected' : ''}>100</option>
                        </select>
                    </div>
                </div>
            </div>

            <div id="players-table-container">
                <!-- Table will be rendered here -->
            </div>

            <div id="pagination-container" class="mt-3">
                <!-- Pagination will be rendered here -->
            </div>
        `;

        $('#content').html(html);

        // Set up event handlers
        $('#create-player-btn').on('click', function() {
            editingPlayer = null;
            renderFormView();
        });

        $('#search-btn').on('click', function() {
            searchQuery = $('#player-search-input').val();
            currentPage = 1;
            loadPlayers();
        });

        $('#player-search-input').on('keyup', function(e) {
            if (e.key === 'Enter') {
                searchQuery = $(this).val();
                currentPage = 1;
                loadPlayers();
            }
        });

        $('#clear-search-btn').on('click', function() {
            searchQuery = '';
            $('#player-search-input').val('');
            currentPage = 1;
            loadPlayers();
        });

        $('#players-per-page-select').on('change', function() {
            playersPerPage = parseInt($(this).val());
            currentPage = 1;
            loadPlayers();
        });

        // Load players
        loadPlayers();
    }

    /**
     * Load players from the server
     */
    function loadPlayers() {
        App.showLoading();

        $.ajax({
            url: '/api/players',
            method: 'GET',
            data: {
                page: currentPage - 1,
                per_page: playersPerPage,
                search: searchQuery,
            },
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    renderPlayersTable(response.players, response.total_count);
                } else {
                    App.showError('Failed to load players: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load players: ' + error);
            },
        });
    }

    /**
     * Render the players table
     */
    function renderPlayersTable(players, totalCount) {
        let html = '';

        if (players.length === 0) {
            html = '<div class="alert alert-info">No players found.</div>';
        } else {
            html = `
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nickname</th>
                                <th>Full Name</th>
                                <th>Email</th>
                                <th>Year of Birth</th>
                                <th>Over 13</th>
                                <th>Character Name</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            players.forEach(function(player) {
                let characterName = player.mobile && player.mobile.what_we_call_you 
                    ? player.mobile.what_we_call_you 
                    : 'N/A';
                let over13Badge = getOverThirteenBadge(player.over_13);

                html += `
                    <tr>
                        <td>${player.id || 'N/A'}</td>
                        <td><strong>${App.escapeHtml(player.what_we_call_you)}</strong></td>
                        <td>${App.escapeHtml(player.full_name)}</td>
                        <td>${App.escapeHtml(player.email)}</td>
                        <td>${player.year_of_birth || 'N/A'}</td>
                        <td>${over13Badge}</td>
                        <td>${App.escapeHtml(characterName)}</td>
                        <td>
                            <button class="btn btn-sm btn-primary show-player-btn" data-player-id="${player.id}">
                                <i class="bi bi-eye"></i> Show
                            </button>
                            <button class="btn btn-sm btn-outline-primary edit-player-btn" data-player-id="${player.id}">
                                <i class="bi bi-pencil"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-player-btn" data-player-id="${player.id}">
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

        $('#players-table-container').html(html);

        // Set up action button handlers
        $('.show-player-btn').on('click', function() {
            let playerId = $(this).data('player-id');
            loadPlayerForShow(playerId);
        });

        $('.edit-player-btn').on('click', function() {
            let playerId = $(this).data('player-id');
            loadPlayerForEdit(playerId);
        });

        $('.delete-player-btn').on('click', function() {
            let playerId = $(this).data('player-id');
            deletePlayer(playerId);
        });

        // Render pagination
        renderPagination(totalCount);
    }

    /**
     * Get over 13 badge HTML
     */
    function getOverThirteenBadge(over13) {
        if (over13) {
            return '<span class="badge bg-success">Yes</span>';
        } else {
            return '<span class="badge bg-danger">No</span>';
        }
    }

    /**
     * Render pagination controls
     */
    function renderPagination(totalCount) {
        let totalPages = Math.ceil(totalCount / playersPerPage);

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
                loadPlayers();
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
        let isEdit = editingPlayer !== null;
        let title = isEdit ? 'Edit Player' : 'Create Player';
        let player = editingPlayer || {};

        // Initialize mobile attributes from editing player
        if (isEdit && player.mobile && player.mobile.attributes) {
            currentMobileAttributes = App.clone(player.mobile.attributes);
        } else {
            currentMobileAttributes = {};
        }

        // Calculate over_13 for display
        let over13Display = '';
        if (player.year_of_birth) {
            let currentYear = new Date().getFullYear();
            let isOver13 = (currentYear - player.year_of_birth) >= 13;
            over13Display = getOverThirteenBadge(isOver13);
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

            <form id="player-form">
                <!-- Hidden ID fields -->
                <input type="hidden" id="player-id" value="${player.id || ''}">
                <input type="hidden" id="mobile-id" value="${player.mobile && player.mobile.id ? player.mobile.id : ''}">
                <input type="hidden" id="security-token" value="">

                <!-- Player Information Card -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5><i class="bi bi-person-circle"></i> Player Information</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="full-name" class="form-label">Full Name *</label>
                                <input
                                    type="text"
                                    class="form-control"
                                    id="full-name"
                                    required
                                    value="${App.escapeHtml(player.full_name || '')}"
                                >
                                <div class="form-text">Player's full legal name</div>
                            </div>

                            <div class="col-md-6 mb-3">
                                <label for="what-we-call-you" class="form-label">Nickname *</label>
                                <input
                                    type="text"
                                    class="form-control"
                                    id="what-we-call-you"
                                    required
                                    value="${App.escapeHtml(player.what_we_call_you || '')}"
                                >
                                <div class="form-text">What we call this player</div>
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="email" class="form-label">Email *</label>
                                <input
                                    type="email"
                                    class="form-control"
                                    id="email"
                                    required
                                    value="${App.escapeHtml(player.email || '')}"
                                >
                                <div class="form-text">Player's email address</div>
                            </div>

                            <div class="col-md-3 mb-3">
                                <label for="year-of-birth" class="form-label">Year of Birth *</label>
                                <input
                                    type="number"
                                    class="form-control"
                                    id="year-of-birth"
                                    required
                                    min="1900"
                                    max="2025"
                                    value="${player.year_of_birth || ''}"
                                >
                                <div class="form-text">Birth year (YYYY)</div>
                            </div>

                            <div class="col-md-3 mb-3">
                                <label class="form-label">Over 13</label>
                                <div id="over-13-display" class="mt-2">
                                    ${over13Display || '<span class="text-muted">Enter year of birth</span>'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Character Information Card -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5><i class="bi bi-person-badge"></i> Character Information</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="character-name" class="form-label">Character Name *</label>
                                <input
                                    type="text"
                                    class="form-control"
                                    id="character-name"
                                    required
                                    value="${App.escapeHtml(player.mobile && player.mobile.what_we_call_you ? player.mobile.what_we_call_you : '')}"
                                >
                                <div class="form-text">The name of this player's character in the game</div>
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
                        <i class="bi bi-save"></i> ${isEdit ? 'Update' : 'Create'} Player
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
        $('#player-form').on('submit', function(e) {
            e.preventDefault();
            savePlayer();
        });

        // Year of birth change handler to update over_13 display
        $('#year-of-birth').on('input', function() {
            let yearOfBirth = parseInt($(this).val());
            if (yearOfBirth) {
                let currentYear = new Date().getFullYear();
                let isOver13 = (currentYear - yearOfBirth) >= 13;
                $('#over-13-display').html(getOverThirteenBadge(isOver13));
            } else {
                $('#over-13-display').html('<span class="text-muted">Enter year of birth</span>');
            }
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
            owner: { mobile_id: editingPlayer && editingPlayer.mobile ? editingPlayer.mobile.id : 0 },
        };

        // Add to current attributes
        currentMobileAttributes[attrType] = attr;

        // Remove form and re-render
        $('#new-attribute-form').remove();
        renderMobileAttributesTable();

        App.showSuccess('Attribute added');
    }

    // ========================================================================
    // Save Player
    // ========================================================================

    /**
     * Save the player (create or update)
     */
    function savePlayer() {
        // Gather form data
        let playerId = $('#player-id').val();
        let mobileId = $('#mobile-id').val();
        let fullName = $('#full-name').val();
        let whatWeCallYou = $('#what-we-call-you').val();
        let email = $('#email').val();
        let yearOfBirth = $('#year-of-birth').val();
        let characterName = $('#character-name').val();
        let securityToken = $('#security-token').val();

        if (!fullName || !whatWeCallYou || !email || !yearOfBirth || !characterName) {
            App.showError('Please fill in all required fields');
            return;
        }

        // Build mobile object
        let mobile = {
            what_we_call_you: characterName,
            attributes: currentMobileAttributes,
        };

        if (mobileId) {
            mobile.id = parseInt(mobileId);
        }

        // Build player object
        let playerData = {
            full_name: fullName,
            what_we_call_you: whatWeCallYou,
            email: email,
            year_of_birth: parseInt(yearOfBirth),
            security_token: securityToken,
            mobile: mobile,
        };

        if (playerId) {
            playerData.id = parseInt(playerId);
        }

        // Determine if create or update
        let isUpdate = !!playerId;
        let url = isUpdate ? '/api/players/' + playerId : '/api/players';
        let method = isUpdate ? 'PUT' : 'POST';

        App.showLoading();

        $.ajax({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(playerData),
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    App.showSuccess(isUpdate ? 'Player updated successfully' : 'Player created successfully');
                    renderListView();
                } else {
                    App.showError('Failed to save player: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to save player: ' + error);
            },
        });
    }

    // ========================================================================
    // Show View
    // ========================================================================

    /**
     * Render the show/detail view for a player
     */
    function renderShowView(player) {
        let over13Badge = getOverThirteenBadge(player.over_13);
        let characterName = player.mobile && player.mobile.what_we_call_you 
            ? player.mobile.what_we_call_you 
            : 'N/A';

        let html = `
            <div class="row mb-3">
                <div class="col">
                    <h2><i class="bi bi-eye"></i> Player Details</h2>
                </div>
                <div class="col-auto">
                    <button class="btn btn-outline-secondary" id="back-to-list-btn">
                        <i class="bi bi-arrow-left"></i> Back to List
                    </button>
                </div>
            </div>

            <div class="card mb-3">
                <div class="card-header">
                    <h5>Player Information</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>ID:</strong> ${player.id || 'N/A'}</p>
                            <p><strong>Full Name:</strong> ${App.escapeHtml(player.full_name)}</p>
                            <p><strong>Nickname:</strong> ${App.escapeHtml(player.what_we_call_you)}</p>
                            <p><strong>Email:</strong> ${App.escapeHtml(player.email)}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Year of Birth:</strong> ${player.year_of_birth || 'N/A'}</p>
                            <p><strong>Over 13:</strong> ${over13Badge}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card mb-3">
                <div class="card-header">
                    <h5>Character Information</h5>
                </div>
                <div class="card-body">
                    <p><strong>Character Name:</strong> ${App.escapeHtml(characterName)}</p>
        `;

        // Show mobile attributes if they exist
        if (player.mobile && player.mobile.attributes && Object.keys(player.mobile.attributes).length > 0) {
            html += `
                    <hr>
                    <h6>Character Attributes</h6>
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

            for (let attrTypeKey in player.mobile.attributes) {
                let attr = player.mobile.attributes[attrTypeKey];
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
            `;
        } else {
            html += '<p class="text-muted">No character attributes.</p>';
        }

        html += `
                </div>
            </div>
        `;

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
     * Load a player for display
     */
    function loadPlayerForShow(playerId) {
        App.showLoading();

        $.ajax({
            url: '/api/players/' + playerId,
            method: 'GET',
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    renderShowView(response.player);
                } else {
                    App.showError('Failed to load player: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load player: ' + error);
            },
        });
    }

    /**
     * Load a player for editing
     */
    function loadPlayerForEdit(playerId) {
        App.showLoading();

        $.ajax({
            url: '/api/players/' + playerId,
            method: 'GET',
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    editingPlayer = response.player;
                    renderFormView();
                } else {
                    App.showError('Failed to load player: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to load player: ' + error);
            },
        });
    }

    /**
     * Delete a player
     */
    function deletePlayer(playerId) {
        if (!confirm('Are you sure you want to delete this player? This will also delete their character and all associated data.')) {
            return;
        }

        App.showLoading();

        $.ajax({
            url: '/api/players/' + playerId,
            method: 'DELETE',
            success: function(response) {
                App.hideLoading();

                if (response.success) {
                    App.showSuccess('Player deleted successfully');
                    loadPlayers(); // Reload the list
                } else {
                    App.showError('Failed to delete player: ' + response.error);
                }
            },
            error: function(xhr, status, error) {
                App.hideLoading();
                App.showError('Failed to delete player: ' + error);
            },
        });
    }

    // Public API
    return {
        init: init,
    };
})();
