<template>
  <div class="home-view">
    <v-container fluid class="eventos-container">
      <v-row>
        <v-col>
          <h1 class="text-h4 primary--text mb-6" data-testid="title">Lista de Eventos</h1>
          <v-text-field
            v-model="search"
            label="Buscar eventos por nombre"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            clearable
            class="mb-6 primary-text-field"
            dense
            hide-details
            data-testid="search-field"
            @input="debouncedFetchEventos"
          />
          <v-data-table
            :items="eventos"
            :headers="headers"
            :loading="loading"
            :items-per-page="itemsPerPage"
            :page="page"
            :server-items-length="totalEventos"
            class="elevation-1 evento-table"
            hide-default-footer
            data-testid="eventos-table"
          >
            <template v-slot:item.actions="{ item }">
              <v-btn
                color="primary"
                small
                class="primary-btn"
                :to="{ name: 'EventDetail', params: { id: item.id } }"
                data-testid="detail-button"
              >
                Ver Detalles
              </v-btn>
            </template>
            <template v-slot:bottom>
              <v-container fluid>
                <v-row align="center" justify="center">
                  <v-col cols="12" sm="6">
                    <v-select
                      v-model="itemsPerPage"
                      :items="[5, 10, 20, 50]"
                      label="Eventos por página"
                      variant="outlined"
                      dense
                      hide-details
                      class="items-per-page-select"
                      data-testid="items-per-page-select"
                      @update:modelValue="updateItemsPerPage"
                    />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-pagination
                      v-model="page"
                      :length="totalPages"
                      :total-visible="7"
                      prev-icon="mdi-chevron-left"
                      next-icon="mdi-chevron-right"
                      class="eventos-pagination"
                      active-color="#6ac6dc"
                      data-testid="pagination"
                      @update:modelValue="updatePage"
                    />
                  </v-col>
                </v-row>
              </v-container>
            </template>
          </v-data-table>
          <v-alert
            v-if="errorMessage"
            type="error"
            class="mt-4 primary-alert"
            dismissible
            data-testid="error-alert"
            @input="errorMessage = ''"
          >
            {{ errorMessage }}
          </v-alert>
          <v-row v-if="showCards" class="mt-6">
            <v-col v-for="evento in eventos" :key="evento.id" cols="12" sm="6" md="4">
              <EventoCard :evento="evento" data-testid="evento-card" />
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import api from '../services/api';
import EventoCard from '../components/EventoCard.vue';
import { debounce } from 'lodash';

export default {
  name: 'HomeView',
  components: { EventoCard },
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    const eventos = ref([]);
    const loading = ref(false);
    const errorMessage = ref('');
    const search = ref('');
    const page = ref(1);
    const itemsPerPage = ref(10);
    const totalEventos = ref(0);
    const totalPages = ref(1);
    const showCards = ref(false);
    let isMounted = ref(true);

    const headers = [
      { title: 'Nombre', key: 'nombre', sortable: true },
      {
        title: 'Fecha Inicio',
        key: 'fecha_inicio',
        sortable: true,
        value: (item) =>
          new Date(item.fecha_inicio).toLocaleString('es-ES', {
            dateStyle: 'medium',
            timeStyle: 'short',
          }),
      },
      { title: 'Capacidad', key: 'capacidad_maxima', sortable: true },
      { title: 'Estado', key: 'estado', sortable: true },
      { title: 'Acciones', key: 'actions', sortable: false },
    ];

    const fetchEventos = async () => {
      if (!isMounted.value || !authStore.token) {
        if (!authStore.token) {
          errorMessage.value = 'Por favor, inicia sesión para ver los eventos';
          router.push('/login');
        }
        return;
      }

      loading.value = true;
      errorMessage.value = '';

      try {
        const params = {
          nombre: search.value || '',
          page: page.value,
          per_page: itemsPerPage.value,
        };
        const response = await api.get('/eventos/eventos', { params });

        if (!isMounted.value) return;

        if (!response.data || typeof response.data !== 'object') {
          throw new Error('Respuesta inválida: datos no encontrados');
        }

        const { eventos: responseEventos, total, total_pages } = response.data;
        eventos.value = Array.isArray(responseEventos) ? responseEventos : [];
        totalEventos.value = Number.isInteger(total) ? total : 0;
        totalPages.value = Number.isInteger(total_pages) ? total_pages : 1;

        if (eventos.value.length === 0 && page.value > 1) {
          page.value = Math.max(1, page.value - 1);
          await fetchEventos();
        }
      } catch (error) {
        console.error('Error al obtener eventos:', error);
        if (error.response) {
          const { status, data } = error.response;
          if (status === 401) {
            errorMessage.value = 'Sesión expirada. Por favor, inicia sesión de nuevo';
            authStore.logout();
            router.push('/login');
          } else if (status === 404) {
            errorMessage.value = data.message || 'Eventos no encontrados';
            eventos.value = [];
            totalEventos.value = 0;
            totalPages.value = 1;
          } else if (status === 400) {
            errorMessage.value = data.message || 'Parámetros inválidos';
          } else {
            errorMessage.value = data.message || 'Error al obtener los eventos';
          }
        } else {
          errorMessage.value = `Error de conexión: ${error.message}`;
        }
      } finally {
        loading.value = false;
      }
    };

    const debouncedFetchEventos = debounce(() => {
      page.value = 1;
      fetchEventos();
    }, 500);

    const updatePage = (newPage) => {
      page.value = newPage;
      fetchEventos();
    };

    const updateItemsPerPage = (newItemsPerPage) => {
      itemsPerPage.value = newItemsPerPage;
      page.value = 1;
      fetchEventos();
    };

    watch(search, () => {
      debouncedFetchEventos();
    });

    onUnmounted(() => {
      isMounted.value = false;
      debouncedFetchEventos.cancel();
    });

    onMounted(() => {
      if (router.currentRoute.value.name === 'Home') {
        fetchEventos();
      }
    });

    return {
      eventos,
      loading,
      errorMessage,
      search,
      page,
      itemsPerPage,
      totalEventos,
      totalPages,
      headers,
      showCards,
      fetchEventos,
      debouncedFetchEventos,
      updatePage,
      updateItemsPerPage,
    };
  },
};
</script>

<style scoped>
@import '@/assets/styles/HomeView.css';
</style>