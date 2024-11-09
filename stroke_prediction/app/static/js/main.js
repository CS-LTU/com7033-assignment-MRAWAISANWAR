// main.js

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

// Initialize flash messages
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

    // Search functionality
    initializeSearch();
});

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
                    navSearchForm.addEventListener('submit', () => moveSearchToNav());
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

    // Initial state check
    if (patientDetails && patientDetails.children.length > 0) {
        moveSearchToNav();
    } else {
        restoreSearchToCenter();
    }

    // Search form submission
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            moveSearchToNav();
        });
    }

    // Browser back button handling
    window.addEventListener('popstate', function () {
        if (!patientDetails || patientDetails.children.length === 0) {
            restoreSearchToCenter();
        }
    });
}