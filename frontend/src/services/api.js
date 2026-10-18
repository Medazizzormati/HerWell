const BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
  if (!response.ok) throw new Error(`API error ${response.status}`);
  return response.json();
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
