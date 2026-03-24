/**
 * StudentLabs API Service Layer
 * Complete API integration with all backend endpoints
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

class APIService {
    constructor() {
        this.token = localStorage.getItem('auth_token');
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // ===== AUTHENTICATION =====
    async register(name, email, password) {
        return this.request('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ name, email, password }),
        });
    }

    async login(email, password) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });

        if (response.access_token) {
            this.token = response.access_token;
            localStorage.setItem('auth_token', this.token);
        }

        return response;
    }

    async logout() {
        localStorage.removeItem('auth_token');
        this.token = null;
    }

    async getCurrentUser() {
        return this.request('/users/me');
    }

    // ===== PROJECTS =====
    async getProjects() {
        return this.request('/projects');
    }

    async getProject(projectId) {
        return this.request(`/projects/${projectId}`);
    }

    async createProject(title, topic) {
        return this.request('/projects', {
            method: 'POST',
            body: JSON.stringify({ title, topic }),
        });
    }

    async updateProject(projectId, data) {
        return this.request(`/projects/${projectId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async deleteProject(projectId) {
        return this.request(`/projects/${projectId}`, {
            method: 'DELETE',
        });
    }

    async getProjectPapers(projectId) {
        return this.request(`/projects/${projectId}/papers`);
    }

    // ===== RESEARCH =====
    async searchResearchPapers(topic, projectId = null) {
        return this.request('/research/search', {
            method: 'POST',
            body: JSON.stringify({ topic, project_id: projectId }),
        });
    }

    async addPapersToProject(projectId, papers) {
        return this.request(`/research/${projectId}/papers/add`, {
            method: 'POST',
            body: JSON.stringify(papers),
        });
    }

    async summarizePaper(paperId) {
        return this.request('/research/summarize', {
            method: 'POST',
            body: JSON.stringify({ paper_id: paperId }),
        });
    }

    // ===== GENERATION =====
    async generateAssignment(projectId, paperIds = null) {
        return this.request(`/generate/${projectId}/assignment`, {
            method: 'POST',
            body: JSON.stringify({ paper_ids: paperIds }),
        });
    }

    async generateAssignmentAsync(projectId) {
        return this.request(`/generate/${projectId}/assignment-async`, {
            method: 'POST',
            body: JSON.stringify({}),
        });
    }

    async getAssignment(projectId) {
        return this.request(`/generate/${projectId}/assignment`);
    }

    async updateAssignment(projectId, title, content, citations = null) {
        return this.request(`/generate/${projectId}/assignment`, {
            method: 'PUT',
            body: JSON.stringify({ title, content, citations }),
        });
    }

    async generatePresentation(projectId, assignmentId = null) {
        return this.request(`/generate/${projectId}/ppt`, {
            method: 'POST',
            body: JSON.stringify({ assignment_id: assignmentId }),
        });
    }

    async generatePresentationAsync(projectId) {
        return this.request(`/generate/${projectId}/ppt-async`, {
            method: 'POST',
            body: JSON.stringify({}),
        });
    }

    async getPresentation(projectId) {
        return this.request(`/generate/${projectId}/ppt`);
    }

    async updatePresentation(projectId, slides) {
        return this.request(`/generate/${projectId}/ppt`, {
            method: 'PUT',
            body: JSON.stringify(slides),
        });
    }

    // ===== EXPORT =====
    async exportToPDF(projectId, assignmentId) {
        return this.request('/export/pdf', {
            method: 'POST',
            body: JSON.stringify({ project_id: projectId, assignment_id: assignmentId }),
        });
    }

    async exportToPPTX(projectId, presentationId) {
        return this.request('/export/pptx', {
            method: 'POST',
            body: JSON.stringify({ project_id: projectId, presentation_id: presentationId }),
        });
    }

    async getExports(projectId) {
        return this.request(`/export/${projectId}/downloads`);
    }

    // ===== JOBS (Async Task Tracking) =====
    async getJobStatus(jobId) {
        return this.request(`/jobs/${jobId}`);
    }

    async getJobResult(jobId) {
        return this.request(`/jobs/${jobId}/result`);
    }

    async cancelJob(jobId) {
        return this.request(`/jobs/${jobId}`, {
            method: 'DELETE',
        });
    }
}

const api = new APIService();
