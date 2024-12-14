let page = 1;
let loading = false;
let hasMore = true;
let totalPatients = [];


function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function togglePatientList(btn) {
    const container = document.querySelector('.Patient-List-Container');
    const isHidden = container.classList.contains('hidden');

    if (isHidden) {
        container.classList.remove('hidden');
        showLoader();
        if (totalPatients.length > 0) {
            //await delay(1000);
            clearPatients();
            await renderPatients(totalPatients);
        } else {
            await loadPatients(true);
        }

        // Smooth scroll to the container
        container.scrollIntoView({
            behavior: 'smooth',
            block: 'end'
        });
    } else {
        container.classList.add('hidden');
    }
}

async function loadPatients(reset = false) {
    if (loading || !hasMore) return;

    if (reset) {
        page = 1;
        hasMore = true;
        totalPatients = [];
        clearPatients();
    }

    loading = true;
    showLoader();
    await delay(1000);
    try {
        const response = await fetch(`/patient/list?page=${page}`);
        const data = await response.json();

        if (data.patients.length < 10) {
            hasMore = false;
        }

        totalPatients = [...totalPatients, ...data.patients];
        renderPatients(data.patients);
        page++;
    } catch (error) {
        console.error('Error loading patients:', error);
        showToast(error);
    } finally {
        loading = false;
        hideLoader();
    }
}

async function totalPatientsCount() {
    try {
        const response = await fetch('/patient/count');
        const data = await response.json();
        const totalCount = data.count
        const patientCount = document.getElementById('total-patients');
        if (patientCount) {
            patientCount.textContent = totalCount;
        }
    } catch (error) {
        console.error('Error counting patients:', error);
        return "N/A";
    }
}

async function renderPatients(patients) {
    const tbody = document.getElementById('patient-list-body');
    const template = document.getElementById('patient-row-template');

    totalPatientsCount();

    patients.forEach((patient, index) => {
        const clone = template.content.cloneNode(true);
        const row = clone.querySelector('tr');

        row.querySelector('[data-field="patient_id"]').textContent = "SW" + patient.patient_id;
        row.querySelector('[data-field="name"]').textContent = patient.name;
        row.querySelector('[data-field="age"]').textContent = patient.age;
        row.querySelector('[data-field="gender"]').textContent = patient.gender;

        const riskBadge = row.querySelector('.risk-badge');
        riskBadge.textContent = `${Number(patient.stroke_risk).toFixed(2)}%`;
        riskBadge.style.backgroundColor = getRiskColor(patient.stroke_risk);

        row.querySelector('[data-field="date"]').textContent =
            new Date(patient.record_entry_date).toLocaleDateString();

        const show_details = row;
        const deleteBtn = row.querySelector('.delete-btn');

        // Add row click for details
        show_details.onclick = (e) => {
            // Don't trigger if clicking delete button
            if (!e.target.closest('.delete-btn')) {
                window.location.href = `/patient/search?patient_id=${patient.patient_id}`;
            }
        };

        // Add delete functionality
        deleteBtn.onclick = (e) => {
            e.stopPropagation(); // Stop the row click event from triggering
            deletePatient(patient.patient_id, row);
        };

        tbody.appendChild(row);
    });
}

function getRiskColor(risk) {
    // Convert risk percentage to RGB
    const red = Math.round((risk / 100) * 255);
    const green = Math.round(((100 - risk) / 100) * 255);
    return `rgb(${red}, ${green}, 0)`;
}

function clearPatients() {
    const tbody = document.getElementById('patient-list-body');
    tbody.innerHTML = '';
}

function showLoader() {
    document.querySelector('.windows-loader').classList.remove('hidden');
}

function hideLoader() {
    document.querySelector('.windows-loader').classList.add('hidden');
}

function isScrolledToBottom(element) {
    return Math.abs(element.scrollHeight - element.scrollTop - element.clientHeight) < 1;
}

// Initialize scroll handler after DOM loads
document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.Patient-List-Container');
    if (container) {
        container.addEventListener('scroll', () => {
            if (isScrolledToBottom(container)) {
                loadPatients();
            }
        });
    }
});