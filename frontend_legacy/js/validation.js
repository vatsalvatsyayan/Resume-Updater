/**
 * Validation utilities for the User Signup Form
 */

const Validation = {
    /**
     * Validate email format
     * @param {string} email
     * @returns {boolean}
     */
    validateEmail(email) {
        if (!email) return true; // Empty is handled by required validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email.trim());
    },

    /**
     * Validate URL format
     * @param {string} url
     * @returns {boolean}
     */
    validateURL(url) {
        if (!url) return true; // Empty is handled by required validation
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },

    /**
     * Validate required field
     * @param {string} value
     * @returns {boolean}
     */
    validateRequired(value) {
        return value !== null && value !== undefined && value.toString().trim() !== '';
    },

    /**
     * Validate date format
     * @param {string} date
     * @returns {boolean}
     */
    validateDate(date) {
        if (!date) return true; // Empty is handled by required validation
        const dateObj = new Date(date);
        return !isNaN(dateObj.getTime());
    },

    /**
     * Validate GPA (0-4 scale)
     * @param {string|number} gpa
     * @returns {boolean}
     */
    validateGPA(gpa) {
        if (!gpa && gpa !== 0) return true; // Empty is optional
        const gpaNum = parseFloat(gpa);
        return !isNaN(gpaNum) && gpaNum >= 0 && gpaNum <= 4;
    },

    /**
     * Show error message for a field
     * @param {HTMLElement} field
     * @param {string} message
     */
    showError(field, message) {
        field.classList.add('error');
        const errorSpan = field.parentElement.querySelector('.error-message');
        if (errorSpan) {
            errorSpan.textContent = message;
        }
    },

    /**
     * Clear error message for a field
     * @param {HTMLElement} field
     */
    clearError(field) {
        field.classList.remove('error');
        const errorSpan = field.parentElement.querySelector('.error-message');
        if (errorSpan) {
            errorSpan.textContent = '';
        }
    },

    /**
     * Validate a single field based on its type and requirements
     * @param {HTMLElement} field
     * @returns {boolean}
     */
    validateField(field) {
        const value = field.value;
        const isRequired = field.hasAttribute('required');
        const type = field.type;

        // Clear previous error
        this.clearError(field);

        // Required validation
        if (isRequired && !this.validateRequired(value)) {
            this.showError(field, 'This field is required');
            return false;
        }

        // Type-specific validation
        if (value) {
            switch (type) {
                case 'email':
                    if (!this.validateEmail(value)) {
                        this.showError(field, 'Please enter a valid email address');
                        return false;
                    }
                    break;
                case 'url':
                    if (!this.validateURL(value)) {
                        this.showError(field, 'Please enter a valid URL');
                        return false;
                    }
                    break;
                case 'date':
                    if (!this.validateDate(value)) {
                        this.showError(field, 'Please enter a valid date');
                        return false;
                    }
                    break;
                case 'number':
                    if (field.name && field.name.toLowerCase().includes('gpa')) {
                        if (!this.validateGPA(value)) {
                            this.showError(field, 'GPA must be between 0 and 4');
                            return false;
                        }
                    }
                    break;
            }
        }

        return true;
    },

    /**
     * Validate all fields within a section
     * @param {string} sectionId
     * @returns {boolean}
     */
    validateSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (!section) return true;

        const fields = section.querySelectorAll('input, select, textarea');
        let isValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    },

    /**
     * Validate the entire form
     * @returns {boolean}
     */
    validateForm() {
        const form = document.getElementById('userSignupForm');
        if (!form) return false;

        const sections = [
            'personalInfoSection',
            'educationSection',
            'workExperienceSection',
            'projectsSection',
            'skillsSection',
            'certificationsSection',
            'volunteerSection',
            'leadershipSection'
        ];

        let isValid = true;
        let firstInvalidField = null;

        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                const fields = section.querySelectorAll('input, select, textarea');
                fields.forEach(field => {
                    if (!this.validateField(field)) {
                        isValid = false;
                        if (!firstInvalidField) {
                            firstInvalidField = field;
                        }
                    }
                });
            }
        });

        // Scroll to first invalid field
        if (firstInvalidField) {
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstInvalidField.focus();
        }

        return isValid;
    },

    /**
     * Setup real-time validation on blur
     */
    setupRealtimeValidation() {
        const form = document.getElementById('userSignupForm');
        if (!form) return;

        form.addEventListener('focusout', (e) => {
            if (e.target.matches('input, select, textarea')) {
                this.validateField(e.target);
            }
        });

        // Clear error on input
        form.addEventListener('input', (e) => {
            if (e.target.matches('input, select, textarea')) {
                if (e.target.classList.contains('error')) {
                    this.clearError(e.target);
                }
            }
        });
    }
};

// Make Validation available globally
window.Validation = Validation;
