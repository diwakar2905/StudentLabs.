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

// ============ INITIALIZATION ============
document.addEventListener('DOMContentLoaded', async () => {
    // Check if user is already logged in
    const token = localStorage.getItem('auth_token');
    
    if (token) {
        try {
            currentUser = await api.getCurrentUser();
            showDashboard();
            loadDashboardData();
        } catch (error) {
            // Token is invalid or expired
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
    document.querySelectorAll('.auth-screen').forEach(s => {
        s.classList.remove('active');
    });
    document.getElementById(`${screen}-screen`).classList.add('active');
}

async function handleLogout() {
    await api.logout();
    currentUser = null;
    localStorage.removeItem('auth_token');
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
    // Update header
    const headers = {
        dashboard: 'Dashboard',
        projects: 'Projects',
        research: 'Research',
        generate: 'Generate Content',
        export: 'Export Documents'
    };
    document.getElementById('header-subtitle').textContent = headers[pageName] || 'Page';

    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show selected page
    document.getElementById(`${pageName}-page`).classList.add('active');

    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.dataset.page === pageName) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Load page-specific data
    if (pageName === 'projects') {
        loadProjects();
    }
}

// ============ USER INFO ============
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

        // Load projects
        const projectsData = await api.getProjects();
        projects = projectsData;

        // Update stats
        document.getElementById('stat-projects').textContent = projects.length;
        document.getElementById('stat-tasks').textContent = '0'; // TODO: implement tasks
        document.getElementById('stat-time').textContent = '0h'; // TODO: calculate time saved

        // Load recent projects
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
        <div class="project-card" onclick="viewProject('${project.id}')">
            <h3>${project.title}</h3>
            <p>${project.topic || 'No description'}</p>
            <div class="project-meta">
                <span>${new Date(project.created_at).toLocaleDateString()}</span>
                <span>${project.status || 'Active'}</span>
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
            <div class="project-card" onclick="viewProject('${project.id}')">
                <h3>${project.title}</h3>
                <p>${project.topic || 'No description'}</p>
                <div class="project-meta">
                    <span>${new Date(project.created_at).toLocaleDateString()}</span>
                    <span>${project.status || 'Active'}</span>
                </div>
            </div>
        `).join('');

        // Update export project list
        const exportSelect = document.getElementById('export-project-select');
        exportSelect.innerHTML = '<option value="">Choose a project...</option>' + 
            projects.map(p => `<option value="${p.id}">${p.title}</option>`).join('');

    } catch (error) {
        showToast(`Error loading projects: ${error.message}`, 'error');
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

    const name = document.getElementById('project-name').value;
    const description = document.getElementById('project-description').value;
    const deadline = document.getElementById('project-deadline').value;

    if (!name.trim()) {
        showToast('Project name is required', 'error');
        return;
    }

    try {
        showLoading(true);
        await api.createProject({
            name,
            description,
            deadline: deadline || null,
        });
        
        showToast('Project created successfully!', 'success');
        closeProjectModal();
        await loadProjects();
    } catch (error) {
        showToast(`Error creating project: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function viewProject(projectId) {
    const project = projects.find(p => p.id === projectId);
    if (project) {
        showToast(`Opening project: ${project.name}`, 'info');
        // TODO: Implement project detail view
    }
}

// ============ RESEARCH ============
async function handleStartResearch() {
    const topic = document.getElementById('research-topic').value;
    const keywords = document.getElementById('research-keywords').value;
    const depth = document.getElementById('research-depth').value;

    if (!topic.trim()) {
        showToast('Please enter a research topic', 'error');
        return;
    }

    try {
        showLoading(true);
        const result = await api.startResearch(topic, keywords, depth);
        
        document.getElementById('research-results').classList.remove('hidden');
        document.getElementById('research-content').innerHTML = `
            <h4>${topic}</h4>
            <p><strong>Status:</strong> ${result.status || 'Processing'}</p>
            <p>${result.content || 'Research is being processed...'}</p>
        `;

        showToast('Research started!', 'success');
    } catch (error) {
        showToast(`Research error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ GENERATE ============
async function handleGenerate() {
    const type = document.getElementById('generate-type').value;
    const topic = document.getElementById('generate-topic').value;
    const requirements = document.getElementById('generate-requirements').value;

    if (!topic.trim()) {
        showToast('Please enter a topic', 'error');
        return;
    }

    try {
        showLoading(true);
        const result = await api.generateContent(type, topic, requirements);
        
        document.getElementById('generate-results').classList.remove('hidden');
        document.getElementById('generated-content').innerHTML = `
            <h4>${topic}</h4>
            <p><strong>Type:</strong> ${type}</p>
            <hr style="margin: 1rem 0; border: none; border-top: 1px solid var(--border-color);">
            <div>${result.content || 'Content is being generated...'}</div>
        `;

        showToast('Content generated!', 'success');
    } catch (error) {
        showToast(`Generation error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ EXPORT ============
async function handleExport() {
    const projectId = document.getElementById('export-project-select').value;
    const format = document.getElementById('export-format').value;

    if (!projectId) {
        showToast('Please select a project', 'error');
        return;
    }

    try {
        showLoading(true);
        const result = await api.exportDocument(projectId, format);
        
        document.getElementById('export-status').classList.remove('hidden');
        document.getElementById('export-message').textContent = 
            `Document exported successfully as ${format.toUpperCase()}!`;
        
        showToast('Export completed!', 'success');
    } catch (error) {
        showToast(`Export error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ SIDEBAR ============
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('open');
}

// ============ UI UTILITIES ============
function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    if (show) {
        spinner.classList.remove('hidden');
    } else {
        spinner.classList.add('hidden');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// ============ EVENT LISTENERS ============
function attachEventListeners() {
    // Auth forms
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Logout
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            showPage(page);
        });
    });

    // Project Modal
    document.getElementById('create-project-btn').addEventListener('click', openProjectModal);
    document.getElementById('project-form').addEventListener('submit', handleCreateProject);

    // Research
    document.getElementById('start-research-btn').addEventListener('click', handleStartResearch);

    // Generate
    document.getElementById('generate-btn').addEventListener('click', handleGenerate);

    // Export
    document.getElementById('export-btn').addEventListener('click', handleExport);
}
