import { defineStore } from 'pinia';

export const useSessionsStore = defineStore('sessions', {
  state: () => ({
    sessions: [],
    currentSession: null,
    loading: false,
    error: null,
  }),
  actions: {
    setSessions(sessions) {
      this.sessions = sessions;
    },
    setCurrentSession(session) {
      this.currentSession = session;
    },
    setError(error) {
      this.error = error;
    },
  },
});