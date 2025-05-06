import { defineStore } from 'pinia';

export const useEventsStore = defineStore('events', {
  state: () => ({
    events: [],
    currentEvent: null,
    loading: false,
    error: null,
  }),
  actions: {
    setEvents(events) {
      this.events = events;
    },
    setCurrentEvent(event) {
      this.currentEvent = event;
    },
    setError(error) {
      this.error = error;
    },
  },
});