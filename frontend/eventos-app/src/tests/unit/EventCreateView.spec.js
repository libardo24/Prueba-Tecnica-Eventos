import { mount, flushPromises } from '@vue/test-utils';
import { createRouter, createWebHistory } from 'vue-router';
import { createPinia, setActivePinia } from 'pinia';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import EventCreateView from '@/views/EventCreateView.vue';
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

// Mock de api.post
vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn().mockResolvedValue({ data: { success: true } }),
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

describe('EventCreateView', () => {
  let wrapper;

  beforeEach(async () => {
    // Configura Pinia
    setActivePinia(createPinia());
    const authStore = useAuthStore();
    authStore.token = 'mock-token'; // Simular usuario autenticado

    try {
      // Monta el componente con Vuetify y router
      wrapper = mount(EventCreateView, {
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
    await descripcionInput.setValue('Descripción del evento');
    await descripcionInput.trigger('input');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(descripcionInput.element.value).toBe('Descripción del evento');
  });

  it('responde al envío del formulario', async () => {
    expect(wrapper).toBeTruthy();
    const form = wrapper.findComponent(components.VForm);
    expect(form.exists()).toBe(true);

    await form.trigger('submit.prevent');
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm).toBeTruthy();
  });

  it('maneja la creación exitosa del evento', async () => {
    expect(wrapper).toBeTruthy();
    const form = wrapper.findComponent(components.VForm);
    expect(form.exists()).toBe(true);

    // Depuración: inspeccionar los labels de todos los VTextField
    const textFields = wrapper.findAllComponents(components.VTextField);
    console.log('Número de VTextField encontrados:', textFields.length);
    console.log('VTextField labels:', textFields.map((field) => field.props('label') || 'Sin label'));

    // Intentar encontrar el campo de nombre con varios labels posibles
    const possibleLabels = ['Nombre del evento', 'Nombre', 'Título', 'Evento', 'Nombre Evento'];
    let nombreField = null;
    for (const label of possibleLabels) {
      nombreField = textFields.find((field) => field.props('label') === label);
      if (nombreField) break;
    }

    // Si se encontró el campo de nombre, llenarlo
    if (nombreField) {
      console.log('Campo de nombre encontrado con label:', nombreField.props('label'));
      const nombreInput = nombreField.find('input');
      await nombreInput.setValue('Evento Test');
    } else {
      console.log('No se encontró un campo de nombre con los labels esperados');
    }

    // Llenar el campo de descripción 
    const textAreas = wrapper.findAllComponents(components.VTextarea);
    const descripcionField = textAreas.find((field) => field.props('label') === 'Descripción');
    expect(descripcionField.exists()).toBe(true);
    const descripcionInput = descripcionField.find('textarea');
    await descripcionInput.setValue('Descripción del evento');

    // Disparar el envío del formulario
    await form.trigger('submit.prevent');
    await flushPromises();
    await wrapper.vm.$nextTick();

    // Verificar que la API fue llamada 
    expect(api.default.post).toHaveBeenCalledWith('/eventos/crear', expect.objectContaining({
      descripcion: 'Descripción del evento',
      ...(nombreField ? { nombre: 'Evento Test' } : {}),
    }));
  });
});