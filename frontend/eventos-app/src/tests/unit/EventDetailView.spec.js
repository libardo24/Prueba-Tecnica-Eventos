// src/tests/unit/EventDetailView.spec.js
import { mount, flushPromises } from '@vue/test-utils';
import { createRouter, createWebHistory } from 'vue-router';
import { createPinia, setActivePinia } from 'pinia';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import EventDetailView from '@/views/EventDetailView.vue';
import { vi } from 'vitest';
import * as api from '@/services/api';
import { useAuthStore } from '@/stores/auth';

// Crear instancia de Vuetify
const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
  },
});

// Mock del router y route
const mockRouter = {
  push: vi.fn(),
};
const mockRoute = {
  params: { id: '1' },
};

// Mock de vue-router
vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  useRoute: () => mockRoute,
  createRouter: vi.fn().mockReturnValue({
    push: vi.fn(),
    isReady: vi.fn().mockResolvedValue(),
  }),
  createWebHistory: vi.fn(),
}));

// Mock de api.get, api.post, api.put, api.delete
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

// Configura el router para pruebas
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Home', component: { template: '<div>Home</div>' } },
    { path: '/login', name: 'Login', component: { template: '<div>Login</div>' } },
    { path: '/sesiones/:id/editar', name: 'SessionUpdate', component: { template: '<div>SessionUpdate</div>' } },
  ],
});

describe('EventDetailView', () => {
  let wrapper;
  let authStore;

  beforeEach(async () => {
    // Configura Pinia
    setActivePinia(createPinia());
    authStore = useAuthStore();
    authStore.token = 'mock-token'; // Simular usuario autenticado
    authStore.user = { id: 1 }; // Simular usuario con ID

    // Mockear api.get para devolver evento y sesiones
    api.default.get.mockImplementation((url) => {
      if (url === '/eventos/1') {
        return Promise.resolve({
          data: {
            id: 1,
            nombre: 'Evento Test',
            descripcion: 'Descripción del evento',
            fecha_inicio: '2025-06-01T18:00:00',
            fecha_fin: '2025-06-01T22:00:00',
            capacidad_maxima: 100,
            estado: 'activo',
          },
        });
      }
      if (url === '/sesiones/sesiones') {
        return Promise.resolve({
          data: {
            sesiones: [
              {
                id: 1,
                evento_id: 1,
                nombre: 'Sesión 1',
                descripcion: 'Descripción de la sesión',
                fecha_inicio: '2025-06-01T18:00:00',
                fecha_fin: '2025-06-01T19:00:00',
                capacidad_maxima: 50,
                asistentes_actuales: 10,
                capacidad_disponible: 40,
                ponente: 'Juan Pérez',
              },
            ],
          },
        });
      }
      return Promise.reject(new Error('URL no mockeada'));
    });

    // Monta el componente con Vuetify y router
    wrapper = mount(EventDetailView, {
      global: {
        plugins: [router, vuetify],
        components,
        mocks: {
          $router: mockRouter,
          $route: mockRoute,
        },
      },
    });

    // Simular formRef.validate y resetValidation
    wrapper.vm.formRef = {
      validate: vi.fn().mockResolvedValue({ valid: true }),
      resetValidation: vi.fn(),
    };

    await router.isReady();
    await flushPromises();
    await wrapper.vm.$nextTick();
  });

  afterEach(() => {
    wrapper.unmount();
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it('valida el campo de descripción en modo edición', async () => {
    // Activar modo edición
    wrapper.vm.editMode = true;
    await wrapper.vm.$nextTick();

    const textAreas = wrapper.findAllComponents(components.VTextarea);
    const descripcionField = textAreas.find(field => field.props('label') === 'Descripción');

    expect(descripcionField.exists()).toBe(true);
    const descripcionInput = descripcionField.find('textarea');
    await descripcionInput.setValue('');
    await descripcionInput.trigger('input');
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.form.descripcion).toBe('');
    expect(wrapper.vm.errorMessage).toBe('');

    await descripcionInput.setValue('Descripción actualizada');
    await descripcionInput.trigger('input');
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.form.descripcion).toBe('Descripción actualizada');
    expect(wrapper.vm.errorMessage).toBe('');
  });

  it('maneja acciones fallidas por usuario no autenticado', async () => {
    vi.useFakeTimers();

    // Simular usuario no autenticado
    authStore.token = null;

    // Simular acción de registrarse
    await wrapper.vm.registrarseEvento();
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.errorMessage).toBe('Por favor, inicia sesión');
    expect(api.default.post).not.toHaveBeenCalled();

    // Avanzar el tiempo para manejar cualquier asincronía
    vi.advanceTimersByTime(100);
    await wrapper.vm.$nextTick();

    expect(mockRouter.push).toHaveBeenCalledWith('/login');

    vi.useRealTimers();
  });

  it('maneja errores de validación del servidor al actualizar', async () => {
    // Activar modo edición
    wrapper.vm.editMode = true;
    await wrapper.vm.$nextTick();

    // Configurar el mock para simular errores de validación del servidor
    api.default.put.mockRejectedValue({
      response: {
        status: 400,
        data: {
          errors: {
            nombre: ['El nombre ya está en uso'],
            descripcion: ['La descripción es demasiado corta'],
          },
        },
      },
    });

    // Simular valores del formulario
    wrapper.vm.form.nombre = 'Evento Test Actualizado';
    wrapper.vm.form.descripcion = 'Descripción actualizada';
    wrapper.vm.form.fecha_inicio = '2025-06-01 18:00:00';
    wrapper.vm.form.fecha_fin = '2025-06-01 22:00:00';
    wrapper.vm.form.capacidad_maxima = 100;
    wrapper.vm.form.estado = 'activo';
    await wrapper.vm.$nextTick();

    // Simular envío del formulario
    const form = wrapper.findComponent(components.VForm);
    await form.trigger('submit.prevent');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(api.default.put).toHaveBeenCalledWith('/eventos/1/actualizar', {
      nombre: 'Evento Test Actualizado',
      descripcion: 'Descripción actualizada',
      fecha_inicio: '2025-06-01 18:00:00',
      fecha_fin: '2025-06-01 22:00:00',
      capacidad_maxima: 100,
      estado: 'activo',
    });
    expect(wrapper.vm.errorMessage).toContain('El nombre ya está en uso');
    expect(wrapper.vm.errorMessage).toContain('La descripción es demasiado corta');
    expect(mockRouter.push).not.toHaveBeenCalled();
  });

  it('muestra el estado de carga durante la obtención del evento', async () => {
    // Configurar el mock para simular demora en la respuesta
    api.default.get.mockImplementation((url) =>
      new Promise((resolve) =>
        setTimeout(
          () =>
            resolve({
              data:
                url === '/eventos/1'
                  ? {
                      id: 1,
                      nombre: 'Evento Test',
                      descripcion: 'Descripción del evento',
                      fecha_inicio: '2025-06-01T18:00:00',
                      fecha_fin: '2025-06-01T22:00:00',
                      capacidad_maxima: 100,
                      estado: 'activo',
                    }
                  : {
                      sesiones: [
                        {
                          id: 1,
                          evento_id: 1,
                          nombre: 'Sesión 1',
                          descripcion: 'Descripción de la sesión',
                          fecha_inicio: '2025-06-01T18:00:00',
                          fecha_fin: '2025-06-01T19:00:00',
                          capacidad_maxima: 50,
                          asistentes_actuales: 10,
                          capacidad_disponible: 40,
                          ponente: 'Juan Pérez',
                        },
                      ],
                    },
            }),
          100
        )
      )
    );

    // Remontar para disparar fetchEvento
    wrapper = mount(EventDetailView, {
      global: {
        plugins: [router, vuetify],
        components,
        mocks: { $router: mockRouter, $route: mockRoute },
      },
    });

    expect(wrapper.vm.loading).toBe(true);
    await new Promise((resolve) => setTimeout(resolve, 150));
    await flushPromises();
    expect(wrapper.vm.loading).toBe(false);
  });
});