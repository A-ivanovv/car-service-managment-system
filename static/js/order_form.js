// Order Form JavaScript
let eurRate = 1.95583; // Default rate, will be updated from server

document.addEventListener('DOMContentLoaded', function() {
    // Load EUR rate from server
    loadEurRate();
    
    // Initialize autocomplete functionality
    initializeAutocomplete();
    
    // Initialize calculations
    initializeCalculations();
    
    // Initialize sklad modal
    initializeSkladModal();
    
    // Initialize form interactions
    initializeFormInteractions();
    
    // Populate unit dropdowns after everything is loaded
    setTimeout(function() {
        populateExistingUnitDropdowns();
    }, 100);
});

function loadEurRate() {
    // Load EUR rate from server
    fetch('/poruchki/currency-rate/')
        .then(response => response.json())
        .then(data => {
            if (data.rate) {
                eurRate = data.rate;
            }
        })
        .catch(error => {
            console.log('Using default EUR rate:', eurRate);
        });
}

function initializeAutocomplete() {
    // Car VIN autocomplete
    const carVinInput = document.getElementById('car-vin');
    if (carVinInput) {
        setupAutocomplete(carVinInput, '/poruchki/autocomplete/car-vin/', function(selectedItem) {
            // Fill car information when VIN is selected
            fillCarInfo(selectedItem);
        });
    }
    
    // Car plate number autocomplete
    const carPlateInput = document.getElementById('car-plate-number');
    if (carPlateInput) {
        setupAutocomplete(carPlateInput, '/poruchki/autocomplete/car-plate/', function(selectedItem) {
            // Fill car information when plate is selected
            fillCarInfo(selectedItem);
        });
    }
    
    // Client name autocomplete
    const clientNameInput = document.getElementById('client-name');
    if (clientNameInput) {
        setupAutocomplete(clientNameInput, '/poruchki/autocomplete/client/', function(selectedItem) {
            // Fill client information when client is selected
            fillClientInfo(selectedItem);
        });
    }
}

function setupAutocomplete(input, url, onSelect) {
    let timeout;
    let dropdown;
    
    input.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Clear previous timeout
        clearTimeout(timeout);
        
        // Remove existing dropdown
        if (dropdown) {
            dropdown.remove();
        }
        
        if (query.length < 2) {
            return;
        }
        
        // Set timeout to avoid too many requests
        timeout = setTimeout(() => {
            fetch(`${url}?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.suggestions && data.suggestions.length > 0) {
                        showAutocompleteDropdown(input, data.suggestions, onSelect);
                    }
                })
                .catch(error => console.error('Autocomplete error:', error));
        }, 300);
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (dropdown && !dropdown.contains(e.target) && e.target !== input) {
            dropdown.remove();
        }
    });
}

function showAutocompleteDropdown(input, suggestions, onSelect) {
    // Remove existing dropdown
    const existingDropdown = document.querySelector('.autocomplete-dropdown');
    if (existingDropdown) {
        existingDropdown.remove();
    }
    
    // Create dropdown
    const dropdown = document.createElement('div');
    dropdown.className = 'autocomplete-dropdown position-absolute bg-white border border-secondary rounded shadow-sm';
    dropdown.style.zIndex = '1000';
    dropdown.style.maxHeight = '200px';
    dropdown.style.overflowY = 'auto';
    dropdown.style.width = input.offsetWidth + 'px';
    
    // Position dropdown
    const rect = input.getBoundingClientRect();
    dropdown.style.top = (rect.bottom + window.scrollY) + 'px';
    dropdown.style.left = (rect.left + window.scrollX) + 'px';
    
    // Add suggestions
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item p-2 border-bottom cursor-pointer';
        item.style.cursor = 'pointer';
        item.innerHTML = suggestion.display_text;
        
        item.addEventListener('click', function() {
            onSelect(suggestion);
            dropdown.remove();
        });
        
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'white';
        });
        
        dropdown.appendChild(item);
    });
    
    // Add to document
    document.body.appendChild(dropdown);
}

function fillCarInfo(carData, clientData) {
    // Fill car select
    const carSelect = document.getElementById('car-select');
    if (carSelect) {
        carSelect.value = carData.id;
    }
    
    // Fill car fields
    const brandModelInput = document.getElementById('car-brand-model');
    if (brandModelInput) {
        brandModelInput.value = carData.brand_model || '';
    }
    
    const vinInput = document.getElementById('car-vin');
    if (vinInput) {
        vinInput.value = carData.vin || '';
    }
    
    const plateInput = document.getElementById('car-plate-number');
    if (plateInput) {
        plateInput.value = carData.plate_number || '';
    }
    
    const mileageInput = document.getElementById('car-mileage');
    if (mileageInput) {
        mileageInput.value = carData.mileage || '';
    }
    
    // Fill client information if available
    if (clientData) {
        // Fill client select dropdown
        const clientSelect = document.getElementById('client-select');
        if (clientSelect) {
            clientSelect.value = clientData.id;
        }
        
        // Fill client fields
        const clientNameInput = document.getElementById('client-name');
        if (clientNameInput) {
            clientNameInput.value = clientData.name || '';
        }
        
        const clientAddressInput = document.getElementById('client-address');
        if (clientAddressInput) {
            clientAddressInput.value = clientData.address || '';
        }
        
        const clientPhoneInput = document.getElementById('client-phone');
        if (clientPhoneInput) {
            clientPhoneInput.value = clientData.phone || '';
        }
    }
}

function fillClientInfo(clientData) {
    // Fill client select
    const clientSelect = document.getElementById('client-select');
    if (clientSelect) {
        clientSelect.value = clientData.id;
    }
    
    // Fill client fields
    const clientNameInput = document.getElementById('client-name');
    if (clientNameInput) {
        clientNameInput.value = clientData.name;
    }
    
    const clientAddressInput = document.getElementById('client-address');
    if (clientAddressInput) {
        clientAddressInput.value = clientData.address;
    }
    
    const clientPhoneInput = document.getElementById('client-phone');
    if (clientPhoneInput) {
        clientPhoneInput.value = clientData.phone;
    }
}

function initializeCalculations() {
    // Add event listeners to all quantity and price inputs
    document.addEventListener('input', function(e) {
        if (e.target.matches('input[name$="-quantity"], input[name$="-purchase_price"]')) {
            calculateRowTotal(e.target.closest('tr'));
            calculateGrandTotal();
        }
    });
    
    // Add event listeners to VAT checkboxes
    document.addEventListener('change', function(e) {
        if (e.target.matches('input[name$="-include_vat"]')) {
            calculateRowTotal(e.target.closest('tr'));
            calculateGrandTotal();
        }
    });
    
    // Initial calculation
    calculateGrandTotal();
}

function calculateRowTotal(row) {
    const quantityInput = row.querySelector('input[name$="-quantity"]');
    const priceInput = row.querySelector('input[name$="-purchase_price"]');
    const includeVatCheckbox = row.querySelector('input[name$="-include_vat"]');
    
    const quantity = parseFloat(quantityInput?.value) || 0;
    const price = parseFloat(priceInput?.value) || 0;
    const includeVat = includeVatCheckbox?.checked || false;
    
    const totalPrice = quantity * price;
    const priceWithVat = includeVat ? price * 1.20 : price;
    const totalWithVat = includeVat ? totalPrice * 1.20 : totalPrice;
    
    // Update display values with dual currency
    const priceWithVatCell = row.querySelector('.price-with-vat');
    if (priceWithVatCell) {
        const bgnPrice = priceWithVatCell.querySelector('.bgn-price');
        const eurPrice = priceWithVatCell.querySelector('.eur-price');
        if (bgnPrice) bgnPrice.textContent = priceWithVat.toFixed(2) + ' лв.';
        if (eurPrice) eurPrice.textContent = (priceWithVat / eurRate).toFixed(2) + ' €';
    }
    
    const totalPriceCell = row.querySelector('.total-price');
    if (totalPriceCell) {
        const bgnPrice = totalPriceCell.querySelector('.bgn-price');
        const eurPrice = totalPriceCell.querySelector('.eur-price');
        if (bgnPrice) bgnPrice.textContent = totalPrice.toFixed(2) + ' лв.';
        if (eurPrice) eurPrice.textContent = (totalPrice / eurRate).toFixed(2) + ' €';
    }
}

function calculateGrandTotal() {
    let totalWithoutVat = 0;
    let totalVat = 0;
    let totalWithVat = 0;
    let hasVatItems = false;
    
    // Calculate total from all rows
    document.querySelectorAll('#itemsTableBody tr').forEach(row => {
        const quantityInput = row.querySelector('input[name$="-quantity"]');
        const priceInput = row.querySelector('input[name$="-purchase_price"]');
        const includeVatCheckbox = row.querySelector('input[name$="-include_vat"]');
        
        const quantity = parseFloat(quantityInput?.value) || 0;
        const price = parseFloat(priceInput?.value) || 0;
        const includeVat = includeVatCheckbox?.checked || false;
        
        const rowTotal = quantity * price;
        totalWithoutVat += rowTotal;
        
        if (includeVat) {
            hasVatItems = true;
            const rowVat = rowTotal * 0.20;
            totalVat += rowVat;
            totalWithVat += rowTotal + rowVat;
        } else {
            totalWithVat += rowTotal;
        }
    });
    
    // Update totals with dual currency
    updateTotalDisplay('totalWithoutVat', totalWithoutVat);
    updateTotalDisplay('totalVat', totalVat);
    updateTotalDisplay('totalWithVat', totalWithVat);
    
    // Show/hide VAT row and update total label
    const vatRow = document.getElementById('vatRow');
    const totalLabel = document.getElementById('totalLabel');
    
    if (hasVatItems) {
        if (vatRow) vatRow.style.display = '';
        if (totalLabel) totalLabel.textContent = 'Общо с ДДС:';
    } else {
        if (vatRow) vatRow.style.display = 'none';
        if (totalLabel) totalLabel.textContent = 'Общо:';
    }
}

function updateTotalDisplay(elementId, amount) {
    const element = document.getElementById(elementId);
    if (element) {
        const bgnPrice = element.querySelector('.bgn-price');
        const eurPrice = element.querySelector('.eur-price');
        if (bgnPrice) bgnPrice.textContent = amount.toFixed(2) + ' лв.';
        if (eurPrice) eurPrice.textContent = (amount / eurRate).toFixed(2) + ' €';
    }
}

function initializeSkladModal() {
    const skladModal = new bootstrap.Modal(document.getElementById('skladModal'));
    let currentRow = null;
    let currentPage = 1;
    let searchTimeout;
    
    // Add event listeners to sklad modal buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.sklad-modal-btn')) {
            currentRow = e.target.closest('tr');
            currentPage = 1;
            loadSkladData();
            skladModal.show();
        }
    });
    
    // Load units for filter
    loadSkladUnits();
    
    // Search functionality with autocomplete
    const searchInput = document.getElementById('skladSearch');
    const unitFilter = document.getElementById('skladUnitFilter');
    const clearBtn = document.getElementById('skladClearBtn');
    
    // Setup autocomplete search
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            // Clear previous timeout
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                // If query is too short, load all data
                currentPage = 1;
                loadSkladData();
                return;
            }
            
            // Set timeout to avoid too many requests
            searchTimeout = setTimeout(() => {
                currentPage = 1;
                loadSkladData();
            }, 300);
        });
    }
    
    if (unitFilter) {
        unitFilter.addEventListener('change', function() {
            currentPage = 1;
            loadSkladData();
        });
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            searchInput.value = '';
            unitFilter.value = '';
            currentPage = 1;
            loadSkladData();
        });
    }
    
    function loadSkladUnits() {
        fetch('/poruchki/sklad-units/')
            .then(response => response.json())
            .then(data => {
                const unitFilter = document.getElementById('skladUnitFilter');
                if (unitFilter) {
                    // Clear existing options except the first one
                    unitFilter.innerHTML = '<option value="">Всички мерни единици</option>';
                    
                    data.units.forEach(unit => {
                        const option = document.createElement('option');
                        option.value = unit;
                        option.textContent = unit;
                        unitFilter.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('Error loading units:', error));
    }
    
    function loadSkladData() {
        const searchQuery = searchInput.value.trim();
        const unit = unitFilter.value;
        
        const params = new URLSearchParams({
            page: currentPage
        });
        
        if (searchQuery) {
            params.append('search', searchQuery);
        }
        
        if (unit) {
            params.append('unit', unit);
        }
        
        fetch(`/poruchki/sklad-modal-data/?${params}`)
            .then(response => response.json())
            .then(data => {
                displaySkladItems(data.items);
                displaySkladPagination(data.pagination);
            })
            .catch(error => console.error('Sklad data error:', error));
    }
    
    function displaySkladItems(items) {
        const tbody = document.getElementById('skladTableBody');
        tbody.innerHTML = '';
        
        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Няма намерени артикули</td></tr>';
            return;
        }
        
        items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.article_number}</td>
                <td>${item.name}</td>
                <td>${item.unit}</td>
                <td>${item.quantity}</td>
                <td>${item.purchase_price.toFixed(2)} лв.</td>
                <td>${item.total_value.toFixed(2)} лв.</td>
                <td>
                    <button type="button" class="btn btn-sm btn-primary select-sklad-item" 
                            data-item='${JSON.stringify(item)}'>
                        <i class="fas fa-check me-1"></i>Избери
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    function displaySkladPagination(pagination) {
        const paginationList = document.getElementById('skladPaginationList');
        paginationList.innerHTML = '';
        
        if (pagination.total_pages <= 1) {
            return;
        }
        
        const currentPage = pagination.current_page;
        const totalPages = pagination.total_pages;
        const maxVisiblePages = 7; // Show max 7 page numbers
        
        // Previous button
        if (pagination.has_previous) {
            const prevLi = document.createElement('li');
            prevLi.className = 'page-item';
            prevLi.innerHTML = `<a class="page-link" href="#" data-page="${pagination.previous_page}">Предишна</a>`;
            paginationList.appendChild(prevLi);
        }
        
        // Calculate which pages to show
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        // Adjust start page if we're near the end
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        // First page and ellipsis
        if (startPage > 1) {
            const firstLi = document.createElement('li');
            firstLi.className = 'page-item';
            firstLi.innerHTML = `<a class="page-link" href="#" data-page="1">1</a>`;
            paginationList.appendChild(firstLi);
            
            if (startPage > 2) {
                const ellipsisLi = document.createElement('li');
                ellipsisLi.className = 'page-item disabled';
                ellipsisLi.innerHTML = `<span class="page-link">...</span>`;
                paginationList.appendChild(ellipsisLi);
            }
        }
        
        // Page numbers
        for (let i = startPage; i <= endPage; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
            pageLi.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
            paginationList.appendChild(pageLi);
        }
        
        // Last page and ellipsis
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsisLi = document.createElement('li');
                ellipsisLi.className = 'page-item disabled';
                ellipsisLi.innerHTML = `<span class="page-link">...</span>`;
                paginationList.appendChild(ellipsisLi);
            }
            
            const lastLi = document.createElement('li');
            lastLi.className = 'page-item';
            lastLi.innerHTML = `<a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>`;
            paginationList.appendChild(lastLi);
        }
        
        // Next button
        if (pagination.has_next) {
            const nextLi = document.createElement('li');
            nextLi.className = 'page-item';
            nextLi.innerHTML = `<a class="page-link" href="#" data-page="${pagination.next_page}">Следваща</a>`;
            paginationList.appendChild(nextLi);
        }
        
        // Add click handlers for pagination (remove existing listeners first)
        const existingHandler = paginationList.getAttribute('data-handler-attached');
        if (!existingHandler) {
            paginationList.addEventListener('click', function(e) {
                e.preventDefault();
                if (e.target.matches('.page-link')) {
                    currentPage = parseInt(e.target.dataset.page);
                    loadSkladData();
                }
            });
            paginationList.setAttribute('data-handler-attached', 'true');
        }
    }
    
    // Handle sklad item selection
    document.addEventListener('click', function(e) {
        if (e.target.closest('.select-sklad-item')) {
            const itemData = JSON.parse(e.target.dataset.item);
            selectSkladItem(itemData);
            skladModal.hide();
        }
    });
    
    function selectSkladItem(itemData) {
        if (!currentRow) return;
        
        // Fill the row with sklad item data
        const skladItemInput = currentRow.querySelector('select[name$="-sklad_item"]');
        if (skladItemInput) {
            skladItemInput.value = itemData.id;
        }
        
        const articleNumberInput = currentRow.querySelector('input[name$="-article_number"]');
        if (articleNumberInput) {
            articleNumberInput.value = itemData.article_number;
        }
        
        const nameInput = currentRow.querySelector('input[name$="-name"]');
        if (nameInput) {
            nameInput.value = itemData.name;
        }
        
        const unitSelect = currentRow.querySelector('select[name$="-unit"]');
        if (unitSelect) {
            unitSelect.value = itemData.unit;
        }
        
        const priceInput = currentRow.querySelector('input[name$="-purchase_price"]');
        if (priceInput) {
            priceInput.value = itemData.purchase_price;
        }
        
        // Recalculate totals
        calculateRowTotal(currentRow);
        calculateGrandTotal();
    }
}

function populateExistingUnitDropdowns() {
    // Get all existing unit dropdowns - try both naming patterns
    const unitDropdowns = document.querySelectorAll('select[name*="unit"], select[name$="-unit"]');
    
    console.log('Found unit dropdowns:', unitDropdowns.length);
    
    if (unitDropdowns.length > 0) {
        // Fetch units and populate all dropdowns
        fetch('/poruchki/sklad-units/')
            .then(response => response.json())
            .then(data => {
                console.log('Units data:', data);
                unitDropdowns.forEach(dropdown => {
                    // Clear existing options except the first one
                    dropdown.innerHTML = '<option value="">Избери мерна единица</option>';
                    
                    data.units.forEach(unit => {
                        const option = document.createElement('option');
                        option.value = unit;
                        option.textContent = unit;
                        dropdown.appendChild(option);
                    });
                });
            })
            .catch(error => console.error('Error loading units:', error));
    }
}

function initializeFormInteractions() {
    // Add new item button
    const addItemBtn = document.getElementById('addItemBtn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            addNewItemRow();
        });
    }
    
    // Remove item buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.remove-item-btn')) {
            const row = e.target.closest('tr');
            if (row) {
                row.remove();
                updateFormsetManagement();
                calculateGrandTotal();
            }
        }
    });
    
    // Unit dropdowns are populated in the main initialization
    
    // Car select change is now handled in the inline script in the template
    
    // Client select change - populate client information when client is selected
    const clientSelect = document.getElementById('client-select');
    if (clientSelect) {
        clientSelect.addEventListener('change', function() {
            if (this.value) {
                // Fetch client information and populate fields
                fetchClientInfo(this.value);
            } else {
                // Clear client fields if no client selected
                clearClientFields();
            }
        });
    }
}

function fetchCarInfo(carId) {
    // Fetch car information by ID
    fetch(`/poruchki/get-car-info/?car_id=${carId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fillCarInfo(data.car, data.client);
            }
        })
        .catch(error => console.error('Error fetching car info:', error));
}

function fetchClientInfo(clientId) {
    // Fetch client information by ID
    fetch(`/poruchki/get-client-info/?client_id=${clientId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fillClientInfo(data.client);
            }
        })
        .catch(error => console.error('Error fetching client info:', error));
}

function updateFormsetManagement() {
    // Update the TOTAL_FORMS count in the management form
    const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');
    if (totalFormsInput) {
        const tbody = document.getElementById('itemsTableBody');
        const rowCount = tbody.querySelectorAll('tr').length;
        totalFormsInput.value = rowCount;
    }
}

function addNewItemRow() {
    const tbody = document.getElementById('itemsTableBody');
    const rowCount = tbody.querySelectorAll('tr').length;
    
    const newRow = document.createElement('tr');
    newRow.className = 'item-row';
    newRow.innerHTML = `
        <td class="text-center">${rowCount + 1}</td>
        <td style="display: none;">
            <select class="form-select" name="order_items-${rowCount}-sklad_item">
                <option value="">---------</option>
            </select>
        </td>
        <td>
            <input type="text" class="form-control" name="order_items-${rowCount}-article_number" placeholder="Артикул номер">
        </td>
        <td>
            <input type="text" class="form-control" name="order_items-${rowCount}-name" placeholder="Наименование" required>
        </td>
        <td>
            <select class="form-select" name="order_items-${rowCount}-unit" required>
                <option value="">Избери мерна единица</option>
            </select>
        </td>
        <td>
            <input type="number" class="form-control quantity-input" name="order_items-${rowCount}-quantity" step="0.01" min="0" placeholder="0.00" required>
        </td>
        <td>
            <input type="number" class="form-control price-input" name="order_items-${rowCount}-purchase_price" step="0.01" min="0" placeholder="0.00" required>
        </td>
        <td class="price-with-vat">
            <div class="bgn-price">0.00 лв.</div>
            <div class="eur-price text-muted small">0.00 €</div>
        </td>
        <td class="total-price">
            <div class="bgn-price">0.00 лв.</div>
            <div class="eur-price text-muted small">0.00 €</div>
        </td>
        <td class="text-center">
            <input type="checkbox" class="form-check-input include-vat-checkbox" name="order_items-${rowCount}-include_vat" checked>
        </td>
        <td class="text-center">
            <button type="button" class="btn btn-sm btn-outline-primary sklad-modal-btn" title="Избери от склад">
                <i class="fas fa-warehouse"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-danger remove-item-btn" title="Премахни">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    
    tbody.appendChild(newRow);
    
    // Update formset management form
    updateFormsetManagement();
    
    // Populate unit dropdown
    const unitSelect = newRow.querySelector('select[name*="unit"]');
    if (unitSelect) {
        fetch('/poruchki/sklad-units/')
            .then(response => response.json())
            .then(data => {
                // Clear existing options except the first one
                unitSelect.innerHTML = '<option value="">Избери мерна единица</option>';
                
                data.units.forEach(unit => {
                    const option = document.createElement('option');
                    option.value = unit;
                    option.textContent = unit;
                    unitSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error loading units:', error));
    }
    
    // Add event listeners to new inputs
    const quantityInput = newRow.querySelector('input[name$="-quantity"]');
    const priceInput = newRow.querySelector('input[name$="-purchase_price"]');
    const includeVatCheckbox = newRow.querySelector('input[name$="-include_vat"]');
    
    if (quantityInput) {
        quantityInput.addEventListener('input', function() {
            calculateRowTotal(newRow);
            calculateGrandTotal();
        });
    }
    
    if (priceInput) {
        priceInput.addEventListener('input', function() {
            calculateRowTotal(newRow);
            calculateGrandTotal();
        });
    }
    
    if (includeVatCheckbox) {
        includeVatCheckbox.addEventListener('change', function() {
            calculateRowTotal(newRow);
            calculateGrandTotal();
        });
    }
}

function clearCarFields() {
    const fields = ['car-brand-model', 'car-vin', 'car-plate-number', 'car-mileage'];
    fields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = '';
        }
    });
}

function clearClientFields() {
    const fields = ['client-name', 'client-address', 'client-phone'];
    fields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = '';
        }
    });
}
