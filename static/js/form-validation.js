// Global Form Validation System
class FormValidator {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        this.errors = {};
        this.init();
    }

    init() {
        if (!this.form) return;
        
        // Add required asterisks to labels
        this.addRequiredAsterisks();
        
        // Add real-time validation
        this.addRealTimeValidation();
        
        // Add form submission validation
        this.form.addEventListener('submit', (e) => this.validateForm(e));
    }

    addRequiredAsterisks() {
        const requiredFields = this.form.querySelectorAll('input[required], select[required], textarea[required]');
        
        requiredFields.forEach(field => {
            const label = this.form.querySelector(`label[for="${field.id}"]`) || 
                         field.closest('.validation-container')?.querySelector('label') ||
                         field.previousElementSibling;
            
            if (label && label.tagName === 'LABEL') {
                label.classList.add('required');
            }
        });
    }

    addRealTimeValidation() {
        const fields = this.form.querySelectorAll('input, select, textarea');
        
        fields.forEach(field => {
            // Wrap field in validation container if not already wrapped
            if (!field.closest('.validation-container')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'validation-container';
                field.parentNode.insertBefore(wrapper, field);
                wrapper.appendChild(field);
            }

            // Add event listeners
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => this.clearFieldError(field));
        });
    }

    validateField(field) {
        const errors = [];
        const value = field.value.trim();
        const fieldName = field.name || field.id;

        // Required validation
        if (field.hasAttribute('required') && !value) {
            errors.push(`${this.getFieldLabel(field)} is required`);
        }

        // Email validation
        if (field.type === 'email' && value && !this.isValidEmail(value)) {
            errors.push('Please enter a valid email address');
        }

        // Phone validation
        if (field.type === 'tel' && value && !this.isValidPhone(value)) {
            errors.push('Please enter a valid phone number');
        }

        // Number validation
        if (field.type === 'number' && value) {
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            const numValue = parseFloat(value);
            
            if (isNaN(numValue)) {
                errors.push('Please enter a valid number');
            } else {
                if (min && numValue < parseFloat(min)) {
                    errors.push(`Value must be at least ${min}`);
                }
                if (max && numValue > parseFloat(max)) {
                    errors.push(`Value must not exceed ${max}`);
                }
            }
        }

        // Date validation
        if (field.type === 'date' && value) {
            const date = new Date(value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (field.hasAttribute('data-min-date') && field.getAttribute('data-min-date') === 'today') {
                if (date < today) {
                    errors.push('Date cannot be in the past');
                }
            }
        }

        // Custom validation patterns
        const pattern = field.getAttribute('pattern');
        if (pattern && value && !new RegExp(pattern).test(value)) {
            const patternTitle = field.getAttribute('title') || 'Invalid format';
            errors.push(patternTitle);
        }

        // Update field state
        if (errors.length > 0) {
            this.showFieldError(field, errors[0]);
            this.errors[fieldName] = errors;
        } else {
            this.clearFieldError(field);
            delete this.errors[fieldName];
        }

        return errors.length === 0;
    }

    validateForm(event) {
        // Clear previous validation summary
        this.clearValidationSummary();
        
        // Validate all fields
        const fields = this.form.querySelectorAll('input, select, textarea');
        let isValid = true;
        const allErrors = [];

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
                const fieldErrors = this.errors[field.name || field.id] || [];
                allErrors.push(...fieldErrors);
            }
        });

        // Custom validations
        const customErrors = this.runCustomValidations();
        if (customErrors.length > 0) {
            isValid = false;
            allErrors.push(...customErrors);
        }

        if (!isValid) {
            event.preventDefault();
            this.showValidationSummary(allErrors);
            this.scrollToFirstError();
            return false;
        }

        // Show loading state
        this.showLoadingState();
        return true;
    }

    runCustomValidations() {
        const errors = [];

        // Check if room is selected for reservation forms
        if (this.form.id === 'reservationForm') {
            const roomSelected = this.form.querySelector('input[name="room"]:checked');
            if (!roomSelected) {
                errors.push('Please select a room');
            }

            // Check date range
            const checkIn = this.form.querySelector('input[name="check_in"]').value;
            const checkOut = this.form.querySelector('input[name="check_out"]').value;
            
            if (checkIn && checkOut && new Date(checkIn) >= new Date(checkOut)) {
                errors.push('Check-out date must be after check-in date');
            }
        }

        // Guest form validation
        if (this.form.querySelector('input[name="guest_first_name"]')) {
            const guestSelect = this.form.querySelector('select[name="guest"]');
            const isNewGuest = guestSelect && guestSelect.value === 'new';
            
            if (isNewGuest) {
                const firstName = this.form.querySelector('input[name="guest_first_name"]').value.trim();
                const lastName = this.form.querySelector('input[name="guest_last_name"]').value.trim();
                const email = this.form.querySelector('input[name="guest_email"]').value.trim();
                
                if (!firstName) errors.push('Guest first name is required');
                if (!lastName) errors.push('Guest last name is required');
                if (!email) errors.push('Guest email is required');
            }
        }

        return errors;
    }

    showFieldError(field, message) {
        field.classList.add('form-error');
        field.classList.remove('form-success');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i>${message}`;
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('form-error');
        field.classList.add('form-success');
        
        const errorMessage = field.parentNode.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }

    showValidationSummary(errors) {
        let summaryDiv = document.querySelector('.validation-summary');
        
        if (!summaryDiv) {
            summaryDiv = document.createElement('div');
            summaryDiv.className = 'validation-summary';
            this.form.insertBefore(summaryDiv, this.form.firstChild);
        }

        const uniqueErrors = [...new Set(errors)];
        
        summaryDiv.innerHTML = `
            <h4><i class="fas fa-exclamation-triangle"></i> Please correct the following errors:</h4>
            <ul>
                ${uniqueErrors.map(error => `<li>${error}</li>`).join('')}
            </ul>
        `;
        
        summaryDiv.classList.add('show');
    }

    clearValidationSummary() {
        const summaryDiv = document.querySelector('.validation-summary');
        if (summaryDiv) {
            summaryDiv.classList.remove('show');
        }
    }

    scrollToFirstError() {
        const firstError = this.form.querySelector('.form-error');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }

    showLoadingState() {
        this.form.classList.add('form-submitting');
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.setAttribute('data-original-text', submitBtn.textContent);
            submitBtn.textContent = 'Processing...';
        }
    }

    getFieldLabel(field) {
        const label = this.form.querySelector(`label[for="${field.id}"]`) || 
                     field.closest('.validation-container')?.querySelector('label') ||
                     field.previousElementSibling;
        
        if (label && label.tagName === 'LABEL') {
            return label.textContent.replace('*', '').trim();
        }
        
        return field.getAttribute('placeholder') || field.name || 'Field';
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidPhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
    }
}

// Auto-initialize validation for common forms
document.addEventListener('DOMContentLoaded', function() {
    // Initialize validation for all forms with validation class
    const forms = document.querySelectorAll('form.validate, #reservationForm, #guestForm, #hotelForm');
    
    forms.forEach(form => {
        new FormValidator(`#${form.id}`);
    });
    
    // Add validation class to forms that don't have it
    const allForms = document.querySelectorAll('form');
    allForms.forEach(form => {
        if (!form.classList.contains('validate')) {
            form.classList.add('validate');
            new FormValidator(`#${form.id}`);
        }
    });
});

// Export for manual initialization
window.FormValidator = FormValidator;