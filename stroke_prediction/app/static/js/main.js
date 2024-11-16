// Constants
const SELECTORS = {
    mainSearchForm: '#search-form',
    mainSearch: '.search-container',
    navSearch: '#nav-search',
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
        this.mainSearchForm = document.querySelector(SELECTORS.mainSearchForm);
        this.mainSearch = document.querySelector(SELECTORS.mainSearch);
        this.navSearch = document.querySelector(SELECTORS.navSearch);
        this.patientDetails = document.querySelector(SELECTORS.patientDetails);
        this.isSearchInNav = false;

        this.initialize();
    }

    initialize() {
        if (this.mainSearchForm) {
            this.mainSearchForm.addEventListener('submit', this.handleSearch.bind(this));
        }

        // Initialize search position based on patient details
        if (this.patientDetails?.children.length > 0) {
            this.moveSearchToNav();
        }

        // Handle browser back button
        window.addEventListener('popstate', () => {
            if (!this.patientDetails?.children.length) {
                this.moveSearchToCenter();
            }
        });
    }

    async handleSearch(e) {
        e.preventDefault();
        const form = e.target;
        const patientId = form.querySelector('#patient_id').value;

        try {
            const response = await fetchWithCSRF(`${form.action}?patient_id=${patientId}`, {
                method: 'GET',
                headers: { 'Accept': 'text/html' }
            });

            if (response.ok) {
                const html = await response.text();
                if (this.patientDetails) {
                    this.patientDetails.innerHTML = html;
                    this.moveSearchToNav();
                    history.pushState({}, '', `${form.action}?patient_id=${patientId}`);
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

                // If nav search doesn't have the form yet, copy it
                if (!this.navSearch.querySelector('.search-input-container')) {
                    // Get only the search input container from main search
                    const searchContent = this.mainSearch.querySelector('.search-input-container').cloneNode(true);

                    // Create a new form with proper structure
                    const navSearchForm = document.createElement('form');
                    navSearchForm.action = this.mainSearchForm.action;
                    navSearchForm.method = 'get';
                    navSearchForm.id = 'nav-search-form';
                    navSearchForm.className = 'search-form';

                    // Add the search content to the form
                    navSearchForm.appendChild(searchContent);

                    // Clear and add to nav search
                    this.navSearch.innerHTML = '';
                    this.navSearch.appendChild(navSearchForm);

                    // Add event listener to new form
                    navSearchForm.addEventListener('submit', this.handleSearch.bind(this));
                }

                // Show nav search with transition
                this.navSearch.classList.add('active');
            }, 300);

            this.isSearchInNav = true;
        }
    }

    moveSearchToCenter() {
        if (this.isSearchInNav && this.mainSearch && this.navSearch) {
            // Hide nav search
            this.navSearch.classList.remove('active');

            // Clear nav search content after transition
            setTimeout(() => {
                this.navSearch.innerHTML = '';
            }, 300);

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

    static async handleSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        try {
            const response = await fetchWithCSRF(form.action, {
                method: form.method,
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                showToast(data.message || 'Operation successful', 'success');
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            } else {
                showToast(data.message || 'Operation failed', 'danger');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            showToast('An error occurred', 'danger');
        }
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

        // Add submit handlers to ajax forms
        document.querySelectorAll('form[data-ajax="true"]').forEach(form => {
            form.addEventListener('submit', this.handleSubmit);
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
        backgroundColor: TOAST_TYPES[type],
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

/**
 * Initialize everything when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function () {
    // Initialize search functionality
    new SearchManager();

    // Initialize form protection and handlers
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