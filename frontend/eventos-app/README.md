# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).


eventos-app/
├── public/                     # Archivos estáticos (imágenes, favicon, etc.)
├── src/                        # Código fuente del proyecto
│   ├── assets/                 # Recursos como imágenes, CSS, fuentes
│   │   └── assets/styles/             # Estilos globales (CSS o SCSS)
│   ├── components/             # Componentes reutilizables
│   │   ├── common/             # Componentes genéricos (Button, Input, etc.)
│   │   ├── events/             # Componentes específicos de eventos (EventoCard, FormularioEvento)
│   │   └── layout/             # Componentes de diseño (Navbar, Footer)
│   ├── views/                  # Vistas asociadas a rutas (páginas)
│   ├── router/                 # Configuración de Vue Router
│   ├── stores/                 # Almacenes de estado con Pinia
│   ├── services/               # Lógica para interactuar con la API
│   ├── tests/                  # Pruebas unitarias
│   ├── App.vue                 # Componente raíz
│   └── main.js                 # Punto de entrada de la aplicación
├── .gitignore                  # Archivos ignorados por Git
├── index.html                  # Plantilla HTML principal
├── package.json                # Dependencias y scripts
├── vite.config.js              # Configuración de Vite
└── README.md                   # Documentación del proyecto


Documentación del Proyecto: Sistema de Gestión de Eventos y Sesiones
Descripción del Proyecto
El Sistema de Gestión de Eventos y Sesiones es una aplicación web diseñada para gestionar eventos, sesiones asociadas, y el registro de asistentes. Permite a los usuarios autenticados crear, editar, eliminar y visualizar eventos y sesiones, así como registrarse en ellos y verificar la capacidad disponible. La aplicación incluye una interfaz de usuario moderna y responsiva, con soporte para búsqueda dinámica, validación de formularios, y manejo de errores.
Objetivos
Proporcionar una plataforma para que los administradores creen y gestionen eventos y sesiones.

Permitir a los usuarios registrarse en eventos y sesiones, y consultar su disponibilidad.

Garantizar la seguridad mediante autenticación de usuarios.

Ofrecer una experiencia de usuario fluida con una interfaz intuitiva y mensajes claros de éxito o error.

Tecnologías Utilizadas
Frontend:
Vue.js 3: Framework JavaScript para construir la interfaz de usuario.

Vuetify 3: Biblioteca de componentes UI basada en Material Design para una interfaz moderna y responsiva.

Vue Router: Para la navegación entre vistas.

Pinia: Gestión del estado global (por ejemplo, autenticación).

Lodash: Utilidad para funciones como debounce en búsquedas dinámicas.

@mdi
/font: Iconos de Material Design para la interfaz.

Backend (asumido, no proporcionado):
API RESTful (Python) con endpoints como /eventos, /sesiones, /sesiones/asistencias, etc.

Autenticación basada en tokens JWT.

Pruebas:
Vitest: Framework de pruebas para pruebas unitarias.

@vue
/test-utils: Utilidades para probar componentes Vue.

Otros:
Axios: Cliente HTTP para interactuar con la API (implementado en services/api.js).

CSS personalizado: Estilos específicos en archivos como HomeView.css, SessionCreateView.css, y event-detail.css.

Estructura del Proyecto


src/
├── assets/
│   ├── styles/
│   │   ├── HomeView.css
│   │   ├── SessionCreateView.css
│   │   └── event-detail.css
├── components/
│   └── EventoCard.vue
├── services/
│   └── api.js
├── stores/
│   └── auth.js
├── tests/
│   └── unit/
│       ├── HomeView.spec.js
│       ├── SessionCreateView.spec.js
│       ├── EventDetailView.spec.js
│       └── SessionAssistantsView.spec.js
├── views/
│   ├── HomeView.vue
│   ├── SessionCreateView.vue
│   ├── EventDetailView.vue
│   └── SessionAssistantsView.vue
├── main.js
└── App.vue

Descripción de directorios y archivos
src/assets/styles/: Contiene archivos CSS específicos para cada vista.

src/components/: Componentes reutilizables, como EventoCard.vue (mockeado en pruebas).

src/services/: Configuración de Axios (api.js) para interactuar con la API.

src/stores/: Gestión del estado con Pinia, incluyendo auth.js para autenticación.

src/tests/unit/: Pruebas unitarias para los componentes principales.

src/views/: Vistas principales de la aplicación, cada una con una funcionalidad específica.

src/main.js: Punto de entrada donde se inicializan Vue, Vuetify, Vue Router, y Pinia.

src/App.vue: Componente raíz (no proporcionado, pero asumido).

Funcionalidades Principales
1. HomeView
Ruta: /

Descripción: Muestra una lista paginada de eventos con búsqueda dinámica por nombre.

Funcionalidades:
Tabla de eventos (v-data-table) con columnas para nombre, fecha, capacidad y estado.

Campo de búsqueda con debounce (500ms) para filtrar eventos.

Paginación y selección de ítems por página.

Botones para ver detalles de cada evento.

Modo tarjetas (EventoCard) opcional (desactivado por defecto).

API:
GET /eventos/eventos: Obtiene la lista de eventos con parámetros nombre, page, y per_page.

2. SessionCreateView
Ruta: Asumida como /sesiones/crear

Descripción: Permite crear una nueva sesión asociada a un evento.

Funcionalidades:
Formulario con campos para evento (autocompletado), nombre, descripción, fechas de inicio/fin, capacidad máxima, y ponente.

Búsqueda dinámica de eventos con debounce (300ms).

Validación de todos los campos (requeridos, formatos de fecha/hora, capacidad positiva).

Selección de fechas y horas mediante v-date-picker y v-text-field.

Mensajes de éxito o error tras enviar el formulario.

API:
GET /eventos/buscar: Busca eventos por nombre.

POST /sesiones/crear: Crea una nueva sesión.

3. EventDetailView
Ruta: /eventos/:id

Descripción: Muestra los detalles de un evento y sus sesiones asociadas, con opciones para editar, eliminar, o registrarse.

Funcionalidades:
Detalles del evento (nombre, descripción, fechas, capacidad, estado).

Botones para registrarse, verificar capacidad, editar, o eliminar el evento.

Formulario de edición con validación (activado con editMode).

Lista de sesiones con acciones para registrarse, editar, o eliminar.

Diálogos de confirmación para eliminar evento o sesión.

API:
GET /eventos/:id: Obtiene detalles del evento.

GET /sesiones/sesiones: Obtiene todas las sesiones.

POST /eventos/:id/registrarse: Registra al usuario en el evento.

GET /eventos/:id/validar-capacidad: Verifica la capacidad disponible.

PUT /eventos/:id/actualizar: Actualiza el evento.

DELETE /eventos/:id/eliminar: Elimina el evento.

POST /sesiones/registrar_asistente/:id: Registra al usuario en una sesión.

DELETE /sesiones/eliminar/:id: Elimina una sesión.

4. SessionAssistantsView
Ruta: Asumida como /sesiones/asistencias

Descripción: Muestra una tabla con las asistencias a sesiones.

Funcionalidades:
Tabla (v-data-table) con columnas para ID de usuario, email, ID de sesión, nombre de la sesión, y fecha de inicio.

Indicador de carga (v-progress-linear) durante la obtención de datos.

Mensajes de error para problemas de autenticación o API.

API:
GET /sesiones/asistencias: Obtiene la lista de asistencias.

Requisitos Previos
Node.js: Versión 16 o superior.

NPM: Versión 8 o superior.

Navegador moderno: Chrome, Firefox, Edge, o Safari.

Backend: Un servidor API RESTful configurado con los endpoints mencionados.

Instalación
Clona el repositorio:
bash

git clone https://github.com/libardo24/Prueba-Tecnica-Eventos.git
cd Prueba-Tecnica-Eventos

Instala las dependencias:
bash

npm install

Configura las variables de entorno:
Crea un archivo .env en la raíz del proyecto.

Configura la URL del backend (por ejemplo):

VUE_APP_API_URL=http://localhost:3000/api

Asegúrate de que services/api.js use esta variable para las solicitudes HTTP.

Configura el backend:
Asegúrate de que el servidor backend esté ejecutándose y accesible.

Verifica que los endpoints (/eventos, /sesiones, etc.) estén disponibles.

Ejecución
Ejecuta en modo desarrollo:
bash

npm run dev

La aplicación estará disponible en http://localhost:5173 (o el puerto configurado).

Construye para producción:
bash

npm run build

Los archivos generados estarán en la carpeta dist.

Pruebas Unitarias
El proyecto incluye pruebas unitarias para los componentes principales, ubicadas en src/tests/unit/. Las pruebas usan Vitest y @vue
/test-utils.
Instalación de dependencias para pruebas
bash

npm install --save-dev vitest @vue/test-utils

Ejecución de pruebas
Ejecuta todas las pruebas:
bash

npm run test

Ejecuta pruebas específicas:
Para EventCreateView:
bash

npm run test -- tests/unit/EventCreateView.spec.js

Para SessionCreateView:
bash

npm run test -- tests/unit/SessionCreateView.spec.js

Para EventDetailView:
bash

npm run test -- tests/unit/EventDetailView.spec.js

Para LoginView:
bash

npm run test -- tests/unit/LoginView.spec.js

Cobertura de pruebas:
bash
npm run test:coverage
- **Ubicación del reporte**: La carpeta `coverage/` contiene el reporte de cobertura. Abre `coverage/index.html` en un navegador para ver el reporte visual. por temas de tiempo(Trabajo actualmente) no logre hacer la cobertura que me gustaria.
## Endpoints de la API

los endpoints utilizados son:

| Método  | Endpoint                              | Descripción                                    |
|---------|---------------------------------------|------------------------------------------------|
| GET     | `/eventos/eventos`                   | Lista eventos con filtros (nombre, page, per_page). |
| GET     | `/eventos/buscar`                    | Busca eventos por nombre.                      |
| POST    | `/sesiones/crear`                    | Crea una nueva sesión.                         |
| GET     | `/eventos/:id`                       | Obtiene detalles de un evento.                 |
| GET     | `/sesiones/sesiones`                 | Lista todas las sesiones.                      |
| POST    | `/eventos/:id/registrarse`           | Registra al usuario en un evento.              |
| GET     | `/eventos/:id/validar-capacidad`     | Verifica la capacidad disponible de un evento. |
| PUT     | `/eventos/:id/actualizar`            | Actualiza un evento.                           |
| DELETE  | `/eventos/:id/eliminar`              | Elimina un evento.                             |
| POST    | `/sesiones/registrar_asistente/:id`  | Registra al usuario en una sesión.             |
| DELETE  | `/sesiones/eliminar/:id`             | Elimina una sesión.                            |
| GET     | `/sesiones/asistencias`              | Lista las asistencias a sesiones.              |

Notas sobre la API
Todos los endpoints requieren autenticación (token JWT en el header Authorization).

Los errores comunes incluyen:
401: Sesión expirada o no autenticado.

400: Datos inválidos (con detalles en data.errors).

404: Recurso no encontrado.

500: Error del servidor.


Mejoras Futuras
Pruebas adicionales:

Cubrir más casos de uso en v-data-table (ordenamiento, filtrado).

Soporte multilingüe: Implementar vue-i18n para soportar varios idiomas.

Mejor manejo de fechas: Usar una librería de fechas para evitar problemas de zonas horarias.


Optimización de rendimiento: Implementar carga perezosa para componentes pesados como v-data-table.

Contribución
Clona el repositorio y crea una rama para tu funcionalidad:
bash

git checkout -b feature/nueva-funcionalidad

Realiza los cambios y escribe pruebas unitarias.

Ejecuta las pruebas para verificar que no haya regresiones:
bash

npm run test

Haz commit de los cambios y crea un pull request:
bash

git commit -m "Agrega nueva funcionalidad"
git push origin feature/nueva-funcionalidad





