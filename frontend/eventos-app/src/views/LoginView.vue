<template>
  <div class="login-view">
    <v-container fluid class="fill-height login-container">
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card class="login-card elevation-12" rounded="lg">
            <v-card-title class="text-center py-6">
              <h2 class="text-h4 font-weight-bold primary--text">Iniciar Sesión</h2>
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
              <v-form @submit.prevent="handleLogin" ref="formRef" :disabled="loading">
                <v-text-field
                  v-model="form.email"
                  label="Correo Electrónico"
                  type="email"
                  prepend-inner-icon="mdi-email"
                  variant="outlined"
                  required
                  :rules="emailRules"
                  class="mb-4 primary-text-field"
                  dense
                />
                <v-text-field
                  v-model="form.password"
                  label="Contraseña"
                  :type="showPassword ? 'text' : 'password'"
                  prepend-inner-icon="mdi-lock"
                  :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  variant="outlined"
                  required
                  :rules="passwordRules"
                  @click:append-inner="showPassword = !showPassword"
                  class="mb-4 primary-text-field"
                  dense
                />
                <v-btn
                  type="submit"
                  color="primary"
                  block
                  large
                  :loading="loading"
                  class="login-btn primary-btn"
                >
                  Iniciar Sesión
                </v-btn>
              </v-form>
              <v-row class="mt-4">
                <v-col class="text-center">
                  <v-btn text color="primary" :to="{ name: 'Register' }" class="secondary-btn">
                    ¿No tienes cuenta? Regístrate
                  </v-btn>
                </v-col>
              </v-row>
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
import { useAuthStore } from '../stores/auth';

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const form = ref({
      email: '',
      password: '',
    });
    const loading = ref(false);
    const errorMessage = ref('');
    const formRef = ref(null);
    const showPassword = ref(false);

    const emailRules = [
      (v) => !!v || 'El correo es requerido',
      (v) => /.+@.+\..+/.test(v) || 'El correo debe ser válido',
    ];
    const passwordRules = [(v) => !!v || 'La contraseña es requerida'];

    const handleLogin = async () => {
      errorMessage.value = '';
      if (!formRef.value) {
        errorMessage.value = 'Formulario no inicializado';
        return;
      }

      const { valid } = await formRef.value.validate();
      if (!valid) {
        errorMessage.value = 'Por favor, corrige los errores en el formulario';
        return;
      }

      loading.value = true;
      const result = await authStore.login(form.value.email, form.value.password);
      loading.value = false;

      if (result.success) {
        router.push({ name: 'Home' });
      } else {
        errorMessage.value = result.message;
      }
    };

    return {
      form,
      loading,
      errorMessage,
      formRef,
      showPassword,
      emailRules,
      passwordRules,
      handleLogin,
    };
  },
};
</script>

<style scoped>
@import '@/assets/styles/LoginView.css';
</style>