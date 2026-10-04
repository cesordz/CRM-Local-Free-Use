# CRM Local - Plataforma de Uso Libre y Entorno Didactico de QA

[![CI - QA Tests & Coverage](https://github.com/cesordz/CRM-Local-Free-Use/actions/workflows/ci.yml/badge.svg)](https://github.com/cesordz/CRM-Local-Free-Use/actions/workflows/ci.yml)

Sistema de gestion de clientes (CRM) local desarrollado con Python, FastAPI, SQLite y Jinja2. Este proyecto esta concebido como una aplicacion de codigo abierto, utilitaria y de uso libre, disenada explicitamente para servir como entorno didactico y de referencia para profesionales y estudiantes de Control y Aseguramiento de Calidad (QA) y Automatizacion de Pruebas de Software.

---

## Proposito y Enfoque Educativo

En la formacion practica de QA, frecuentemente faltan aplicaciones completas, ligeras y predecibles que permitan enseñar y ejercitar las distintas tecnicas de prueba sin depender de infraestructuras complejas en la nube. 

Este proyecto resuelve esa necesidad ofreciendo:
1. **Ejercitacion de Tecnicas de Diseno de Pruebas**:
   - **Particion de Equivalencia**: Validacion de formatos de correo y campos de texto requeridos.
   - **Analisis de Valores Limite**: Control estricto de longitud de telefono (9, 10 y 11 digitos, caracteres no numericos).
   - **Pruebas de Unicidad**: Validacion de correos duplicados con codigos de estado semanticos.
   - **Integridad Referencial de Datos**: Borrado en cascada verificado entre clientes y sus notas asociadas.
2. **Implementacion del Patron Page Object Model (POM)**:
   - Estructura desacoplada y mantenible para pruebas End-to-End con Playwright, aislando selectores y acciones de los asertos.
3. **Piramide de Pruebas Completa**:
   - Cobertura integral organizada en pruebas unitarias, de integracion y E2E sobre navegador real.
4. **Ambiente de Aprendizaje Seguro**:
   - Ejecutable en local con cero dependencias externas o costos operativos, ideal para talleres, cursos o demostraciones de portafolio.

---

## Caracteristicas del Sistema

- **Gestion Integral de Clientes (CRUD)**:
  - Registro, modificacion, consulta detallada y eliminacion de clientes.
  - Atributos: Nombre completo, correo electronico, telefono de 10 digitos y empresa.
- **Modulo de Notas de Seguimiento**:
  - Relacion uno a muchos: multiples notas cronologicas por cliente.
  - Eliminacion individual de notas.
  - Persistencia relacional con eliminacion en cascada mediante activacion de `PRAGMA foreign_keys = ON;` en SQLite.
- **Busqueda Dinamica**:
  - Filtrado en tiempo real por coincidencia parcial de nombre (case-insensitive).
- **Doble Interfaz de Consumo**:
  - **Interfaz Web (SSR con Jinja2)**: Diseno utilitario y sobrio, tipografia local Cascadia Mono (sin llamadas externas a CDN), contraste alto bajo estandar WCAG AA y selectores `data-testid` estables.
  - **API REST (JSON)**: Endpoints semanticos (`/api/clients`, `/api/notes`) con documentacion interactiva OpenAPI / Swagger en `/docs`.

---

## Reglas de Negocio y Comportamiento Esperado

| Campo | Regla de Negocio | Tecnica de QA Aplicable | Resultado del Sistema |
| :--- | :--- | :--- | :--- |
| **Nombre** | Obligatorio, sanitizado contra espacios en blanco. | Particion de Equivalencia. | Rechaza cadenas vacias o de solo espacios (HTTP 422). |
| **Correo** | Formato RFC estandar y valor unico en base de datos. | Pruebas de unicidad e invalidos. | Rechaza duplicados y formatos corruptos (HTTP 422 en Web / 409 en API). |
| **Telefono** | Exactamente 10 digitos numericos (`^\d{10}$`). | Analisis de Valores Limite (9, 10 y 11 digitos). | Rechaza longitudes incorrectas, letras o caracteres especiales (HTTP 422). |
| **Notas** | Contenido requerido no vacio. | Pruebas negativas de obligatoriedad. | Rechaza notas vacias (HTTP 422). |

---

## Estructura del Repositorio

```text
CRM-Local Free Use/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de integracion continua (CI) y cobertura
├── app/
│   ├── database.py              # Configuracion de SQLite con claves foraneas activas
│   ├── models.py                # Modelos ORM relacionales (Client, Note)
│   ├── schemas.py               # Validadores Pydantic v2 (regex, tipos, sanitizacion)
│   ├── services.py              # Capa de logica de negocio y excepciones de dominio
│   ├── routers/
│   │   ├── clients.py           # Rutas y controladores de vistas web para clientes
│   │   ├── notes.py             # Controladores de notas de seguimiento
│   │   └── api.py               # Endpoints de API REST en formato JSON
│   ├── static/
│   │   ├── style.css            # Estilos utilitarios locales sin dependencias externas
│   │   └── fonts/               # Tipografia local Cascadia Mono (.woff2)
│   └── templates/
│       ├── base.html            # Plantilla maestra con navegacion minima
│       ├── components/          # Componentes reutilizables (alertas)
│       └── clients/             # Vistas de listado, formulario y detalle
├── pages/                       # Page Object Model (POM) para automatizacion E2E
│   ├── base_page.py             # Clase base con utilidades de navegacion y alertas
│   ├── client_list_page.py      # Page Object de tabla y buscador de clientes
│   ├── client_form_page.py      # Page Object de formulario de alta y edicion
│   └── client_detail_page.py    # Page Object de ficha de detalle y notas
├── tests/                       # Suite automatizada de pruebas
│   ├── conftest.py              # Fixtures de base de datos en memoria y TestClient
│   ├── test_validations.py      # Pruebas unitarias de esquemas y validaciones
│   ├── test_services.py         # Pruebas de capa de servicio y persistencia
│   ├── test_endpoints.py        # Pruebas funcionales de endpoints y vistas
│   ├── test_client_crud.py      # Pruebas de integracion del flujo de clientes
│   ├── test_notes_and_cascade.py# Pruebas de integridad referencial en cascada
│   └── e2e/                     # Pruebas End-to-End con Playwright
│       ├── conftest.py          # Fixture de servidor local y capturas en fallo
│       ├── test_client_crud_flow.py        # Flujos de usuario completos
│       └── test_client_validation_flow.py  # Pruebas de validacion visual
├── requirements.txt
└── README.md
```

---

## Puesta en Marcha Local

### Requisitos Previos
- Python 3.10 o superior instalado.

### 1. Creacion y Activacion del Entorno Virtual
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalacion de Dependencias y Navegadores
```powershell
pip install -r requirements.txt
playwright install chromium
```

### 3. Ejecucion del Servidor
```powershell
uvicorn app.main:app --reload
```

- **Interfaz Web**: http://127.0.0.1:8000
- **Documentacion Interactiva OpenAPI**: http://127.0.0.1:8000/docs

---

## Ejecucion de la Suite de Pruebas

El proyecto cuenta con 135 pruebas automatizadas organizadas modularmente.

```powershell
# Ejecutar todas las pruebas (Unitarias, Integracion y E2E)
pytest

# Ejecutar con salida detallada por caso
pytest -v

# Ejecutar exclusivamente la suite E2E con Playwright
pytest tests/e2e/ -v

# Ejecutar con medicion y reporte de cobertura de codigo
pytest --cov=app --cov-report=term-missing
```

### Diagnostico Visual de Fallos (Screenshots)
La suite E2E incorpora un hook de captura automatica (`pytest_runtest_makereport`). Si alguna prueba en el navegador falla, se genera instantaneamente una captura de pantalla del estado exacto del DOM dentro del directorio `tests/e2e/screenshots/` para su analisis forense.

---

## Selectores Semanticos para Automatizacion (`data-testid`)

Para garantizar que los scripts de prueba no dependan de clases visuales que puedan variar, la interfaz expone atributos estables:

- **Formularios**:
  - `data-testid="input-client-name"`
  - `data-testid="input-client-email"`
  - `data-testid="input-client-phone"`
  - `data-testid="input-client-company"`
  - `data-testid="btn-submit-client"`
  - `data-testid="btn-cancel-form"`
- **Errores de Validacion**:
  - `data-testid="error-name"`
  - `data-testid="error-email"`
  - `data-testid="error-phone"`
  - `data-testid="error-company"`
  - `data-testid="error-note-content"`
- **Tabla y Buscador**:
  - `data-testid="search-input"`
  - `data-testid="search-submit-btn"`
  - `data-testid="search-clear-btn"`
  - `data-testid="clients-table"`
  - `data-testid="client-row-{id}"`
- **Ficha y Notas**:
  - `data-testid="input-note-content"`
  - `data-testid="btn-submit-note"`
  - `data-testid="notes-list"`
  - `data-testid="delete-note-{id}"`

---

## Uso Libre y Licencia

Este software se distribuye de manera libre y abierta. Esta permitido su uso, copia, modificacion y adaptacion tanto para fines de ensenanza, practica academica, evaluaciones tecnicas de reclutamiento o integracion en portafolios personales.
