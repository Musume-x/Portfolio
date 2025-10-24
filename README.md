# Personal Portfolio with Blog System

A Flask-based personal portfolio website with an integrated blog system and admin panel.

## Features

- **Personal Portfolio**: Showcase your skills, projects, and experience
- **Blog System**: Write and publish blog posts
- **Admin Panel**: Manage blog posts with full CRUD operations
- **Authentication**: Secure login system for admin access
- **Responsive Design**: Mobile-friendly interface

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   - Main portfolio: http://localhost:5000
   - Admin login: http://localhost:5000/login

### Default Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

**Important**: Change these credentials in production by modifying the `ADMIN_USERNAME` and `ADMIN_PASSWORD_HASH` variables in `app.py`.

## Usage

### Admin Panel

1. Navigate to `/login` and enter your credentials
2. Once logged in, you'll have access to:
   - Create new blog posts
   - Edit existing posts
   - Delete posts
   - View all posts with their status (published/draft)

### Blog Management

- **Create Post**: Write new blog posts with title, content, and optional excerpt
- **Edit Post**: Modify existing posts
- **Publish/Draft**: Toggle between published and draft status
- **Delete Post**: Remove posts permanently

### Public Blog

- Visitors can view published blog posts on the `/blog` page
- Latest blog posts appear on the homepage
- Individual blog posts are accessible via `/blog/<post_id>`

## File Structure

```
portfolio/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── portfolio.db          # SQLite database (created automatically)
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── script.js     # JavaScript functionality
│   └── images/           # Image assets
└── templates/
    ├── admin/            # Admin panel templates
    │   ├── dashboard.html
    │   ├── new_post.html
    │   └── edit_post.html
    ├── blog.html         # Blog listing page
    ├── blog_post.html    # Individual blog post page
    ├── home.html         # Homepage
    ├── login.html        # Login page
    └── ...               # Other portfolio pages
```

## Customization

### Changing Admin Credentials

Edit the following lines in `app.py`:

```python
ADMIN_USERNAME = "your_username"
ADMIN_PASSWORD_HASH = hashlib.sha256("your_password".encode()).hexdigest()
```

### Styling

Modify `static/css/style.css` to customize the appearance of your portfolio and blog.

### Database

The application uses SQLite by default. The database file (`portfolio.db`) will be created automatically when you first run the application.

## Security Notes

- Change default login credentials before deploying
- Consider using environment variables for sensitive configuration
- Implement proper password hashing for production use
- Add CSRF protection for forms in production

## License

This project is open source and available under the MIT License.
