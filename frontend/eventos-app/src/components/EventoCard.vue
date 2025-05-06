<template>
  <v-card class="mb-4" elevation="2">
    <v-card-title>{{ evento.nombre }}</v-card-title>
    <v-card-text>
      <p>{{ evento.descripcion }}</p>
      <p><strong>Fecha:</strong> {{ formatDate(evento.fecha_inicio) }} - {{ formatDate(evento.fecha_fin) }}</p>
      <p><strong>Capacidad:</strong> {{ evento.capacidad_maxima }} personas</p>
      <p><strong>Estado:</strong> {{ evento.estado }}</p>
    </v-card-text>
    <v-card-actions>
      <v-btn color="primary" :to="{ name: 'EventDetail', params: { id: evento.id } }">
        Ver Detalles
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: 'EventoCard',
  props: {
    evento: {
      type: Object,
      required: true,
      validator: (evento) => {
        return (
          'id' in evento &&
          'nombre' in evento &&
          'descripcion' in evento &&
          'fecha_inicio' in evento &&
          'fecha_fin' in evento &&
          'capacidad_maxima' in evento &&
          'estado' in evento
        );
      },
    },
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString('es-ES', {
        dateStyle: 'medium',
        timeStyle: 'short',
      });
    },
  },
};
</script>