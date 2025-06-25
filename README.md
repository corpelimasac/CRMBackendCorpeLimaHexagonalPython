# 🏗️ CRM Backend - Arquitectura Hexagonal

Sistema CRM desarrollado con **FastAPI** y **SQLAlchemy** siguiendo los principios de la **Arquitectura Hexagonal** (Puertos y Adaptadores).

## 📋 Tabla de Contenidos

- [🏗️ Arquitectura](#️-arquitectura)
- [📁 Estructura de Carpetas](#-estructura-de-carpetas)
- [🚀 Características](#-características)
- [📋 Prerrequisitos](#-prerrequisitos)
- [🛠️ Instalación](#️-instalación)
- [🏃‍♂️ Uso](#️-uso)
- [🧪 Testing](#-testing)
- [🐳 Docker](#-docker)
- [📚 Documentación](#-documentación)
- [🤝 Contribución](#-contribución)

## 🏗️ Arquitectura

Este proyecto implementa la **Arquitectura Hexagonal** (también conocida como Ports & Adapters), que separa la lógica de negocio de los detalles de implementación técnica, permitiendo:

- ✅ **Independencia de frameworks**: La lógica de negocio no depende de FastAPI
- ✅ **Testabilidad**: Fácil testing mediante mocks de los puertos
- ✅ **Flexibilidad**: Cambio de implementaciones sin afectar el core
- ✅ **Mantenibilidad**: Código organizado y fácil de mantener

### Principios de la Arquitectura Hexagonal

1. **Núcleo (Core)**: Contiene la lógica de negocio pura
2. **Puertos**: Definen interfaces para comunicación con el exterior
3. **Adaptadores**: Implementan los puertos para tecnologías específicas
4. **Inversión de dependencias**: El core no conoce los detalles de implementación

## 📁 Estructura de Carpetas

```
CRMBackendHexagonalPython/
├── 📁 app/                              # Aplicación principal
│   ├── 📄 main.py                       # Punto de entrada FastAPI
│   │
│   ├── 📁 core/                         # 🎯 NÚCLEO - Lógica de negocio
│   │   ├── 📁 domain/                   # Dominio del negocio
│   │   │   ├── 📁 entities/             # Entidades del dominio
│   │   │   │   ├── 📄 user.py           # Entidad Usuario
│   │   │   │   ├── 📄 product.py        # Entidad Producto
│   │   │   │   └── 📄 order.py          # Entidad Orden
│   │   │   │
│   │   │   ├── 📁 value_objects/        # Objetos de valor
│   │   │   │   ├── 📄 email.py          # Value Object Email
│   │   │   │   └── 📄 money.py          # Value Object Money
│   │   │   │
│   │   │   └── 📁 exceptions/           # Excepciones del dominio
│   │   │       ├── 📄 business_exceptions.py
│   │   │       └── 📄 validation_exceptions.py
│   │   │
│   │   ├── 📁 ports/                    # 🔌 PUERTOS - Interfaces
│   │   │   ├── 📁 repositories/         # Puertos de repositorios
│   │   │   │   ├── 📄 user_repository.py
│   │   │   │   ├── 📄 product_repository.py
│   │   │   │   └── 📄 order_repository.py
│   │   │   │
│   │   │   └── 📁 services/             # Puertos de servicios externos
│   │   │       ├── 📄 email_service.py
│   │   │       ├── 📄 payment_service.py
│   │   │       └── 📄 notification_service.py
│   │   │
│   │   └── 📁 use_cases/                # 🎯 CASOS DE USO
│   │       ├── 📁 user/                 # Casos de uso de usuarios
│   │       │   ├── 📄 create_user.py    # Crear usuario
│   │       │   ├── 📄 get_user.py       # Obtener usuario
│   │       │   ├── 📄 update_user.py    # Actualizar usuario
│   │       │   └── 📄 delete_user.py    # Eliminar usuario
│   │       │
│   │       ├── 📁 product/              # Casos de uso de productos
│   │       │   ├── 📄 create_product.py
│   │       │   ├── 📄 get_products.py
│   │       │   └── 📄 update_product.py
│   │       │
│   │       └── 📁 order/                # Casos de uso de órdenes
│   │           ├── 📄 create_order.py
│   │           ├── 📄 get_orders.py
│   │           └── 📄 process_order.py
│   │
│   ├── 📁 adapters/                     # 🔌 ADAPTADORES
│   │   ├── 📁 inbound/                  # Adaptadores de entrada
│   │   │   ├── 📁 api/                  # REST API (FastAPI)
│   │   │   │   ├── 📄 dependencies.py   # Inyección de dependencias
│   │   │   │   ├── 📄 middleware.py     # Middlewares personalizados
│   │   │   │   │
│   │   │   │   ├── 📁 routers/          # Routers de FastAPI
│   │   │   │   │   ├── 📄 users.py      # Endpoints de usuarios
│   │   │   │   │   ├── 📄 products.py   # Endpoints de productos
│   │   │   │   │   ├── 📄 orders.py     # Endpoints de órdenes
│   │   │   │   │   └── 📄 health.py     # Health check
│   │   │   │   │
│   │   │   │   └── 📁 schemas/          # Esquemas Pydantic
│   │   │   │       ├── 📄 user_schemas.py
│   │   │   │       ├── 📄 product_schemas.py
│   │   │   │       ├── 📄 order_schemas.py
│   │   │   │       └── 📄 common_schemas.py
│   │   │   │
│   │   │   └── 📁 cli/                  # Command Line Interface
│   │   │       └── 📄 commands.py
│   │   │
│   │   └── 📁 outbound/                 # Adaptadores de salida
│   │       ├── 📁 database/             # Persistencia de datos
│   │       │   ├── 📄 connection.py     # Conexión a BD
│   │       │   │
│   │       │   ├── 📁 models/           # Modelos SQLAlchemy
│   │       │   │   ├── 📄 base.py       # Modelo base
│   │       │   │   ├── 📄 user_model.py
│   │       │   │   ├── 📄 product_model.py
│   │       │   │   └── 📄 order_model.py
│   │       │   │
│   │       │   ├── 📁 repositories/     # Implementaciones
│   │       │   │   ├── 📄 sqlalchemy_user_repository.py
│   │       │   │   ├── 📄 sqlalchemy_product_repository.py
│   │       │   │   └── 📄 sqlalchemy_order_repository.py
│   │       │   │
│   │       │   └── 📁 migrations/       # Migraciones Alembic
│   │       │       ├── 📄 env.py
│   │       │       └── 📁 versions/
│   │       │
│   │       ├── 📁 external_services/    # Servicios externos
│   │       │   ├── 📁 email/            # Servicio de email
│   │       │   │   └── 📄 smtp_email_service.py
│   │       │   │
│   │       │   ├── 📁 payment/          # Servicio de pagos
│   │       │   │   └── 📄 stripe_payment_service.py
│   │       │   │
│   │       │   └── 📁 notification/     # Servicio de notificaciones
│   │       │       └── 📄 firebase_notification_service.py
│   │       │
│   │       └── 📁 cache/                # Sistema de caché
│   │           └── 📄 redis_cache.py
│   │
│   ├── 📁 config/                       # ⚙️ CONFIGURACIÓN
│   │   ├── 📄 settings.py               # Configuración principal
│   │   ├── 📄 database.py               # Configuración de BD
│   │   └── 📄 dependencies.py           # Inyección de dependencias
│   │
│   └── 📁 shared/                       # 🔧 UTILIDADES COMPARTIDAS
│       ├── 📁 utils/                    # Utilidades generales
│       │   ├── 📄 datetime_utils.py
│       │   ├── 📄 validation_utils.py
│       │   └── 📄 security_utils.py
│       │
│       ├── 📁 constants/                # Constantes de la aplicación
│       │   └── 📄 app_constants.py
│       │
│       └── 📁 types/                    # Tipos personalizados
│           └── 📄 custom_types.py
│
├── 📁 tests/                            # 🧪 TESTS
│   ├── 📁 unit/                         # Tests unitarios
│   │   ├── 📁 core/                     # Tests del core
│   │   │   ├── 📁 domain/               # Tests del dominio
│   │   │   │   ├── 📄 test_entities.py
│   │   │   │   └── 📄 test_value_objects.py
│   │   │   │
│   │   │   └── 📁 use_cases/            # Tests de casos de uso
│   │   │       ├── 📄 test_user_use_cases.py
│   │   │       ├── 📄 test_product_use_cases.py
│   │   │       └── 📄 test_order_use_cases.py
│   │   │
│   │   └── 📁 adapters/                 # Tests de adaptadores
│   │       ├── 📄 test_repositories.py
│   │       └── 📄 test_services.py
│   │
│   ├── 📁 integration/                  # Tests de integración
│   │   ├── 📄 test_api_endpoints.py
│   │   ├── 📄 test_database_integration.py
│   │   └── 📄 test_external_services.py
│   │
│   ├── 📁 e2e/                          # Tests end-to-end
│   │   └── 📄 test_complete_workflows.py
│   │
│   ├── 📁 fixtures/                     # Fixtures para tests
│   │   ├── 📄 database_fixtures.py
│   │   └── 📄 test_data.py
│   │
│   └── 📄 conftest.py                   # Configuración pytest
│
├── 📁 docs/                             # 📚 DOCUMENTACIÓN
│   ├── 📁 api/                          # Documentación API
│   │   └── 📄 openapi.yaml
│   │
│   ├── 📁 architecture/                 # Documentación arquitectura
│   │   ├── 📄 hexagonal_architecture.md
│   │   └── 📄 domain_model.md
│   │
│   └── 📁 deployment/                   # Documentación despliegue
│       └── 📄 docker_setup.md
│
├── 📁 scripts/                          # 🔧 SCRIPTS DE UTILIDAD
│   ├── 📄 setup_db.py                   # Configurar base de datos
│   ├── 📄 seed_data.py                  # Cargar datos de prueba
│   └── 📄 run_migrations.py             # Ejecutar migraciones
│
├── 📁 docker/                           # 🐳 CONFIGURACIÓN DOCKER
│   ├── 📄 Dockerfile                    # Imagen Docker
│   ├── 📄 docker-compose.yml            # Servicios producción
│   └── 📄 docker-compose.dev.yml        # Servicios desarrollo
│
├── 📄 .env.example                      # Variables de entorno ejemplo
├── 📄 .env                              # Variables de entorno (no versionar)
├── 📄 .gitignore                        # Archivos ignorados por Git
├── 📄 requirements.txt                  # Dependencias Python
├── 📄 requirements-dev.txt              # Dependencias desarrollo
├── 📄 pyproject.toml                    # Configuración del proyecto
└── 📄 README.md                         # Este archivo
```

## 🚀 Características

### Arquitectura y Diseño
- ✅ **Arquitectura Hexagonal**: Separación clara entre lógica de negocio e infraestructura
- ✅ **Domain-Driven Design**: Modelado basado en el dominio del negocio
- ✅ **SOLID Principles**: Código mantenible y extensible
- ✅ **Clean Code**: Código legible y bien documentado

### Tecnologías
- ✅ **FastAPI**: Framework moderno y rápido para APIs REST
- ✅ **SQLAlchemy**: ORM potente con soporte para múltiples bases de datos
- ✅ **Pydantic**: Validación de datos y serialización
- ✅ **Python 3.11**: Aprovechando las últimas características del lenguaje

### Funcionalidades
- ✅ **API REST**: Endpoints bien documentados con OpenAPI/Swagger
- ✅ **Validación automática**: Validación de datos de entrada y salida
- ✅ **Inyección de dependencias**: Desacoplamiento de componentes
- ✅ **Manejo de errores**: Sistema robusto de manejo de excepciones
- ✅ **Logging**: Sistema de logs configurable
- ✅ **Testing**: Estructura completa para diferentes tipos de tests

### Calidad y Desarrollo
- ✅ **Type Hints**: Tipado estático para mejor desarrollo
- ✅ **Documentación automática**: Swagger UI y ReDoc
- ✅ **Migraciones**: Control de versiones de base de datos con Alembic
- ✅ **Docker**: Configuración para contenedorización
- ✅ **Environment-based Config**: Configuración por entornos

## 📋 Prerrequisitos

- **Python 3.11+**
- **MySQL 8.0+** (o PostgreSQL/SQLite)
- **Redis** (opcional, para caché)
- **Docker** (opcional, para contenedorización)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd CRMBackendHexagonalPython
```

### 2. Crear entorno virtual
```bash
python -m venv .venv

# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
# Dependencias de producción
pip install -r requirements.txt

# Dependencias de desarrollo (opcional)
pip install -r requirements-dev.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones específicas
```

### 5. Configurar base de datos
```bash
# Crear la base de datos MySQL
mysql -u root -p
CREATE DATABASE crm_db;

# Ejecutar migraciones (cuando estén configuradas)
alembic upgrade head
```

## 🏃‍♂️ Uso

### Ejecutar la aplicación

```bash
# Desarrollo (con auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# O usando el archivo main.py directamente
python app/main.py

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Acceder a la documentación
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

### Endpoints principales
```
GET    /api/v1/health              # Health check
GET    /api/v1/users               # Listar usuarios
POST   /api/v1/users               # Crear usuario
GET    /api/v1/users/{id}          # Obtener usuario
PUT    /api/v1/users/{id}          # Actualizar usuario
DELETE /api/v1/users/{id}          # Eliminar usuario
```

## 🧪 Testing

### Ejecutar tests
```bash
# Todos los tests
pytest

# Tests unitarios
pytest tests/unit/

# Tests de integración
pytest tests/integration/

# Tests E2E
pytest tests/e2e/

# Con coverage
pytest --cov=app --cov-report=html
```

### Estructura de testing
- **Unit Tests**: Prueban componentes individuales del core
- **Integration Tests**: Prueban la integración entre adaptadores
- **E2E Tests**: Prueban flujos completos de usuario

## 🐳 Docker

### Desarrollo
```bash
docker-compose -f docker/docker-compose.dev.yml up -d
```

### Producción
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### Construir imagen personalizada
```bash
docker build -t crm-backend -f docker/Dockerfile .
```

## 📚 Documentación

### Documentación adicional disponible:
- **Arquitectura Hexagonal**: `docs/architecture/hexagonal_architecture.md`
- **Modelo de Dominio**: `docs/architecture/domain_model.md`
- **Configuración Docker**: `docs/deployment/docker_setup.md`
- **API Documentation**: Disponible en `/docs` cuando la app está corriendo

## 🔧 Scripts de Utilidad

```bash
# Configurar base de datos inicial
python scripts/setup_db.py

# Cargar datos de prueba
python scripts/seed_data.py

# Ejecutar migraciones
python scripts/run_migrations.py
```

## 🤝 Contribución

### Flujo de trabajo
1. Fork del proyecto
2. Crear rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

### Estándares de código
- Seguir PEP 8 para el estilo de código Python
- Usar type hints en todas las funciones
- Documentar todas las clases y métodos públicos
- Mantener cobertura de tests > 80%
- Ejecutar tests antes de hacer commit

## 📝 Notas Importantes

### Arquitectura Hexagonal
- **Core**: Nunca debe importar de `adapters`
- **Ports**: Solo definen interfaces, no implementaciones
- **Adapters**: Implementan los puertos para tecnologías específicas
- **Use Cases**: Orquestan la lógica de negocio usando puertos

### Python 3.11 Features
- Este proyecto **NO utiliza archivos `__init__.py`** aprovechando las **Implicit Namespace Packages** de Python 3.3+
- Se aprovechan las nuevas características de tipado de Python 3.11
- Mejor rendimiento y sintaxis más limpia

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Autores

- **Tu Nombre** - *Desarrollo inicial* - [@tu_usuario](https://github.com/tu_usuario)

## 🙏 Agradecimientos

- Inspirado en los principios de **Clean Architecture** de Robert C. Martin
- Basado en las mejores prácticas de **FastAPI**
- Siguiendo los patrones de **Domain-Driven Design**
- Implementando **Ports & Adapters Pattern** de Alistair Cockburn

---

⭐ **¡No olvides dar una estrella al proyecto si te fue útil!** ⭐ 