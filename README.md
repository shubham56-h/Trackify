# Trackify - Fitness Tracking Application

A modern, full-stack fitness tracking application built with Flask and PostgreSQL.

## Features

- 🏋️ **Workout Tracking**: Track exercises, sets, reps, and weights
- 📊 **Progress Monitoring**: View detailed workout history with set-wise breakdown
- 🗓️ **Custom Splits**: Create and manage personalized workout splits
- 💪 **Muscle Group Focus**: Organize workouts by specific muscle groups
- ✅ **Exercise Tracking**: Mark completed exercises during your workout
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: Tailwind CSS, Alpine.js
- **Authentication**: JWT tokens
- **Database Migrations**: Flask-Migrate (Alembic)

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL database
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd trackify
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```env
DATABASE_URL=postgresql://username:password@localhost/trackify
JWT_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

5. Initialize the database:
```bash
flask db upgrade
```

6. (Optional) Seed exercise data:
```bash
python seed_exercises.py
```

7. Run the development server:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Deployment

### Heroku Deployment

1. Create a Heroku app:
```bash
heroku create your-app-name
```

2. Add PostgreSQL addon:
```bash
heroku addons:create heroku-postgresql:mini
```

3. Set environment variables:
```bash
heroku config:set JWT_SECRET_KEY=your-secret-key-here
heroku config:set FLASK_ENV=production
```

4. Deploy:
```bash
git push heroku main
```

5. Run migrations:
```bash
heroku run flask db upgrade
```

6. (Optional) Seed exercises:
```bash
heroku run python seed_exercises.py
```

### Other Platforms

The application is compatible with any platform that supports:
- Python 3.11+
- PostgreSQL database
- Environment variables

Platforms like Railway, Render, or DigitalOcean App Platform work great!

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes |
| `FLASK_ENV` | Environment (development/production) | No |

## Project Structure

```
trackify/
├── app.py                 # Main application file
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku deployment config
├── runtime.txt           # Python version specification
├── migrations/           # Database migrations
├── routes/               # API route handlers
│   ├── auth.py          # Authentication routes
│   ├── exercises.py     # Exercise management
│   ├── progress.py      # Progress tracking
│   ├── splits.py        # Workout splits
│   └── today.py         # Current workout session
├── templates/            # HTML templates
│   ├── base.html        # Base template (authenticated)
│   ├── base_public.html # Base template (public)
│   ├── dashboard.html   # Main dashboard
│   ├── login.html       # Login page
│   ├── signup.html      # Signup page
│   └── ...              # Other pages
└── utils/               # Utility functions
    └── workout_manager.py
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login and get JWT token

### Workouts
- `GET /api/today` - Get today's workout
- `POST /api/today/start` - Start workout session
- `POST /api/today/finish` - Complete workout
- `POST /api/today/cancel` - Cancel workout
- `POST /api/today/add-set` - Add exercise set

### Splits
- `GET /api/splits` - Get user's workout splits
- `POST /api/splits` - Create new split
- `POST /api/splits/assign` - Assign split to user

### Progress
- `GET /api/progress/stats` - Get workout statistics
- `GET /api/progress/volume` - Get volume over time
- `GET /api/progress/best-lifts` - Get personal records

### Exercises
- `GET /api/exercises/:muscle/:specific` - Get exercises for muscle
- `POST /api/exercises` - Create custom exercise

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please open an issue on GitHub.

---

Built with 💪 by fitness enthusiasts, for fitness enthusiasts.
