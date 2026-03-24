/**
 * StudentLabs Frontend Application
 * Enhanced with complete backend API integration
 */

// ============ GLOBAL STATE ============
let currentUser = null;
let projects = [];
let currentProject = null;
let currentAssignment = null;
let currentPresentation = null;
let researchPapers = [];
let selectedPapers = [];
let jobPolling = {};

// ============ INITIALIZATION ============
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('auth_token');
    
    if (token) {
        try {
            currentUser = await api.getCurrentUser();
            showDashboard();
            loadDashboardData();
        } catch (error) {
            localStorage.removeItem('auth_token');
            showAuthScreen();
        }
    } else {
        showAuthScreen();
    }

    attachEventListeners();
});

// ============ AUTHENTICATION ============
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    if (!email || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    showLoading(true);
    try {
        await api.login(email, password);
        currentUser = await api.getCurrentUser();
        showToast('Login successful!', 'success');
        document.getElementById('login-form').reset();
        showDashboard();
        loadDashboardData();
    } catch (error) {
        showToast(`Login failed: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-password-confirm').value;

    if (!name || !email || !password || !confirmPassword) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }

    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }

    showLoading(true);
    try {
        await api.register(name, email, password);
        showToast('Registration successful! Please login.', 'success');
        document.getElementById('register-form').reset();
        switchAuth('login');
    } catch (error) {
        showToast(`Registration failed: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function switchAuth(screen) {
    document.querySelectorAll('.auth-screen').forEach(s => s.classList.remove('active'));
    document.getElementById(`${screen}-screen`).classList.add('active');
}

async function handleLogout() {
    await api.logout();
    currentUser = null;
    showAuthScreen();
    showToast('Logged out successfully', 'info');
}

// ============ SCREEN SWITCHING ============
function showAuthScreen() {
    document.getElementById('auth-container').classList.remove('hidden');
    document.getElementById('dashboard-container').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('auth-container').classList.add('hidden');
    document.getElementById('dashboard-container').classList.remove('hidden');
    updateUserInfo();
}

function showPage(pageName) {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById(`${pageName}-page`)?.classList.add('active');

    document.querySelectorAll('.nav-item').forEach(item => {
        item.dataset.page === pageName ? item.classList.add('active') : item.classList.remove('active');
    });

    if (pageName === 'projects') loadProjects();
}

function updateUserInfo() {
    if (currentUser) {
        document.getElementById('user-name').textContent = currentUser.name || currentUser.email;
        document.getElementById('user-email').textContent = currentUser.email;
    }
}

// ============ DASHBOARD ============
async function loadDashboardData() {
    try {
        showLoading(true);
        const projectsData = await api.getProjects();
        projects = projectsData;

        document.getElementById('stat-projects').textContent = projects.length;
        document.getElementById('stat-tasks').textContent = projects.filter(p => p.status !== 'completed').length;

        loadRecentProjects();
    } catch (error) {
        showToast(`Error loading dashboard: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function loadRecentProjects() {
    const container = document.getElementById('recent-projects-list');
    
    if (projects.length === 0) {
        container.innerHTML = '<p class="empty-state">No projects yet. Create one to get started!</p>';
        return;
    }

    container.innerHTML = projects.slice(0, 3).map(project => `
        <div class="project-card" onclick="openProjectDetail(${project.id})">
            <h3>${project.title}</h3>
            <p>${project.topic || 'No topic'}</p>
            <div class="project-meta">
                <span>${new Date(project.created_at).toLocaleDateString()}</span>
                <span class="status-badge ${project.status}">${project.status}</span>
            </div>
        </div>
    `).join('');
}

// ============ PROJECTS ============
async function loadProjects() {
    try {
        showLoading(true);
        const projectsData = await api.getProjects();
        projects = projectsData;

        const container = document.getElementById('projects-list');
        
        if (projects.length === 0) {
            container.innerHTML = '<p class="empty-state">No projects yet. Create one to get started!</p>';
            return;
        }

        container.innerHTML = projects.map(project => `
            <div class="project-card" onclick="openProjectDetail(${project.id})">
                <div class="card-header">
                    <h3>${project.title}</h3>
                    <button class="btn-icon" onclick="deleteProject(${project.id}, event)" title="Delete">🗑️</button>
                </div>
                <p>${project.topic || 'No topic'}</p>
                <div class="project-stats">
                    <span>📄 Papers: ${project.papers_count || 0}</span>
                    <span>${project.has_assignment ? '✓ Assignment' : 'No Assignment'}</span>
                    <span>${project.has_presentation ? '✓ Presentation' : 'No Presentation'}</span>
                </div>
                <div class="project-meta">
                    <span>${new Date(project.created_at).toLocaleDateString()}</span>
                    <span class="status-badge ${project.status}">${project.status}</span>
                </div>
            </div>
        `).join('');

    } catch (error) {
        showToast(`Error loading projects: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function openProjectDetail(projectId) {
    try {
        showLoading(true);
        currentProject = await api.getProject(projectId);
        showPage('project-detail');
        renderProjectDetail();
    } catch (error) {
        showToast(`Error loading project: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function renderProjectDetail() {
    if (!currentProject) return;

    const container = document.getElementById('project-detail-content');
    container.innerHTML = `
        <div class="project-detail-header">
            <h2>${currentProject.title}</h2>
            <p class="topic">${currentProject.topic}</p>
            <p class="status-badge ${currentProject.status}">${currentProject.status}</p>
        </div>

        <div class="project-workflow">
            <div class="workflow-step" id="research-step">
                <h3>1. 🔍 Research</h3>
                <p>Search for academic papers</p>
                <button class="btn btn-secondary" onclick="openResearchModal()">Start Research</button>
                <p class="step-status">${currentProject.papers_count || 0} papers added</p>
            </div>

            <div class="workflow-step" id="assignment-step">
                <h3>2. 📝 Assignment</h3>
                <p>Generate assignment from papers</p>
                <button class="btn btn-secondary" onclick="generateAssignment()" ${!currentProject.papers_count ? 'disabled' : ''}>Generate Assignment</button>
                <p class="step-status">${currentProject.has_assignment ? '✓ Ready' : 'Not started'}</p>
            </div>

            <div class="workflow-step" id="presentation-step">
                <h3>3. 🎨 Presentation</h3>
                <p>Create PowerPoint slides</p>
                <button class="btn btn-secondary" onclick="generatePresentation()" ${!currentProject.has_assignment ? 'disabled' : ''}>Generate Slides</button>
                <p class="step-status">${currentProject.has_presentation ? '✓ Ready' : 'Not started'}</p>
            </div>

            <div class="workflow-step" id="export-step">
                <h3>4. 📥 Export</h3>
                <p>Download your documents</p>
                <button class="btn btn-secondary" onclick="showExportOptions()" ${!currentProject.has_assignment && !currentProject.has_presentation ? 'disabled' : ''}>Export</button>
                <p class="step-status">${currentProject.exports_count || 0} exports</p>
            </div>
        </div>

        <div class="project-papers" id="papers-section">
            <h3>Research Papers</h3>
            <div id="papers-list"></div>
        </div>
    `;

    loadProjectPapers();
}

async function loadProjectPapers() {
    try {
        const papers = await api.getProjectPapers(currentProject.id);
        const container = document.getElementById('papers-list');
        
        if (!papers || papers.length === 0) {
            container.innerHTML = '<p class="empty-state">No papers added yet</p>';
            return;
        }

        container.innerHTML = papers.map(paper => `
            <div class="paper-item">
                <div class="paper-info">
                    <h4>${paper.title}</h4>
                    <p>${paper.authors || 'Unknown authors'}</p>
                    <p class="year">${paper.year || 'Unknown year'}</p>
                </div>
                <a href="${paper.url}" target="_blank" class="btn btn-small">View Paper</a>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading papers:', error);
    }
}

async function deleteProject(projectId, event) {
    event.stopPropagation();
    if (!confirm('Are you sure you want to delete this project?')) return;

    try {
        showLoading(true);
        await api.deleteProject(projectId);
        showToast('Project deleted successfully', 'success');
        loadProjects();
    } catch (error) {
        showToast(`Error deleting project: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function openProjectModal() {
    document.getElementById('project-modal').classList.remove('hidden');
}

function closeProjectModal() {
    document.getElementById('project-modal').classList.add('hidden');
    document.getElementById('project-form').reset();
}

async function handleCreateProject(e) {
    e.preventDefault();
    const title = document.getElementById('project-name').value;
    const topic = document.getElementById('project-description').value;

    if (!title.trim() || !topic.trim()) {
        showToast('Project title and topic are required', 'error');
        return;
    }

    try {
        showLoading(true);
        await api.createProject(title, topic);
        showToast('Project created successfully!', 'success');
        closeProjectModal();
        loadProjects();
    } catch (error) {
        showToast(`Error creating project: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ RESEARCH ============
function openResearchModal() {
    document.getElementById('research-modal').classList.remove('hidden');
    document.getElementById('research-papers-list').innerHTML = '';
    selectedPapers = [];
}

function closeResearchModal() {
    document.getElementById('research-modal').classList.add('hidden');
}

async function searchPapers(e) {
    e.preventDefault();
    const topic = document.getElementById('research-search-topic').value;

    if (!topic.trim()) {
        showToast('Please enter a search topic', 'error');
        return;
    }

    try {
        showLoading(true);
        researchPapers = await api.searchResearchPapers(topic, currentProject?.id);
        
        const container = document.getElementById('research-papers-list');
        container.innerHTML = researchPapers.map((paper, idx) => `
            <div class="paper-item">
                <input type="checkbox" class="paper-checkbox" data-index="${idx}" onchange="togglePaper(${idx})">
                <div class="paper-info">
                    <h4>${paper.title}</h4>
                    <p>${paper.authors || 'Unknown authors'}</p>
                    <p>${paper.year || 'Year unknown'}</p>
                    <p class="abstract">${paper.abstract ? paper.abstract.substring(0, 200) + '...' : 'No abstract'}</p>
                </div>
                ${paper.url ? `<a href="${paper.url}" target="_blank" class="btn btn-small">View</a>` : ''}
            </div>
        `).join('');

        showToast(`Found ${researchPapers.length} papers`, 'success');
    } catch (error) {
        showToast(`Search error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function togglePaper(index) {
    const checkbox = document.querySelector(`input[data-index="${index}"]`);
    if (checkbox.checked) {
        if (!selectedPapers.includes(index)) {
            selectedPapers.push(index);
        }
    } else {
        selectedPapers = selectedPapers.filter(i => i !== index);
    }
}

async function addSelectedPapers() {
    if (selectedPapers.length === 0) {
        showToast('Please select at least one paper', 'error');
        return;
    }

    try {
        showLoading(true);
        const papers = selectedPapers.map(idx => researchPapers[idx]);
        await api.addPapersToProject(currentProject.id, papers);
        showToast(`${papers.length} papers added successfully!`, 'success');
        closeResearchModal();
        loadProjectPapers();
        currentProject.papers_count = (currentProject.papers_count || 0) + papers.length;
        renderProjectDetail();
    } catch (error) {
        showToast(`Error adding papers: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ GENERATION ============
async function generateAssignment() {
    if (!currentProject) return;

    try {
        showLoading(true);
        await api.generateAssignmentAsync(currentProject.id);
        showToast('Assignment generation started! This may take a few moments.', 'success');
        
        // Poll for completion
        setTimeout(() => loadProjectDetail(), 2000);
    } catch (error) {
        showToast(`Error generating assignment: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function generatePresentation() {
    if (!currentProject) return;

    try {
        showLoading(true);
        await api.generatePresentationAsync(currentProject.id);
        showToast('Presentation generation started! This may take a few moments.', 'success');
        
        setTimeout(() => loadProjectDetail(), 2000);
    } catch (error) {
        showToast(`Error generating presentation: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ EXPORT ============
function showExportOptions() {
    document.getElementById('export-modal').classList.remove('hidden');
}

function closeExportModal() {
    document.getElementById('export-modal').classList.add('hidden');
}

async function exportProjectPDF() {
    if (!currentProject?.has_assignment) {
        showToast('No assignment to export', 'error');
        return;
    }

    try {
        showLoading(true);
        const result = await api.exportToPDF(currentProject.id, currentProject.id);
        showToast('PDF export started!', 'success');
        setTimeout(() => loadProjectDetail(), 2000);
    } catch (error) {
        showToast(`Export error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function exportProjectPPTX() {
    if (!currentProject?.has_presentation) {
        showToast('No presentation to export', 'error');
        return;
    }

    try {
        showLoading(true);
        const result = await api.exportToPPTX(currentProject.id, currentProject.id);
        showToast('PowerPoint export started!', 'success');
        setTimeout(() => loadProjectDetail(), 2000);
    } catch (error) {
        showToast(`Export error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ MODALS ============
function createModal(id, title, content) {
    const modal = `
        <div id="${id}" class="modal hidden">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close" onclick="closeModal('${id}')">✕</button>
                </div>
                ${content}
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modal);
}

function closeModal(id) {
    document.getElementById(id)?.classList.add('hidden');
}

// ============ UI UTILITIES ============
function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    if (show) {
        spinner?.classList.remove('hidden');
    } else {
        spinner?.classList.add('hidden');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container?.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4000);
}

function toggleSidebar() {
    document.querySelector('.sidebar')?.classList.toggle('open');
}

// ============ EVENT LISTENERS ============
function attachEventListeners() {
    // Auth
    document.getElementById('login-form')?.addEventListener('submit', handleLogin);
    document.getElementById('register-form')?.addEventListener('submit', handleRegister);
    document.getElementById('logout-btn')?.addEventListener('click', handleLogout);

    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            showPage(page);
        });
    });

    // Projects
    document.getElementById('create-project-btn')?.addEventListener('click', openProjectModal);
    document.getElementById('project-form')?.addEventListener('submit', handleCreateProject);

    // Research
    document.getElementById('research-search-form')?.addEventListener('submit', searchPapers);
    document.getElementById('add-papers-btn')?.addEventListener('click', addSelectedPapers);

    // Export
    document.getElementById('export-pdf-btn')?.addEventListener('click', exportProjectPDF);
    document.getElementById('export-pptx-btn')?.addEventListener('click', exportProjectPPTX);
}
