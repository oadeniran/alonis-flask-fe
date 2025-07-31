Try Alonis - [Url](https://alonis-db5cde379486.herokuapp.com/)

# Alonis - AI Companion Frontend

Alonis is an AI-powered personal companion platform designed to understand and support users through natural conversation and personalized insights. This repository contains the **frontend user interface** built with Flask, serving as the presentation layer for the Alonis ecosystem.

## 🌟 About Alonis

Alonis is more than just a chatbot - it's a comprehensive AI companion that helps users:

- **Discover their personality** through conversational assessments based on the Big Five model
- **Explore mental wellness** in a safe, private MindLab environment
- **Set and track personal goals** with intelligent note-taking
- **Receive personalized recommendations** for books, movies, music, and content
- **Build self-awareness** through meaningful AI conversations

## 🏗️ Architecture Overview

This Flask application serves as the **UI layer** of the Alonis platform:

- **Frontend Role**: Renders HTML templates, handles user interactions, manages sessions
- **Backend Communication**: All AI processing, data storage, and business logic handled via API calls to external backend services
- **Flask Purpose**: Lightweight web server focused purely on serving the user interface and routing requests

### Key Components

```text
├── app.py              # Main Flask application and routing
├── api_calls.py        # Backend API communication layer  
├── templates/          # HTML templates for all pages
├── static/            # CSS, JavaScript, and assets
├── config.py          # Configuration management
└── content_markdowns.py # Static content definitions
```

## 🚀 Features

### Core Functionality

- **Personality Assessment**: Conversational Big Five personality analysis
- **MindLab**: Private mental wellness reflection space
- **Alonis Chat**: Context-aware AI conversations with memory
- **Notes & Goals**: Personal goal tracking and achievement system
- **Smart Recommendations**: Personalized content suggestions
- **User Profiles**: Session management and history tracking

### Technical Features

- Session-based authentication and state management
- Responsive design for desktop and mobile
- Real-time AJAX communication with backend APIs
- Pagination for large datasets
- Modal-based interactions
- Background task processing

## 🛠️ Technology Stack

- **Framework**: Flask 3.1.1
- **Session Management**: Flask-Session with filesystem storage
- **HTTP Client**: Requests library for API communication
- **Templating**: Jinja2
- **Styling**: Custom CSS with responsive design
- **JavaScript**: Vanilla JS for dynamic interactions
- **Deployment**: Gunicorn WSGI server ready

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- Access to Alonis backend API services

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/oadeniran/alonis-flask-fe.git
   cd alonis-flask-fe
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Create a `config.py` file with your API base URL and secret key
   - Set up backend API endpoint configuration

5. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

Key configuration in `config.py`:
- `API_BASE_URL`: Backend API endpoint
- `SECRET_KEY`: Flask session encryption key
- Session storage settings and timeouts

## 📁 Project Structure

```
alonis-flask-fe/
├── app.py                 # Main Flask application
├── api_calls.py           # Backend API interface
├── config.py              # Configuration settings
├── content_markdowns.py   # Static content
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── layout.html        # Base template
│   ├── home.html          # Dashboard
│   ├── assessment.html    # Personality & MindLab
│   ├── chat.html          # AI conversation
│   ├── notes.html         # Notes & goals
│   ├── recommendations.html # Content suggestions
│   └── ...
├── static/
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Static assets
└── flask_session/        # Session storage
```

## 🌐 API Integration

The frontend communicates with backend services through `api_calls.py`:

- **User Management**: Authentication, profiles, sessions
- **Assessment Engine**: Personality tests, MindLab analysis
- **Chat System**: AI conversation processing
- **Content Management**: Notes, goals, recommendations
- **Analytics**: User interactions and progress tracking

## 🎨 UI/UX Features

- **Responsive Design**: Works seamlessly on desktop and mobile
- **Modal Interactions**: Smooth overlay experiences
- **Real-time Updates**: Dynamic content loading without page refresh
- **Progress Tracking**: Visual indicators for goals and assessments
- **Personalized Dashboard**: Tailored content based on user data

## 🚢 Deployment

The application is configured for production deployment:

- **Gunicorn**: WSGI server for production
- **Dockerfile**: Container deployment ready
- **Procfile**: Heroku deployment configuration
- **Session Management**: Filesystem-based session storage
