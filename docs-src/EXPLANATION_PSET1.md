# Guía del Proyecto 01: Design Systems - Demand Prediction Service

## 1. Glosario General (Conceptos Clave)

Antes de empezar, definamos los términos que aparecen en todo el documento:

* **MVP (Minimum Viable Product):** Producto Mínimo Viable. No se pide un sistema perfecto, sino uno que cumpla las *funciones esenciales* descritas en el alcance.
* **CRUD (Create, Read, Update, Delete):** Son las 4 operaciones básicas de cualquier sistema de datos: Crear, Leer, Actualizar y Borrar.
* **Endpoint:** Es una dirección específica en nuestra API (ej. `/zones` o `/health`) a la que el Frontend le pide datos o le envía información.
* **Parquet (`.parquet`):** Un formato de archivo para guardar datos (como un Excel super eficiente y comprimido). Se usa en el proyecto para manejar los datos de viajes de taxi de NYC.
* **Microservicios:** Arquitectura donde dividimos el programa en piezas independientes. Aquí tendremos dos: **Backend** (API) y **Frontend** (App).
* **Docker Compose:** Herramienta para "encender" todos nuestros servicios al mismo tiempo y asegurar que se conecten entre ellos.

---

## 2. Objetivo General

Vamos a construir un **"Demand Prediction Service"** (Sistema de Predicción de Demanda). Imaginen que es el sistema interno para una app de transporte.

El sistema consta de dos aplicaciones que corren simultáneamente:
1.  **Backend (`api`):** Hecho con **FastAPI**. Es el cerebro que procesa y guarda los datos.
2.  **Frontend (`app`):** Hecho con **Streamlit**. Es la web visual donde el usuario interactúa.

---

## 3. Desglose de Instrucciones por Componente

### A. El Backend (API - FastAPI)
*Referencia en PDF: Sección 4 (Páginas 3-4)*

El objetivo es construir una API REST que corra en el puerto 8000. Debe seguir estrictamente las especificaciones de endpoints descritos.

**1. Persistencia (Regla Crítica)**
* **Regla:** La persistencia debe ser **en memoria** (`dict`) para este PSet #1.
* *Significado:* No usaremos base de datos SQL todavía. Los datos se guardan en variables de Python. Si reiniciamos el servidor, se borran.

**2. Health Check (Punto 4.1)**
* **Endpoint:** `GET /health`
* **Qué hace:** Devuelve `{ "status": "ok" }`. Sirve para confirmar que el servicio vive.

**3. CRUD de Zones (Punto 4.2)**
Deben implementar las operaciones para la entidad `Zone` (lugares físicos).
* **Endpoints:** `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`.
* **Validaciones Obligatorias:**
    * `id`: Debe ser positivo.
    * `zone_name` y `borough`: No pueden estar vacíos.

**4. CRUD de Routes (Punto 4.3)**
La entidad `Route` conecta dos zonas (`pickup` y `dropoff`).
* **Endpoints:** `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`.
* **Reglas de Negocio Críticas:**
    * **Validación de Existencia:** Los campos `pickup_zone_id` y `dropoff_zone_id` deben corresponder a zonas que *ya existen*. Si no, devolver error **400**.
    * **Lógica de Ruta:** El origen y destino NO pueden ser iguales (`pickup != dropoff`). Si son iguales, error **400**.
    * **Nombre:** Debe tener al menos 3 caracteres.

---

### B. El Frontend (App - Streamlit)
*Referencia en PDF: Sección 5 (Página 4)*

La aplicación debe correr en el puerto 8501 y consumir la API mediante HTTP.

**1. Configuración de Conexión**
* La URL del backend debe ser configurable (`API_URL`). No la escriban fija ("hardcoded") porque debe funcionar tanto en `localhost` como dentro de Docker (`http://api:8000`).

**2. Página Home (Punto 5.1)**
* Debe mostrar el título y el **estado del backend** (llamando a `/health`).

**3. Páginas de Gestión (Punto 5.2)**
* **Zones:** Tabla para listar y formularios para Crear/Editar/Eliminar.
* **Routes:**
    * *Requisito UX:* Para seleccionar las zonas de origen/destino, deben usar **Dropdowns** (listas desplegables) que carguen las zonas disponibles desde el endpoint `/zones`.

---

### C. La Lógica de "Upload" (Carga de Datos)
*Referencia en PDF: Sección 6 (Páginas 5-7)*

Esta funcionalidad procesa datos reales de viajes.

**1. El Flujo de Trabajo (Punto 6.4)**
1.  **Leer:** El backend recibe el archivo `.parquet` y lo lee con Pandas. Deben usar `limit_rows` para evitar llenar la memoria.
2.  **Analizar:** Calcular los pares (`PULocationID`, `DOLocationID`) más frecuentes y elegir el **Top N**.
3.  **Upsert (Crear o Actualizar):**
    * El sistema recorre esas rutas Top N.
    * Si la ruta *no existe* -> Llama a crear (`POST`).
    * Si la ruta *ya existe* -> Llama a actualizar (`PUT`).
4.  **Zonas:** Durante la carga, si se detectan zonas nuevas en el archivo, también deben crearse.

**2. Respuesta del Endpoint (Punto 6.2)**
El backend debe devolver un JSON con un resumen exacto de qué pasó (filas leídas, rutas creadas vs actualizadas, errores).

---

### D. Infraestructura y DevOps
*Referencia en PDF: Secciones 7 y 8 (Páginas 7-8)*

**1. Dockerización**
* Un `Dockerfile` independiente para el backend y otro para el frontend.
* Un `docker-compose.yml` en la raíz que levante ambos servicios y configure la red.

**2. Git & GitHub**
* **Ramas:** Usar ramas de `feature/...` o `fix/...`. Todo entra por Pull Request (PR).
* **Evidencia:** Se requieren al menos 5 Issues reales y 2 PRs con review.

---

## 4. Estructura del Repositorio

Debemos respetar esta estructura de archivos obligatoria:

```text
/ (Raíz del proyecto)
├── docker-compose.yml       # Orquestador
├── README.md                # Instrucciones de uso
├── CONTRIBUTING.md          # Reglas del equipo
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py          # App FastAPI
│   │   ├── routes_zones.py
│   │   ├── routes_routes.py
│   │   ├── storage.py       # Diccionarios (Memoria)
│   │   └── ...
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── Home.py          # Página principal
│   │   └── pages/
│   │       ├── 1_Zones.py
│   │       ├── 2_Routes.py
│   │       └── 3_Upload_Parquet.py

```

--- 

## 5. Rúbrica de Evaluación y Checklist Final

Esta sección detalla los criterios exactos con los que se calificará el proyecto (Total: 100 Puntos) y la lista de verificación obligatoria para el README.

### A. Git & GitHub (20 Puntos)
*Fuente: PDF Sección 11*
* [ ] **Issues:** Deben tener al menos 5 issues creados describiendo tareas reales (ej. "Crear endpoint de users", "Arreglar bug de docker").
* [ ] **Pull Requests (PRs):** Mínimo 2 PRs que incluyan revisión o comentarios de otros miembros del equipo.
* [ ] **Uso de Ramas:** No subir todo directo a `main`. Usar ramas como `feature/nueva-funcionalidad` o `fix/error-x`.
* [ ] **Tags:** Usar tags de git para marcar versiones (opcional pero recomendado en la rúbrica).

### B. Docker & Compose (25 Puntos)
*Fuente: PDF Sección 11*
* [ ] **Build Reproducible:** El comando `docker compose up --build` debe levantar todo el sistema (backend y frontend) sin errores y sin que el profesor tenga que instalar librerías extra.
* [ ] **Networking Correcto:** El contenedor de Streamlit (`app`) debe poder comunicarse con la API (`api`) usando la red interna de Docker (ej. `http://api:8000`).

### C. FastAPI: CRUD Zones + Routes (30 Puntos)
*Fuente: PDF Sección 11*
* [ ] **Endpoints Completos:** Deben funcionar `GET`, `POST`, `PUT`, `DELETE` para ambas entidades (`Zones` y `Routes`).
* [ ] **Validaciones:**
    * Error **400**: Para reglas de negocio (ej. Origen y Destino son iguales).
    * Error **404**: Cuando se busca un ID que no existe.
    * Error **422**: Validación automática de tipos (Pydantic).

### D. Upload Parquet (15 Puntos)
*Fuente: PDF Sección 11*
* [ ] **Flujo Completo:** El sistema recibe el archivo, lo procesa y **crea o actualiza** las rutas en memoria automáticamente.
* [ ] **Resumen:** El usuario debe ver un resumen con el conteo de: filas leídas, rutas creadas, rutas actualizadas y errores.

### E. Streamlit UX (10 Puntos)
*Fuente: PDF Sección 11*
* [ ] **Navegación:** Menú lateral o botones para ir a "Home", "Zones", "Routes" y "Upload".
* [ ] **Manejo de Errores:** Si la API falla, la interfaz debe mostrar un mensaje amigable, no el error crudo de Python.