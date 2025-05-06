<template>
    <v-form @submit.prevent="handleSubmit" v-model="isValid">
      <v-text-field
        v-model="form.nombre"
        label="Nombre de la Sesión"
        :rules="[v => !!v || 'El nombre es requerido']"
        required
      ></v-text-field>
  
      <v-textarea
        v-model="form.descripcion"
        label="Descripción"
        :rules="[v => !!v || 'La descripción es requerida']"
        required
      ></v-textarea>
  
      <v-select
        v-model="form.evento_id"
        :items="eventos"
        item-title="nombre"
        item-value="id"
        label="Evento"
        :rules="[v => !!v || 'Selecciona un evento']"
        required
      ></v-select>
  
      <v-text-field
        v-model="form.fecha_inicio"
        label="Fecha de Inicio (YYYY-MM-DD HH:MM:SS)"
        :rules="[v => !!v || 'La fecha de inicio es requerida', validateDateFormat]"
        required
      ></v-text-field>
  
      <v-text-field
        v-model="form.fecha_fin"
        label="Fecha de Fin (YYYY-MM-DD HH:MM:SS)"
        :rules="[v => !!v || 'La fecha de fin es requerida', validateDateFormat]"
        required
      ></v-text-field>
  
      <v-text-field
        v-model.number="form.capacidad_maxima"
        label="Capacidad Máxima"
        type="number"
        :rules="[v => v > 0 || 'La capacidad debe ser mayor a 0']"
        required
      ></v-text-field>
  
      <v-text-field
        v-model="form.ponente"
        label="Ponente"
        :rules="[v => !!v || 'El ponente es requerido']"
        required
      ></v-text-field>
  
      <v-btn
        type="submit"
        color="primary"
        :disabled="!isValid || loading"
        :loading="loading"
      >
        Crear Sesión
      </v-btn>
  
      <v-alert
        v-if="errorMessage"
        type="error"
        class="mt-4"
      >
        {{ errorMessage }}
      </v-alert>
  
      <v-alert
        v-if="successMessage"
        type="success"
        class="mt-4"
      >
        {{ successMessage }}
      </v-alert>
    </v-form>
  </template>
  
  <script>
  import { ref } from 'vue';
  import { createSession } from '../../services/api';
  import { useEventsStore } from '../../stores/events';
  
  export default {
    name: 'FormularioSesion',
    props: {
      eventos: {
        type: Array,
        default: () => [],
      },
    },
    setup(props, { emit }) {
      const eventsStore = useEventsStore();
      const isValid = ref(false);
      const loading = ref(false);
      const errorMessage = ref('');
      const successMessage = ref('');
      const form = ref({
        evento_id: null,
        nombre: '',
        descripcion: '',
        fecha_inicio: '',
        fecha_fin: '',
        capacidad_maxima: 0,
        ponente: '',
      });
  
      const validateDateFormat = (value) => {
        const regex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/;
        return regex.test(value) || 'Formato de fecha inválido (YYYY-MM-DD HH:MM:SS)';
      };
  
      const handleSubmit = async () => {
        loading.value = true;
        errorMessage.value = '';
        successMessage.value = '';
  
        const response = await createSession(form.value);
  
        if (response.success) {
          successMessage.value = response.data.message || 'Sesión creada exitosamente';
          emit('session-created');
          form.value = {
            evento_id: null,
            nombre: '',
            descripcion: '',
            fecha_inicio: '',
            fecha_fin: '',
            capacidad_maxima: 0,
            ponente: '',
          };
        } else {
          errorMessage.value = response.message;
        }
  
        loading.value = false;
      };
  
      return {
        form,
        isValid,
        loading,
        errorMessage,
        successMessage,
        validateDateFormat,
        handleSubmit,
      };
    },
  };
  </script>
  
  <style scoped>
  .v-form {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }
  </style>