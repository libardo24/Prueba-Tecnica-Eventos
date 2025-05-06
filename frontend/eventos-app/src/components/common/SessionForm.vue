<template>
    <div class="session-form-view">
      <v-container fluid class="fill-height session-form-container">
        <v-row justify="center">
          <v-col cols="12" md="8" lg="6">
            <v-card class="elevation-4 session-form-card">
              <v-card-title class="text-h4 primary--text mb-6">
                {{ isUpdateMode ? 'Actualizar Sesión' : 'Crear Sesión' }}
              </v-card-title>
              <v-card-text>
                <v-alert
                  v-if="errorMessage"
                  type="error"
                  class="mb-6 primary-alert"
                  dismissible
                  @input="errorMessage = ''"
                >
                  {{ errorMessage }}
                </v-alert>
                <v-alert
                  v-if="successMessage"
                  type="success"
                  class="mb-6 primary-alert"
                  dismissible
                  @input="successMessage = ''"
                >
                  {{ successMessage }}
                </v-alert>
                <v-form @submit.prevent="submitForm" ref="formRef" :disabled="loading">
                  <v-autocomplete
                    v-model="form.evento_id"
                    :items="eventos"
                    :loading="eventsLoading"
                    item-title="nombre"
                    item-value="id"
                    label="Evento"
                    prepend-inner-icon="mdi-calendar-check"
                    variant="outlined"
                    required
                    :rules="eventoRules"
                    class="mb-4 primary-text-field"
                    dense
                    :search="eventSearch"
                    placeholder="Buscar un evento..."
                    no-data-text="No se encontraron eventos"
                    @update:search="debouncedSearchEvents"
                  >
                    <template v-slot:item="{ item, props }">
                      <v-list-item v-bind="props" :subtitle="formatDate(item.raw.fecha_inicio)" />
                    </template>
                  </v-autocomplete>
                  <v-text-field
                    v-model="form.nombre"
                    label="Nombre de la Sesión"
                    prepend-inner-icon="mdi-text-box"
                    variant="outlined"
                    required
                    :rules="nombreRules"
                    class="mb-4 primary-text-field"
                    dense
                    placeholder="Ej. Taller de Programación"
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
                    placeholder="Describe el propósito y contenido de la sesión"
                  />
                  <v-row>
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
                            class="primary-text-field"
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
                            />
                            <v-text-field
                              v-model="fechaInicioTime"
                              label="Hora (HH:MM)"
                              prepend-inner-icon="mdi-clock"
                              variant="outlined"
                              :rules="[v => isValidTime(v) || 'Formato HH:MM inválido']"
                              placeholder="10:00"
                              class="mt-4 primary-text-field"
                              dense
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
                    </v-col>
                    <v-col cols="12" sm="6">
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
                            class="primary-text-field"
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
                            />
                            <v-text-field
                              v-model="fechaFinTime"
                              label="Hora (HH:MM)"
                              prepend-inner-icon="mdi-clock"
                              variant="outlined"
                              :rules="[v => isValidTime(v) || 'Formato HH:MM inválido']"
                              placeholder="12:00"
                              class="mt-4 primary-text-field"
                              dense
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
                    </v-col>
                  </v-row>
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
                    placeholder="Ej. 50"
                  />
                  <v-text-field
                    v-model="form.ponente"
                    label="Ponente"
                    prepend-inner-icon="mdi-account"
                    variant="outlined"
                    required
                    :rules="ponenteRules"
                    class="mb-6 primary-text-field"
                    dense
                    placeholder="Ej. Juan Pérez"
                  />
                  <div class="text-right">
                    <v-btn
                      type="submit"
                      color="primary"
                      class="primary-btn mr-2"
                      :loading="loading"
                    >
                      {{ isUpdateMode ? 'Actualizar Sesión' : 'Crear Sesión' }}
                    </v-btn>
                    <v-btn
                      color="secondary"
                      class="secondary-btn mr-2"
                      :to="cancelRoute"
                      :disabled="loading"
                    >
                      Cancelar
                    </v-btn>
                    <v-btn
                      v-if="isUpdateMode"
                      color="warning"
                      class="warning-btn"
                      @click="asignarPonente"
                      :loading="loadingPonente"
                      :disabled="loading || !form.ponente"
                    >
                      Asignar Ponente
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </template>
  
  <script>
  import { ref, computed, onMounted } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { useAuthStore } from '@/stores/auth';
  import { debounce } from 'lodash';
  import api from '@/services/api';
  
  export default {
    name: 'SessionForm',
    props: {
      sessionId: {
        type: [String, Number],
        default: null,
      },
    },
    setup(props) {
      const router = useRouter();
      const route = useRoute();
      const authStore = useAuthStore();
      const form = ref({
        evento_id: null,
        nombre: '',
        descripcion: '',
        fecha_inicio: '',
        fecha_fin: '',
        capacidad_maxima: 0,
        ponente: '',
      });
      const eventos = ref([]);
      const eventsLoading = ref(false);
      const eventSearch = ref('');
      const loading = ref(false);
      const loadingPonente = ref(false);
      const errorMessage = ref('');
      const successMessage = ref('');
      const formRef = ref(null);
      const menuFechaInicio = ref(false);
      const menuFechaFin = ref(false);
      const fechaInicioDate = ref(null);
      const fechaInicioTime = ref('');
      const fechaFinDate = ref(null);
      const fechaFinTime = ref('');
  
      const isUpdateMode = computed(() => !!props.sessionId);
  
      const cancelRoute = computed(() => {
        return isUpdateMode.value && form.value.evento_id
          ? { name: 'EventDetail', params: { id: form.value.evento_id } }
          : { name: 'Home' };
      });
  
      const eventoRules = [v => !!v || 'El evento es requerido'];
      const nombreRules = [v => !!v || 'El nombre es requerido'];
      const descripcionRules = [v => !!v || 'La descripción es requerida'];
      const fechaInicioRules = [
        v => !!v || 'La fecha de inicio es requerida',
        v => isValidDateTime(v) || 'Formato de fecha inválido (YYYY-MM-DDTHH:MM:SS)',
      ];
      const fechaFinRules = [
        v => !!v || 'La fecha de fin es requerida',
        v => isValidDateTime(v) || 'Formato de fecha inválido (YYYY-MM-DDTHH:MM:SS)',
      ];
      const capacidadRules = [
        v => v !== null && v !== '' || 'La capacidad es requerida',
        v => Number.isInteger(Number(v)) && v >= 0 || 'Debe ser un número entero no negativo',
      ];
      const ponenteRules = [v => !!v || 'El ponente es requerido'];
  
      const searchEvents = async (query = '') => {
        eventsLoading.value = true;
        try {
          const response = await api.get('/eventos/buscar', {
            params: { nombre: query },
          });
          eventos.value = response.data?.map(event => ({
            id: event.id,
            nombre: event.nombre,
            fecha_inicio: event.fecha_inicio,
          })) || [];
        } catch (error) {
          errorMessage.value = 'No se pudieron cargar los eventos';
        } finally {
          eventsLoading.value = false;
        }
      };
  
      const debouncedSearchEvents = debounce(query => {
        eventSearch.value = query;
        searchEvents(query);
      }, 300);
  
      const formatDate = dateString => {
        try {
          const date = new Date(dateString);
          if (isNaN(date.getTime())) throw new Error('Fecha inválida');
          return date.toLocaleString('es-ES', {
            dateStyle: 'medium',
            timeStyle: 'short',
          });
        } catch (error) {
          return 'Fecha inválida';
        }
      };
  
      const loadSession = async () => {
        if (!isUpdateMode.value) return;
        try {
          loading.value = true;
          const response = await api.get(`/sesiones/sesiones`);
          const sesion = response.data.sesiones.find(s => s.id === parseInt(props.sessionId));
          if (!sesion) {
            errorMessage.value = 'Sesión no encontrada';
            return;
          }
          form.value = {
            evento_id: sesion.evento_id,
            nombre: sesion.nombre,
            descripcion: sesion.descripcion,
            fecha_inicio: sesion.fecha_inicio,
            fecha_fin: sesion.fecha_fin,
            capacidad_maxima: sesion.capacidad_maxima,
            ponente: sesion.ponente,
          };
          const inicio = new Date(sesion.fecha_inicio);
          const fin = new Date(sesion.fecha_fin);
          fechaInicioDate.value = inicio.toISOString().split('T')[0];
          fechaInicioTime.value = inicio.toTimeString().slice(0, 5);
          fechaFinDate.value = fin.toISOString().split('T')[0];
          fechaFinTime.value = fin.toTimeString().slice(0, 5);
        } catch (error) {
          handleError(error);
        } finally {
          loading.value = false;
        }
      };
  
      const isValidTime = value => {
        if (!value) return true;
        const regex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
        return regex.test(value);
      };
  
      const isValidDateTime = value => {
        if (!value) return true;
        const regex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/;
        if (!regex.test(value)) return false;
        const date = new Date(value);
        return !isNaN(date.getTime());
      };
  
      const confirmFechaInicio = () => {
        if (fechaInicioDate.value && isValidTime(fechaInicioTime.value)) {
          const date = new Date(fechaInicioDate.value);
          const [hours, minutes] = fechaInicioTime.value.split(':');
          date.setHours(parseInt(hours), parseInt(minutes), 0);
          form.value.fecha_inicio = date.toISOString().slice(0, 19);
          menuFechaInicio.value = false;
        } else {
          errorMessage.value = 'Por favor, selecciona una fecha y hora de inicio válidas (HH:MM)';
        }
      };
  
      const confirmFechaFin = () => {
        if (fechaFinDate.value && isValidTime(fechaFinTime.value)) {
          const date = new Date(fechaFinDate.value);
          const [hours, minutes] = fechaFinTime.value.split(':');
          date.setHours(parseInt(hours), parseInt(minutes), 0);
          form.value.fecha_fin = date.toISOString().slice(0, 19);
          menuFechaFin.value = false;
        } else {
          errorMessage.value = 'Por favor, selecciona una fecha y hora de fin válidas (HH:MM)';
        }
      };
  
      const submitForm = async () => {
        if (!authStore.token) {
          errorMessage.value = 'Por favor, inicia sesión';
          router.push('/login');
          return;
        }
        try {
          const valid = await validateForm();
          if (!valid) {
            errorMessage.value = 'Por favor, corrige los errores en el formulario';
            return;
          }
          if (!eventos.value.find(e => e.id === form.value.evento_id)) {
            errorMessage.value = 'Por favor, selecciona un evento válido';
            return;
          }
          const fechaInicio = new Date(form.value.fecha_inicio);
          const fechaFin = new Date(form.value.fecha_fin);
          if (fechaFin <= fechaInicio) {
            errorMessage.value = 'La fecha de fin debe ser posterior a la fecha de inicio';
            return;
          }
          loading.value = true;
          const payload = {
            evento_id: form.value.evento_id,
            nombre: form.value.nombre,
            descripcion: form.value.descripcion,
            fecha_inicio: form.value.fecha_inicio,
            fecha_fin: form.value.fecha_fin,
            capacidad_maxima: parseInt(form.value.capacidad_maxima),
            ponente: form.value.ponente,
          };
          let response;
          if (isUpdateMode.value) {
            response = await api.put(`/sesiones/actualizar/${props.sessionId}`, payload);
            successMessage.value = response.data.message || 'Sesión actualizada exitosamente';
            setTimeout(() => router.push({ name: 'EventDetail', params: { id: form.value.evento_id } }), 2000);
          } else {
            response = await api.post('/sesiones/crear', payload);
            successMessage.value = response.data.message || 'Sesión creada exitosamente';
            setTimeout(() => router.push({ name: 'Home' }), 2000);
          }
        } catch (error) {
          handleError(error);
        } finally {
          loading.value = false;
        }
      };
  
      const asignarPonente = async () => {
        if (!authStore.token) {
          errorMessage.value = 'Por favor, inicia sesión';
          router.push('/login');
          return;
        }
        try {
          loadingPonente.value = true;
          const payload = { ponente: form.value.ponente };
          const response = await api.put(`/sesiones/asignar_ponente/${props.sessionId}`, payload);
          successMessage.value = response.data.message || 'Ponente asignado exitosamente';
        } catch (error) {
          handleError(error);
        } finally {
          loadingPonente.value = false;
        }
      };
  
      const validateForm = async () => {
        if (!formRef.value) {
          console.error('formRef no está definido');
          return false;
        }
        try {
          const { valid } = await formRef.value.validate();
          return valid;
        } catch (error) {
          console.error('Error durante la validación:', error);
          return false;
        }
      };
  
      const handleError = error => {
        if (error.response) {
          const { status, data } = error.response;
          const messages = {
            400: data.errors ? Object.values(data.errors).flat().join(', ') : data.message || 'Datos inválidos',
            401: 'Sesión expirada. Por favor, inicia sesión de nuevo',
            404: data.message || (isUpdateMode.value ? 'Sesión no encontrada' : 'Evento no encontrado'),
            500: 'Error del servidor. Intenta de nuevo más tarde',
          };
          errorMessage.value = messages[status] || `No se pudo ${isUpdateMode.value ? 'actualizar' : 'crear'} la sesión`;
          if (status === 401) {
            authStore.logout();
            router.push('/login');
          }
        } else {
          errorMessage.value = `Error de red: ${error.message}`;
        }
      };
  
      onMounted(() => {
        searchEvents();
        loadSession();
      });
  
      return {
        form,
        eventos,
        eventsLoading,
        eventSearch,
        loading,
        loadingPonente,
        errorMessage,
        successMessage,
        formRef,
        menuFechaInicio,
        menuFechaFin,
        fechaInicioDate,
        fechaInicioTime,
        fechaFinDate,
        fechaFinTime,
        isUpdateMode,
        cancelRoute,
        submitForm,
        asignarPonente,
        isValidTime,
        isValidDateTime,
        eventoRules,
        nombreRules,
        descripcionRules,
        fechaInicioRules,
        fechaFinRules,
        capacidadRules,
        ponenteRules,
        formatDate,
        confirmFechaInicio,
        confirmFechaFin,
        debouncedSearchEvents,
      };
    },
  };
  </script>
  
  <style scoped>
  @import '@/assets/styles/SessionForm.css';
  </style>