<template>
  <v-container class="profile-container">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <!-- Título -->
        <h1 class="text-h4 mb-6">Mi Perfil</h1>

        <!-- Alertas -->
        <v-alert
          v-if="errorMessage"
          type="error"
          class="mb-6 rounded-lg primary-alert"
          dismissible
          @input="errorMessage = ''"
        >
          {{ errorMessage }}
        </v-alert>

        <!-- Tabla de Eventos -->
        <v-card elevation="4" class="rounded-lg mb-8">
          <v-card-title class="text-h5 primary--text text-center py-4">
            Eventos Registrados
          </v-card-title>
          <v-divider></v-divider>
          <v-data-table
            :headers="headers"
            :items="eventos"
            :items-per-page="itemsPerPage"
            :page="page"
            :server-items-length="totalEventos"
            :loading="loading"
            class="elevation-0"
            hide-default-footer
            @update:options="fetchEventos"
          >
            <template v-slot:item="{ item }">
              <tr>
                <td>{{ item.nombre }}</td>
                <td>{{ formatDate(item.fecha_inicio) }}</td>
                <td>{{ item.estado }}</td>
                <td>
                  <v-btn
                    color="primary"
                    :to="{ name: 'EventDetail', params: { id: item.id } }"
                    class="mx-2 primary-btn"
                    prepend-icon="mdi-eye"
                    small
                  >
                    Ver Detalles
                  </v-btn>
                  <v-btn
                    color="secondary"
                    @click="openSessionsModal(item.id)"
                    class="mx-2 secondary-btn"
                    prepend-icon="mdi-calendar"
                    small
                    :loading="loadingSessions === item.id"
                  >
                    Ver Sesiones
                  </v-btn>
                  <v-btn
                    color="error"
                    @click="selectEventoToDelete(item)"
                    class="mx-2 error-btn"
                    prepend-icon="mdi-close"
                    small
                    :loading="loadingDelete === item.id"
                  >
                    Cancelar Registro
                  </v-btn>
                </td>
              </tr>
            </template>
            <template v-slot:bottom>
              <v-container fluid>
                <v-row align="center" justify="center">
                  <v-col cols="12" sm="6">
                    <v-select
                      v-model="itemsPerPage"
                      :items="[5, 10, 20, 50]"
                      label="Eventos por página"
                      variant="outlined"
                      dense
                      hide-details
                      class="items-per-page-select"
                      @update:modelValue="updateItemsPerPage"
                    />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-pagination
                      v-model="page"
                      :length="totalPages"
                      :total-visible="7"
                      prev-icon="mdi-chevron-left"
                      next-icon="mdi-chevron-right"
                      class="eventos-pagination"
                      active-color="#6ac6dc"
                      @update:modelValue="updatePage"
                    />
                  </v-col>
                </v-row>
              </v-container>
            </template>
          </v-data-table>
        </v-card>

        <!-- Diálogo de Confirmación para Cancelar Registro -->
        <v-dialog
          v-model="showDeleteDialog"
          max-width="500"
          persistent
        >
          <v-card class="dialog-card rounded-lg">
            <v-card-title class="text-h6 primary--text">
              <v-icon color="error" class="mr-2">mdi-alert</v-icon>
              Confirmar Cancelación
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pt-4">
              ¿Estás seguro de que quieres cancelar tu registro al evento
              <strong>{{ eventoToDelete?.nombre }}</strong>? Esta acción no se puede deshacer.
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="secondary"
                class="secondary-btn"
                text
                @click="showDeleteDialog = false"
              >
                Cancelar
              </v-btn>
              <v-btn
                color="error"
                class="error-btn white--text"
                :loading="loadingDelete === eventoToDelete?.id"
                @click="eliminarRegistro"
              >
                Confirmar
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Modal de Sesiones -->
        <v-dialog
          v-model="showSessionsModal"
          max-width="800"
          persistent
        >
          <v-card class="rounded-lg">
            <v-card-title class="text-h6 primary--text">
              Sesiones del Evento
              <v-spacer></v-spacer>
              <v-btn icon @click="closeSessionsModal">
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pt-4">
              <v-alert
                v-if="sessionErrorMessage"
                type="error"
                class="mb-4 rounded-lg primary-alert"
                dismissible
                @input="sessionErrorMessage = ''"
              >
                {{ sessionErrorMessage }}
              </v-alert>
              <v-alert
                v-if="sessionSuccessMessage"
                type="success"
                class="mb-4 rounded-lg primary-alert"
                dismissible
                @input="sessionSuccessMessage = ''"
              >
                {{ sessionSuccessMessage }}
              </v-alert>
              <div v-if="sessions.length === 0 && !loadingSessions">
                <p class="text-center">No hay sesiones disponibles para este evento.</p>
              </div>
              <v-row v-else>
                <v-col cols="12">
                  <v-card
                    v-for="session in sessions"
                    :key="session.id"
                    class="session-card mb-4"
                    outlined
                  >
                    <v-card-title class="text-subtitle-1">
                      {{ session.nombre }}
                    </v-card-title>
                    <v-card-text>
                      <p><strong>Fecha de Inicio:</strong> {{ formatDate(session.fecha_inicio) }}</p>
                      <p><strong>Fecha de Fin:</strong> {{ formatDate(session.fecha_fin) }}</p>
                      <p><strong>Capacidad:</strong> {{ session.capacidad_maxima }}</p>
                      <p v-if="session.is_registered" class="text-success">
                        <v-icon color="success" small>mdi-check</v-icon> Ya estás registrado
                      </p>
                      <p v-else-if="session.asistentes_count >= session.capacidad_maxima" class="text-error">
                        <v-icon color="error" small>mdi-alert</v-icon> Sesión llena
                      </p>
                      <p v-else-if="isDatePast(session.fecha_inicio)" class="text-error">
                        <v-icon color="error" small>mdi-alert</v-icon> Fecha pasada
                      </p>
                    </v-card-text>
                    <v-card-actions class="session-actions">
                      <v-btn
                        color="primary"
                        class="primary-btn"
                        @click="registerForSession(session.id)"
                        :loading="loadingRegister === session.id"
                        :disabled="session.asistentes_count >= session.capacidad_maxima || session.is_registered || isDatePast(session.fecha_inicio)"
                        :title="session.is_registered ? 'Ya estás registrado' : session.asistentes_count >= session.capacidad_maxima ? 'Sesión llena' : isDatePast(session.fecha_inicio) ? 'Fecha pasada' : 'Registrarse'"
                      >
                        {{ session.is_registered ? 'Registrado' : 'Registrarse' }}
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="secondary"
                class="secondary-btn rounded-lg"
                @click="closeSessionsModal"
              >
                Cerrar
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Botón Volver -->
        <div class="text-center mt-6">
          <v-btn
            color="secondary"
            class="secondary-btn rounded-lg"
            :to="{ name: 'Home' }"
            prepend-icon="mdi-arrow-left"
          >
            Volver
          </v-btn>
        </div>
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
  name: 'ProfileView',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const eventos = ref([]);
    const totalEventos = ref(0);
    const totalPages = ref(1);
    const page = ref(1);
    const itemsPerPage = ref(10);
    const loading = ref(false);
    const errorMessage = ref('');
    const showSessionsModal = ref(false);
    const sessions = ref([]);
    const loadingSessions = ref(null);
    const sessionErrorMessage = ref('');
    const sessionSuccessMessage = ref('');
    const loadingRegister = ref(null);
    const showDeleteDialog = ref(false);
    const eventoToDelete = ref(null);
    const loadingDelete = ref(null);

    const headers = [
      { title: 'Nombre', key: 'nombre', sortable: true },
      { title: 'Fecha de Inicio', key: 'fecha_inicio', sortable: true },
      { title: 'Estado', key: 'estado', sortable: true },
      { title: 'Acciones', key: 'actions', sortable: false },
    ];

    const fetchEventos = async (options = {}) => {
      if (!authStore.isAuthenticated() || !authStore.user?.id) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      const { page: currentPage, itemsPerPage: perPage } = options;
      page.value = currentPage || page.value;
      itemsPerPage.value = perPage || itemsPerPage.value;

      loading.value = true;
      errorMessage.value = '';

      try {
        const response = await api.get('/eventos/mis-eventos', {
          params: {
            page: page.value,
            per_page: itemsPerPage.value,
          },
        });
        eventos.value = response.data.eventos || [];
        totalEventos.value = response.data.total || 0;
        totalPages.value = response.data.total_pages || 1;
      } catch (error) {
        handleError(error);
      } finally {
        loading.value = false;
      }
    };

    const selectEventoToDelete = (evento) => {
      eventoToDelete.value = evento;
      showDeleteDialog.value = true;
    };

    const eliminarRegistro = async () => {
      if (!authStore.isAuthenticated()) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      if (!eventoToDelete.value) return;

      loadingDelete.value = eventoToDelete.value.id;
      errorMessage.value = '';

      try {
        const response = await api.delete(`/eventos/${eventoToDelete.value.id}/eliminar-registro`);
        showDeleteDialog.value = false;
        eventoToDelete.value = null;
        await fetchEventos();
      } catch (error) {
        handleError(error);
      } finally {
        loadingDelete.value = null;
      }
    };

    const openSessionsModal = async (eventoId) => {
      if (!authStore.isAuthenticated() || !authStore.user?.id) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      loadingSessions.value = eventoId;
      sessionErrorMessage.value = '';
      sessionSuccessMessage.value = '';
      sessions.value = [];

      try {
        const response = await api.get(`/sesiones/${eventoId}/sesiones`);
        sessions.value = (response.data || []).map(session => ({
          ...session,
          asistentes_count: Number(session.asistentes_count) || 0,
          capacidad_maxima: Number(session.capacidad_maxima) || 0,
          is_registered: session.is_registered || false,
        }));
        showSessionsModal.value = true;
      } catch (error) {
        handleError(error, true);
      } finally {
        loadingSessions.value = null;
      }
    };

    const closeSessionsModal = () => {
      showSessionsModal.value = false;
      sessions.value = [];
      sessionErrorMessage.value = '';
      sessionSuccessMessage.value = '';
    };

    const isDatePast = (fechaInicio) => {
      try {
        const sessionDate = new Date(fechaInicio);
        const now = new Date();
        return sessionDate < now;
      } catch (error) {
        console.error('Error al validar fecha:', fechaInicio, error);
        return true; // Deshabilitar si la fecha es inválida
      }
    };

    const registerForSession = async (sesionId) => {
      if (!authStore.isAuthenticated() || !authStore.user?.id) {
        sessionErrorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }
      loadingRegister.value = sesionId;
      sessionErrorMessage.value = '';
      sessionSuccessMessage.value = '';

      try {
        const response = await api.post(`/sesiones/registrar_asistente/${sesionId}`, {
          usuario_id: authStore.user.id,
        });
        sessionSuccessMessage.value = response.data.message || 'Registrado exitosamente en la sesión';

        // Actualizar localmente
        const session = sessions.value.find(s => s.id === sesionId);
        if (session) {
          session.is_registered = true;
          session.asistentes_count = (session.asistentes_count || 0) + 1;
        }

        // Recargar sesiones
        const eventoId = session?.evento_id;
        if (eventoId) {
          await openSessionsModal(eventoId);
        }
      } catch (error) {
        console.error('Error al registrar en sesión:', error);
        handleError(error, true);
      } finally {
        loadingRegister.value = null;
      }
    };

    const updatePage = (newPage) => {
      page.value = newPage;
      fetchEventos();
    };

    const updateItemsPerPage = (newItemsPerPage) => {
      itemsPerPage.value = newItemsPerPage;
      page.value = 1;
      fetchEventos();
    };

    const handleError = (error, isSessionError = false) => {
      const targetMessage = isSessionError ? sessionErrorMessage : errorMessage;
      if (error.response) {
        const { status, data } = error.response;
        console.error('Error del servidor:', { status, data });
        if (status === 401) {
          targetMessage.value = 'Sesión expirada. Por favor, inicia sesión de nuevo';
          authStore.logout();
          router.push('/login');
        } else if (status === 404) {
          targetMessage.value = data.message || 'Sesión no encontrada';
        } else if (status === 400) {
          targetMessage.value = data.message || 'No se puede registrar en esta sesión';
          if (data.message?.includes('ya registrado')) {
            targetMessage.value = 'Ya estás registrado en esta sesión';
            const sesionId = error.response.config.url.split('/').pop();
            const session = sessions.value.find(s => s.id === Number(sesionId));
            if (session) session.is_registered = true;
          }
        } else if (status === 409) {
          targetMessage.value = data.message || 'Conflicto: ya estás registrado o la sesión está llena';
        } else {
          targetMessage.value = data.message || 'Error en la operación';
        }
      } else {
        console.error('Error de conexión:', error.message);
        targetMessage.value = `Error de conexión: ${error.message}`;
      }
    };

    const formatDate = (dateString) => {
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) throw new Error('Fecha inválida');
        return date.toLocaleString('es-ES', {
          dateStyle: 'medium',
          timeStyle: 'short',
        });
      } catch (error) {
        console.error('Error al formatear fecha:', dateString, error);
        return 'Fecha inválida';
      }
    };

    onMounted(() => {
      fetchEventos();
    });

    return {
      eventos,
      totalEventos,
      totalPages,
      page,
      itemsPerPage,
      loading,
      errorMessage,
      headers,
      fetchEventos,
      formatDate,
      showSessionsModal,
      sessions,
      loadingSessions,
      sessionErrorMessage,
      sessionSuccessMessage,
      loadingRegister,
      openSessionsModal,
      closeSessionsModal,
      registerForSession,
      isDatePast,
      showDeleteDialog,
      eventoToDelete,
      loadingDelete,
      selectEventoToDelete,
      eliminarRegistro,
      updatePage,
      updateItemsPerPage,
    };
  },
};
</script>

<style scoped>
@import '@/assets/styles/profile.css';
</style>