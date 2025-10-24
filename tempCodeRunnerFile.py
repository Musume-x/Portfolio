from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import hashlib
import secrets
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)

# Database Models
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300), nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

# Simple authentication (hardcoded for single user)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

def is_authenticated():
    return session.get('authenticated', False)

def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Create upload directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    blog_posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    return render_template('home.html', blog_posts=blog_posts)

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog')
def blog():
    blog_posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', blog_posts=blog_posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('blog_post.html', post=post)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD_HASH:
            session['authenticated'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('home'))

@app.route('/admin')
@require_auth
def admin_dashboard():
    blog_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/dashboard.html', blog_posts=blog_posts)

@app.route('/admin/blog/new', methods=['GET', 'POST'])
@require_auth
def new_blog_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        excerpt = request.form.get('excerpt', '')
        published = 'published' in request.form
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                image_filename = save_uploaded_file(file)
                if not image_filename:
                    flash('Invalid image file type. Please upload PNG, JPG, JPEG, GIF, or WEBP files.', 'error')
                    return render_template('admin/new_post.html')
        
        post = BlogPost(title=title, content=content, excerpt=excerpt, image_filename=image_filename, published=published)
        db.session.add(post)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/new_post.html')

@app.route('/admin/blog/<int:post_id>/edit', methods=['GET', 'POST'])
@require_auth
def edit_blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.excerpt = request.form.get('excerpt', '')
        post.published = 'published' in request.form
        post.updated_at = datetime.utcnow()
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                image_filename = save_uploaded_file(file)
                if image_filename:
                    # Delete old image if it exists
                    if post.image_filename:
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], post.image_filename)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    post.image_filename = image_filename
                else:
                    flash('Invalid image file type. Please upload PNG, JPG, JPEG, GIF, or WEBP files.', 'error')
                    return render_template('admin/edit_post.html', post=post)
        
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_post.html', post=post)

@app.route('/admin/blog/<int:post_id>/delete', methods=['POST'])
@require_auth
def delete_blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    
    # Delete associated image file if it exists
    if post.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], post.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Initialize database
with app.app_context():
    db.create_all()
    
    # Add image_filename column if it doesn't exist
    try:
        db.engine.execute("ALTER TABLE blog_post ADD COLUMN image_filename VARCHAR(255)")
    except Exception:
        # Column already exists, ignore the error
        pass

if __name__ == '__main__':
    app.run(debug=True)
