# ReWear - Community Clothing Exchange Platform

A sustainable fashion platform that enables users to exchange unused clothing through direct swaps or a point-based redemption system. Built with FastAPI, PostgreSQL, and Redis.

## 🎯 Problem Statement

**ReWear** addresses the growing problem of textile waste and overconsumption in the fashion industry. Our platform promotes sustainable fashion by:

- **Reducing Textile Waste**: Enabling users to exchange unused clothing instead of discarding them
- **Promoting Circular Economy**: Creating a community-driven marketplace for pre-owned clothing
- **Incentivizing Reuse**: Implementing a points-based system to encourage participation
- **Building Sustainable Communities**: Connecting fashion-conscious individuals who value environmental responsibility

### Target Users
- Fashion enthusiasts looking for unique pieces
- Environmentally conscious consumers
- Budget-conscious shoppers seeking quality clothing
- People wanting to declutter their wardrobes responsibly

### Key Features
- **Direct Item Swapping**: Users can exchange items directly with each other
- **Points-Based Redemption**: Earn points by listing items, spend points to acquire desired pieces
- **User Authentication**: Secure user registration and profile management
- **Admin Moderation**: Content moderation to ensure quality and safety
- **Real-time Notifications**: Stay updated on swap requests and activity

## 👥 Team Members

- **Mohammed Huzaifa** - huzaifa.coder785@gmail.com
- **Omar Nahdi** - omarnahdi2021@gmail.com  
- **Shaikh Rayyan** - shaikhrayyanofficial@gmail.com

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/rewear-backend.git
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
   
   # Copy and edit environment file
   cp .env.example .env  # Edit with your generated secret key
   ```

6. **Initialize database**
   ```bash
   # Create tables
   python -c "from app.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)"
   ```

7. **Start the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Verify Installation

- **API Health**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Database UI**: http://localhost:8080 (pgAdmin: admin@rewear.com / admin123)

## 🏗️ Project Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend Framework** | FastAPI | High-performance async web framework |
| **Database** | PostgreSQL 15 | Primary data storage with complex relationships |
| **ORM** | SQLAlchemy 2.0 | Database abstraction and modeling |
| **Authentication** | JWT + BCrypt | Secure user authentication |
| **Validation** | Pydantic | Request/response validation |
| **Cache** | Redis 7 | Session storage and performance optimization |
| **Migrations** | Alembic | Database schema versioning |
| **Development** | Docker Compose | Local service orchestration |

### Database Schema

```
users (👤)
├── id, email, username
├── authentication (hashed_password)
├── profile (name, location, bio)
├── points (balance, earned, spent)
└── timestamps

categories (📂)  
├── id, name, slug
├── description, icon, color
└── metadata

items (👕)
├── id, title, description
├── owner_id → users.id
├── category_id → categories.id
├── specifications (size, condition, brand)
├── points_value, images
└── status tracking

swaps (🔄)
├── id, requester_id → users.id
├── item_id → items.id, item_owner_id → users.id
├── swap_type (direct_swap, points_redemption)
├── status (pending, accepted, completed)
├── communication (messages, responses)
└── timestamps

point_transactions (💰)
├── id, user_id → users.id
├── amount, transaction_type
├── related records (swap_id, item_id)
└── audit trail
```

### Key Relationships
- **Users** can own multiple **Items** (1:N)
- **Items** belong to **Categories** (N:1)
- **Swaps** connect **Users** as requesters and item owners (N:1, N:1)
- **Swaps** reference **Items** for exchanges (N:1)
- **PointTransactions** track user point history (N:1)

## 📋 Implementation Phases

### Phase 1: Foundation & Infrastructure
- FastAPI application setup with organized project structure
- PostgreSQL and Redis integration
- Docker Compose development environment
- Configuration management with environment variables
- Health monitoring and CORS setup

### Phase 2: Database Models & Authentication
- Complete SQLAlchemy models with relationships
- JWT token authentication with BCrypt password hashing
- Pydantic schemas for request/response validation
- Database migrations with Alembic
- User management utilities and points system foundation

### Phase 3: API Endpoints & Business Logic
- Authentication endpoints (register, login, logout)
- User profile management and dashboard
- Item CRUD operations with search and filtering
- Swap request system (create, approve, reject, complete)
- Points management and transaction history

### Phase 4: Advanced Features
- Real-time notifications with WebSockets
- Image upload and processing
- Advanced search and recommendation system
- Admin moderation panel
- Email notifications for important events

### Phase 5: Production & Deployment
- Comprehensive testing (unit, integration, API)
- Performance optimization and caching strategies
- Security hardening and rate limiting
- CI/CD pipeline and deployment configuration
- Monitoring, logging, and error tracking

## 🔧 Development

### Project Structure
```
rewear-backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes and dependencies
│   ├── core/                # Security and utilities
│   └── services/            # Business logic
├── alembic/                 # Database migrations
├── docker-compose.yml       # Development services
└── requirements.txt         # Python dependencies
```

### Environment Configuration

```bash
# Database
DATABASE_URL=postgresql+psycopg2://postgres:password@127.0.0.1:5432/rewear

# Security
SECRET_KEY=your-generated-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Services
REDIS_URL=redis://localhost:6379/0

# Development
ENVIRONMENT=development
DEBUG=True
```

### Database Management
```bash
# View current migration status
alembic current

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 🧪 Testing

### Sample Data Creation
```python
# Create test users, categories, and items
python -c "
from app.database import get_db
from app.models import User, Category, Item
from app.core.security import get_password_hash

# Create sample data for testing
# (See full implementation in repository)
"
```

### API Testing
- **Health Check**: `GET /health`
- **API Documentation**: Available at `/docs` with interactive testing
- **Database Inspection**: pgAdmin UI at http://localhost:8080

## 🌱 Sustainability Impact

ReWear contributes to environmental sustainability by:

- **Extending Clothing Lifespan**: Keeping garments in use longer
- **Reducing Manufacturing Demand**: Less need for new clothing production
- **Minimizing Textile Waste**: Diverting items from landfills
- **Promoting Conscious Consumption**: Encouraging thoughtful fashion choices
- **Building Community**: Connecting like-minded environmentally conscious users

## 📄 License

This project is licensed under the MIT License - promoting open-source sustainability solutions.

## 🙏 Acknowledgments

Built with passion for sustainable fashion and environmental consciousness. Every piece of clothing deserves a second life! 🌱

---

*Odoo Hackathon Project - Building a more sustainable future through technology*