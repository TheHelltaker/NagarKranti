# NagarKranti - Citizen Issue and Grievance Addressal Platform

NagarKranti is a civic engagement platform that enables citizens to report urban issues and municipal authorities to track and address these concerns efficiently.

## Project Setup

### Prerequisites

- Python 3.13+
- PostgreSQL with PostGIS extension
- GDAL library
- Virtual environment

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nagarkranti.git
cd nagarkranti
```

2. Create and activate a virtual environment:
```bash
python -m venv nagarkranti_env
source nagarkranti_env/bin/activate  # On Windows: nagarkranti_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a PostgreSQL database with PostGIS extension:
```sql
CREATE DATABASE nagarkranti;
\c nagarkranti
CREATE EXTENSION postgis;
```

5. Update database settings in `nagarkranti/settings.py` to match your configuration.

6. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Create a superuser:
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/users/register/` - Register a new user
- `POST /api/users/token/` - Get JWT token
- `POST /api/users/token/refresh/` - Refresh JWT token
- `POST /api/users/token/verify/` - Verify JWT token

### User Management

- `GET /api/users/me/` - Get current user profile
- `POST /api/users/change_password/` - Change password
- `GET /api/users/` - List all users (municipal officers only)
- `GET /api/users/{id}/` - Get user details (own profile or municipal officers)
- `PATCH /api/users/{id}/` - Update user profile (own profile or municipal officers)

### Issue Management

- `GET /api/issues/` - List issues (own issues for citizens, all for municipal officers)
- `POST /api/issues/` - Create a new issue
- `GET /api/issues/{id}/` - Get issue details
- `PATCH /api/issues/{id}/` - Update issue status (municipal officers only)
- `DELETE /api/issues/{id}/` - Delete an issue (municipal officers only)
- `POST /api/issues/nearby/` - Find issues near a location
- `POST /api/issues/{id}/add_image/` - Add an image to an issue

### Issue Images

- `GET /api/issues/images/{id}/` - Get image details
- `DELETE /api/issues/images/{id}/` - Delete an image

## User Types and Permissions

### Citizen Users
- Can register and login
- Can create new issue reports with images and location
- Can view and track their own issue reports
- Can view nearby issues

### Municipal Users
- Can view all issue reports
- Can update issue status and priority
- Can delete issues if needed
- Can view all user profiles

## Issue Statuses

- **PENDING**: Initial status when issue is reported
- **ACCEPTED**: Issue verified and accepted by municipal officers
- **IN PROGRESS**: Issue being addressed by municipal staff
- **RESOLVED**: Issue has been resolved

## Issue Types

- **INFRASTRUCTURE**: Roads, bridges, public buildings, etc.
- **SERVICES**: Water supply, electricity, waste management, etc.
- **ENCROACHMENT**: Illegal constructions, unauthorized use of public space
- **OTHER**: Any other issues not covered by the above categories

## Issue Priorities

- **HIGH**: Urgent issues requiring immediate attention
- **NORMAL**: Standard priority issues
- **LOW**: Issues that can be addressed later
- **NA**: Priority not assigned yet

## Technologies Used

- **Backend**: Django, Django REST Framework, PostGIS
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: PostgreSQL with PostGIS extension
- **Geospatial**: GDAL, Leaflet