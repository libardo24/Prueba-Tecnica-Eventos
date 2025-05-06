<template>
    <v-container>
      <v-row>
        <v-col>
          <h1>Asistencias a Sesiones</h1>
          <v-alert v-if="errorMessage" type="error" class="mb-4" dismissible @input="errorMessage = ''">
            {{ errorMessage }}
          </v-alert>
          <v-progress-linear v-if="loading" indeterminate color="primary"></v-progress-linear>
          <v-data-table
            :headers="headers"
            :items="asistencias"
            :loading="loading"
            class="elevation-1"
          >
            <template v-slot:item.fecha_inicio="{ item }">
              {{ formatDate(item.fecha_inicio) }}
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '../stores/auth';
  import api from '../services/api';
  
  export default {
    name: 'SessionAssistantsView',
    setup() {
      const router = useRouter();
      const authStore = useAuthStore();
      const asistencias = ref([]);
      const loading = ref(false);
      const errorMessage = ref('');
      const headers = [
        { title: 'Usuario ID', key: 'usuario_id' },
        { title: 'Email', key: 'email' },
        { title: 'Sesión ID', key: 'sesion_id' },
        { title: 'Nombre de la Sesión', key: 'nombre_sesion' },
        { title: 'Fecha de Inicio', key: 'fecha_inicio' },
      ];
  
      const loadAssistants = async () => {
        if (!authStore.token) {
          errorMessage.value = 'Por favor, inicia sesión';
          router.push('/login');
          return;
        }
        try {
          loading.value = true;
          const response = await api.get('/sesiones/asistencias');
          asistencias.value = response.data.asistencias;
        } catch (error) {
          handleError(error);
        } finally {
          loading.value = false;
        }
      };
  
      const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleString('es-ES', { dateStyle: 'medium', timeStyle: 'short' });
      };
  
      const handleError = (error) => {
        if (error.response) {
          const { status, data } = error.response;
          if (status === 401) {
            errorMessage.value = 'Sesión expirada. Por favor, inicia sesión de nuevo';
            authStore.logout();
            router.push('/login');
          } else {
            errorMessage.value = data.message || 'Error al cargar asistencias';
          }
        } else {
          errorMessage.value = `Error: ${error.message}`;
          console.error('Detalles del error:', error);
        }
      };
  
      onMounted(() => {
        loadAssistants();
      });
  
      return {
        asistencias,
        loading,
        errorMessage,
        headers,
        formatDate,
      };
    },
  };
  </script>
  
  <style scoped>
  .elevation-1 {
    margin-top: 20px;
  }
  </style>