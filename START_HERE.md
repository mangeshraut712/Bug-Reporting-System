# 🚀 Bug Reporting System - START HERE

Welcome! This is a complete, production-ready bug tracking application. Here's how to get started.

## 📖 Documentation Guide

Read these in order:

1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ⚡ (5 min read)
   - Quick start commands
   - Key endpoints
   - Common tasks
   - **Start here if you want to run it immediately**

2. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** 🔧 (15 min read)
   - Detailed setup instructions
   - Backend setup
   - Frontend setup
   - Docker setup
   - Troubleshooting guide
   - **Read this for step-by-step instructions**

3. **[README.md](README.md)** 📚 (20 min read)
   - Project features
   - Tech stack
   - Project structure
   - API endpoints overview
   - Database models
   - **Read this for complete project overview**

4. **[API_REFERENCE.md](API_REFERENCE.md)** 🔌 (30 min read)
   - Complete API documentation
   - All endpoints with examples
   - Request/response formats
   - Error codes
   - **Read this to understand the API**

5. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** 📋 (15 min read)
   - Project completion status
   - Technology stack details
   - File structure
   - Database models
   - Performance metrics
   - **Read this for technical details**

6. **[IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)** ✅ (10 min read)
   - Complete implementation checklist
   - All features verified
   - Code quality metrics
   - Verification steps
   - **Read this to verify everything is complete**

---

## ⚡ Quick Start (Choose One)

### Option 1: Local Development (Recommended for first-time)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend (in new terminal)
cd frontend
npm install
cp .env.example .env
npm start
```

**Access**: 
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs/

### Option 2: Docker (Recommended for production)

```bash
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

**Access**:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## 🎯 What You Can Do

### Create & Manage Projects
- Create new projects
- View all your projects
- Update project details
- Delete projects

### Track Issues
- Create issues with title, description, priority
- Assign issues to team members
- Update issue status (open → in_progress → closed)
- Filter issues by status and priority
- Search issues by keyword

### Collaborate with Comments
- Add comments to issues
- View all comments on an issue
- Edit your comments
- Delete comments

### User Management
- Register new accounts
- Login with email/password
- Manage your profile
- Logout securely

---

## 📁 Project Structure

```
Bug-Reporting-System/
├── backend/              Django REST API
│   ├── accounts/        User authentication
│   ├── projects/        Project management
│   ├── issues/          Issue tracking
│   ├── comments/        Issue comments
│   └── requirements.txt
├── frontend/            React application
│   ├── src/
│   │   ├── pages/       Login, Register, Dashboard, Issues
│   │   ├── components/  Navbar, PrivateRoute, Spinner
│   │   ├── contexts/    AuthContext for state
│   │   └── services/    API client
│   └── package.json
├── docker-compose.yml   Docker configuration
└── Documentation files  (README, SETUP_GUIDE, API_REFERENCE, etc.)
```

---

## 🔑 Key Features

✅ **JWT Authentication** - Secure token-based auth
✅ **Role-Based Permissions** - Only reporters/assignees can update issues
✅ **Query Optimization** - Eliminated N+1 queries
✅ **Responsive Design** - Works on mobile and desktop
✅ **API Documentation** - Interactive Swagger UI
✅ **Docker Support** - Easy deployment
✅ **Comprehensive Tests** - 22 unit tests
✅ **Error Handling** - Proper HTTP status codes
✅ **Pagination** - Efficient data loading
✅ **Search & Filter** - Find issues quickly

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific app tests
pytest accounts/tests.py
pytest projects/tests.py
pytest issues/tests.py
pytest comments/tests.py
```

---

## 📊 API Overview

| Resource | Endpoints |
|----------|-----------|
| Auth | Register, Login, Logout, Get User |
| Projects | List, Create, Get, Update, Delete |
| Issues | List, Create, Get, Update, Delete, Status, Assign |
| Comments | List, Create, Get, Update, Delete |

**Total: 20+ endpoints**

See [API_REFERENCE.md](API_REFERENCE.md) for complete documentation.

---

## 🔧 Environment Setup

### Backend (.env)
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `python manage.py runserver 8001` |
| Port 3000 in use | `PORT=3001 npm start` |
| CORS error | Check `CORS_ALLOWED_ORIGINS` in .env |
| Database error | Delete `db.sqlite3` and run migrations |
| Module not found | Activate venv and reinstall dependencies |

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more troubleshooting.

---

## 📚 Technology Stack

### Backend
- Django 4.2 + Django REST Framework
- PostgreSQL / SQLite
- JWT Authentication
- Gunicorn

### Frontend
- React 18 + React Router v6
- Axios + Tailwind CSS
- Lucide Icons
- React Toastify

### DevOps
- Docker & Docker Compose
- PostgreSQL 15

---

## 🚀 Deployment

### Backend (Render)
1. Push to GitHub
2. Create Web Service on Render
3. Set environment variables
4. Deploy

### Frontend (Netlify)
1. Push to GitHub
2. Connect to Netlify
3. Set build command: `npm run build`
4. Deploy

---

## 📞 Need Help?

1. **Quick questions?** → Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. **Setup issues?** → Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. **API questions?** → Check [API_REFERENCE.md](API_REFERENCE.md)
4. **Project details?** → Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
5. **Verify everything?** → Check [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)

---

## ✅ Next Steps

1. **Read** [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (5 minutes)
2. **Follow** [SETUP_GUIDE.md](SETUP_GUIDE.md) to set up locally
3. **Test** the application by creating projects and issues
4. **Explore** the API at http://localhost:8000/api/docs/
5. **Review** the code structure
6. **Run** the test suite: `pytest`
7. **Deploy** using Docker or your preferred platform

---

## 📈 Project Stats

- **Backend**: 50+ Python files
- **Frontend**: 20+ JavaScript files
- **Documentation**: 6 comprehensive guides
- **Tests**: 22 unit tests
- **API Endpoints**: 20+
- **Database Models**: 4
- **Components**: 3
- **Pages**: 5

---

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

## 💡 Pro Tips

1. **Use Docker** for consistent development environment
2. **Run tests** before deploying to catch issues early
3. **Check API docs** at `/api/docs/` for endpoint details
4. **Use admin panel** at `/admin/` to manage data
5. **Enable debug mode** only in development
6. **Keep .env files** out of version control
7. **Use meaningful commit messages** for better history

---

## 🎉 You're Ready!

Everything is set up and ready to go. Choose your setup method above and start building!

**Questions?** Check the documentation files listed above.

**Ready to start?** Go to [QUICK_REFERENCE.md](QUICK_REFERENCE.md) →

---

**Happy bug tracking! 🐛**
