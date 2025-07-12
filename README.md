# ReWear Backend - Community Clothing Exchange Platform

> **Phase 1: Foundation & Infrastructure** ✅ COMPLETED

A sustainable fashion platform that enables users to exchange unused clothing through direct swaps or a point-based redemption system. Built with FastAPI, PostgreSQL, and Redis.

## 🎯 Project Overview

ReWear promotes sustainable fashion and reduces textile waste by encouraging users to reuse wearable garments instead of discarding them. The platform features user authentication, item listings, swap mechanisms, and an admin moderation system.

## 📋 Phase 1 Accomplishments

### ✅ Infrastructure Setup
- **FastAPI Application**: Complete project structure with organized directories
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Caching Layer**: Redis integration for performance optimization
- **Development Environment**: Docker Compose for local development
- **Configuration Management**: Environment-based settings with Pydantic

### ✅ Core Systems
- **Health Monitoring**: Database and Redis connection testing
- **CORS Configuration**: Cross-origin resource sharing setup
- **Error Handling**: Basic error handling and logging
- **Development Tools**: Hot reload and debugging capabilities

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rewear-backend
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start services**
   ```bash
   docker-compose up -d
   ```

5. **Configure environment**
   ```bash
   # Generate a secret key
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
   
   # Update .env file with your secret key
   cp .env.example .env  # Edit with your values
   ```

6. **Start the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Verify Installation

- **API Health**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Basic Info**: http://localhost:8000

Expected health check response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "environment": "development"
}
```

## 🏗️ Project Structure

```
rewear-backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection and setup
│   ├── models/              # SQLAlchemy database models
│   │   ├── user.py          # User model and relationships
│   │   ├── item.py          # Item/clothing model
│   │   ├── swap.py          # Swap transaction model
│   │   └── category.py      # Category classification model
│   ├── schemas/             # Pydantic request/response models
│   │   ├── user.py          # User API schemas
│   │   ├── item.py          # Item API schemas
│   │   └── swap.py          # Swap API schemas
│   ├── api/
│   │   ├── deps.py          # API dependencies
│   │   └── routes/          # API route handlers
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── users.py     # User management endpoints
│   │       ├── items.py     # Item CRUD endpoints
│   │       └── admin.py     # Admin panel endpoints
│   ├── core/                # Core utilities and security
│   │   ├── security.py      # JWT auth, password hashing
│   │   └── utils.py         # Helper functions
│   └── services/            # Business logic services
│       ├── auth_service.py  # Authentication business logic
│       ├── item_service.py  # Item management logic
│       └── swap_service.py  # Swap transaction logic
├── alembic/                 # Database migrations
├── docker-compose.yml       # Local development services
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | FastAPI | High-performance async web framework |
| **Database** | PostgreSQL 15 | Primary data storage |
| **ORM** | SQLAlchemy 2.0 | Database abstraction layer |
| **Cache** | Redis 7 | Session storage and caching |
| **Configuration** | Pydantic Settings | Type-safe environment configuration |
| **Development** | Docker Compose | Local service orchestration |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://postgres:password@127.0.0.1:5432/rewear` |
| `SECRET_KEY` | JWT signing secret | *Required - generate unique* |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `DEBUG` | Development mode | `True` |
| `ENVIRONMENT` | Runtime environment | `development` |

### Development Services

```yaml
# docker-compose.yml
services:
  postgres:    # Port 5432
  redis:       # Port 6379
```

## 📈 Next Phases

### 🔄 Phase 2: Database Models & Authentication
- [ ] User, Item, Swap, Category models
- [ ] Database migrations with Alembic
- [ ] JWT authentication system
- [ ] Password hashing and security

### 🔄 Phase 3: Core API Endpoints & Business Logic
- [ ] User management (registration, login, profile)
- [ ] Item CRUD operations
- [ ] Swap request system
- [ ] Points management
- [ ] Service layer implementation

### 🔄 Phase 4: Advanced Features
- [ ] Real-time notifications (WebSockets)
- [ ] Image upload and processing
- [ ] Search and filtering
- [ ] Admin moderation panel

### 🔄 Phase 5: Production Ready
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Deployment configuration
- [ ] Monitoring and logging

## 🧪 Development

### Running Tests
```bash
# Coming in Phase 2
pytest
```

### Code Quality
```bash
# Linting
flake8 app/

# Formatting
black app/

# Type checking
mypy app/
```

### Database Management
```bash
# Coming in Phase 2 with Alembic
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 📊 Health Monitoring

The application includes built-in health checks:

- **Database connectivity**: PostgreSQL connection status
- **Cache availability**: Redis connection status  
- **Service health**: Overall application status

Monitor at: `GET /health`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Built for sustainable fashion and environmental consciousness. Every piece of clothing deserves a second life! 🌱

---

**Status**: Phase 1 Complete ✅ | **Next**: Database Models & Authentication 🔄