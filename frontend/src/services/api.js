const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function request(path, options = {}) {
  try {
    const headers = {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...(options.headers || {})
    };
    
    const response = await fetch(`${BASE}${path}`, { 
      headers,
      ...options 
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw { response: { data: error }, status: response.status };
    }
    
    return response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

export const api = {
  health: () => request('/health'),
  resources: () => request('/api/resources'),
  checkins: () => request('/api/checkins'),
  saveCheckin: (data) => request('/api/checkins', { method: 'POST', body: JSON.stringify(data) }),
  tasks: () => request('/api/tasks'),
  addTask: (data) => request('/api/tasks', { method: 'POST', body: JSON.stringify(data) }),
  updateTask: (id, data) => request(`/api/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteTask: (id) => request(`/api/tasks/${id}`, { method: 'DELETE' }),
  plan: (data) => request('/api/plans', { method: 'POST', body: JSON.stringify(data) }),
  chat: (message) => request('/api/chat', { method: 'POST', body: JSON.stringify({ message }) }),
  // Authentication
  login: (email, password) => request('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  register: (email, password, full_name) => request('/api/auth/register', { method: 'POST', body: JSON.stringify({ email, password, full_name }) }),
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return Promise.resolve();
  },
  getCurrentUser: () => {
    const token = localStorage.getItem('token');
    if (!token) return Promise.reject(new Error('No token'));
    return request('/api/auth/me?token=' + token);
  },
  // Technical PFE Assistant API
  projects: () => request('/api/projects'),
  createProject: (data) => request('/api/projects', { method: 'POST', body: JSON.stringify(data) }),
  updateProject: (id, data) => request(`/api/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteProject: (id) => request(`/api/projects/${id}`, { method: 'DELETE' }),
  projectDocuments: (projectId) => request(`/api/projects/${projectId}/documents`),
  createProjectDocument: (projectId, data) => request(`/api/projects/${projectId}/documents`, { method: 'POST', body: JSON.stringify(data) }),
  deleteDocument: (id) => request(`/api/documents/${id}`, { method: 'DELETE' }),
  projectTasks: (projectId) => request(`/api/projects/${projectId}/tasks`),
  createProjectTask: (projectId, data) => request(`/api/projects/${projectId}/tasks`, { method: 'POST', body: JSON.stringify(data) }),
  updateProjectTask: (id, data) => request(`/api/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteProjectTask: (id) => request(`/api/tasks/${id}`, { method: 'DELETE' }),
  technicalChat: (data) => request('/api/technical-chat', { method: 'POST', body: JSON.stringify(data) }),
  // Women's Wellbeing API
  listCycles: () => request('/api/menstrual/cycles'),
  menstrualCycles: () => request('/api/menstrual/cycles'),
  createCycle: (data) => request('/api/menstrual/cycles', { method: 'POST', body: JSON.stringify(data) }),
  deleteCycle: (id) => request(`/api/menstrual/cycles/${id}`, { method: 'DELETE' }),
  listSymptoms: () => request('/api/menstrual/symptoms'),
  menstrualSymptoms: () => request('/api/menstrual/symptoms'),
  createSymptomLog: (data) => request('/api/menstrual/symptoms', { method: 'POST', body: JSON.stringify(data) }),
  deleteSymptomLog: (id) => request(`/api/menstrual/symptoms/${id}`, { method: 'DELETE' }),
  estimateNextPeriod: () => request('/api/menstrual/estimate-next-period'),
  deleteAllMenstrualData: () => request('/api/menstrual/all-data', { method: 'DELETE' })
};
