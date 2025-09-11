/**
 * Reusable Autocomplete Component
 * Usage: new Autocomplete(inputElement, options)
 */
class Autocomplete {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.options = {
            minLength: 2,
            delay: 300,
            apiUrl: '/sklad/autocomplete/',
            field: 'article_number',
            onSelect: null,
            placeholder: 'Търсене...',
            ...options
        };
        
        this.container = null;
        this.suggestions = [];
        this.selectedIndex = -1;
        this.timeout = null;
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        // Create container for suggestions
        this.createContainer();
        
        // Add event listeners
        this.input.addEventListener('input', this.handleInput.bind(this));
        this.input.addEventListener('keydown', this.handleKeydown.bind(this));
        this.input.addEventListener('blur', this.handleBlur.bind(this));
        this.input.addEventListener('focus', this.handleFocus.bind(this));
        
        // Add visual indicator
        this.input.style.position = 'relative';
    }
    
    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'autocomplete-suggestions';
        this.container.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 4px 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        `;
        
        // Insert after input
        this.input.parentNode.insertBefore(this.container, this.input.nextSibling);
    }
    
    handleInput(event) {
        const query = event.target.value.trim();
        
        // Clear previous timeout
        if (this.timeout) {
            clearTimeout(this.timeout);
        }
        
        // Hide suggestions if query is too short
        if (query.length < this.options.minLength) {
            this.hideSuggestions();
            return;
        }
        
        // Debounce the search
        this.timeout = setTimeout(() => {
            this.search(query);
        }, this.options.delay);
    }
    
    handleKeydown(event) {
        if (!this.isOpen) return;
        
        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.suggestions.length - 1);
                this.updateSelection();
                break;
            case 'ArrowUp':
                event.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection();
                break;
            case 'Enter':
                event.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectSuggestion(this.suggestions[this.selectedIndex]);
                }
                break;
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }
    
    handleBlur(event) {
        // Delay hiding to allow clicks on suggestions
        setTimeout(() => {
            this.hideSuggestions();
        }, 150);
    }
    
    handleFocus(event) {
        if (this.input.value.trim().length >= this.options.minLength) {
            this.search(this.input.value.trim());
        }
    }
    
    async search(query) {
        try {
            const url = `${this.options.apiUrl}?q=${encodeURIComponent(query)}&field=${this.options.field}`;
            const response = await fetch(url);
            const data = await response.json();
            
            this.suggestions = data.suggestions || [];
            this.selectedIndex = -1;
            this.renderSuggestions();
        } catch (error) {
            console.error('Autocomplete search error:', error);
            this.hideSuggestions();
        }
    }
    
    renderSuggestions() {
        if (this.suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }
        
        this.container.innerHTML = '';
        
        this.suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.style.cssText = `
                padding: 8px 12px;
                cursor: pointer;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            `;
            
            item.innerHTML = `
                <div>
                    <div style="font-weight: bold; color: #333;">${suggestion.article_number}</div>
                    <div style="font-size: 0.9em; color: #666;">${suggestion.name}</div>
                </div>
                <div style="text-align: right; font-size: 0.8em; color: #888;">
                    <div>${suggestion.quantity} ${suggestion.unit}</div>
                    <div>${suggestion.purchase_price.toFixed(2)} лв.</div>
                </div>
            `;
            
            item.addEventListener('mouseenter', () => {
                this.selectedIndex = index;
                this.updateSelection();
            });
            
            item.addEventListener('click', () => {
                this.selectSuggestion(suggestion);
            });
            
            this.container.appendChild(item);
        });
        
        this.showSuggestions();
    }
    
    updateSelection() {
        const items = this.container.querySelectorAll('.autocomplete-item');
        
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.style.backgroundColor = '#f0f0f0';
            } else {
                item.style.backgroundColor = 'white';
            }
        });
    }
    
    selectSuggestion(suggestion) {
        this.input.value = suggestion[this.options.field];
        
        // Call custom onSelect callback if provided
        if (this.options.onSelect && typeof this.options.onSelect === 'function') {
            this.options.onSelect(suggestion);
        }
        
        this.hideSuggestions();
    }
    
    showSuggestions() {
        this.container.style.display = 'block';
        this.isOpen = true;
    }
    
    hideSuggestions() {
        this.container.style.display = 'none';
        this.isOpen = false;
        this.selectedIndex = -1;
    }
    
    // Public method to clear suggestions
    clear() {
        this.suggestions = [];
        this.hideSuggestions();
    }
    
    // Public method to destroy the autocomplete
    destroy() {
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        
        this.input.removeEventListener('input', this.handleInput);
        this.input.removeEventListener('keydown', this.handleKeydown);
        this.input.removeEventListener('blur', this.handleBlur);
        this.input.removeEventListener('focus', this.handleFocus);
    }
}

// Auto-initialize autocomplete for elements with data-autocomplete attribute
document.addEventListener('DOMContentLoaded', function() {
    const autocompleteElements = document.querySelectorAll('[data-autocomplete]');
    
    autocompleteElements.forEach(element => {
        const field = element.getAttribute('data-autocomplete-field') || 'article_number';
        const apiUrl = element.getAttribute('data-autocomplete-url') || '/sklad/autocomplete/';
        
        new Autocomplete(element, {
            field: field,
            apiUrl: apiUrl,
            onSelect: function(suggestion) {
                // Auto-fill other fields if they exist
                const nameField = document.getElementById('id_name');
                const unitField = document.getElementById('id_unit');
                const quantityField = document.getElementById('id_quantity');
                const priceField = document.getElementById('id_purchase_price');
                
                if (nameField) nameField.value = suggestion.name;
                if (unitField) unitField.value = suggestion.unit;
                if (quantityField) quantityField.value = suggestion.quantity;
                if (priceField) priceField.value = suggestion.purchase_price;
                
                // Trigger change events for any calculations
                if (quantityField) quantityField.dispatchEvent(new Event('input'));
                if (priceField) priceField.dispatchEvent(new Event('input'));
            }
        });
    });
});
