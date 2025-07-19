# MindTrack - Mental Health Tracking Application

## Overview

MindTrack is a Flask-based web application for personal mental health tracking and wellness monitoring. The application provides tools for mood tracking, sleep monitoring, habit building, secure journaling, insights generation, and motivational notifications. It now features a complete authentication system with user registration, login, and personalized user profiles. The app is designed as a multi-user solution with individual data isolation and privacy-focused features.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework) with Flask-Login for authentication
- **Application Structure**: Modular Flask app with separated route handling and user management
- **Data Layer**: User-specific JSON file storage system via custom DataManager class
- **Authentication**: Flask-Login with secure password hashing using Werkzeug
- **User Management**: Custom UserManager class with JSON-based user storage
- **Security**: Session-based authentication, password hashing, and user data isolation
- **Deployment**: WSGI-compatible with ProxyFix middleware for production deployment

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default templating)
- **CSS Framework**: Bootstrap 5 with Replit's dark theme
- **JavaScript Libraries**: 
  - Chart.js for data visualization
  - Feather Icons for consistent iconography
  - Bootstrap JavaScript for interactive components
- **Design Pattern**: Responsive, mobile-first design with dark theme

### Data Storage Solution
- **Primary Storage**: JSON file system (`data/user_data.json`)
- **Data Structure**: Single JSON file containing all user data with nested objects for different data types
- **Backup Strategy**: File-based storage allows for easy backup and migration
- **Schema**: Flexible JSON schema supporting mood entries, sleep data, habits, journal entries, and settings

## Key Components

### Data Management (`data_manager.py`)
- Custom DataManager class handling all data persistence
- JSON file-based storage with automatic directory creation
- Data integrity checks and default structure initialization
- Support for mood entries, sleep tracking, habit monitoring, and secure journal entries

### Route Handling (`routes.py`)
- Modular route definitions separated from main application
- Dashboard with quick stats and daily reflection prompts
- Individual modules for mood, sleep, habits, journal, and insights
- RESTful patterns for form handling and data submission

### Security Features
- Session management with configurable secret keys
- Password hashing for journal entries using Werkzeug's security utilities
- Environment variable support for sensitive configuration

### User Interface Components
- Base template with consistent navigation and Bootstrap integration
- Specialized templates for each tracking module
- Interactive forms with real-time feedback
- Chart.js integration for data visualization
- Responsive design optimized for both desktop and mobile

## Data Flow

1. **User Input**: Forms collect user data through web interface
2. **Route Processing**: Flask routes validate and process form submissions
3. **Data Persistence**: DataManager saves data to JSON file storage
4. **Data Retrieval**: Dashboard and analytics pages fetch data through DataManager
5. **Visualization**: Chart.js renders data visualizations on insights pages
6. **Session Management**: Flask sessions maintain user state and journal authentication

## External Dependencies

### Python Packages
- **Flask**: Web framework and templating
- **Werkzeug**: Security utilities and WSGI support

### Frontend Libraries (CDN)
- **Bootstrap 5**: UI framework with Replit dark theme
- **Chart.js**: Data visualization library
- **Feather Icons**: Icon library for consistent UI elements

### Development Dependencies
- **Logging**: Built-in Python logging for debugging
- **JSON**: Built-in Python JSON handling for data persistence
- **OS/Datetime**: Built-in Python modules for file system and date operations

## Deployment Strategy

### Local Development
- Flask development server with debug mode enabled
- Hot reloading for development efficiency
- Debug logging for troubleshooting

### Production Considerations
- WSGI-compatible with ProxyFix middleware for reverse proxy deployment
- Environment variable configuration for sensitive settings
- File-based storage suitable for single-user deployments
- Session secret key configuration through environment variables

### Hosting Requirements
- Python 3.x runtime environment
- File system write permissions for data storage
- Standard Flask hosting capabilities (supports most Python hosting platforms)

### Scalability Notes
- Current JSON file storage suitable for single-user applications
- Database migration path available if multi-user support needed
- Modular architecture supports easy extension and feature addition

## Recent Changes

### July 19, 2025 - Garden Layout Enhancement & User Flow Improvement
- **Grid-Based Garden Layout**: Implemented structured 10x8 grid with chronological plant placement
- **Direct Mood-to-Plant Mapping**: Amazing→🌻, Good→🌷, Okay→🌱, Down→🥀, Anxious→🌿
- **Multi-Dimensional Rewards**: Journal reflections add rare plants, milestone streaks unlock special plants
- **Dynamic Feedback System**: Toast notifications, achievement badges, milestone progress tracking
- **Enhanced Garden Visualization**: Improved text contrast, structured grid layout with progress indicators
- **Automatic Dashboard Redirects**: After mood/sleep/habit logging, users redirect to dashboard for consistent flow
- **User Experience Improvements**: Garden shows chronological mood history, milestone celebrations, visual feedback