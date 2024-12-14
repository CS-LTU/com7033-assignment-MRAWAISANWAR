function deletePatient(patientId, row = null) {
    if (confirm("Patient ID: SW" + patientId + "\nAre you sure you want to delete this patient record?")) {
        fetch(`/patient/delete/${patientId}`, {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
                "Content-Type": "application/json",
            },
            credentials: "same-origin",
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    if (row) {
                        // Delete from list view
                        showToast("Patient record deleted successfully", "success");
                        row.remove();
                        totalPatients = totalPatients.filter(p => p.patient_id !== patientId);
                        totalPatientsCount();
                    } else {
                        // Delete from details view
                        window.location.href = data.redirect;
                        // Toast will show after redirect
                    }
                } else {
                    showToast(data.message || "Error deleting record", "danger");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                showToast("Error deleting patient record", "danger");
            });
    }
}