// Constants
const SELECTORS = {
    mainSearchForm: '#main-search-form',
    mainSearch: '#main-search',
    navSearch: '#nav-search',
    navSearchForm: '#nav-search-form',
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
        this.PREFIX = "SW";
        this.MAX_DIGITS = 9;

        this.mainSearchForm = document.querySelector(SELECTORS.mainSearchForm);
        this.mainSearch = document.querySelector(SELECTORS.mainSearch);
        this.navSearch = document.querySelector(SELECTORS.navSearch);
        this.navSearchForm = document.querySelector(SELECTORS.navSearchForm);
        this.patientDetails = document.querySelector(SELECTORS.patientDetails);
        this.isSearchInNav = false;

        this.handleSearch = this.handleSearch.bind(this);
        this.initialize();
    }

    initialize() {
        // Setup both search inputs
        ['#main-patient-id', '#nav-patient-id'].forEach(selector => {
            const input = document.querySelector(selector);
            if (input) this.setupSearchInput(input);
        });

        // Setup main search form
        if (this.mainSearchForm) {
            this.mainSearchForm.addEventListener('submit', this.handleSearch);
        }

        // Setup nav search form
        if (this.navSearchForm) {
            this.navSearchForm.addEventListener('submit', this.handleSearch);
        }

        // Initialize search position based on patient details
        if (this.patientDetails?.children.length > 0) {
            this.moveSearchToNav();
        }

        // Handle browser back button
        window.addEventListener('popstate', () => {
            console.log('Back button clicked');
            if (!this.patientDetails?.children.length) {
                this.moveSearchToCenter();
            }
        });
    }

    setupSearchInput(input) {
        if (!input) return;

        // Set initial value with prefix
        input.value = this.PREFIX;

        // Handle input changes
        input.addEventListener('input', (e) => {
            let value = e.target.value;

            // Always ensure prefix is present
            if (!value.startsWith(this.PREFIX)) {
                value = this.PREFIX;
            }

            // Remove any non-numeric characters after prefix
            const numericPart = value.substring(this.PREFIX.length).replace(/[^\d]/g, '');

            // Limit to MAX_DIGITS after prefix
            const limitedNumericPart = numericPart.substring(0, this.MAX_DIGITS);

            // Set the final value
            e.target.value = this.PREFIX + limitedNumericPart;
        });

        // Prevent deletion of prefix
        input.addEventListener('keydown', (e) => {
            const cursorPosition = e.target.selectionStart;

            // Prevent backspace/delete if it would affect the prefix
            if ((e.key === 'Backspace' && cursorPosition <= this.PREFIX.length) ||
                (e.key === 'Delete' && cursorPosition < this.PREFIX.length)) {
                e.preventDefault();
            }

            // Prevent cursor placement before prefix
            if (e.key === 'ArrowLeft' && cursorPosition <= this.PREFIX.length) {
                e.preventDefault();
            }

            // Prevent cutting/copying prefix
            if ((e.ctrlKey || e.metaKey) && (e.key === 'x' || e.key === 'a')) {
                e.preventDefault();
            }
        });

        // Prevent paste unless it's only numbers
        input.addEventListener('paste', (e) => {
            e.preventDefault();
            const pastedText = (e.clipboardData || window.clipboardData).getData('text');
            const numericPart = pastedText.replace(/[^\d]/g, '');
            const currentNumericPart = input.value.substring(this.PREFIX.length);
            const newNumericPart = (currentNumericPart + numericPart).substring(0, this.MAX_DIGITS);
            input.value = this.PREFIX + newNumericPart;
        });

        // Prevent drag and drop
        input.addEventListener('drop', (e) => {
            e.preventDefault();
        });
    }

    async handleSearch(e) {
        e.preventDefault();
        console.log('Search initiated');

        const form = e.target;
        const input = form.querySelector('input[name="patient_id"]');
        const numericValue = input.value.substring(this.PREFIX.length);

        console.log('Input value:', input.value);
        console.log('Numeric value:', numericValue);

        // Only submit if we have exactly MAX_DIGITS numbers
        if (numericValue.length !== this.MAX_DIGITS) {
            showToast(`Please enter exactly ${this.MAX_DIGITS} digits after ${this.PREFIX}`, 'warning');
            return;
        }

        const searchUrl = '/patient/search';

        try {
            const response = await fetchWithCSRF(`${searchUrl}?patient_id=${numericValue}`, {
                method: 'GET',
                headers: { 'Accept': 'text/html' }
            });

            if (response.ok) {
                const html = await response.text();
                if (this.patientDetails) {
                    this.patientDetails.innerHTML = html;
                    this.moveSearchToNav();
                    history.pushState({}, '', `${searchUrl}?patient_id=${numericValue}`);
                }
            } else {
                showToast('Patient not found', 'warning');
            }
        } catch (error) {
            console.error('Search error:', error);
            showToast('Error searching for patient', 'danger');
        }
    }

    moveSearchToNav() {

        if (!this.isSearchInNav && this.mainSearch && this.navSearch) {
            // Hide main search container with transition
            this.mainSearch.style.opacity = '0';
            this.mainSearch.style.transform = 'translateY(-20px)';

            setTimeout(() => {
                // Completely hide the main search
                this.mainSearch.style.display = 'none';
                // Show nav search with transition
                this.navSearch.classList.add('active');

                // Ensure nav search input has the same value
                const mainInput = document.querySelector('#main-patient-id');
                const navInput = document.querySelector('#nav-patient-id');
                if (mainInput && navInput) {
                    navInput.value = mainInput.value;
                }
            }, 300);

            this.isSearchInNav = true;
        }
    }

    moveSearchToCenter() {
        if (this.isSearchInNav && this.mainSearch && this.navSearch) {
            // Hide nav search
            this.navSearch.classList.remove('active');

            // Show main search with transition
            this.mainSearch.style.display = 'flex';
            setTimeout(() => {
                this.mainSearch.style.opacity = '1';
                this.mainSearch.style.transform = 'translateY(0)';
            }, 10);

            this.isSearchInNav = false;
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

// Initialize everything when DOM is loaded
let searchManager;
document.addEventListener('DOMContentLoaded', function () {
    searchManager = new SearchManager();
    window.searchManager = searchManager;

    // Initialize form protection
    FormManager.initialize();

    // Initialize flash messages
    const flashContainer = document.getElementById('flash-messages');
    if (flashContainer) {
        try {
            const messages = JSON.parse(flashContainer.dataset.messages || '[]');
            messages.forEach(([category, message]) => {
                showToast(message, category);
            });
        } catch (e) {
            console.error('Error parsing flash messages:', e);
        }
    }
});

// Export necessary functions for global use
window.showToast = showToast;
window.fetchWithCSRF = fetchWithCSRF;