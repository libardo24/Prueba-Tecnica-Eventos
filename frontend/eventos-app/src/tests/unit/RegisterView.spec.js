// src/tests/unit/RegisterView.spec.js
import { mount } from '@vue/test-utils';
import { createRouter, createWebHistory } from 'vue-router';
import { createPinia, setActivePinia } from 'pinia';
import RegisterView from '@/views/RegisterView.vue';
import { vi } from 'vitest';
import * as api from '@/services/api';

// Mock del router
const mockRouter = {
  push: vi.fn(),
};

// Mock de api.post
vi.mock('@/services/api', () => ({
  default: {
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

describe('RegisterView', () => {
  let wrapper;

  beforeEach(async () => {
    // Configura Pinia
    setActivePinia(createPinia());

    // Monta el componente con la configuración global
    wrapper = mount(RegisterView, {
      global: {
        plugins: [router],
        mocks: {
          $router: mockRouter,
        },
      },
    });

    // Simular formRef.validate para pruebas de registro
    wrapper.vm.formRef = {
      validate: vi.fn().mockResolvedValue({ valid: true }),
      resetValidation: vi.fn(), // Mock inicial, puede sobrescribirse en pruebas específicas
    };

    await router.isReady();
  });

  afterEach(() => {
    wrapper.unmount();
    vi.clearAllMocks();
  });

  it('renderiza el formulario de registro correctamente', () => {
    expect(wrapper.find('h2').text()).toBe('Registrarse');
    expect(wrapper.find('input[type="email"]').exists()).toBe(true);
    expect(wrapper.find('input[type="password"]').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').text()).toContain('Registrarse');
    expect(wrapper.findComponent({ name: 'router-link' }).text()).toContain('Inicia sesión');
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

    await passwordInput.setValue('123');
    await passwordInput.trigger('input');
    const passwordValid2 = wrapper.vm.passwordRules.every(rule => rule(wrapper.vm.form.password) === true);
    if (!passwordValid2) {
      wrapper.vm.errorMessage = 'Por favor, corrige los errores en el formulario';
    }
    expect(wrapper.vm.errorMessage).toBe('Por favor, corrige los errores en el formulario');

    await passwordInput.setValue('password123');
    await passwordInput.trigger('input');
    const passwordValid3 = wrapper.vm.passwordRules.every(rule => rule(wrapper.vm.form.password) === true);
    if (passwordValid3) {
      wrapper.vm.errorMessage = '';
    }
    expect(wrapper.vm.errorMessage).toBe('');
  });
// -----------------------------------------------------------------------------------
  it('maneja el registro exitoso', async () => {
    // Configurar el mock para simular registro exitoso
    api.default.post.mockResolvedValue({ data: { success: true } });
  
    // Configurar el mock para formRef.validate
    wrapper.vm.formRef = {
      validate: vi.fn().mockResolvedValue({ valid: true }),
      resetValidation: vi.fn(),
    };
  
    // Simular valores del formulario
    wrapper.vm.form.email = 'test@example.com';
    wrapper.vm.form.password = 'password123';
    await wrapper.vm.$nextTick();
  
    // Simular envío del formulario
    await wrapper.find('form').trigger('submit.prevent');
  
    // Esperar a que se procesen todas las operaciones asíncronas
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 100));
  
    expect(api.default.post).toHaveBeenCalledWith('/auth/register', {
      email: 'test@example.com',
      password: 'password123',
    });
    expect(wrapper.vm.successMessage).toBe('Usuario registrado exitosamente. Por favor, inicia sesión.');
    expect(wrapper.vm.form.email).toBe('');
    expect(wrapper.vm.form.password).toBe('');
    expect(wrapper.vm.errors.email).toBe(''); // Verificar que no hay errores
    expect(wrapper.vm.errors.password).toBe(''); // Verificar que no hay errores

  });
// ----------------------------------------------------------------------------------------------------------
  it('maneja el registro fallido por correo ya registrado', async () => {
    // Configurar el mock para simular error de correo registrado
    api.default.post.mockRejectedValue({
      response: {
        status: 400,
        data: { message: 'El correo ya está registrado' },
      },
    });

    // Simular valores del formulario
    wrapper.vm.form.email = 'test@example.com';
    wrapper.vm.form.password = 'password123';
    await wrapper.vm.$nextTick();

    // Simular envío del formulario
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();

    expect(api.default.post).toHaveBeenCalledWith('/auth/register', {
      email: 'test@example.com',
      password: 'password123',
    });
    expect(wrapper.vm.errorMessage).toBe('El correo ya está registrado');
    expect(mockRouter.push).not.toHaveBeenCalled();
  });

  it('maneja el registro fallido por validación de formulario', async () => {
    // Simular validación fallida
    wrapper.vm.formRef.validate.mockResolvedValue({ valid: false });

    // Simular valores del formulario
    wrapper.vm.form.email = '';
    wrapper.vm.form.password = '';
    await wrapper.vm.$nextTick();

    // Simular envío del formulario
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.errorMessage).toBe('Por favor, corrige los errores en el formulario');
    expect(api.default.post).not.toHaveBeenCalled();
    expect(mockRouter.push).not.toHaveBeenCalled();
  });

  it('muestra el estado de carga durante el registro', async () => {
    // Configurar el mock para simular demora en la respuesta
    api.default.post.mockImplementation(() =>
      new Promise(resolve => setTimeout(() => resolve({ data: { success: true } }), 100))
    );

    // Simular valores del formulario
    wrapper.vm.form.email = 'test@example.com';
    wrapper.vm.form.password = 'password123';
    await wrapper.vm.$nextTick();

    // Simular envío del formulario
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.loading).toBe(true);
    await new Promise(resolve => setTimeout(resolve, 150));
    expect(wrapper.vm.loading).toBe(false);
  });

  it('maneja errores de validación del servidor', async () => {
    // Configurar el mock para simular errores de validación del servidor
    api.default.post.mockRejectedValue({
      response: {
        status: 400,
        data: {
          errors: {
            email: ['El correo ya está en uso'],
            password: ['La contraseña es demasiado débil'],
          },
        },
      },
    });

    // Simular valores del formulario
    wrapper.vm.form.email = 'test@example.com';
    wrapper.vm.form.password = 'weak';
    await wrapper.vm.$nextTick();

    // Simular envío del formulario
    await wrapper.find('form').trigger('submit.prevent');
    await wrapper.vm.$nextTick();

    expect(api.default.post).toHaveBeenCalledWith('/auth/register', {
      email: 'test@example.com',
      password: 'weak',
    });
    expect(wrapper.vm.errors.email).toBe('El correo ya está en uso');
    expect(wrapper.vm.errors.password).toBe('La contraseña es demasiado débil');
    expect(mockRouter.push).not.toHaveBeenCalled();
  });
});