// Global variables
let jobs = [];

// DOM elements
const addJobForm = document.getElementById('addJobForm');
const jobsList = document.getElementById('jobsList');
const jobModal = document.getElementById('jobModal');
const jobDetails = document.getElementById('jobDetails');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadJobs();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Add job form submission
    addJobForm.addEventListener('submit', handleAddJob);
    
    // Modal close button
    const closeBtn = document.querySelector('.close');
    closeBtn.addEventListener('click', closeModal);
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === jobModal) {
            closeModal();
        }
    });
}

// Load all jobs from the API
async function loadJobs() {
    try {
        const response = await fetch('/api/jobs');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        jobs = await response.json();
        displayJobs();
    } catch (error) {
        console.error('Error loading jobs:', error);
        showError('Failed to load jobs. Please try again.');
    }
}

// Display jobs in the UI
function displayJobs() {
    if (jobs.length === 0) {
        jobsList.innerHTML = '<div class="no-jobs">No cron jobs found. Create your first job above!</div>';
        return;
    }

    jobsList.innerHTML = jobs.map(job => `
        <div class="job-card">
            <div class="job-header">
                <div class="job-name">${escapeHtml(job.name)}</div>
                <div class="job-status ${job.enabled ? 'enabled' : 'disabled'}">
                    ${job.enabled ? 'Enabled' : 'Disabled'}
                </div>
            </div>
            
            <div class="job-details">
                <div class="job-detail">
                    <span class="job-detail-label">Schedule:</span>
                    <span class="job-detail-value">${escapeHtml(job.expression)}</span>
                </div>
                ${job.description ? `
                <div class="job-detail">
                    <span class="job-detail-label">Description:</span>
                    <span class="job-detail-value">${escapeHtml(job.description)}</span>
                </div>
                ` : ''}
                <div class="job-detail">
                    <span class="job-detail-label">Command:</span>
                    <span class="job-detail-value">${escapeHtml(job.command.substring(0, 50))}${job.command.length > 50 ? '...' : ''}</span>
                </div>
            </div>
            
            <div class="job-actions">
                <button class="btn btn-secondary" onclick="viewJobDetails(${job.id})">View Details</button>
                ${job.enabled ? 
                    `<button class="btn btn-secondary" onclick="disableJob(${job.id})">Disable</button>` :
                    `<button class="btn btn-success" onclick="enableJob(${job.id})">Enable</button>`
                }
                <button class="btn btn-danger" onclick="deleteJob(${job.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

// Handle add job form submission
async function handleAddJob(event) {
    event.preventDefault();
    
    const formData = new FormData(addJobForm);
    const jobData = {
        name: formData.get('name'),
        expression: formData.get('expression'),
        command: formData.get('command'),
        description: formData.get('description') || null
    };
    
    try {
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jobData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create job');
        }
        
        const newJob = await response.json();
        showSuccess('Job created successfully!');
        addJobForm.reset();
        await loadJobs(); // Reload jobs list
    } catch (error) {
        console.error('Error creating job:', error);
        showError(error.message);
    }
}

// View job details in modal
async function viewJobDetails(jobId) {
    try {
        const response = await fetch(`/api/jobs/${jobId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch job details');
        }
        
        const job = await response.json();
        
        jobDetails.innerHTML = `
            <div class="job-detail">
                <span class="job-detail-label">Name:</span>
                <span class="job-detail-value">${escapeHtml(job.name)}</span>
            </div>
            <div class="job-detail">
                <span class="job-detail-label">Schedule:</span>
                <span class="job-detail-value">${escapeHtml(job.expression)}</span>
            </div>
            ${job.description ? `
            <div class="job-detail">
                <span class="job-detail-label">Description:</span>
                <span class="job-detail-value">${escapeHtml(job.description)}</span>
            </div>
            ` : ''}
            <div class="job-detail">
                <span class="job-detail-label">Status:</span>
                <span class="job-detail-value ${job.enabled ? 'enabled' : 'disabled'}">${job.enabled ? 'Enabled' : 'Disabled'}</span>
            </div>
            <div class="job-detail">
                <span class="job-detail-label">Created:</span>
                <span class="job-detail-value">${new Date(job.created_at).toLocaleString()}</span>
            </div>
            <div class="job-detail">
                <span class="job-detail-label">Updated:</span>
                <span class="job-detail-value">${new Date(job.updated_at).toLocaleString()}</span>
            </div>
            <div class="job-detail">
                <span class="job-detail-label">Command:</span>
                <pre class="job-detail-value" style="white-space: pre-wrap; max-height: 200px; overflow-y: auto;">${escapeHtml(job.command)}</pre>
            </div>
        `;
        
        jobModal.style.display = 'block';
    } catch (error) {
        console.error('Error fetching job details:', error);
        showError('Failed to load job details');
    }
}

// Enable a job
async function enableJob(jobId) {
    try {
        const response = await fetch(`/api/jobs/${jobId}/enable`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to enable job');
        }
        
        showSuccess('Job enabled successfully!');
        await loadJobs(); // Reload jobs list
    } catch (error) {
        console.error('Error enabling job:', error);
        showError('Failed to enable job');
    }
}

// Disable a job
async function disableJob(jobId) {
    try {
        const response = await fetch(`/api/jobs/${jobId}/disable`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to disable job');
        }
        
        showSuccess('Job disabled successfully!');
        await loadJobs(); // Reload jobs list
    } catch (error) {
        console.error('Error disabling job:', error);
        showError('Failed to disable job');
    }
}

// Delete a job
async function deleteJob(jobId) {
    if (!confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/jobs/${jobId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete job');
        }
        
        showSuccess('Job deleted successfully!');
        await loadJobs(); // Reload jobs list
    } catch (error) {
        console.error('Error deleting job:', error);
        showError('Failed to delete job');
    }
}

// Close modal
function closeModal() {
    jobModal.style.display = 'none';
}

// Show success message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(successDiv, container.firstChild);
    
    setTimeout(() => {
        successDiv.remove();
    }, 5000);
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(errorDiv, container.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
} 