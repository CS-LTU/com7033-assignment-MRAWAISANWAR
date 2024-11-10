// CSRF Token handling
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : null;
}

// Enhanced fetch with CSRF
function fetchWithCSRF(url, options = {}) {
    const defaultOptions = {
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            ...options.headers
        },
    };
    return fetch(url, { ...defaultOptions, ...options });
}

// Toast notification function
function showToast(message, type = 'info') {
    const bgColors = {
        'success': '#22c55e',
        'danger': '#ef4444',
        'warning': '#f59e0b',
        'info': '#3b82f6'
    };

    Toastify({
        text: message,
        duration: 3000,
        gravity: "bottom",
        position: "right",
        backgroundColor: bgColors[type] || bgColors.info,
        stopOnFocus: true,
        className: "custom-toast",
        offset: {
            x: 20,
            y: 20
        }
    }).showToast();
}

// Settings form toggle functionality
function handleFormToggle(formId) {
    const allForms = document.querySelectorAll('.settings-form');
    const targetForm = document.getElementById(formId);

    // Hide all forms first
    allForms.forEach(form => {
        form.classList.add('hidden');
    });

    // Show target form if it exists
    if (targetForm) {
        targetForm.classList.toggle('hidden');

        // Clear form inputs when hiding
        if (targetForm.classList.contains('hidden')) {
            targetForm.reset();
        }
    }
}

// Search functionality
function initializeSearch() {
    const searchForm = document.getElementById('search-form');
    const searchContainer = document.querySelector('.search-container');
    const navSearch = document.getElementById('nav-search');
    const patientDetails = document.getElementById('patient-details');

    function moveSearchToNav() {
        if (searchContainer && navSearch) {
            searchContainer.style.opacity = '0';
            setTimeout(() => {
                searchContainer.style.display = 'none';
                navSearch.innerHTML = searchContainer.innerHTML;
                navSearch.classList.add('active');

                // Reinitialize search form event listener in navbar
                const navSearchForm = navSearch.querySelector('#search-form');
                if (navSearchForm) {
                    navSearchForm.addEventListener('submit', handleSearchSubmit);
                }
            }, 300);
        }
    }

    function restoreSearchToCenter() {
        if (searchContainer && navSearch) {
            navSearch.classList.remove('active');
            navSearch.innerHTML = '';
            searchContainer.style.display = 'flex';
            setTimeout(() => {
                searchContainer.style.opacity = '1';
            }, 10);
        }
    }

    // Enhanced search form submission handler
    async function handleSearchSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const patientId = form.querySelector('#patient_id').value;

        try {
            const response = await fetchWithCSRF(`${form.action}?patient_id=${patientId}`, {
                method: 'GET',
                headers: {
                    'Accept': 'text/html'
                }
            });

            if (response.ok) {
                const html = await response.text();
                if (patientDetails) {
                    patientDetails.innerHTML = html;
                    moveSearchToNav();
                    // Update URL without reloading
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

    // Initial state check
    if (patientDetails && patientDetails.children.length > 0) {
        moveSearchToNav();
    } else {
        restoreSearchToCenter();
    }

    // Search form submission
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearchSubmit);
    }

    // Browser back button handling
    window.addEventListener('popstate', function () {
        if (!patientDetails || patientDetails.children.length === 0) {
            restoreSearchToCenter();
        }
    });
}

// Form submission handler with CSRF
async function handleFormSubmit(e) {
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

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Flash messages initialization
    const flashContainer = document.getElementById('flash-messages');
    if (flashContainer) {
        try {
            const messages = JSON.parse(flashContainer.dataset.messages || '[]');
            messages.forEach(function (item) {
                const [category, message] = item;
                showToast(message, category);
            });
        } catch (e) {
            console.error('Error parsing flash messages:', e);
        }
    }

    // Initialize search functionality
    initializeSearch();

    // Add CSRF protection to all forms
    document.querySelectorAll('form:not([data-no-csrf])').forEach(form => {
        if (!form.querySelector('input[name="csrf_token"]')) {
            const csrfToken = getCSRFToken();
            if (csrfToken) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
            }
        }
    });

    // Enhanced form submission handling
    document.querySelectorAll('form[data-ajax="true"]').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
});

// Export functions for use in other scripts
window.showToast = showToast;
window.handleFormToggle = handleFormToggle;
window.fetchWithCSRF = fetchWithCSRF;