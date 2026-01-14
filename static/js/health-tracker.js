/**
 * Health Tracker JavaScript
 * Handles BP, Sugar, and Medication CRUD operations
 */

// Get CSRF token from the page
function getCSRFToken() {
    const tokenInput = document.querySelector('input[name="csrf_token"]');
    return tokenInput ? tokenInput.value : '';
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('healthToast');
    const toastBody = document.getElementById('toastMessage');
    const toastIcon = toast.querySelector('.toast-header i');

    toastBody.textContent = message;

    // Update icon based on type
    toastIcon.className = type === 'success'
        ? 'fas fa-check-circle text-success me-2'
        : 'fas fa-exclamation-circle text-danger me-2';

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Generic API request helper
async function healthAPI(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        credentials: 'same-origin',  // Include session cookie
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`/api/health/${endpoint}`, options);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: error.message };
    }
}

// ============= BP Functions =============

async function saveBP() {
    const systolic = document.getElementById('bpSystolic').value;
    const diastolic = document.getElementById('bpDiastolic').value;
    const pulse = document.getElementById('bpPulse').value;
    const timestamp = document.getElementById('bpTimestamp').value;
    const notes = document.getElementById('bpNotes').value;

    if (!systolic || !diastolic) {
        showToast('Please enter systolic and diastolic values', 'error');
        return;
    }

    const result = await healthAPI('bp', 'POST', {
        systolic: parseInt(systolic),
        diastolic: parseInt(diastolic),
        pulse: pulse ? parseInt(pulse) : null,
        timestamp: timestamp ? new Date(timestamp).toISOString() : null,
        notes
    });

    if (result.success) {
        showToast('Blood pressure reading saved!');
        // Close modal and reload page
        bootstrap.Modal.getInstance(document.getElementById('addBPModal')).hide();
        setTimeout(() => location.reload(), 500);
    } else {
        showToast(result.error || 'Failed to save reading', 'error');
    }
}

async function deleteBP(id) {
    if (!confirm('Delete this BP reading?')) return;

    const result = await healthAPI(`bp/${id}`, 'DELETE');

    if (result.success) {
        showToast('BP reading deleted');
        setTimeout(() => location.reload(), 500);
    } else {
        showToast(result.error || 'Failed to delete', 'error');
    }
}

// ============= Sugar Functions =============

async function saveSugar() {
    const value = document.getElementById('sugarValue').value;
    const timestamp = document.getElementById('sugarTimestamp').value;
    const notes = document.getElementById('sugarNotes').value;

    if (!value) {
        showToast('Please enter a sugar reading', 'error');
        return;
    }

    const result = await healthAPI('sugar', 'POST', {
        value: parseInt(value),
        timestamp: timestamp ? new Date(timestamp).toISOString() : null,
        notes
    });

    if (result.success) {
        showToast('Blood sugar reading saved!');
        bootstrap.Modal.getInstance(document.getElementById('addSugarModal')).hide();
        setTimeout(() => location.reload(), 500);
    } else {
        showToast(result.error || 'Failed to save reading', 'error');
    }
}

async function deleteSugar(id) {
    if (!confirm('Delete this sugar reading?')) return;

    const result = await healthAPI(`sugar/${id}`, 'DELETE');

    if (result.success) {
        showToast('Sugar reading deleted');
        setTimeout(() => location.reload(), 500);
    } else {
        showToast(result.error || 'Failed to delete', 'error');
    }
}

// ============= Medication Functions =============

async function saveMedication() {
    const name = document.getElementById('medName').value;
    const dosage = document.getElementById('medDosage').value;
    const frequency = document.getElementById('medFrequency').value;
    const instructions = document.getElementById('medInstructions').value;

    if (!name || !dosage || !frequency) {
        showToast('Please fill in all required fields', 'error');
        return;
    }

    const result = await healthAPI('medications', 'POST', {
        name,
        dosage,
        frequency,
        instructions
    });

    if (result.success) {
        showToast('Medication added!');
        bootstrap.Modal.getInstance(document.getElementById('addMedModal')).hide();
        setTimeout(() => location.reload(), 500);
    } else {
        showToast(result.error || 'Failed to add medication', 'error');
    }
}

async function deleteMedication(id) {
    if (!confirm('Stop tracking this medication?')) return;

    const result = await healthAPI(`medications/${id}`, 'DELETE');

    if (result.success) {
        showToast('Medication removed');
        setTimeout(() => location.reload(), 500);
    } else {
        showToast(result.error || 'Failed to remove medication', 'error');
    }
}

// ============= BP Status Helper =============

function getBPStatus(systolic, diastolic) {
    if (systolic < 120 && diastolic < 80) {
        return { label: 'Normal', class: 'success' };
    } else if (systolic < 130 && diastolic < 80) {
        return { label: 'Elevated', class: 'warning' };
    } else if (systolic < 140 || diastolic < 90) {
        return { label: 'High Stage 1', class: 'warning' };
    }
    return { label: 'High Stage 2', class: 'danger' };
}

// ============= Sugar Status Helper =============

function getSugarStatus(value, isFasting = true) {
    if (isFasting) {
        if (value < 100) return { label: 'Normal', class: 'success' };
        if (value < 126) return { label: 'Prediabetes', class: 'warning' };
        return { label: 'Diabetes Range', class: 'danger' };
    } else {
        if (value < 140) return { label: 'Normal', class: 'success' };
        if (value < 200) return { label: 'Prediabetes', class: 'warning' };
        return { label: 'Diabetes Range', class: 'danger' };
    }
}

// Network features disabled - personal health tracking only
