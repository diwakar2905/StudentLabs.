/**
 * API Service Layer
 * Handles all communication with the StudentLabs backend API
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

class APIService {
    constructor() {
        this.token = localStorage.getItem('auth_token');
    }

    /**
     * Generic fetch wrapper with error handling
     */
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

    /**
     * Authentication
     */

    async register(name, email, password) {
        return this.request('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({
                name,
                email,
                password,
            }),
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

    /**
     * Users
     */

    async getCurrentUser() {
        return this.request('/users/me');
    }

    async updateProfile(data) {
        return this.request('/users/me', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    /**
     * Projects
     */

    async getProjects() {
        return this.request('/projects');
    }

    async getProject(projectId) {
        return this.request(`/projects/${projectId}`);
    }

    async createProject(data) {
        return this.request('/projects', {
            method: 'POST',
            body: JSON.stringify({
                title: data.name,
                topic: data.description,
            }),
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

    /**
     * Research
     */

    async startResearch(topic, keywords, depth = 'basic') {
        return this.request('/research', {
            method: 'POST',
            body: JSON.stringify({
                topic,
                keywords,
                depth,
            }),
        });
    }

    async getResearchResults(projectId) {
        return this.request(`/research/${projectId}`);
    }

    /**
     * Generate
     */

    async generateContent(type, topic, requirements = '') {
        return this.request('/generate', {
            method: 'POST',
            body: JSON.stringify({
                type,
                topic,
                requirements,
            }),
        });
    }

    /**
     * Export
     */

    async exportDocument(projectId, format) {
        return this.request('/export', {
            method: 'POST',
            body: JSON.stringify({
                project_id: projectId,
                format,
            }),
        });
    }

    /**
     * Jobs (for tracking async tasks)
     */

    async getJobs() {
        return this.request('/jobs');
    }

    async getJob(jobId) {
        return this.request(`/jobs/${jobId}`);
    }
}

// Create global API instance
const api = new APIService();
