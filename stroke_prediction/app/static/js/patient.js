// Patient form and prediction handling
class PatientManager {
    constructor() {
        this.predictionModal = document.getElementById('predictionModal');
    }

    async handlePrediction(event) {
        event.preventDefault();
        const form = event.target.closest('form');
        const formData = new FormData(form);

        try {
            const response = await fetchWithCSRF('/patient/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.showPredictionResults(data);
            } else {
                showToast(data.message || 'Error predicting risk', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Error processing request', 'danger');
        }
    }

    showPredictionResults(data) {
        const riskValue = document.getElementById('riskValue');
        const riskFill = document.getElementById('riskFill');
        const riskMessage = document.getElementById('riskMessage');

        // Update risk value and fill
        riskValue.textContent = `${data.risk}%`;
        riskFill.style.width = `${Math.min(data.risk, 100)}%`;

        // Update risk class and message
        riskValue.className = 'risk-value';
        riskValue.classList.add(this.getRiskClass(data.risk));
        riskMessage.textContent = this.getRiskMessage(data.risk_level);

        // Show modal
        this.showModal();
    }

    getRiskClass(riskPercentage) {
        if (riskPercentage >= 60) return 'high-risk';
        if (riskPercentage >= 30) return 'medium-risk';
        return 'low-risk';
    }

    getRiskMessage(riskLevel) {
        const messages = {
            'Critical': 'Critical risk of stroke detected. Immediate medical attention is recommended.',
            'Very High': 'Very high risk of stroke detected. Urgent medical consultation recommended.',
            'High': 'High risk of stroke detected. Prompt medical consultation recommended.',
            'Moderate': 'Moderate risk of stroke detected. Regular medical check-ups recommended.',
            'Low': 'Low risk of stroke detected. Maintain healthy lifestyle habits.'
        };
        return messages[riskLevel] || messages['Low'];
    }

    showModal() {
        this.predictionModal.classList.add('show');
    }

    closeModal() {
        this.predictionModal.classList.remove('show');
        // Redirect to home after successful prediction and save
        window.location.href = '/';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const patientManager = new PatientManager();

    // Attach event listeners
    const predictButton = document.querySelector('[data-action="predict"]');
    if (predictButton) {
        predictButton.addEventListener('click', (e) => patientManager.handlePrediction(e));
    }

    const closeModalButton = document.querySelector('[data-action="close-modal"]');
    if (closeModalButton) {
        closeModalButton.addEventListener('click', () => patientManager.closeModal());
    }
});

// Export for global use if needed
window.PatientManager = PatientManager;