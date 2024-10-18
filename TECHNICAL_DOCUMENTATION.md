
# VMT Office Hour Reservation System - Technical Documentation

## Overview
The VMT Office Hour Reservation System is designed to facilitate the coordination of office hours between mentors and mentees. This document provides technical details for installation, configuration, and maintenance of the application.

## System Requirements
- Python 3.11 or higher
- Flask
- SQLAlchemy
- JWT (PyJWT)
- Requests
- SQLite (for local development)

## Installation Instructions
1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**
   - The application uses SQLite by default. Ensure the database file `vmt.db` is created in the project directory.

5. **Run the Application**
   ```bash
   python app.py
   ```

## Configuration
- **Environment Variables**: Configure environment variables for sensitive data such as `SECRET_KEY` and `JOTFORM_API_KEY`.
- **Database URL**: Update `DATABASE_URL` in `app.py` if using a different database.

## Maintenance
- **Database Migrations**: Use Alembic for database migrations if needed.
- **Dependency Updates**: Regularly update dependencies using `pip` to ensure security and performance.

## Troubleshooting
- **Common Issues**: Check logs for errors and ensure all dependencies are installed.
- **Support**: Contact the development team for further assistance.

## Deployment
- For production deployment, consider using a WSGI server like Gunicorn and a reverse proxy like Nginx.
- Ensure all environment variables are set and secure.

