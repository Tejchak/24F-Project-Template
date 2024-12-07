# CoopConnect - Cooperative Education Management Platform

CoopConnectis a comprehensive platform designed to streamline the co-op experience for Northeastern University students, employers, and parents. The platform provides tools for housing search, job postings, cost analysis, and system administration.

## Project Overview

CoopConnect consists of three main components running in separate Docker containers:

- **Frontend**: A Streamlit web application (`./app` directory)
- **Backend API**: A Flask REST API (`./api` directory) 
- **Database**: MySQL database with schema files (`./database-files` directory)

## System Architecture

### Frontend (Streamlit)
The frontend is built using Streamlit, providing an intuitive interface for different user roles:

- **Students**: Browse jobs, search housing, view city statistics
- **Employers**: Post jobs, access demographic data, analyze work trends
- **Parents**: Research housing, view safety ratings, access cost data
- **System Administrators**: Monitor performance, manage databases

Reference implementation:

```python:app/src/Home.py
startLine: 35
endLine: 46
```

### Backend API (Flask)
The Flask REST API serves as the middleware between the frontend and database, handling:

- Data validation and processing
- Role-based access control
- Database operations
- Performance monitoring

Key API routes are organized by user role:
*Note we added more routes then what is shown in the referenced user stories*
- `/employer/*` - Employer-specific endpoints
- `/parent/*` - Parent-specific endpoints
- `/student/*` - Student-specific endpoints
- `/system_admin/*` - Administrative endpoints

Reference implementation:

```python:api/backend/rest_entry.py
startLine: 11
endLine: 42
```

### Database (MySQL)
The MySQL database stores all application data with tables for:

- Users and role management
- Cities and locations
- Housing information
- Job postings
- System performance metrics

Reference schema:

```sql:database-files/coopConnect.sql
startLine: 9
endLine: 91
```

## Role-Based Access Control (RBAC)

CoopConnect implements role-based access control to provide appropriate features for each user type:

1. Authentication is managed through Streamlit's session state
2. Navigation links are dynamically generated based on user role
3. API endpoints validate role permissions
4. Database queries are filtered by role access levels

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11 or higher
- Git

### Installation Steps

1. Clone the repository
2. Copy the `.envtemplate` file in `./api` directory using template
3. Start the containers:

```bash
docker compose up -d
```

### Container Management
- Start all services: `docker compose up -d`
- Stop services: `docker compose stop`
- Remove containers: `docker compose down`
- Start specific service: `docker compose up [service] -d`

## Development Notes

- Frontend changes in `./app/src` are hot-reloaded
- API changes in `./api` require container restart
- Database changes require running new migrations
- Environment variables are loaded from `.env` file

## API Documentation

The REST API provides endpoints for:

1. User Management
   - Authentication
   - Profile updates
   - Role management

2. Housing Operations
   - Listings
   - Search
   - Safety ratings

3. Job Management
   - Posting
   - Applications
   - Statistics

4. System Administration
   - Performance monitoring
   - Database management
   - User activity tracking

For detailed API documentation, see the route files in `./api/backend/coopconnect_routes/`.
