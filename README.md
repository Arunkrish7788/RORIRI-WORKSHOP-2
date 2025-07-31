# Dynamic AWS Workshop Registration System

A comprehensive web-based registration system for daily AWS workshops with persistent QR code functionality.

## Features

- **Dynamic Registration Form**: Single persistent form that updates with daily workshop details
- **Persistent QR Code**: One QR code that always links to the current active workshop
- **Admin Dashboard**: Easy-to-use interface for managing workshops and registrations
- **Real-time Updates**: Live availability tracking and registration counts
- **Data Export**: CSV export functionality for registration data
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the system**:
   - Admin Dashboard: `http://localhost:5000/admin`
   - Registration Page: `http://localhost:5000/register`

## Usage

### Admin Dashboard (`/admin`)
- Add new workshops with date, time, topic, instructor, price, and participant limits
- View and manage all workshops
- Generate persistent QR code for registration
- View current registration counts
- Export registration data to CSV

### Registration Page (`/register`)
- Participants can register for the currently active workshop
- Real-time availability updates
- Form validation and user-friendly interface
- Success confirmation with workshop details

### Key Features

1. **Persistent QR Code**: The QR code generated in the admin dashboard always points to `/register` and automatically shows the currently active workshop details.

2. **Workshop Management**: Only one workshop can be active at a time. When you create a new workshop, it automatically becomes active and deactivates previous ones.

3. **Data Collection**: All registration data is stored in SQLite database and can be exported to CSV format.

4. **Real-time Updates**: The system provides live updates on registration counts and availability.

## File Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   ├── base.html         # Base template with styling
│   ├── admin.html        # Admin dashboard
│   ├── register.html     # Registration form
│   ├── success.html      # Registration success page
│   ├── registrations.html # View all registrations
│   └── no_workshop.html  # No active workshop page
└── workshop.db           # SQLite database (created automatically)
```

## Database Schema

### Workshops Table
- `id`: Primary key
- `date`: Workshop date
- `topic`: Workshop topic/title
- `instructor`: Instructor name
- `time`: Workshop time
- `price`: Workshop price
- `max_participants`: Maximum number of participants
- `is_active`: Whether this workshop is currently active
- `created_at`: Creation timestamp

### Registrations Table
- `id`: Primary key
- `workshop_id`: Foreign key to workshops table
- `name`: Participant name
- `email`: Participant email
- `phone`: Participant phone (optional)
- `company`: Participant company (optional)
- `experience_level`: AWS experience level
- `registration_date`: Registration timestamp

## Customization

You can customize the system by:

1. **Styling**: Modify the CSS in `templates/base.html`
2. **Form Fields**: Add/remove fields in the registration form
3. **Workshop Details**: Modify workshop information fields
4. **Email Integration**: Add email notifications (requires additional setup)
5. **Payment Integration**: Add payment processing (requires additional setup)

## Production Deployment

For production deployment:

1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn
3. Configure a reverse proxy (nginx)
4. Use environment variables for sensitive configuration
5. Consider using PostgreSQL instead of SQLite for better performance

## Support

This system provides a complete solution for managing daily AWS workshop registrations with minimal manual overhead. The persistent QR code eliminates the need to generate new codes daily, while the admin interface makes it easy to update workshop details without technical expertise.