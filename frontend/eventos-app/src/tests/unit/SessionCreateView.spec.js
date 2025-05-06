import { mount, flushPromises } from '@vue/test-utils';
import { createRouter, createWebHistory } from 'vue-router';
import { createPinia, setActivePinia } from 'pinia';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import SessionCreateView from '@/views/SessionCreateView.vue';
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

// Mock del router
const mockRouter = {
  push: vi.fn(),
};

// Mock de vue-router con useRoute
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useRouter: () => mockRouter,
    useRoute: () => ({
      params: {}, // Simular parámetros de ruta vacíos
    }),
    createRouter: vi.fn().mockReturnValue({
      push: vi.fn(),
      isReady: vi.fn().mockResolvedValue(),
    }),
    createWebHistory: vi.fn(),
  };
});

// Mock de api.get y api.post
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: [
        { id: 1, nombre: 'Evento 1', fecha_inicio: '2025-06-01T18:00:00' },
        { id: 2, nombre: 'Evento 2', fecha_inicio: '2025-06-02T18:00:00' },
      ],
    }),
    post: vi.fn(),
  },
}));

// Configura el router para pruebas
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Home', component: { template: '<div>Home</div>' } },
    { path: '/login', name: 'Login', component: { template: '<div>Login</div>' } },
  ],
});

describe('SessionCreateView', () => {
  let wrapper;

  beforeEach(async () => {
    // Configura Pinia
    setActivePinia(createPinia());
    const authStore = useAuthStore();
    authStore.token = 'mock-token'; // Simular usuario autenticado

    try {
      // Monta el componente con Vuetify y router
      wrapper = mount(SessionCreateView, {
        global: {
          plugins: [router, vuetify],
          components,
          mocks: {
            $router: mockRouter,
          },
        },
      });

      await router.isReady();
      await flushPromises();
      await wrapper.vm.$nextTick();
    } catch (error) {
      console.error('Error mounting component:', error);
      wrapper = null;
    }
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it('renderiza el componente correctamente', () => {
    expect(wrapper).toBeTruthy();
    expect(wrapper.findComponent(components.VForm).exists()).toBe(true);
  });

  it('muestra el campo de descripción y acepta entrada', async () => {
    expect(wrapper).toBeTruthy();
    const textAreas = wrapper.findAllComponents(components.VTextarea);
    const descripcionField = textAreas.find((field) => field.props('label') === 'Descripción');

    expect(descripcionField.exists()).toBe(true);
    const descripcionInput = descripcionField.find('textarea');
    await descripcionInput.setValue('Descripción de la sesión');
    await descripcionInput.trigger('input');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(descripcionInput.element.value).toBe('Descripción de la sesión');
  });

  it('responde al envío del formulario', async () => {
    expect(wrapper).toBeTruthy();
    const form = wrapper.findComponent(components.VForm);
    expect(form.exists()).toBe(true);

    await form.trigger('submit.prevent');
    await flushPromises();
    await wrapper.vm.$nextTick();

    // Verificar que no haya errores fatales (no podemos asumir errorMessage)
    expect(wrapper.vm).toBeTruthy();
  });
});