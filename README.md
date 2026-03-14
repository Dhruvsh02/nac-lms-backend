# NAC LMS Backend API

**Next Art Creations — Learning Management System**  
Backend Developer Intern: Dhruv Sharma | Jan 2026 – June 2026

---

## Tech Stack

- **Language:** Python 3.11
- **Framework:** Django 4.2 + Django REST Framework
- **Auth:** JWT via `djangorestframework-simplejwt`
- **Database:** SQLite (dev) → PostgreSQL (prod)
- **Tools:** Postman, Git, VS Code, dotenv

---

## Project Structure

```
nac_lms_project/
├── apps/
│   ├── authentication/    # Register, Login, JWT, Profile
│   ├── courses/           # Course CRUD (Admin-only write)
│   ├── enrollment/        # Enroll, Unenroll, Progress
│   └── dashboard/         # Student & Admin analytics
├── nac_lms_project/
│   ├── settings.py
│   └── urls.py
├── requirements.txt
└── manage.py
```

---

## API Endpoints

### Auth
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/auth/register/ | Create account | No |
| POST | /api/auth/login/ | Login → JWT tokens | No |
| POST | /api/auth/logout/ | Blacklist refresh token | Yes |
| POST | /api/auth/refresh/ | Get new access token | No |
| GET/PUT | /api/auth/me/ | View/Edit profile | Yes |

### Courses
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/courses/ | List all courses (paginated) | No |
| POST | /api/courses/ | Create course | Admin |
| GET | /api/courses/<id>/ | Course detail | No |
| PUT | /api/courses/<id>/ | Update course | Admin |
| DELETE | /api/courses/<id>/ | Remove course | Admin |

### Enrollment
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/enrollment/enroll/ | Enroll in course | Student |
| DELETE | /api/enrollment/unenroll/<id>/ | Unenroll | Student |
| GET | /api/enrollment/my-courses/ | My enrolled courses | Student |
| GET | /api/enrollment/status/<id>/ | Check enrollment | Student |
| PUT | /api/enrollment/progress/<id>/ | Update progress % | Student |

### Dashboard
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/dashboard/student/ | Student summary | Student |
| GET | /api/dashboard/admin/ | Platform stats | Admin |

---

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
# nac-lms-backend
