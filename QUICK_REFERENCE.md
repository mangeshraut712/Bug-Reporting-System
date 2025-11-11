# Bug Reporting System - Quick Reference

## 🚀 Quick Start (5 minutes)

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend (new terminal)
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

**Access**: Frontend at `http://localhost:3000` | Backend at `http://localhost:8000`

---

## 🐳 Docker Quick Start

```bash
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

**Access**: `http://localhost:3000` (frontend) | `http://localhost:8000` (backend)

---

## 📁 Project Structure

```
backend/          Django REST API
├── accounts/     User authentication
├── projects/     Project management
├── issues/       Issue tracking
└── comments/     Issue comments

frontend/         React application
├── components/   Reusable UI components
├── pages/        Page components
├── contexts/     State management
└── services/     API client
```

---

## 🔑 Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register user |
| POST | `/api/auth/login/` | Login user |
| GET | `/api/projects/` | List projects |
| POST | `/api/projects/` | Create project |
| GET | `/api/issues/` | List issues |
| POST | `/api/issues/` | Create issue |
| GET | `/api/comments/` | List comments |
| POST | `/api/comments/` | Create comment |

See `API_REFERENCE.md` for complete API documentation.

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific app
pytest accounts/tests.py
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `SETUP_GUIDE.md` | Detailed setup & troubleshooting |
| `API_REFERENCE.md` | Complete API documentation |
| `PROJECT_SUMMARY.md` | Project overview |
| `QUICK_REFERENCE.md` | This quick reference |

---

## 🔧 Environment Variables

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

## 🎯 Common Tasks

### Create Superuser
```bash
python manage.py createsuperuser
```

### Run Migrations
```bash
python manage.py migrate
```

### Create Test Data
```bash
python manage.py shell
```

### Access Admin Panel
```
http://localhost:8000/admin/
```

### View API Documentation
```
http://localhost:8000/api/docs/
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `python manage.py runserver 8001` |
| Port 3000 in use | `PORT=3001 npm start` |
| CORS error | Check `CORS_ALLOWED_ORIGINS` in .env |
| Database error | Delete `db.sqlite3` and run migrations |
| Module not found | Activate venv and reinstall: `pip install -r requirements.txt` |

See `SETUP_GUIDE.md` for more troubleshooting.

---

## 📊 Database Models

- **User**: Custom user model with email authentication
- **Project**: Contains multiple issues
- **Issue**: Has status, priority, reporter, assignee
- **Comment**: Attached to issues

---

## 🔐 Authentication Flow

1. User registers with email/password
2. User logs in → receives JWT tokens
3. Tokens stored in localStorage
4. Axios interceptor adds token to requests
5. Token expires → user redirected to login

---

## 🎨 Frontend Pages

| Page | Route | Purpose |
|------|-------|---------|
| Login | `/login` | User authentication |
| Register | `/register` | New user signup |
| Dashboard | `/dashboard` | View all projects |
| Issue List | `/projects/:id/issues` | View project issues |
| Issue Detail | `/issues/:id` | View issue + comments |

---

## 🔄 API Request Example

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"pass123","password_confirm":"pass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'

# Create Project (requires token)
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Project","description":"Description"}'
```

---

## 📦 Dependencies

### Backend
- Django 4.2.7
- Django REST Framework 3.14.0
- djangorestframework-simplejwt 5.3.2
- PostgreSQL (optional)

### Frontend
- React 18.2.0
- React Router 6.20.0
- Axios 1.6.2
- Tailwind CSS 3.3.6

---

## 🚢 Deployment

### Backend (Render)
1. Push to GitHub
2. Create Web Service
3. Set environment variables
4. Deploy

### Frontend (Netlify)
1. Push to GitHub
2. Connect to Netlify
3. Build: `npm run build`
4. Deploy

---

## 📞 Support

- Check `README.md` for features and setup
- Check `SETUP_GUIDE.md` for detailed instructions
- Check `API_REFERENCE.md` for API details
- Check `PROJECT_SUMMARY.md` for project overview

---

## ✅ Checklist

- [ ] Clone repository
- [ ] Set up backend
- [ ] Set up frontend
- [ ] Run migrations
- [ ] Create superuser
- [ ] Test login/register
- [ ] Create project
- [ ] Create issue
- [ ] Add comment
- [ ] Run tests

---

## 🎓 Learning Resources

- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- React: https://react.dev/
- Tailwind: https://tailwindcss.com/

---

**Ready to start? Follow the Quick Start section above!**
