# AI Interview Simulator

## Overview

This is a Flask-based AI Interview Simulator that helps users practice for job interviews. The application provides role-specific interview questions, collects user responses, evaluates answers using keyword matching algorithms, and provides detailed feedback and performance analytics. Users can practice interviews for various tech roles including Python Developer, Data Engineer, Web Developer, Data Scientist, DevOps Engineer, and Software Engineer.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM for database operations
- **Authentication**: Flask-Login for session management with username/password authentication
- **Database**: PostgreSQL with SQLAlchemy models for Users, Questions, Interviews, and Answers
- **Forms**: WTForms for form validation and rendering with CSRF protection
- **Evaluation Engine**: Custom keyword-matching algorithm in utils.py for scoring user responses

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Styling**: Custom CSS with dark theme and gradient designs
- **JavaScript**: Client-side timer functionality and form handling for interview sessions
- **Components**: Role selection, question presentation, answer submission, and results display

### Data Models
- **User Model**: Stores user credentials, registration info, and relationships to interviews
- **Question Model**: Contains role-specific questions with model answers, keywords, and difficulty levels
- **Interview Model**: Tracks interview sessions with user association and total scores
- **Answer Model**: Stores individual question responses with scores and feedback

### Authentication System
- User registration with email and username validation
- Password hashing using Werkzeug security utilities
- Session-based authentication with Flask-Login
- Protected routes requiring login for interview functionality

### Evaluation System
- Keyword-based scoring algorithm comparing user answers to expected keywords
- Length bonus scoring for detailed responses
- Automated feedback generation based on performance metrics
- Performance analytics and insights generation

## External Dependencies

### Core Web Framework
- Flask: Main web framework
- Flask-SQLAlchemy: Database ORM
- Flask-Login: User session management
- Flask-WTF: Form handling and validation

### Database
- PostgreSQL: Primary database (configurable via DATABASE_URL environment variable)
- SQLAlchemy: Database abstraction layer with connection pooling

### Frontend Libraries
- Bootstrap 5: CSS framework for responsive design
- Font Awesome: Icon library for UI elements
- Custom CSS: Dark theme styling with gradient effects

### Security
- Werkzeug: Password hashing and security utilities
- CSRF protection via Flask-WTF
- Session management with configurable secret keys

### Development Tools
- ProxyFix: Handles proxy headers for deployment
- Logging: Built-in Python logging for debugging
- Environment variables for configuration management