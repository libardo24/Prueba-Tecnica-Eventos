<template>
  <v-text-field
    :label="label"
    :type="type"
    :value="modelValue"
    :error-messages="error"
    @input="$emit('update:modelValue', $event.target.value)"
    :prepend-inner-icon="type === 'email' ? 'mdi-email' : type === 'password' ? 'mdi-lock' : null"
    variant="outlined"
    clearable
    :class="$attrs.class"
    :dense="$attrs.dense"
  />
</template>

<script>
export default {
  name: 'Input',
  props: {
    label: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      default: 'text',
    },
    modelValue: {
      type: String,
      default: '',
    },
    error: {
      type: String,
      default: '',
    },
  },
  watch: {
    modelValue(newValue) {
    },
  },
};
</script>

<style scoped>
/* Eliminamos estilos locales para evitar interferencias */
</style>