/**
 * Main Application Logic for User Signup Form
 */

const App = {
    // API endpoint
    API_URL: 'http://127.0.0.1:8000/user/registration',

    /**
     * Initialize the application
     */
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    },

    /**
     * Setup all event listeners and initialize components
     */
    setup() {
        // Initialize form handlers for dynamic entries
        FormHandlers.init();

        // Setup validation
        Validation.setupRealtimeValidation();

        // Setup form submission
        this.setupFormSubmission();

        // Setup reset button
        this.setupResetButton();

        // Setup modal close buttons
        this.setupModals();
    },

    /**
     * Setup form submission handler
     */
    setupFormSubmission() {
        const form = document.getElementById('userSignupForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Validate form
            if (!Validation.validateForm()) {
                return;
            }

            // Collect form data
            const formData = this.collectFormData();

            // Submit to API
            await this.submitForm(formData);
        });
    },

    /**
     * Setup reset button handler
     */
    setupResetButton() {
        const resetBtn = document.getElementById('resetFormBtn');
        if (!resetBtn) return;

        resetBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to reset the form? All data will be lost.')) {
                this.resetForm();
            }
        });
    },

    /**
     * Setup modal close buttons
     */
    setupModals() {
        const closeSuccessModal = document.getElementById('closeSuccessModal');
        const closeErrorModal = document.getElementById('closeErrorModal');
        const successModal = document.getElementById('successModal');
        const errorModal = document.getElementById('errorModal');

        if (closeSuccessModal) {
            closeSuccessModal.addEventListener('click', () => {
                successModal.style.display = 'none';
            });
        }

        if (closeErrorModal) {
            closeErrorModal.addEventListener('click', () => {
                errorModal.style.display = 'none';
            });
        }

        // Close modals on background click
        [successModal, errorModal].forEach(modal => {
            if (modal) {
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        modal.style.display = 'none';
                    }
                });
            }
        });
    },

    /**
     * Collect all form data into JSON structure
     * @returns {Object}
     */
    collectFormData() {
        return {
            personalInfo: this.collectPersonalInfo(),
            education: this.collectEntries('education'),
            workExperience: this.collectEntries('workExperience'),
            projects: this.collectProjects(),
            skills: this.collectSkills(),
            certifications: this.collectEntries('certifications'),
            volunteer: this.collectEntries('volunteer'),
            leadership: this.collectEntries('leadership')
        };
    },

    /**
     * Collect personal information
     * @returns {Object}
     */
    collectPersonalInfo() {
        return {
            name: this.getValue('name'),
            email: this.getValue('email'),
            portfolioWebsite: this.getValue('portfolioWebsite') || null,
            githubUrl: this.getValue('githubUrl') || null,
            linkedinUrl: this.getValue('linkedinUrl') || null
        };
    },

    /**
     * Collect entries from a multi-entry section
     * @param {string} sectionType
     * @returns {Array}
     */
    collectEntries(sectionType) {
        const container = document.getElementById(`${sectionType}Entries`);
        if (!container) return [];

        const entries = container.querySelectorAll('.entry-card');
        const data = [];

        entries.forEach(entry => {
            const entryData = this.collectEntryData(entry, sectionType);
            if (this.hasValidData(entryData)) {
                data.push(entryData);
            }
        });

        return data;
    },

    /**
     * Collect data from a single entry card
     * @param {HTMLElement} entry
     * @param {string} sectionType
     * @returns {Object}
     */
    collectEntryData(entry, sectionType) {
        const inputs = entry.querySelectorAll('input, select, textarea');
        const data = {};

        inputs.forEach(input => {
            const name = input.name;
            if (!name) return;

            // Extract field name from input name pattern: sectionType[index][fieldName]
            const match = name.match(/\[(\w+)\]$/);
            if (match) {
                const fieldName = match[1];

                if (input.type === 'checkbox') {
                    data[fieldName] = input.checked;
                } else {
                    const value = input.value.trim();
                    data[fieldName] = value || null;
                }
            }
        });

        return data;
    },

    /**
     * Collect projects with tech stack as array
     * @returns {Array}
     */
    collectProjects() {
        const container = document.getElementById('projectsEntries');
        if (!container) return [];

        const entries = container.querySelectorAll('.entry-card');
        const data = [];

        entries.forEach(entry => {
            const entryData = this.collectEntryData(entry, 'projects');

            // Convert techStack string to array
            if (entryData.techStack) {
                entryData.techStack = entryData.techStack
                    .split(',')
                    .map(tech => tech.trim())
                    .filter(tech => tech);
            } else {
                entryData.techStack = [];
            }

            if (this.hasValidData(entryData)) {
                data.push(entryData);
            }
        });

        return data;
    },

    /**
     * Collect skills from all categories
     * @returns {Object}
     */
    collectSkills() {
        const categories = [
            'programmingLanguages',
            'frameworks',
            'databases',
            'toolsAndTechnologies',
            'cloud',
            'ai',
            'otherSkills'
        ];

        const skills = {};

        categories.forEach(category => {
            const input = document.getElementById(category);
            if (input && input.value.trim()) {
                const key = category === 'otherSkills' ? 'other' : category;
                skills[key] = input.value
                    .split(',')
                    .map(skill => skill.trim())
                    .filter(skill => skill);
            } else {
                const key = category === 'otherSkills' ? 'other' : category;
                skills[key] = [];
            }
        });

        return skills;
    },

    /**
     * Check if entry has at least some valid data
     * @param {Object} data
     * @returns {boolean}
     */
    hasValidData(data) {
        return Object.values(data).some(value => {
            if (value === null || value === undefined) return false;
            if (typeof value === 'boolean') return false; // Don't count checkboxes alone
            if (typeof value === 'string') return value.trim() !== '';
            if (Array.isArray(value)) return value.length > 0;
            return true;
        });
    },

    /**
     * Get value from an input by ID
     * @param {string} id
     * @returns {string}
     */
    getValue(id) {
        const element = document.getElementById(id);
        return element ? element.value.trim() : '';
    },

    /**
     * Submit form data to API
     * @param {Object} formData
     */
    async submitForm(formData) {
        const submitBtn = document.getElementById('submitBtn');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoader = submitBtn.querySelector('.btn-loader');

        try {
            // Show loading state
            submitBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'inline-flex';

            // Make API request
            const response = await fetch(this.API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                this.showSuccessModal();
                this.resetForm();
            } else {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.detail || errorData.message || 'Registration failed. Please try again.';
                this.showErrorModal(errorMessage);
            }
        } catch (error) {
            console.error('Submission error:', error);
            this.showErrorModal('Network error. Please check your connection and try again.');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
        }
    },

    /**
     * Show success modal
     */
    showSuccessModal() {
        const modal = document.getElementById('successModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    },

    /**
     * Show error modal with message
     * @param {string} message
     */
    showErrorModal(message) {
        const modal = document.getElementById('errorModal');
        const errorMessage = document.getElementById('errorMessage');

        if (errorMessage) {
            errorMessage.textContent = message;
        }

        if (modal) {
            modal.style.display = 'flex';
        }
    },

    /**
     * Reset the form to initial state
     */
    resetForm() {
        const form = document.getElementById('userSignupForm');
        if (form) {
            form.reset();
        }

        // Clear all entries and re-add initial ones
        const sections = ['education', 'workExperience', 'projects', 'certifications', 'volunteer', 'leadership'];

        sections.forEach(section => {
            const container = document.getElementById(`${section}Entries`);
            if (container) {
                container.innerHTML = '';
            }
            FormHandlers.entryCounts[section] = 0;
        });

        // Add initial entries for main sections
        FormHandlers.addEntry('education');
        FormHandlers.addEntry('workExperience');
        FormHandlers.addEntry('projects');

        // Clear all error states
        document.querySelectorAll('.error').forEach(el => {
            el.classList.remove('error');
        });
        document.querySelectorAll('.error-message').forEach(el => {
            el.textContent = '';
        });

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};

// Initialize the application
App.init();
