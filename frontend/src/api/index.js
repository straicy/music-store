import api from './axios'

// ── Auth ─────────────────────────────────────────────────
export const authApi = {
  register: (data)        => api.post('/auth/register', data),
  login:    (data)        => api.post('/auth/login', data),
  refresh:  (token)       => api.post('/auth/refresh', { refresh_token: token }),
  getMe:    ()            => api.get('/auth/me'),
  updateMe: (data)        => api.put('/auth/me', data),
  deleteMe: ()            => api.delete('/auth/me'),
}

// ── Listings ─────────────────────────────────────────────
export const listingsApi = {
  getAll: (params) => api.get('/listings', { params }),
  getMy:  (params) => api.get('/listings/my', { params }),
  getOne: (id)     => api.get(`/listings/${id}`),
  create: (data)   => api.post('/listings', data),
  update: (id, data) => api.put(`/listings/${id}`, data),
  delete: (id)     => api.delete(`/listings/${id}`),

  uploadImages: (id, files) => {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    return api.post(`/listings/${id}/images`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  deleteImage: (id, imageName) =>
    api.delete(`/listings/${id}/images/${imageName}`),
}

// ── Favorites ────────────────────────────────────────────
export const favoritesApi = {
  toggle:  (listingId) => api.post(`/favorites/${listingId}`),
  getAll:  ()          => api.get('/favorites'),
}

// ── Messages ─────────────────────────────────────────────
export const messagesApi = {
  getConversations:       ()    => api.get('/messages/conversations'),
  getConversation: (convId, params) =>
    api.get(`/messages/conversation/${convId}`, { params }),
  send: (data) => api.post('/messages', data),
}

// ── Admin ────────────────────────────────────────────────
export const adminApi = {
  getStats:   ()                    => api.get('/admin/stats'),
  getUsers:   (params)              => api.get('/admin/users', { params }),
  toggleBan:  (userId)              => api.patch(`/admin/users/${userId}/ban`),
  changeRole: (userId, role)        => api.patch(`/admin/users/${userId}/role`, null, { params: { role } }),
  getListings:(params)              => api.get('/admin/listings', { params }),
  setStatus:  (id, status)          => api.patch(`/admin/listings/${id}/status`, null, { params: { status } }),
  deleteListing: (id)               => api.delete(`/admin/listings/${id}`),
}
