// main.js

// Constants
const SELECTORS = {
    //mainSearchForm: '#main-search-form', // Making issues with Moving searchBar
    mainSearch: '#main-search',
    navSearch: '#nav-search',
    //navSearchForm: '#nav-search-form', // Same as 'mainSearchForm'
    patientDetails: '#patient-details',
    flashMessages: '#flash-messages',
};

// Toast Configuration
const TOAST_TYPES = {
    success: '#22c55e',
    danger: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6'
};

/**
 * Search functionality management
 */
class SearchManager {
    constructor() {
        console.log('SearchManager: Initializing...');
        this.PREFIX = ""; // Add "SW" when 'mainSearchForm' issue fixed
        this.MAX_DIGITS = 9;

        this.mainSearchForm = document.querySelector(SELECTORS.mainSearchForm);
        this.mainSearch = document.querySelector(SELECTORS.mainSearch);
        this.navSearch = document.querySelector(SELECTORS.navSearch);
        this.navSearchForm = document.querySelector(SELECTORS.navSearchForm);
        this.patientDetails = document.querySelector(SELECTORS.patientDetails);
        this.isSearchInNav = false;

        console.log('SearchManager: Found elements:', {
            mainSearchForm: !!this.mainSearchForm,
            mainSearch: !!this.mainSearch,
            navSearch: !!this.navSearch,
            navSearchForm: !!this.navSearchForm,
            patientDetails: !!this.patientDetails
        });

        this.handleSearch = this.handleSearch.bind(this);
        this.initialize();
    }

    initialize() {
        console.log('SearchManager: Setting up initialization...');

        // Check if there are patient details on page load
        this.checkAndUpdateSearchPosition();

        // Setup both search inputs
        ['#main-patient-id', '#nav-patient-id'].forEach(selector => {
            const input = document.querySelector(selector);
            console.log(`SearchManager: Setting up input ${selector}:`, !!input);
            if (input) this.setupSearchInput(input);
        });

        // Setup main search form
        if (this.mainSearchForm) {
            console.log('SearchManager: Adding main form submit listener');
            this.mainSearchForm.addEventListener('submit', this.handleSearch.bind(this));
        }

        // Setup nav search form
        if (this.navSearchForm) {
            // console.log('SearchManager: Adding nav form submit listener');
            this.navSearchForm.addEventListener('submit', this.handleSearch);
        }

        // Handle browser back button
        window.addEventListener('popstate', () => {
            console.log('SearchManager: Back button clicked');
            this.checkAndUpdateSearchPosition();
        });
    }

    // New method to check patient details and update search position
    checkAndUpdateSearchPosition() {
        console.log('SearchManager: Checking patient details status');
        if (this.patientDetails && this.patientDetails.children.length > 0) {
            console.log('SearchManager: Patient details found, moving search to nav');
            this.moveSearchToNav();
        } else {
            console.log('SearchManager: No patient details, moving search to center');
            this.moveSearchToCenter();
        }
    }

    setupSearchInput(input) {
        console.log('SearchManager: Setting up input:', input.id);

        // Set initial value with prefix
        input.value = this.PREFIX;

        // Handle input changes
        input.addEventListener('input', (e) => {
            let value = e.target.value;
            console.log('SearchManager: Input change:', { value });

            // Always ensure prefix is present
            if (!value.startsWith(this.PREFIX)) {
                value = this.PREFIX;
            }

            // Remove any non-numeric characters after prefix
            const numericPart = value.substring(this.PREFIX.length).replace(/[^\d]/g, '');
            console.log('SearchManager: Numeric part:', numericPart);

            // Limit to MAX_DIGITS after prefix
            const limitedNumericPart = numericPart.substring(0, this.MAX_DIGITS);

            // Set the final value
            e.target.value = this.PREFIX + limitedNumericPart;
            console.log('SearchManager: Final value:', e.target.value);
        });

        // Prevent deletion of prefix
        input.addEventListener('keydown', (e) => {
            const cursorPosition = e.target.selectionStart;
            console.log('SearchManager: Keydown:', { key: e.key, cursorPosition });

            if ((e.key === 'Backspace' && cursorPosition <= this.PREFIX.length) ||
                (e.key === 'Delete' && cursorPosition < this.PREFIX.length)) {
                console.log('SearchManager: Preventing prefix deletion');
                e.preventDefault();
            }

            if (e.key === 'ArrowLeft' && cursorPosition <= this.PREFIX.length) {
                console.log('SearchManager: Preventing cursor before prefix');
                e.preventDefault();
            }

            if ((e.ctrlKey || e.metaKey) && (e.key === 'x' || e.key === 'a')) {
                console.log('SearchManager: Preventing cut/select all');
                e.preventDefault();
            }
        });

        // Prevent paste unless it's only numbers
        input.addEventListener('paste', (e) => {
            e.preventDefault();
            const pastedText = (e.clipboardData || window.clipboardData).getData('text');
            console.log('SearchManager: Paste attempt:', { pastedText });

            const numericPart = pastedText.replace(/[^\d]/g, '');
            const currentNumericPart = input.value.substring(this.PREFIX.length);
            const newNumericPart = (currentNumericPart + numericPart).substring(0, this.MAX_DIGITS);
            input.value = this.PREFIX + newNumericPart;
            console.log('SearchManager: After paste:', input.value);
        });

        // Prevent drag and drop
        input.addEventListener('drop', (e) => {
            console.log('SearchManager: Preventing drop');
            e.preventDefault();
        });
    }

    async handleSearch(e) {
        e.preventDefault();
        console.log('SearchManager: Search initiated');

        const form = e.target;
        const input = form.querySelector('input[name="patient_id"]');
        const numericValue = input.value.substring(this.PREFIX.length);

        console.log('SearchManager: Search values:', {
            fullValue: input.value,
            numericValue: numericValue
        });

        // Validation check
        if (numericValue.length !== this.MAX_DIGITS) {
            console.log('SearchManager: Invalid length', numericValue.length);
            showToast(`Please enter exactly ${this.MAX_DIGITS} digits after ${this.PREFIX}`, 'warning');
            return;
        }

        const searchUrl = '/patient/search';
        console.log('SearchManager: Making search request to:', searchUrl);

        try {
            const response = await fetchWithCSRF(`${form.action}?patient_id=${numericValue}`, {
                method: 'GET',
                headers: { 'Accept': 'text/html' }
            });

            console.log('SearchManager: Search response status:', response.status);

            if (response.ok) {
                const html = await response.text();
                if (this.patientDetails) {
                    console.log('SearchManager: Updating patient details');
                    this.patientDetails.innerHTML = html;

                    // Check and update search position after content is loaded
                    this.checkAndUpdateSearchPosition();

                    this.moveSearchToNav();
                    history.pushState({}, '', `${form.action}?patient_id=${numericValue}`);
                }
            } else {
                console.log('SearchManager: Patient not found');
                showToast('Patient not found', 'warning');
            }
        } catch (error) {
            console.error('SearchManager: Search error:', error);
            showToast('Error searching for patient', 'danger');
        }
    }

    moveSearchToNav() {
        console.log('SearchManager: Moving search to nav', {
            isSearchInNav: this.isSearchInNav,
            mainSearch: !!this.mainSearch,
            navSearch: !!this.navSearch
        });

        if (!this.isSearchInNav && this.mainSearch && this.navSearch) {
            console.log('SearchManager: Hiding main search');
            // Add hidden class to main search
            this.mainSearch.classList.add('hidden');
            this.mainSearch.style.display = 'none';
            this.mainSearch.style.visibility = 'hidden';
            this.mainSearch.style.opacity = '0';

            console.log('SearchManager: Showing nav search');
            // Show nav search with all required properties
            this.navSearch.classList.add('active');
            this.navSearch.style.display = 'block';
            this.navSearch.style.visibility = 'visible';
            this.navSearch.style.opacity = '1';

            this.isSearchInNav = true;
            console.log('SearchManager: Search moved to nav', {
                mainSearchClasses: this.mainSearch.className,
                navSearchClasses: this.navSearch.className
            });
        }
    }

    moveSearchToCenter() {
        console.log('SearchManager: Moving search to center', {
            isSearchInNav: this.isSearchInNav,
            mainSearch: !!this.mainSearch,
            navSearch: !!this.navSearch
        });

        if (this.isSearchInNav && this.mainSearch && this.navSearch) {
            console.log('SearchManager: Hiding nav search');
            // Hide nav search
            this.navSearch.classList.remove('active');
            this.navSearch.style.display = 'none';
            this.navSearch.style.visibility = 'hidden';
            this.navSearch.style.opacity = '0';

            console.log('SearchManager: Showing main search');
            // Show main search
            this.mainSearch.classList.remove('hidden');
            this.mainSearch.style.display = 'flex';
            this.mainSearch.style.visibility = 'visible';
            this.mainSearch.style.opacity = '1';

            this.isSearchInNav = false;
            console.log('SearchManager: Search moved to center', {
                mainSearchClasses: this.mainSearch.className,
                navSearchClasses: this.navSearch.className
            });
        }
    }
}

/**
 * Form handling with CSRF protection
 */
class FormManager {
    static getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : null;
    }

    static initialize() {
        // Add CSRF protection to forms
        document.querySelectorAll('form:not([data-no-csrf])').forEach(form => {
            if (!form.querySelector('input[name="csrf_token"]')) {
                const csrfToken = this.getCSRFToken();
                if (csrfToken) {
                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrf_token';
                    csrfInput.value = csrfToken;
                    form.appendChild(csrfInput);
                }
            }
        });
    }
}

/**
 * Toast notification system
 */
function showToast(message, type = 'info') {
    Toastify({
        text: message,
        duration: 3000,
        gravity: "bottom",
        position: "right",
        style: {
            background: TOAST_TYPES[type]
        },
        stopOnFocus: true,
        className: "custom-toast",
        offset: {
            x: 20,
            y: 20
        }
    }).showToast();
}

/**
 * Enhanced fetch with CSRF
 */
function fetchWithCSRF(url, options = {}) {
    const defaultOptions = {
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': FormManager.getCSRFToken(),
            ...options.headers
        },
    };
    return fetch(url, { ...defaultOptions, ...options });
}

// Global searchManager instance
let searchManager;

/**
 * Initialize everything when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM Content Loaded: Starting full initialization');

    // Initialize search functionality
    searchManager = new SearchManager();
    window.searchManager = searchManager; // Make it globally accessible
    console.log('SearchManager: Global instance created');

    // Initialize form protection
    if (typeof FormManager !== 'undefined') {
        console.log('FormManager: Initializing...');
        FormManager.initialize();
    } else {
        console.warn('FormManager not found');
    }

    // Initialize flash messages
    const flashContainer = document.getElementById('flash-messages');
    if (flashContainer) {
        console.log('Flash Messages: Container found, processing messages');
        try {
            const messages = JSON.parse(flashContainer.dataset.messages || '[]');
            console.log('Flash Messages:', messages);

            messages.forEach(([category, message]) => {
                console.log('Showing toast:', { category, message });
                showToast(message, category);
            });
        } catch (e) {
            console.error('Error parsing flash messages:', e);
            console.log('Raw flash messages data:', flashContainer.dataset.messages);
        }
    } else {
        console.log('Flash Messages: No flash container found');
    }

    console.log('DOM Content Loaded: Initialization complete');
});

// Export necessary functions for global use
window.showToast = showToast;
window.fetchWithCSRF = fetchWithCSRF;
