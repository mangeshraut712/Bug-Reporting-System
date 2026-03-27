<a id="top"></a>

<div align="center">

# Bug Reporting System

### _Full-stack bug tracker with Django REST and a React UI_

<img src="https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django badge" />
<img src="https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=000000" alt="React badge" />
<img src="https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL badge" />
<img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker badge" />
<img src="https://img.shields.io/badge/License-Project_Defined-22C55E?style=for-the-badge" alt="License badge" />

[Live Demo](https://bug-reporting-system-psi.vercel.app/) • [Repository](https://github.com/mangeshraut712/Bug-Reporting-System) • [Issues](https://github.com/mangeshraut712/Bug-Reporting-System/issues)

**[About](#about) • [Features](#features) • [Tech Stack](#tech-stack) • [Quick Start](#quick-start) • [Project Structure](#project-structure) • [Scripts](#scripts) • [Contact](#contact)**

</div>

---

## 📖 Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Scripts](#scripts)
- [Contact](#contact)

---

<a id="about"></a>

## About

This project is a full-stack bug tracker built around a Django REST backend and a React frontend. It covers the core workflows that engineering teams actually use: authentication, project management, issue tracking, threaded comments, and deployment-friendly packaging.

<a id="features"></a>

## Features

- JWT-backed authentication with role-aware access control.
- Project, issue, and comment workflows that support day-to-day triage.
- React pages for login, registration, dashboards, issue lists, and issue details.
- Docker and Compose files for local orchestration and deployment parity.
- API-first structure that keeps the frontend and backend cleanly separated.

<a id="tech-stack"></a>

## Tech Stack

**Backend**

- Django 4.2
- Django REST Framework
- Simple JWT
- drf-spectacular
- PostgreSQL

**Frontend**

- React 18
- React Router DOM 6
- Axios
- Tailwind CSS
- React Toastify

**Delivery**

- Docker
- Docker Compose
- Gunicorn
- Render
- Vercel

<a id="quick-start"></a>

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL

### Install

```bash
git clone https://github.com/mangeshraut712/Bug-Reporting-System.git
cd Bug-Reporting-System
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

```bash
cd ../frontend
npm install
```

### Run

```bash
# Backend
cd backend
source .venv/bin/activate
python manage.py runserver

# Frontend
cd ../frontend
npm start
```

If you prefer containers, use:

```bash
docker compose up --build
```

<a id="project-structure"></a>

## Project Structure

```text
Bug-Reporting-System/
├── backend/            # Django project, apps, settings, and tests
├── frontend/           # React client and UI components
├── docker-compose.yml  # Local service orchestration
├── render.yaml         # Render deployment config
├── vercel.json         # Vercel configuration
└── Procfile            # Procfile for runtime platforms
```

<a id="scripts"></a>

## Scripts

| Command | Purpose |
| --- | --- |
| `python backend/manage.py runserver` | Start the Django API locally |
| `python backend/manage.py migrate` | Apply database migrations |
| `npm start` | Start the React frontend |
| `npm run build` | Build the frontend bundle |
| `docker compose up --build` | Run the full stack in containers |

<a id="contact"></a>

## Contact

- Live demo: [bug-reporting-system-psi.vercel.app](https://bug-reporting-system-psi.vercel.app/)
- Repository issues: [mangeshraut712/Bug-Reporting-System/issues](https://github.com/mangeshraut712/Bug-Reporting-System/issues)

[↑ Back to Top](#top)
