# Bug Reporting System - Setup Guide

## Quick Start (Development)

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Create .env file**:
```bash
cp .env.example .env
```

5. **Run migrations**:
```bash
python manage.py migrate
```

6. **Create superuser**:
```bash
python manage.py createsuperuser
```

7. **Run development server**:
```bash
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory** (in a new terminal):
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Create .env file**:
```bash
cp .env.example .env
```

4. **Start development server**:
```bash
npm start
```

Frontend will be available at: `http://localhost:3000`

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Build and Run

1. **Build images**:
```bash
docker-compose build
```

2. **Start services**:
```bash
docker-compose up -d
```

3. **Run migrations**:
```bash
docker-compose exec backend python manage.py migrate
```

4. **Create superuser**:
```bash
docker-compose exec backend python manage.py createsuperuser
```

5. **Access services**:
   - Frontend: `http://localhost:3000`
   - Backend: `http://localhost:8000`
   - API Docs: `http://localhost:8000/api/docs/`
   - Admin: `http://localhost:8000/admin/`

### Stop services:
```bash
docker-compose down
```

## Testing

### Backend Tests

```bash
# Navigate to backend directory
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

# Run specific test class
pytest accounts/tests.py::TestAuthEndpoints

# Run specific test
pytest accounts/tests.py::TestAuthEndpoints::test_user_registration
```

## First Steps After Setup

1. **Create a test user**:
   - Go to `http://localhost:3000/register`
   - Fill in the registration form
   - Click "Create Account"

2. **Login**:
   - Go to `http://localhost:3000/login`
   - Use your registered credentials

3. **Create a project**:
   - Click "New Project" on the dashboard
   - Fill in project details
   - Click "Create"

4. **Create an issue**:
   - Click on a project
   - Click "New Issue"
   - Fill in issue details
   - Click "Create"

5. **Add a comment**:
   - Click on an issue
   - Scroll to comments section
   - Type your comment
   - Click "Post Comment"

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## Database

### SQLite (Development - Default)
- Database file: `backend/db.sqlite3`
- No additional setup required

### PostgreSQL (Production)

1. **Install PostgreSQL**:
   - macOS: `brew install postgresql`
   - Ubuntu: `sudo apt-get install postgresql`
   - Windows: Download from postgresql.org

2. **Create database and user**:
```bash
createdb bug_tracking
createuser postgres
```

3. **Update .env**:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=bug_tracking
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

4. **Run migrations**:
```bash
python manage.py migrate
```

## Troubleshooting

### Port Already in Use

If port 8000 or 3000 is already in use:

**Backend**:
```bash
python manage.py runserver 8001
```

**Frontend**:
```bash
PORT=3001 npm start
```

### CORS Errors

If you see CORS errors:

1. Check that frontend URL is in `CORS_ALLOWED_ORIGINS` in backend `.env`
2. Ensure backend is running on the correct port
3. Clear browser cache and cookies

### Database Errors

If you see database errors:

1. Delete `db.sqlite3` file
2. Run migrations again: `python manage.py migrate`
3. Create new superuser: `python manage.py createsuperuser`

### Module Not Found

If you see "ModuleNotFoundError":

1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version (should be 3.9+)

### npm Install Errors

If you see npm errors:

1. Clear npm cache: `npm cache clean --force`
2. Delete `node_modules` and `package-lock.json`
3. Reinstall: `npm install`

## Environment Variables Reference

### Backend (.env)

```
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (.env)

```
REACT_APP_API_URL=http://localhost:8000/api
```

## Production Deployment

### Backend (Render)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Set environment variables:
   - `SECRET_KEY`: Generate a strong secret key
   - `DEBUG`: False
   - `ALLOWED_HOSTS`: Your domain
   - `DB_*`: PostgreSQL credentials
5. Deploy

### Frontend (Netlify)

1. Push code to GitHub
2. Connect GitHub repository to Netlify
3. Set build command: `npm run build`
4. Set publish directory: `build`
5. Set environment variables:
   - `REACT_APP_API_URL`: Your backend URL
6. Deploy

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Support

For issues and questions:
1. Check the README.md for more information
2. Review API documentation at `/api/docs/`
3. Check Django logs: `python manage.py runserver` output
4. Check browser console for frontend errors

## Next Steps

After successful setup:
1. Explore the API documentation
2. Try creating projects and issues
3. Test the commenting feature
4. Review the code structure
5. Run the test suite
6. Deploy to production

Happy bug tracking!
