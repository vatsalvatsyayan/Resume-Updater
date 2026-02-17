/**
 * Form Handlers for dynamic entry management
 */

const FormHandlers = {
    // Track entry counts for each section
    entryCounts: {
        education: 0,
        workExperience: 0,
        projects: 0,
        certifications: 0,
        volunteer: 0,
        leadership: 0
    },

    /**
     * Initialize form handlers
     */
    init() {
        this.setupAddButtons();
        this.setupRemoveButtonDelegation();
        this.setupPresentCheckboxDelegation();

        // Add initial empty entries for each section
        this.addEntry('education');
        this.addEntry('workExperience');
        this.addEntry('projects');
    },

    /**
     * Setup click handlers for all add buttons
     */
    setupAddButtons() {
        document.querySelectorAll('.btn-add').forEach(button => {
            button.addEventListener('click', () => {
                const section = button.dataset.section;
                this.addEntry(section);
            });
        });
    },

    /**
     * Setup event delegation for remove buttons
     */
    setupRemoveButtonDelegation() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-remove')) {
                const entryCard = e.target.closest('.entry-card');
                if (entryCard) {
                    this.removeEntry(entryCard);
                }
            }
        });
    },

    /**
     * Setup event delegation for "Present" checkboxes
     */
    setupPresentCheckboxDelegation() {
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('present-checkbox')) {
                const endDateInput = e.target.closest('.entry-card').querySelector('.end-date-input');
                if (endDateInput) {
                    endDateInput.disabled = e.target.checked;
                    if (e.target.checked) {
                        endDateInput.value = '';
                    }
                }
            }
        });
    },

    /**
     * Add a new entry to a section
     * @param {string} sectionType
     */
    addEntry(sectionType) {
        const container = document.getElementById(`${sectionType}Entries`);
        if (!container) return;

        this.entryCounts[sectionType]++;
        const index = this.entryCounts[sectionType];
        const html = this.generateEntryHTML(sectionType, index);

        container.insertAdjacentHTML('beforeend', html);
    },

    /**
     * Remove an entry from a section
     * @param {HTMLElement} entryElement
     */
    removeEntry(entryElement) {
        entryElement.style.animation = 'slideOut 0.2s ease-out';
        setTimeout(() => {
            entryElement.remove();
        }, 200);
    },

    /**
     * Generate HTML for a new entry based on section type
     * @param {string} sectionType
     * @param {number} index
     * @returns {string}
     */
    generateEntryHTML(sectionType, index) {
        switch (sectionType) {
            case 'education':
                return this.generateEducationEntry(index);
            case 'workExperience':
                return this.generateWorkExperienceEntry(index);
            case 'projects':
                return this.generateProjectEntry(index);
            case 'certifications':
                return this.generateCertificationEntry(index);
            case 'volunteer':
                return this.generateVolunteerEntry(index);
            case 'leadership':
                return this.generateLeadershipEntry(index);
            default:
                return '';
        }
    },

    /**
     * Generate Education Entry HTML
     */
    generateEducationEntry(index) {
        return `
            <div class="entry-card" data-entry-type="education" data-entry-index="${index}">
                <div class="entry-header">
                    <span class="entry-title">Education #${index}</span>
                    <button type="button" class="btn-remove">Remove</button>
                </div>
                <div class="entry-grid">
                    <div class="form-group">
                        <label>University Name <span class="required">*</span></label>
                        <input type="text" name="education[${index}][universityName]" required placeholder="Stanford University">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Course Name <span class="required">*</span></label>
                        <input type="text" name="education[${index}][courseName]" required placeholder="Bachelor of Science">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Type of Course</label>
                        <select name="education[${index}][courseType]">
                            <option value="">Select Type</option>
                            <option value="Bachelor's">Bachelor's</option>
                            <option value="Master's">Master's</option>
                            <option value="PhD">PhD</option>
                            <option value="Diploma">Diploma</option>
                            <option value="Certificate">Certificate</option>
                            <option value="Associate">Associate</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Major / Field of Study <span class="required">*</span></label>
                        <input type="text" name="education[${index}][major]" required placeholder="Computer Science">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>GPA</label>
                        <input type="number" name="education[${index}][gpa]" step="0.01" min="0" max="4" placeholder="3.8">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Location</label>
                        <input type="text" name="education[${index}][location]" placeholder="Stanford, CA">
                    </div>
                    <div class="form-group">
                        <label>Start Date</label>
                        <input type="date" name="education[${index}][startDate]">
                    </div>
                    <div class="form-group">
                        <label>End Date</label>
                        <input type="date" name="education[${index}][endDate]" class="end-date-input">
                        <div class="checkbox-group">
                            <input type="checkbox" id="eduPresent${index}" name="education[${index}][isPresent]" class="present-checkbox">
                            <label for="eduPresent${index}">Currently Enrolled</label>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Generate Work Experience Entry HTML
     */
    generateWorkExperienceEntry(index) {
        return `
            <div class="entry-card" data-entry-type="workExperience" data-entry-index="${index}">
                <div class="entry-header">
                    <span class="entry-title">Experience #${index}</span>
                    <button type="button" class="btn-remove">Remove</button>
                </div>
                <div class="entry-grid">
                    <div class="form-group">
                        <label>Company Name <span class="required">*</span></label>
                        <input type="text" name="workExperience[${index}][companyName]" required placeholder="Google">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Position / Title <span class="required">*</span></label>
                        <input type="text" name="workExperience[${index}][position]" required placeholder="Software Engineer">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Location</label>
                        <input type="text" name="workExperience[${index}][location]" placeholder="Mountain View, CA">
                    </div>
                    <div class="form-group">
                        <label>Start Date</label>
                        <input type="date" name="workExperience[${index}][startDate]">
                    </div>
                    <div class="form-group">
                        <label>End Date</label>
                        <input type="date" name="workExperience[${index}][endDate]" class="end-date-input">
                        <div class="checkbox-group">
                            <input type="checkbox" id="workPresent${index}" name="workExperience[${index}][isPresent]" class="present-checkbox">
                            <label for="workPresent${index}">Currently Working</label>
                        </div>
                    </div>
                    <div class="form-group full-width">
                        <label>Summary</label>
                        <textarea name="workExperience[${index}][summary]" placeholder="Brief overview of your role and responsibilities..." rows="2"></textarea>
                    </div>
                    <div class="form-group full-width">
                        <label>Description</label>
                        <textarea name="workExperience[${index}][description]" placeholder="Detailed description of your achievements and contributions..." rows="4"></textarea>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Generate Project Entry HTML
     */
    generateProjectEntry(index) {
        return `
            <div class="entry-card" data-entry-type="projects" data-entry-index="${index}">
                <div class="entry-header">
                    <span class="entry-title">Project #${index}</span>
                    <button type="button" class="btn-remove">Remove</button>
                </div>
                <div class="entry-grid">
                    <div class="form-group">
                        <label>Project Name <span class="required">*</span></label>
                        <input type="text" name="projects[${index}][projectName]" required placeholder="E-commerce Platform">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Project Link</label>
                        <input type="url" name="projects[${index}][link]" placeholder="https://github.com/user/project">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group full-width">
                        <label>Tech Stack</label>
                        <input type="text" name="projects[${index}][techStack]" placeholder="React, Node.js, PostgreSQL, Docker">
                        <span class="hint">Separate technologies with commas</span>
                    </div>
                    <div class="form-group full-width">
                        <label>Summary</label>
                        <textarea name="projects[${index}][summary]" placeholder="One-line description of the project..." rows="2"></textarea>
                    </div>
                    <div class="form-group full-width">
                        <label>Description</label>
                        <textarea name="projects[${index}][description]" placeholder="Detailed description of the project, your role, and key features..." rows="4"></textarea>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Generate Certification Entry HTML
     */
    generateCertificationEntry(index) {
        return `
            <div class="entry-card" data-entry-type="certifications" data-entry-index="${index}">
                <div class="entry-header">
                    <span class="entry-title">Certification #${index}</span>
                    <button type="button" class="btn-remove">Remove</button>
                </div>
                <div class="entry-grid">
                    <div class="form-group">
                        <label>Certification Name <span class="required">*</span></label>
                        <input type="text" name="certifications[${index}][name]" required placeholder="AWS Solutions Architect">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Issuing Organization <span class="required">*</span></label>
                        <input type="text" name="certifications[${index}][issuingOrganization]" required placeholder="Amazon Web Services">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Issue Date</label>
                        <input type="date" name="certifications[${index}][issueDate]">
                    </div>
                    <div class="form-group">
                        <label>Expiry Date</label>
                        <input type="date" name="certifications[${index}][expiryDate]" class="end-date-input">
                        <div class="checkbox-group">
                            <input type="checkbox" id="certNoExpiry${index}" name="certifications[${index}][hasNoExpiry]" class="present-checkbox">
                            <label for="certNoExpiry${index}">No Expiry</label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Credential ID</label>
                        <input type="text" name="certifications[${index}][credentialId]" placeholder="ABC123XYZ">
                    </div>
                    <div class="form-group">
                        <label>Credential URL</label>
                        <input type="url" name="certifications[${index}][credentialUrl]" placeholder="https://verify.cert.com/abc123">
                        <span class="error-message"></span>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Generate Volunteer Entry HTML
     */
    generateVolunteerEntry(index) {
        return `
            <div class="entry-card" data-entry-type="volunteer" data-entry-index="${index}">
                <div class="entry-header">
                    <span class="entry-title">Volunteer Experience #${index}</span>
                    <button type="button" class="btn-remove">Remove</button>
                </div>
                <div class="entry-grid">
                    <div class="form-group">
                        <label>Organization Name <span class="required">*</span></label>
                        <input type="text" name="volunteer[${index}][organizationName]" required placeholder="Red Cross">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Role / Position <span class="required">*</span></label>
                        <input type="text" name="volunteer[${index}][role]" required placeholder="Volunteer Coordinator">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Cause / Category</label>
                        <input type="text" name="volunteer[${index}][cause]" placeholder="Humanitarian Aid">
                    </div>
                    <div class="form-group">
                        <label>Location</label>
                        <input type="text" name="volunteer[${index}][location]" placeholder="New York, NY">
                    </div>
                    <div class="form-group">
                        <label>Start Date</label>
                        <input type="date" name="volunteer[${index}][startDate]">
                    </div>
                    <div class="form-group">
                        <label>End Date</label>
                        <input type="date" name="volunteer[${index}][endDate]" class="end-date-input">
                        <div class="checkbox-group">
                            <input type="checkbox" id="volPresent${index}" name="volunteer[${index}][isPresent]" class="present-checkbox">
                            <label for="volPresent${index}">Currently Volunteering</label>
                        </div>
                    </div>
                    <div class="form-group full-width">
                        <label>Description</label>
                        <textarea name="volunteer[${index}][description]" placeholder="Describe your volunteer work and impact..." rows="3"></textarea>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Generate Leadership Entry HTML
     */
    generateLeadershipEntry(index) {
        return `
            <div class="entry-card" data-entry-type="leadership" data-entry-index="${index}">
                <div class="entry-header">
                    <span class="entry-title">Leadership Experience #${index}</span>
                    <button type="button" class="btn-remove">Remove</button>
                </div>
                <div class="entry-grid">
                    <div class="form-group">
                        <label>Title / Position <span class="required">*</span></label>
                        <input type="text" name="leadership[${index}][title]" required placeholder="President">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Organization <span class="required">*</span></label>
                        <input type="text" name="leadership[${index}][organization]" required placeholder="Computer Science Club">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label>Start Date</label>
                        <input type="date" name="leadership[${index}][startDate]">
                    </div>
                    <div class="form-group">
                        <label>End Date</label>
                        <input type="date" name="leadership[${index}][endDate]" class="end-date-input">
                        <div class="checkbox-group">
                            <input type="checkbox" id="leadPresent${index}" name="leadership[${index}][isPresent]" class="present-checkbox">
                            <label for="leadPresent${index}">Current Position</label>
                        </div>
                    </div>
                    <div class="form-group full-width">
                        <label>Description</label>
                        <textarea name="leadership[${index}][description]" placeholder="Describe your leadership responsibilities and achievements..." rows="3"></textarea>
                    </div>
                </div>
            </div>
        `;
    }
};

// Add slideOut animation to CSS dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
    .hint {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }
`;
document.head.appendChild(style);

// Make FormHandlers available globally
window.FormHandlers = FormHandlers;
