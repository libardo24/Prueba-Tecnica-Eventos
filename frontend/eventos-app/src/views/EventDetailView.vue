<template>
  <v-container class="event-container">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <!-- Título centrado -->
        <h1 class="text-h4 text-center mb-6">Detalles del Evento</h1>

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
        <v-alert
          v-if="successMessage"
          type="success"
          class="mb-6 rounded-lg primary-alert"
          dismissible
          @input="successMessage = ''"
        >
          {{ successMessage }}
        </v-alert>

        <!-- Detalles del Evento -->
        <v-card
          v-if="evento && !editMode"
          elevation="4"
          class="mb-8 rounded-lg event-card"
        >
          <v-card-title class="text-h5 primary--text text-center py-4">
            {{ evento.nombre }}
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pa-6">
            <v-row>
              <v-col cols="12" sm="6">
                <p><strong>Descripción:</strong> {{ evento.descripcion }}</p>
                <p><strong>Fecha Inicio:</strong> {{ formatDate(evento.fecha_inicio) }}</p>
                <p><strong>Fecha Fin:</strong> {{ formatDate(evento.fecha_fin) }}</p>
              </v-col>
              <v-col cols="12" sm="6">
                <p><strong>Capacidad Máxima:</strong> {{ evento.capacidad_maxima }}</p>
                <p><strong>Estado:</strong> {{ evento.estado }}</p>
                <p v-if="capacidadDisponible !== null">
                  <strong>Capacidad Disponible:</strong> {{ capacidadDisponible }} plazas
                </p>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions class="event-actions">
            <v-btn
              color="primary"
              @click="registrarseEvento"
              :loading="loadingRegister"
              class="mx-2 primary-btn"
              prepend-icon="mdi-account-plus"
            >
              Registrarse
            </v-btn>
            <v-btn
              color="info"
              @click="validarCapacidad"
              :loading="loadingCapacity"
              class="mx-2 primary-btn"
              prepend-icon="mdi-information"
            >
              Ver Disponibilidad
            </v-btn>
            <v-btn
              color="warning"
              @click="editMode = true"
              class="mx-2 primary-btn"
              prepend-icon="mdi-pencil"
            >
              Editar
            </v-btn>
            <v-btn
              color="error"
              @click="showDeleteDialog = true"
              :loading="loadingDelete"
              class="mx-2 primary-btn"
              prepend-icon="mdi-delete"
            >
              Eliminar Evento
            </v-btn>
          </v-card-actions>
        </v-card>

        <!-- Formulario de Edición -->
        <v-form
          v-if="editMode"
          @submit.prevent="actualizarEvento"
          ref="formRef"
          class="mb-8 event-form-card"
          :disabled="loadingUpdate"
        >
          <v-card elevation="4" class="rounded-lg pa-6">
            <v-card-title class="text-h4 primary--text mb-6 text-center">
              Editar Evento
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model="form.nombre"
                    label="Nombre del Evento"
                    prepend-inner-icon="mdi-text-box"
                    variant="outlined"
                    required
                    :rules="nombreRules"
                    class="mb-4 primary-text-field"
                    dense
                    placeholder="Ej. Conferencia Tech 2025"
                    @input="logInput('nombre', $event)"
                  />
                  <v-textarea
                    v-model="form.descripcion"
                    label="Descripción"
                    prepend-inner-icon="mdi-text"
                    variant="outlined"
                    required
                    :rules="descripcionRules"
                    class="mb-4 primary-text-field"
                    rows="4"
                    dense
                    placeholder="Describe el propósito y contenido del evento"
                    @input="logInput('descripcion', $event)"
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-menu
                    v-model="menuFechaInicio"
                    :close-on-content-click="false"
                    transition="scale-transition"
                  >
                    <template v-slot:activator="{ props }">
                      <v-text-field
                        v-model="form.fecha_inicio"
                        label="Fecha y Hora de Inicio"
                        prepend-inner-icon="mdi-calendar-clock"
                        variant="outlined"
                        readonly
                        required
                        :rules="fechaInicioRules"
                        v-bind="props"
                        class="mb-4 primary-text-field"
                        dense
                        placeholder="Selecciona una fecha y hora"
                      />
                    </template>
                    <v-card class="elevation-2">
                      <v-card-text>
                        <v-date-picker
                          v-model="fechaInicioDate"
                          title="Fecha de Inicio"
                          color="primary"
                          hide-details
                          @update:modelValue="logDateTime('fechaInicioDate', $event)"
                        />
                        <v-text-field
                          v-model="fechaInicioTime"
                          label="Hora (HH:MM)"
                          prepend-inner-icon="mdi-clock"
                          variant="outlined"
                          :rules="[v => isValidTime(v) || 'Formato HH:MM inválido']"
                          placeholder="18:00"
                          class="mt-4 primary-text-field"
                          dense
                          @input="logDateTime('fechaInicioTime', $event)"
                        />
                      </v-card-text>
                      <v-card-actions>
                        <v-btn color="primary" class="primary-btn" @click="confirmFechaInicio">
                          Confirmar
                        </v-btn>
                        <v-btn
                          color="secondary"
                          class="secondary-btn"
                          @click="menuFechaInicio = false"
                        >
                          Cancelar
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-menu>
                  <v-menu
                    v-model="menuFechaFin"
                    :close-on-content-click="false"
                    transition="scale-transition"
                  >
                    <template v-slot:activator="{ props }">
                      <v-text-field
                        v-model="form.fecha_fin"
                        label="Fecha y Hora de Fin"
                        prepend-inner-icon="mdi-calendar-clock"
                        variant="outlined"
                        readonly
                        required
                        :rules="fechaFinRules"
                        v-bind="props"
                        class="mb-4 primary-text-field"
                        dense
                        placeholder="Selecciona una fecha y hora"
                      />
                    </template>
                    <v-card class="elevation-2">
                      <v-card-text>
                        <v-date-picker
                          v-model="fechaFinDate"
                          title="Fecha de Fin"
                          color="primary"
                          hide-details
                          @update:modelValue="logDateTime('fechaFinDate', $event)"
                        />
                        <v-text-field
                          v-model="fechaFinTime"
                          label="Hora (HH:MM)"
                          prepend-inner-icon="mdi-clock"
                          variant="outlined"
                          :rules="[v => isValidTime(v) || 'Formato HH:MM inválido']"
                          placeholder="22:00"
                          class="mt-4 primary-text-field"
                          dense
                          @input="logDateTime('fechaFinTime', $event)"
                        />
                      </v-card-text>
                      <v-card-actions>
                        <v-btn color="primary" class="primary-btn" @click="confirmFechaFin">
                          Confirmar
                        </v-btn>
                        <v-btn
                          color="secondary"
                          class="secondary-btn"
                          @click="menuFechaFin = false"
                        >
                          Cancelar
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-menu>
                  <v-text-field
                    v-model.number="form.capacidad_maxima"
                    label="Capacidad Máxima"
                    prepend-inner-icon="mdi-account-group"
                    variant="outlined"
                    type="number"
                    required
                    :rules="capacidadRules"
                    class="mb-4 primary-text-field"
                    dense
                    placeholder="Ej. 100"
                    @input="logInput('capacidad_maxima', $event)"
                  />
                  <v-select
                    v-model="form.estado"
                    label="Estado"
                    :items="['activo', 'inactivo']"
                    prepend-inner-icon="mdi-list-status"
                    variant="outlined"
                    required
                    :rules="estadoRules"
                    class="mb-4 primary-text-field"
                    dense
                    @input="logInput('estado', $event)"
                  />
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions class="justify-end">
              <v-btn
                type="submit"
                color="primary"
                :loading="loadingUpdate"
                class="mx-2 primary-btn"
                prepend-icon="mdi-content-save"
              >
                Actualizar Evento
              </v-btn>
              <v-btn
                color="secondary"
                @click="editMode = false"
                class="mx-2 secondary-btn"
                prepend-icon="mdi-cancel"
                :disabled="loadingUpdate"
              >
                Cancelar
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-form>

        <!-- Sesiones -->
        <h2 class="text-h5 text-center mb-6">Sesiones</h2>
        <v-progress-linear
          v-if="loadingSessions"
          indeterminate
          color="primary"
          class="mb-4"
        ></v-progress-linear>
        <v-row v-if="sesiones.length">
          <v-col
            v-for="sesion in sesiones"
            :key="sesion.id"
            cols="12"
            sm="6"
            md="4"
            class="mb-4"
          >
            <v-card elevation="4" class="rounded-lg session-card h-100">
              <v-card-title class="text-h6 primary--text text-center py-3">
                {{ sesion.nombre }}
              </v-card-title>
              <v-divider></v-divider>
              <v-card-text class="pa-4">
                <p><strong>Descripción:</strong> {{ sesion.descripcion }}</p>
                <p><strong>Fecha de Inicio:</strong> {{ formatDate(sesion.fecha_inicio) }}</p>
                <p><strong>Fecha de Fin:</strong> {{ formatDate(sesion.fecha_fin) }}</p>
                <p><strong>Capacidad Máxima:</strong> {{ sesion.capacidad_maxima }}</p>
                <p><strong>Asistentes Actuales:</strong> {{ sesion.asistentes_actuales }}</p>
                <p><strong>Capacidad Disponible:</strong> {{ sesion.capacidad_disponible }} plazas</p>
                <p><strong>Ponente:</strong> {{ sesion.ponente || 'No asignado' }}</p>
              </v-card-text>
              <v-card-actions class="pa-4 session-actions">
                <v-btn
                  color="primary"
                  @click="registrarAsistente(sesion.id)"
                  :loading="loadingRegisterSession"
                  :disabled="sesion.capacidad_disponible <= 0"
                  class="session-btn primary-btn"
                  prepend-icon="mdi-account-plus"
                >
                  Registrarme
                </v-btn>
                <v-btn
                  color="warning"
                  :to="{ name: 'SessionUpdate', params: { id: sesion.id } }"
                  :disabled="loadingSessions"
                  class="session-btn primary-btn"
                  prepend-icon="mdi-pencil"
                >
                  Editar
                </v-btn>
                <v-btn
                  color="error"
                  @click="openDeleteSessionDialog(sesion.id, sesion.nombre)"
                  :loading="loadingDeleteSession"
                  class="session-btn primary-btn"
                  prepend-icon="mdi-delete"
                >
                  Eliminar
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
        <v-alert
          v-else
          type="info"
          class="mb-6 rounded-lg primary-alert text-center"
        >
          No hay sesiones disponibles para este evento.
        </v-alert>

        <!-- Botón Volver -->
        <div class="text-center mt-6">
          <v-btn
            color="secondary"
            :to="{ name: 'Home' }"
            class="rounded-lg secondary-btn"
            prepend-icon="mdi-arrow-left"
          >
            Volver
          </v-btn>
        </div>

        <!-- Diálogo de confirmación para eliminar evento -->
        <v-dialog v-model="showDeleteDialog" max-width="500" persistent>
          <v-card class="rounded-lg">
            <v-card-title class="text-h6 primary--text pa-4">
              <v-icon color="error" class="mr-2">mdi-alert</v-icon>
              Confirmar Eliminación
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-4">
              ¿Estás seguro de que quieres eliminar el evento <strong>{{ evento?.nombre }}</strong>? Esta acción no se puede deshacer.
            </v-card-text>
            <v-card-actions class="justify-end pa-4">
              <v-btn
                color="secondary"
                text
                @click="showDeleteDialog = false"
                class="secondary-btn"
                prepend-icon="mdi-cancel"
              >
                Cancelar
              </v-btn>
              <v-btn
                color="error"
                :loading="loadingDelete"
                @click="eliminarEvento"
                class="primary-btn"
                prepend-icon="mdi-delete"
              >
                Eliminar
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Diálogo de confirmación para eliminar sesión -->
        <v-dialog v-model="showDeleteSessionDialog" max-width="500" persistent>
          <v-card class="rounded-lg">
            <v-card-title class="text-h6 primary--text pa-4">
              <v-icon color="error" class="mr-2">mdi-alert</v-icon>
              Confirmar Eliminación de Sesión
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pa-4">
              ¿Estás seguro de que quieres eliminar la sesión <strong>{{ sessionToDelete?.nombre }}</strong>? Esta acción no se puede deshacer.
            </v-card-text>
            <v-card-actions class="justify-end pa-4">
              <v-btn
                color="secondary"
                text
                @click="showDeleteSessionDialog = false"
                class="secondary-btn"
                prepend-icon="mdi-cancel"
              >
                Cancelar
              </v-btn>
              <v-btn
                color="error"
                :loading="loadingDeleteSession"
                @click="eliminarSesion"
                class="primary-btn"
                prepend-icon="mdi-delete"
              >
                Eliminar
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import api from '@/services/api';
import '@/assets/styles/EventDetail.css';

export default {
  name: 'EventDetailView',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();
    const evento = ref(null);
    const capacidadDisponible = ref(null);
    const sesiones = ref([]);
    const loading = ref(false);
    const loadingRegister = ref(false);
    const loadingCapacity = ref(false);
    const loadingDelete = ref(false);
    const loadingUpdate = ref(false);
    const loadingSessions = ref(false);
    const loadingRegisterSession = ref(false);
    const loadingDeleteSession = ref(false);
    const errorMessage = ref('');
    const successMessage = ref('');
    const editMode = ref(false);
    const showDeleteDialog = ref(false);
    const showDeleteSessionDialog = ref(false);
    const sessionToDelete = ref({ id: null, nombre: '' });
    const formRef = ref(null);
    const form = ref({
      nombre: '',
      descripcion: '',
      fecha_inicio: '',
      fecha_fin: '',
      capacidad_maxima: null,
      estado: '',
    });
    const menuFechaInicio = ref(false);
    const menuFechaFin = ref(false);
    const fechaInicioDate = ref(null);
    const fechaInicioTime = ref('00:00');
    const fechaFinDate = ref(null);
    const fechaFinTime = ref('00:00');

    // Reglas de validación
    const nombreRules = [(v) => !!v || 'El nombre es requerido'];
    const descripcionRules = [(v) => !!v || 'La descripción es requerida'];
    const fechaInicioRules = [
      (v) => !!v || 'La fecha de inicio es requerida',
      (v) => isValidDateTime(v) || 'Formato de fecha inválido',
    ];
    const fechaFinRules = [
      (v) => !!v || 'La fecha de fin es requerida',
      (v) => isValidDateTime(v) || 'Formato de fecha inválido',
    ];
    const capacidadRules = [
      (v) => v !== null && v !== '' || 'La capacidad es requerida',
      (v) => Number.isInteger(Number(v)) && v >= 0 || 'Debe ser un número entero no negativo',
    ];
    const estadoRules = [(v) => !!v || 'El estado es requerido'];

    const fetchEvento = async () => {
      if (!authStore.isAuthenticated()) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      loading.value = true;
      errorMessage.value = '';

      try {
        const response = await api.get(`/eventos/${route.params.id}`);
        evento.value = response.data;
        form.value = {
          nombre: response.data.nombre || '',
          descripcion: response.data.descripcion || '',
          fecha_inicio: response.data.fecha_inicio || '',
          fecha_fin: response.data.fecha_fin || '',
          capacidad_maxima: response.data.capacidad_maxima || null,
          estado: response.data.estado || 'activo',
        };
        initializeDatePickers();
      } catch (error) {
        handleError(error);
      } finally {
        loading.value = false;
      }
    };

    const fetchSesiones = async () => {
      if (!authStore.isAuthenticated()) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      loadingSessions.value = true;
      errorMessage.value = '';

      try {
        const response = await api.get('/sesiones/sesiones');
        sesiones.value = response.data.sesiones.filter(
          (s) => s.evento_id === parseInt(route.params.id)
        );
      } catch (error) {
        handleError(error);
      } finally {
        loadingSessions.value = false;
      }
    };

    const initializeDatePickers = () => {
      if (form.value.fecha_inicio) {
        try {
          const date = new Date(form.value.fecha_inicio);
          if (!isNaN(date.getTime())) {
            fechaInicioDate.value = date.toISOString().split('T')[0];
            fechaInicioTime.value = date.toTimeString().slice(0, 5);
          }
        } catch (error) {
          console.error('Error al inicializar fecha_inicio:', error);
        }
      }
      if (form.value.fecha_fin) {
        try {
          const date = new Date(form.value.fecha_fin);
          if (!isNaN(date.getTime())) {
            fechaFinDate.value = date.toISOString().split('T')[0];
            fechaFinTime.value = date.toTimeString().slice(0, 5);
          }
        } catch (error) {
          console.error('Error al inicializar fecha_fin:', error);
        }
      }
    };

    const logInput = (field, value) => {};

    const logDateTime = (field, value) => {
      console.log(`Campo ${field} actualizado a:`, value);
      console.log('Estado actual de fecha/hora:', {
        fechaInicioDate: fechaInicioDate.value,
        fechaInicioTime: fechaInicioTime.value,
        fechaFinDate: fechaFinDate.value,
        fechaFinTime: fechaFinTime.value,
      });
    };

    const isValidTime = (value) => {
      if (!value) return true;
      const regex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
      return regex.test(value);
    };

    const isValidDateTime = (value) => {
      if (!value) return true;
      const regex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/;
      if (!regex.test(value)) return false;
      const date = new Date(value);
      return !isNaN(date.getTime());
    };

    const confirmFechaInicio = () => {
      if (fechaInicioDate.value && isValidTime(fechaInicioTime.value)) {
        const date = new Date(fechaInicioDate.value);
        const [hours, minutes] = fechaInicioTime.value.split(':');
        date.setHours(parseInt(hours), parseInt(minutes), 0);
        form.value.fecha_inicio = date.toISOString().replace('T', ' ').slice(0, 19);
        logInput('fecha_inicio', form.value.fecha_inicio);
        menuFechaInicio.value = false;
      } else {
        errorMessage.value =
          'Por favor, selecciona una fecha y una hora de inicio válida (HH:MM)';
      }
    };

    const confirmFechaFin = () => {
      if (fechaFinDate.value && isValidTime(fechaFinTime.value)) {
        const date = new Date(fechaFinDate.value);
        const [hours, minutes] = fechaFinTime.value.split(':');
        date.setHours(parseInt(hours), parseInt(minutes), 0);
        form.value.fecha_fin = date.toISOString().replace('T', ' ').slice(0, 19);
        logInput('fecha_fin', form.value.fecha_fin);
        menuFechaFin.value = false;
      } else {
        errorMessage.value =
          'Por favor, selecciona una fecha y una hora de fin válida (HH:MM)';
      }
    };

    const registrarseEvento = async () => {
      if (!authStore.isAuthenticated()) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      loadingRegister.value = true;
      errorMessage.value = '';
      successMessage.value = '';

      try {
        const response = await api.post(`/eventos/${route.params.id}/registrarse`);
        successMessage.value = response.data.message || 'Te has registrado exitosamente';
      } catch (error) {
        handleError(error);
      } finally {
        loadingRegister.value = false;
      }
    };

    const validarCapacidad = async () => {
      if (!authStore.isAuthenticated()) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      loadingCapacity.value = true;
      errorMessage.value = '';

      try {
        const response = await api.get(`/eventos/${route.params.id}/validar-capacidad`);
        capacidadDisponible.value = response.data.capacidad_disponible;
      } catch (error) {
        handleError(error);
      } finally {
        loadingCapacity.value = false;
      }
    };

    const registrarAsistente = async (sesionId) => {
      if (!authStore.isAuthenticated() || !authStore.user?.id) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      loadingRegisterSession.value = true;
      errorMessage.value = '';
      successMessage.value = '';

      try {
        const payload = { usuario_id: authStore.user.id };
        const response = await api.post(`/sesiones/registrar_asistente/${sesionId}`, payload);
        successMessage.value =
          response.data.message || 'Te has registrado exitosamente en la sesión';
        await fetchSesiones();
      } catch (error) {
        handleError(error);
      } finally {
        loadingRegisterSession.value = false;
      }
    };

    const openDeleteSessionDialog = (id, nombre) => {
      sessionToDelete.value = { id, nombre };
      showDeleteSessionDialog.value = true;
    };

    const eliminarSesion = async () => {
      if (!authStore.isAuthenticated()) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      loadingDeleteSession.value = true;
      errorMessage.value = '';
      successMessage.value = '';

      try {
        const response = await api.delete(`/sesiones/eliminar/${sessionToDelete.value.id}`);
        successMessage.value = response.data.message || 'Sesión eliminada exitosamente';
        showDeleteSessionDialog.value = false;
        sessionToDelete.value = { id: null, nombre: '' };
        await fetchSesiones();
      } catch (error) {
        handleError(error);
      } finally {
        loadingDeleteSession.value = false;
      }
    };

    const eliminarEvento = async () => {
      if (!authStore.isAuthenticated()) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      loadingDelete.value = true;
      errorMessage.value = '';

      try {
        const response = await api.delete(`/eventos/${route.params.id}/eliminar`);
        successMessage.value = response.data.message || 'Evento eliminado exitosamente';
        showDeleteDialog.value = false;
        setTimeout(() => router.push({ name: 'Home' }), 2000);
      } catch (error) {
        handleError(error);
      } finally {
        loadingDelete.value = false;
      }
    };

    const actualizarEvento = async () => {
      if (!authStore.isAuthenticated()) {
        errorMessage.value = 'Por favor, inicia sesión';
        router.push('/login');
        return;
      }

      if (!formRef.value) {
        errorMessage.value = 'Formulario no inicializado';
        return;
      }

      const { valid } = await formRef.value.validate();
      if (!valid) {
        errorMessage.value = 'Por favor, corrige los errores en el formulario';
        return;
      }

      loadingUpdate.value = true;
      errorMessage.value = '';
      successMessage.value = '';

      try {
        const fechaInicio = new Date(form.value.fecha_inicio);
        const fechaFin = new Date(form.value.fecha_fin);
        if (fechaFin <= fechaInicio) {
          errorMessage.value = 'La fecha de fin debe ser posterior a la fecha de inicio';
          return;
        }
        const response = await api.put(`/eventos/${route.params.id}/actualizar`, form.value);
        successMessage.value = response.data.message || 'Evento actualizado exitosamente';
        evento.value = { ...form.value };
        editMode.value = false;
      } catch (error) {
        handleError(error);
      } finally {
        loadingUpdate.value = false;
      }
    };

    const handleError = (error) => {
      if (error.response) {
        const { status, data } = error.response;
        if (status === 401) {
          errorMessage.value = 'Sesión expirada. Por favor, inicia sesión de nuevo';
          authStore.logout();
          router.push('/login');
        } else if (status === 404) {
          errorMessage.value = data.message || 'Recurso no encontrado';
        } else if (status === 400) {
          errorMessage.value = data.errors
            ? JSON.stringify(data.errors)
            : data.message || 'Datos inválidos';
        } else {
          errorMessage.value = data.message || 'Error en la operación';
        }
      } else {
        errorMessage.value = `Error de conexión: ${error.message}`;
        console.error('Detalles del error:', error);
      }
    };

    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleString('es-ES', {
        dateStyle: 'medium',
        timeStyle: 'short',
      });
    };

    watch(form, (newValue) => {}, { deep: true });

    onMounted(() => {
      fetchEvento();
      fetchSesiones();
    });

    return {
      evento,
      capacidadDisponible,
      sesiones,
      loading,
      loadingRegister,
      loadingCapacity,
      loadingDelete,
      loadingUpdate,
      loadingSessions,
      loadingRegisterSession,
      loadingDeleteSession,
      errorMessage,
      successMessage,
      editMode,
      showDeleteDialog,
      showDeleteSessionDialog,
      sessionToDelete,
      form,
      formRef,
      menuFechaInicio,
      menuFechaFin,
      fechaInicioDate,
      fechaInicioTime,
      fechaFinDate,
      fechaFinTime,
      registrarseEvento,
      validarCapacidad,
      registrarAsistente,
      openDeleteSessionDialog,
      eliminarSesion,
      eliminarEvento,
      actualizarEvento,
      formatDate,
      isValidTime,
      isValidDateTime,
      confirmFechaInicio,
      confirmFechaFin,
      logInput,
      logDateTime,
      nombreRules,
      descripcionRules,
      fechaInicioRules,
      fechaFinRules,
      capacidadRules,
      estadoRules,
    };
  },
};
</script>