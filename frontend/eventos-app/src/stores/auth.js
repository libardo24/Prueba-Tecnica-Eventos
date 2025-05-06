import { defineStore } from 'pinia';
import api from '../services/api';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(null);
  const user = ref(null);

  // Restaurar token y usuario desde localStorage al inicializar
  const initializeAuth = () => {
    const savedToken = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('auth_user');
    if (savedToken) {
      token.value = savedToken;
    }
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser);
      } catch (error) {
        console.error('Error al parsear auth_user:', error);
        localStorage.removeItem('auth_user');
      }
    }

  };

  // Iniciar sesión
  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      token.value = response.data.token;
      user.value = response.data.user;
      // Guardar en localStorage
      localStorage.setItem('auth_token', token.value);
      localStorage.setItem('auth_user', JSON.stringify(user.value));

      return { success: true };
    } catch (error) {
      console.error('Error en login:', error);
      if (error.response) {
        const { status, data } = error.response;
        return { success: false, message: data.message || 'Error al iniciar sesión' };
      }
      return { success: false, message: error.message || 'Error de conexión' };
    }
  };

  // Cerrar sesión
  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  };

  // Verificar si el usuario está autenticado
  const isAuthenticated = () => !!token.value;

  // Inicializar auth al crear el store
  initializeAuth();

  return {
    token,
    user,
    login,
    logout,
    isAuthenticated,
  };
});