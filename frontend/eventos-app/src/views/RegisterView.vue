<template>
  <div class="register-view">
    <v-container fluid class="fill-height register-container">
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card class="register-card elevation-12" rounded="lg">
            <v-card-title class="text-center py-6">
              <h2 class="text-h4 font-weight-bold primary--text">Registrarse</h2>
            </v-card-title>
            <v-card-text>
              <v-alert
                v-if="errorMessage"
                type="error"
                class="mb-4 primary-alert"
                dismissible
                @input="errorMessage = ''"
              >
                {{ errorMessage }}
              </v-alert>
              <v-alert
                v-if="successMessage"
                type="success"
                class="mb-4 primary-alert"
                dismissible
                @input="successMessage = ''"
              >
                {{ successMessage }}
              </v-alert>
              <v-form @submit.prevent="handleRegister" ref="formRef" :disabled="loading">
                <v-text-field
                  label="Correo Electrónico"
                  type="email"
                  v-model="form.email"
                  :error-messages="errors.email"
                  :rules="emailRules"
                  prepend-inner-icon="mdi-email"
                  variant="outlined"
                  clearable
                  class="primary-text-field mb-4"
                  dense
                  :disabled="loading"
                />
                <v-text-field
                  label="Contraseña"
                  type="password"
                  v-model="form.password"
                  :error-messages="errors.password"
                  :rules="passwordRules"
                  prepend-inner-icon="mdi-lock"
                  variant="outlined"
                  clearable
                  class="primary-text-field mb-4"
                  dense
                  :disabled="loading"
                />
                <v-btn
                  type="submit"
                  color="primary"
                  block
                  large
                  :loading="loading"
                  :disabled="loading"
                  class="primary-btn mt-4"
                >
                  Registrarse
                </v-btn>
              </v-form>
              <p class="text-center mt-4">
                ¿Ya tienes cuenta?
                <router-link to="/login" class="secondary-btn text-decoration-none">
                  Inicia sesión
                </router-link>
              </p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

export default {
  name: 'RegisterView',
  setup() {
    const router = useRouter();
    const form = ref({
      email: '',
      password: '',
    });
    const errors = ref({
      email: '',
      password: '',
    });
    const errorMessage = ref('');
    const successMessage = ref('');
    const loading = ref(false);
    const formRef = ref(null);

    const emailRules = [
      (v) => !!v || 'El correo es requerido',
      (v) => /.+@.+\..+/.test(v) || 'El correo debe ser válido',
    ];
    const passwordRules = [
      (v) => !!v || 'La contraseña es requerida',
      (v) => v.length >= 6 || 'La contraseña debe tener al menos 6 caracteres',
    ];

    const handleRegister = async () => {
      if (loading.value) return; // Evitar envíos múltiples
      loading.value = true;
      errors.value = { email: '', password: '' };
      errorMessage.value = '';
      successMessage.value = '';

      try {
        if (!formRef.value) {
          errorMessage.value = 'Formulario no inicializado';
          return;
        }

        const { valid } = await formRef.value.validate();
        if (!valid) {
          errorMessage.value = 'Por favor, corrige los errores en el formulario';
          return;
        }

        await api.post('/auth/register', form.value);
        successMessage.value = 'Usuario registrado exitosamente. Por favor, inicia sesión.';
        form.value = { email: '', password: '' };
        formRef.value.resetValidation(); // Reiniciar validaciones
        setTimeout(() => {
          router.push('/login');
        }, 2000);
      } catch (error) {
        if (error.response) {
          const { status, data } = error.response;
          if (status === 400 && data.errors) {
            Object.keys(data.errors).forEach((key) => {
              errors.value[key] = data.errors[key][0];
            });
          } else if (status === 400 && data.message) {
            errorMessage.value = 'El correo ya está registrado';
          } else {
            errorMessage.value = `Error al registrarse: ${data.message || 'Desconocido'}`;
          }
        } else {
          errorMessage.value = `Error de conexión: ${error.message}`;
        }
      } finally {
        loading.value = false;
      }
    };

    return {
      form,
      errors,
      errorMessage,
      successMessage,
      loading,
      handleRegister,
      formRef,
      emailRules,
      passwordRules,
    };
  },
};
</script>

<style scoped>
@import '@/assets/styles/RegisterView.css';
</style>