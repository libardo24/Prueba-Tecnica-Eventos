<template>
  <div class="app-bar">
    <v-app-bar app color="primary" elevation="2">
      <v-btn
        v-if="isAuthenticated"
        icon
        @click="drawer = !drawer"
        class="nav-icon-btn"
      >
        <v-icon color="white">mdi-menu</v-icon>
      </v-btn>
      <v-toolbar-title>Gestión de Eventos</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="isAuthenticated" to="/" text class="authenticated-btn">Inicio</v-btn>
      <v-btn v-if="isAuthenticated" to="/event/create" text class="authenticated-btn">Crear Evento</v-btn>
      <v-btn v-if="isAuthenticated" to="/session/create" text class="authenticated-btn">Crear Sesión</v-btn>
      <v-btn v-if="isAuthenticated" to="/profile" text class="authenticated-btn">Perfil</v-btn>
      <v-btn v-if="isAuthenticated" @click="logout" text class="authenticated-btn">Logout</v-btn>
      <v-btn v-if="!isAuthenticated" to="/login" class="authenticated-btn">Login</v-btn>
      <v-btn v-if="!isAuthenticated" to="/register" class="authenticated-btn">Registrarse</v-btn>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" app temporary v-if="isAuthenticated" class="nav-drawer">
      <v-list>
        <v-list-item to="/" title="Inicio" class="nav-item"></v-list-item>
        <v-list-item to="/event/create" title="Crear Evento" class="nav-item"></v-list-item>
        <v-list-item to="/session/create" title="Crear Sesión" class="nav-item"></v-list-item>
        <v-list-item to="/profile" title="Perfil" class="nav-item"></v-list-item>
        <v-list-item @click="logout" title="Cerrar Sesión" class="nav-item"></v-list-item>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import '../assets/styles/AppBar.css';

export default {
  name: 'AppBar',
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    const drawer = ref(false);

    const isAuthenticated = computed(() => !!authStore.token);

    const logout = () => {
      authStore.logout();
      router.push('/login');
    };

    return {
      drawer,
      isAuthenticated,
      logout,
    };
  },
};
</script>

<style scoped>
.nav-icon-btn {
  margin-right: 16px;
}
.nav-icon-btn .v-icon {
  color: var(--text-light) !important;
}
</style>