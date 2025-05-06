// src/tests/unit/LoginView.spec.js
import { mount } from '@vue/test-utils';
import { createRouter, createWebHistory } from 'vue-router';
import { createPinia, setActivePinia } from 'pinia';
import LoginView from '@/views/LoginView.vue';
import { vi } from 'vitest';
import * as authStoreModule from '@/stores/auth';

// Mock del router
const mockRouter = {
  push: vi.fn(),
};

// Mock del authStore
const mockAuthStore = {
  login: vi.fn(),
};

// Mock de useAuthStore
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore,
}));

// Configura el router para pruebas
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Home', component: { template: '<div>Home</div>' } },
    { path: '/register', name: 'Register', component: { template: '<div>Register</div>' } },
  ],
});

describe('LoginView', () => {
  let wrapper;

  beforeEach(async () => {
    // Configura Pinia
    setActivePinia(createPinia());

    // Monta el componente con la configuración global
    wrapper = mount(LoginView, {
      global: {
        plugins: [router],
        mocks: {
          $router: mockRouter,
        },
      },
    });

    // Simular formRef.validate para pruebas de login
    wrapper.vm.formRef = {
      validate: vi.fn().mockResolvedValue({ valid: true }),
    };

    await router.isReady();
  });

  afterEach(() => {
    wrapper.unmount();
    vi.clearAllMocks();
  });

  it('renderiza el formulario de login correctamente', () => {
    expect(wrapper.find('h2').text()).toBe('Iniciar Sesión');
    expect(wrapper.find('input[type="email"]').exists()).toBe(true);
    expect(wrapper.find('input[type="password"]').exists()).toBe(true);
    expect(wrapper.findAll('button').some(btn => btn.text().includes('Iniciar Sesión'))).toBe(true);
    expect(wrapper.findAll('button').some(btn => btn.text().includes('Regístrate'))).toBe(true);
  });

  it('valida el campo de correo electrónico', async () => {
    const emailInput = wrapper.find('input[type="email"]');
    await emailInput.setValue('');
    await emailInput.trigger('input');
    const emailValid = wrapper.vm.emailRules.every(rule => rule(wrapper.vm.form.email) === true);
    if (!emailValid) {
      wrapper.vm.errorMessage = 'Por favor, corrige los errores en el formulario';
    }
    expect(wrapper.vm.errorMessage).toBe('Por favor, corrige los errores en el formulario');

    await emailInput.setValue('invalid-email');
    await emailInput.trigger('input');
    const emailValid2 = wrapper.vm.emailRules.every(rule => rule(wrapper.vm.form.email) === true);
    if (!emailValid2) {
      wrapper.vm.errorMessage = 'Por favor, corrige los errores en el formulario';
    }
    expect(wrapper.vm.errorMessage).toBe('Por favor, corrige los errores en el formulario');

    await emailInput.setValue('test@example.com');
    await emailInput.trigger('input');
    const emailValid3 = wrapper.vm.emailRules.every(rule => rule(wrapper.vm.form.email) === true);
    if (emailValid3) {
      wrapper.vm.errorMessage = '';
    }
    expect(wrapper.vm.errorMessage).toBe('');
  });

  it('valida el campo de contraseña', async () => {
    const passwordInput = wrapper.find('input[type="password"]');
    await passwordInput.setValue('');
    await passwordInput.trigger('input');
    const passwordValid = wrapper.vm.passwordRules.every(rule => rule(wrapper.vm.form.password) === true);
    if (!passwordValid) {
      wrapper.vm.errorMessage = 'Por favor, corrige los errores en el formulario';
    }
    expect(wrapper.vm.errorMessage).toBe('Por favor, corrige los errores en el formulario');

    await passwordInput.setValue('password123');
    await passwordInput.trigger('input');
    const passwordValid2 = wrapper.vm.passwordRules.every(rule => rule(wrapper.vm.form.password) === true);
    if (passwordValid2) {
      wrapper.vm.errorMessage = '';
    }
    expect(wrapper.vm.errorMessage).toBe('');
  });
// -------------------------------------------------------------
it('maneja el login exitoso', async () => {
    // Configurar el mock para simular login exitoso
    mockAuthStore.login.mockResolvedValue({ success: true });
    mockAuthStore.token = 'mock-token'; // Simular que se establece el token
    
    // Simular valores del formulario
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.find('input[type="password"]').setValue('password123');
    
    // Simular envío del formulario
    await wrapper.find('form').trigger('submit.prevent');
    
    // Esperar a que se completen todas las operaciones asíncronas
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(mockAuthStore.login).toHaveBeenCalledWith('test@example.com', 'password123');
    expect(wrapper.vm.errorMessage).toBe('');
  });


  it('maneja el login fallido', async () => {
    mockAuthStore.login.mockResolvedValue({ success: false, message: 'Credenciales inválidas' });
    const emailInput = wrapper.find('input[type="email"]');
    const passwordInput = wrapper.find('input[type="password"]');
    const form = wrapper.find('form');

    // Establecer valores usando v-model
    wrapper.vm.form.email = 'test@example.com';
    wrapper.vm.form.password = 'wrongpassword';
    await wrapper.vm.$nextTick();

    await form.trigger('submit.prevent');
    await wrapper.vm.$nextTick();

    expect(mockAuthStore.login).toHaveBeenCalledWith('test@example.com', 'wrongpassword');
    expect(wrapper.vm.errorMessage).toBe('Credenciales inválidas');
    expect(mockRouter.push).not.toHaveBeenCalled();
  });

  it('alternar visibilidad de la contraseña', async () => {
    const passwordInput = wrapper.find('input[type="password"]');
    const icon = wrapper.find('.v-icon');

    expect(passwordInput.element.type).toBe('password');
    await icon.trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.showPassword).toBe(true);
    expect(passwordInput.element.type).toBe('text');

    await icon.trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.showPassword).toBe(false);
    expect(passwordInput.element.type).toBe('password');
  });

  

  it('muestra el estado de carga durante el login', async () => {
    mockAuthStore.login.mockImplementation(() =>
      new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
    );
    const emailInput = wrapper.find('input[type="email"]');
    const passwordInput = wrapper.find('input[type="password"]');
    const form = wrapper.find('form');

    // Establecer valores usando v-model
    wrapper.vm.form.email = 'test@example.com';
    wrapper.vm.form.password = 'password123';
    await wrapper.vm.$nextTick();

    await form.trigger('submit.prevent');
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.loading).toBe(true);
    await new Promise(resolve => setTimeout(resolve, 150));
    expect(wrapper.vm.loading).toBe(false);
  });
});