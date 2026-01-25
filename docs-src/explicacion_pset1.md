# Guía del Proyecto 01: Design Systems - Demand Prediction Service

## 1. Glosario General (Conceptos Clave)

Antes de empezar, definamos los términos que aparecen en todo el documento:

* **MVP (Minimum Viable Product):** Producto Mínimo Viable. [cite_start]No se pide un sistema perfecto, sino uno que cumpla las *funciones esenciales* descritas en el alcance[cite: 25].
* [cite_start]**CRUD (Create, Read, Update, Delete):** Son las 4 operaciones básicas de cualquier sistema de datos: Crear, Leer, Actualizar y Borrar[cite: 54, 66].
* **Endpoint:** Es una dirección específica en nuestra API (ej. `/zones` o `/health`) a la que el Frontend le pide datos o le envía información.
* **Parquet (`.parquet`):** Un formato de archivo para guardar datos (como un Excel super eficiente y comprimido). [cite_start]Se usa en el proyecto para manejar los datos de viajes de taxi de NYC[cite: 101].
* **Microservicios:** Arquitectura donde dividimos el programa en piezas independientes. [cite_start]Aquí tendremos dos: **Backend** (API) y **Frontend** (App) [cite: 14-16].
* [cite_start]**Docker Compose:** Herramienta para "encender" todos nuestros servicios al mismo tiempo y asegurar que se conecten entre ellos[cite: 6].

---

## 2. Objetivo General

[cite_start]Vamos a construir un **"Demand Prediction Service"** (Sistema de Predicción de Demanda)[cite: 26]. Imaginen que es el sistema interno para una app de transporte.

El sistema consta de dos aplicaciones que corren simultáneamente:
1.  **Backend (`api`):** Hecho con **FastAPI**. [cite_start]Es el cerebro que procesa y guarda los datos[cite: 15].
2.  **Frontend (`app`):** Hecho con **Streamlit**. [cite_start]Es la web visual donde el usuario interactúa[cite: 16].

---

## 3. Desglose de Instrucciones por Componente

### A. El Backend (API - FastAPI)
*Referencia en PDF: Sección 4 (Páginas 3-4)*

[cite_start]El objetivo es construir una API REST que corra en el puerto 8000[cite: 51]. Debe seguir estrictamente las especificaciones de endpoints descritos.

**1. Persistencia (Regla Crítica)**
* [cite_start]**Regla:** La persistencia debe ser **en memoria** (`dict`) para este PSet #1[cite: 49].
* *Significado:* No usaremos base de datos SQL todavía. Los datos se guardan en variables de Python. Si reiniciamos el servidor, se borran.

**2. Health Check (Punto 4.1)**
* **Endpoint:** `GET /health`
* **Qué hace:** Devuelve `{ "status": "ok" }`. [cite_start]Sirve para confirmar que el servicio vive[cite: 53].

**3. CRUD de Zones (Punto 4.2)**
[cite_start]Deben implementar las operaciones para la entidad `Zone` (lugares físicos) [cite: 54-65].
* **Endpoints:** `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`.
* **Validaciones Obligatorias:**
    * `id`: Debe ser positivo.
    * `zone_name` y `borough`: No pueden estar vacíos.

**4. CRUD de Routes (Punto 4.3)**
[cite_start]La entidad `Route` conecta dos zonas (`pickup` y `dropoff`) [cite: 66-75].
* **Endpoints:** `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`.
* **Reglas de Negocio Críticas:**
    * **Validación de Existencia:** Los campos `pickup_zone_id` y `dropoff_zone_id` deben corresponder a zonas que *ya existen*. [cite_start]Si no, devolver error **400**[cite: 48].
    * **Lógica de Ruta:** El origen y destino NO pueden ser iguales (`pickup != dropoff`). [cite_start]Si son iguales, error **400**[cite: 74].
    * [cite_start]**Nombre:** Debe tener al menos 3 caracteres[cite: 75].

---

### B. El Frontend (App - Streamlit)
*Referencia en PDF: Sección 5 (Página 4)*

[cite_start]La aplicación debe correr en el puerto 8501 y consumir la API mediante HTTP[cite: 82].

**1. Configuración de Conexión**
* La URL del backend debe ser configurable (`API_URL`). No la escriban fija ("hardcoded") porque debe funcionar tanto en `localhost` como dentro de Docker (`http://api:8000`) [cite: 82-83].

**2. Página Home (Punto 5.1)**
* [cite_start]Debe mostrar el título y el **estado del backend** (llamando a `/health`) [cite: 85-88].

**3. Páginas de Gestión (Punto 5.2)**
* [cite_start]**Zones:** Tabla para listar y formularios para Crear/Editar/Eliminar [cite: 90-91].
* **Routes:**
    * [cite_start]*Requisito UX:* Para seleccionar las zonas de origen/destino, deben usar **Dropdowns** (listas desplegables) que carguen las zonas disponibles desde el endpoint `/zones`[cite: 94].

---

### C. La Lógica de "Upload" (Carga de Datos)
*Referencia en PDF: Sección 6 (Páginas 5-7)*

Esta funcionalidad procesa datos reales de viajes.

**1. El Flujo de Trabajo (Punto 6.4)**
1.  **Leer:** El backend recibe el archivo `.parquet` y lo lee con Pandas. [cite_start]Deben usar `limit_rows` para evitar llenar la memoria [cite: 128-129].
2.  [cite_start]**Analizar:** Calcular los pares (`PULocationID`, `DOLocationID`) más frecuentes y elegir el **Top N** [cite: 130-131].
3.  **Upsert (Crear o Actualizar):**
    * El sistema recorre esas rutas Top N.
    * Si la ruta *no existe* -> Llama a crear (`POST`).
    * [cite_start]Si la ruta *ya existe* -> Llama a actualizar (`PUT`) [cite: 133-135].
4.  [cite_start]**Zonas:** Durante la carga, si se detectan zonas nuevas en el archivo, también deben crearse[cite: 144].

**2. Respuesta del Endpoint (Punto 6.2)**
[cite_start]El backend debe devolver un JSON con un resumen exacto de qué pasó (filas leídas, rutas creadas vs actualizadas, errores) [cite: 112-121].

---

### D. Infraestructura y DevOps
*Referencia en PDF: Secciones 7 y 8 (Páginas 7-8)*

**1. Dockerización**
* [cite_start]Un `Dockerfile` independiente para el backend y otro para el frontend[cite: 168].
* [cite_start]Un `docker-compose.yml` en la raíz que levante ambos servicios y configure la red[cite: 170].

**2. Git & GitHub**
* **Ramas:** Usar ramas de `feature/...` o `fix/...`. [cite_start]Todo entra por Pull Request (PR) [cite: 176-177].
* [cite_start]**Evidencia:** Se requieren al menos 5 Issues reales y 2 PRs con review [cite: 180-181].

---

## 4. Estructura del Repositorio

[cite_start]Debemos respetar esta estructura de archivos obligatoria [cite: 187-212]:

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

--- 

## 5. Rúbrica de Evaluación y Checklist Final

Esta sección detalla los criterios exactos con los que se calificará el proyecto (Total: 100 Puntos) y la lista de verificación obligatoria para el README.

### A. Git & GitHub (20 Puntos)
[cite_start]*Fuente: PDF Sección 11 [cite: 214]*
* [cite_start][ ] **Issues:** Deben tener al menos 5 issues creados describiendo tareas reales (ej. "Crear endpoint de users", "Arreglar bug de docker")[cite: 180].
* [cite_start][ ] **Pull Requests (PRs):** Mínimo 2 PRs que incluyan revisión o comentarios de otros miembros del equipo[cite: 181].
* [ ] **Uso de Ramas:** No subir todo directo a `main`. [cite_start]Usar ramas como `feature/nueva-funcionalidad` o `fix/error-x`[cite: 176].
* [cite_start][ ] **Tags:** Usar tags de git para marcar versiones (opcional pero recomendado en la rúbrica)[cite: 214].

### B. Docker & Compose (25 Puntos)
[cite_start]*Fuente: PDF Sección 11 [cite: 215]*
* [cite_start][ ] **Build Reproducible:** El comando `docker compose up --build` debe levantar todo el sistema (backend y frontend) sin errores y sin que el profesor tenga que instalar librerías extra[cite: 215].
* [cite_start][ ] **Networking Correcto:** El contenedor de Streamlit (`app`) debe poder comunicarse con la API (`api`) usando la red interna de Docker (ej. `http://api:8000`)[cite: 215].

### C. FastAPI: CRUD Zones + Routes (30 Puntos)
[cite_start]*Fuente: PDF Sección 11 [cite: 216]*
* [ ] **Endpoints Completos:** Deben funcionar `GET`, `POST`, `PUT`, `DELETE` para ambas entidades (`Zones` y `Routes`).
* [ ] **Validaciones:**
    * [cite_start]Error **400**: Para reglas de negocio (ej. Origen y Destino son iguales)[cite: 74, 77].
    * [cite_start]Error **404**: Cuando se busca un ID que no existe[cite: 78].
    * [cite_start]Error **422**: Validación automática de tipos (Pydantic)[cite: 79].

### D. Upload Parquet (15 Puntos)
[cite_start]*Fuente: PDF Sección 11 [cite: 217]*
* [ ] **Flujo Completo:** El sistema recibe el archivo, lo procesa y **crea o actualiza** las rutas en memoria automáticamente.
* [cite_start][ ] **Resumen:** El usuario debe ver un resumen con el conteo de: filas leídas, rutas creadas, rutas actualizadas y errores [cite: 112-121].

### E. Streamlit UX (10 Puntos)
[cite_start]*Fuente: PDF Sección 11 [cite: 218]*
* [ ] **Navegación:** Menú lateral o botones para ir a "Home", "Zones", "Routes" y "Upload".
* [ ] **Manejo de Errores:** Si la API falla, la interfaz debe mostrar un mensaje amigable, no el error crudo de Python.