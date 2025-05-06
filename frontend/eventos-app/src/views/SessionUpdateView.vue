<template>
  <SessionForm :session-id="sessionId" />
</template>

<script>
import { useRoute } from 'vue-router';
import SessionForm from '@/components/common/SessionForm.vue';

export default {
  name: 'SessionUpdateView',
  components: {
    SessionForm,
  },
  setup() {
    const route = useRoute();
    const sessionId = route.params.id;

    return {
      sessionId,
    };
  },
};
</script>