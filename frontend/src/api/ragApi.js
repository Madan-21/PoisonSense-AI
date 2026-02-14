// RAG Chatbot API — connects to the new /rag endpoints
import api from './axios';

export const ragApi = {
  // Ask the RAG chatbot a question
  ask: async (message, sessionId = null, latitude = null, longitude = null) => {
    const payload = {
      message,
      session_id: sessionId,
    };
    if (latitude !== null && longitude !== null) {
      payload.latitude = latitude;
      payload.longitude = longitude;
    }
    const response = await api.post('/rag/ask', payload);
    return response.data;
  },

  // Upload and ingest PDF files
  ingestFiles: async (files, collection = 'general') => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    formData.append('collection', collection);
    const response = await api.post('/rag/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000, // 2 min for large PDFs
    });
    return response.data;
  },

  // Ingest from a server directory
  ingestDirectory: async (directory, collection = 'general') => {
    const response = await api.post('/rag/ingest/directory', {
      directory,
      collection,
    });
    return response.data;
  },

  // List collections + stats
  getCollections: async () => {
    const response = await api.get('/rag/collections');
    return response.data;
  },

  // Delete a collection
  deleteCollection: async (name) => {
    const response = await api.delete(`/rag/collections/${name}`);
    return response.data;
  },

  // Reset chat session
  resetSession: async (sessionId) => {
    const response = await api.post('/rag/reset', {
      session_id: sessionId,
    });
    return response.data;
  },

  // Get RAG system status
  getStatus: async () => {
    const response = await api.get('/rag/status');
    return response.data;
  },

  // Get poison control contacts
  getContacts: async (country = 'nepal') => {
    const response = await api.get(`/rag/tools/contacts/${country}`);
    return response.data;
  },

  // Execute a safe tool
  executeTool: async (toolName, kwargs = {}) => {
    const response = await api.post('/rag/tools/execute', {
      tool_name: toolName,
      kwargs,
    });
    return response.data;
  },

  // Submit feedback on a chatbot answer (helpful / not_helpful)
  submitFeedback: async (interactionId, feedback, note = '') => {
    const response = await api.post('/rag/feedback', {
      interaction_id: interactionId,
      feedback,
      note,
    });
    return response.data;
  },

  // Trigger agentic learning (ingest helpful interactions into KB)
  triggerLearning: async () => {
    const response = await api.post('/rag/learn');
    return response.data;
  },

  // Get learning system stats
  getLearningStats: async () => {
    const response = await api.get('/rag/learning/stats');
    return response.data;
  },
};
