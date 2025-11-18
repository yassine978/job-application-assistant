# Streamlit Dashboard - User Guide

## Phase 7: User Authentication & Profile Management

This dashboard provides a complete authentication and profile management system for the Job Application Assistant.

## Features

### 1. **User Authentication**
- User registration with email and password
- Secure login system (SHA-256 password hashing)
- Session management with Streamlit
- Logout functionality

### 2. **Profile Management**
- Create and update user profiles
- Add skills, experience, education, and languages
- Update account information
- Change password

### 3. **Project Management**
- Upload project README files
- Automatic README parsing using Phase 3.5 parser
- Extract technologies, highlights, and description
- Store projects with embeddings for RAG

### 4. **CV Preferences**
- Set CV length (1 or 2 pages)
- Control project inclusion in CVs
- Configure maximum projects per CV

## Running the Dashboard

### Prerequisites

1. **Install Streamlit** (if not already installed):
```bash
pip install streamlit
```

2. **Configure Database** (required):
   - Set up your PostgreSQL database
   - Configure `DATABASE_URL` in `.env` file
   - Or use a local SQLite database for testing

3. **Initialize Database**:
```bash
python -c "from database.db_manager import db_manager; db_manager.initialize()"
```

### Start the Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Dashboard Pages

### 1. **Login/Register**
- New users can create an account
- Existing users can log in
- Password requirements: minimum 6 characters

### 2. **Dashboard (Home)**
- Quick statistics overview
- Recent activity
- Quick action buttons

### 3. **Profile & Projects**
- View and edit your profile
- Upload and manage projects
- README file parsing
- Project details with technologies and highlights

### 4. **Job Search** (Coming in Phase 8)
- Search for jobs
- Filter and rank results

### 5. **My Applications** (Coming in Phase 8)
- Track applications
- View generated CVs and cover letters

### 6. **Settings**
- Update account information
- Change password
- Configure CV preferences

## Authentication System

### `dashboard/auth.py`

**Features:**
- Password hashing with SHA-256
- User registration with duplicate email detection
- Login authentication
- Profile updates
- Password changes with validation

**Key Methods:**
```python
# Register new user
auth_manager.register_user(
    email="user@example.com",
    password="secure_password",
    full_name="John Doe",
    location_preference="Paris"
)

# Login
result = auth_manager.login_user("user@example.com", "password")

# Get user info
user = auth_manager.get_user_by_id(user_id)

# Update profile
auth_manager.update_user_profile(
    user_id=user_id,
    full_name="New Name",
    location_preference="New Location"
)

# Change password
auth_manager.change_password(
    user_id=user_id,
    old_password="old_pass",
    new_password="new_pass"
)
```

## Session Management

### `utils/session_manager.py`

**Features:**
- Session state initialization
- User authentication tracking
- CV preferences storage
- Notifications system
- Session timeout detection

**Key Methods:**
```python
# Initialize session
session_manager.init_session_state()

# Set user
session_manager.set_user(user_dict)

# Check authentication
if session_manager.is_authenticated():
    user = session_manager.get_user()

# Add notification
session_manager.add_notification("Success!", "success")

# Update CV preferences
session_manager.update_cv_preferences({
    'cv_length': 1,
    'include_projects': True
})
```

## UI Components

### `dashboard/components/`

#### **profile_form.py**
- Reusable profile creation/edit form
- Supports multiple experiences and education entries
- Skills and languages input

#### **project_card.py**
- Display project information
- Show technologies as badges
- Project upload form

#### **stats_card.py**
- Statistics display cards
- Metrics with delta changes

## Testing

### Run Authentication Tests

```bash
python tests/test_dashboard/test_auth.py
```

**Test Coverage:**
1. Password hashing
2. User registration (including duplicate detection)
3. User login (valid and invalid credentials)
4. Get user by ID
5. Update user profile
6. Change password

## Security Considerations

1. **Password Hashing**: Passwords are hashed with SHA-256 before storage
2. **Session Management**: User sessions are managed securely with Streamlit
3. **Input Validation**: All inputs are validated before database operations
4. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## Future Enhancements (Phase 8+)

- OAuth integration (Google, LinkedIn)
- Two-factor authentication (2FA)
- Email verification
- Password reset via email
- User profile photos
- Enhanced session management with Redis

## Troubleshooting

### Database Connection Errors
```
Error: Tenant or user not found
```
**Solution**: Configure your `DATABASE_URL` in `.env` file with valid credentials

### Emoji Encoding Errors
```
UnicodeEncodeError: 'charmap' codec can't encode character
```
**Solution**: Already fixed in codebase (using ASCII alternatives)

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Use a different port:
```bash
streamlit run dashboard/app.py --server.port 8502
```

## Development Notes

### Adding New Pages

1. Create page file in `dashboard/` (e.g., `my_page.py`)
2. Add navigation button in `show_sidebar()` in `app.py`
3. Create page handler function (e.g., `show_my_page()`)
4. Add route in `main()` function

### Adding New Components

1. Create component file in `dashboard/components/`
2. Import and use in page handlers
3. Keep components reusable and parameterized

## Architecture

```
dashboard/
├── app.py                  # Main Streamlit application
├── auth.py                 # Authentication manager
├── components/             # Reusable UI components
│   ├── __init__.py
│   ├── profile_form.py     # Profile creation/edit form
│   ├── project_card.py     # Project display and upload
│   └── stats_card.py       # Statistics cards
└── README.md               # This file

utils/
└── session_manager.py      # Session state management

tests/test_dashboard/
├── __init__.py
└── test_auth.py            # Authentication tests
```

## Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Application
APP_NAME=Job Application Assistant
VERSION=1.0.0
DEBUG=True

# Security (optional, for future enhancements)
SECRET_KEY=your-secret-key-here
SESSION_TIMEOUT_MINUTES=30
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test files for usage examples
3. Check Phase 7 implementation details in `claude_code_spec.txt`
