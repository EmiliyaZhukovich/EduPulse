import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Send cookies (access_token cookie set by backend) with requests
api.defaults.withCredentials = true

// Survey API
export const getSurveyQuestions = async () => {
  const response = await api.get('/surveys/questions')
  return response.data
}

export const getSurveyGroups = async () => {
  const response = await api.get('/surveys/groups')
  return response.data
}

export const submitSurveyByGroup = async (groupId: number, answers: any[]) => {
  const payload = { group_id: groupId, answers }
  const response = await api.post('/surveys/submit-group', payload)
  return response.data
}

// Auth
export const getCurrentUser = async () => {
  const response = await api.get('/auth/user')
  return response.data
}

export const startLogin = (redirectPath = '/') => {
  // Redirect browser to backend login endpoint which in turn forwards to Keycloak
  window.location.href = `/api/auth/login?redirect=${encodeURIComponent(redirectPath)}`
}

// Curator API
export const getGroups = async () => {
  const response = await api.get('/curator/groups')
  return response.data
}

export const getGroupStatistics = async (groupId: number) => {
  const response = await api.get(`/curator/groups/${groupId}/statistics`)
  return response.data
}

export const getGroupLinks = async (groupId: number) => {
  const response = await api.get(`/curator/groups/${groupId}/links`)
  return response.data
}

// Admin API
export const getAllStatistics = async () => {
  const response = await api.get('/admin/statistics/all')
  return response.data
}

export const getFacultyStatistics = async (facultyName: string) => {
  const response = await api.get(`/admin/statistics/faculty/${facultyName}`)
  return response.data
}

export const getAllGroups = async () => {
  const response = await api.get('/admin/groups')
  return response.data
}

// Faculty Management API
export const getFaculties = async () => {
  const response = await api.get('/admin/faculties')
  return response.data
}

export const createFaculty = async (facultyData: { name: string; description?: string }) => {
  const response = await api.post('/admin/faculties', facultyData)
  return response.data
}

export const updateFaculty = async (facultyId: number, facultyData: { name?: string; description?: string }) => {
  const response = await api.put(`/admin/faculties/${facultyId}`, facultyData)
  return response.data
}

export const deleteFaculty = async (facultyId: number) => {
  const response = await api.delete(`/admin/faculties/${facultyId}`)
  return response.data
}

// Group Management API
export const createGroup = async (groupData: { name: string; faculty_id: number; year: number }) => {
  const response = await api.post('/admin/groups', groupData)
  return response.data
}

export const updateGroup = async (groupId: number, groupData: { name?: string; faculty_id?: number; year?: number }) => {
  const response = await api.put(`/admin/groups/${groupId}`, groupData)
  return response.data
}

export const deleteGroup = async (groupId: number) => {
  const response = await api.delete(`/admin/groups/${groupId}`)
  return response.data
}

// Survey Template admin API removed

export default api
