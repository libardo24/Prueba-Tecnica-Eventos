// tests/setup.js
import { config } from '@vue/test-utils';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

// Configura Vuetify para pruebas
const vuetify = createVuetify({
  components,
  directives,
});

// Configuración global para Vue Test Utils
config.global.plugins = [vuetify];

// Stubs para componentes de Vuetify
config.global.stubs = {
  'v-btn': {
    template: `
      <button
        :to="to"
        @click="$emit('click')"
      >
        <slot />
      </button>
    `,
    props: ['to'],
    emits: ['click'],
  },
  'v-text-field': {
    template: `
      <div>
        <input
          :type="type"
          :value="modelValue"
          @input="$emit('update:modelValue', $event.target.value)"
        />
        <i
          v-if="appendInnerIcon"
          class="v-icon"
          @click="$emit('click:append-inner')"
        ></i>
      </div>
    `,
    props: ['modelValue', 'type', 'appendInnerIcon', 'rules'],
    emits: ['update:modelValue', 'click:append-inner'],
  },
  'v-icon': {
    template: '<i class="v-icon" />',
  },
};