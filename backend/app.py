from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ── Register blueprints ─────────────────────────────────────
from routes.auth       import auth_bp
from routes.floorplans import floorplans_bp
from routes.markers    import markers_bp
from routes.qr         import qr_bp
from routes.analytics  import analytics_bp
from routes.navigate   import navigate_bp

app.register_blueprint(auth_bp,       url_prefix='/api/auth')
app.register_blueprint(floorplans_bp, url_prefix='/api/floorplans')
app.register_blueprint(markers_bp,    url_prefix='/api/markers')
app.register_blueprint(qr_bp,         url_prefix='/api/qr')
app.register_blueprint(analytics_bp,  url_prefix='/api/analytics')
app.register_blueprint(navigate_bp,   url_prefix='/api/navigate')

# ── Serve uploaded images ───────────────────────────────────
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ── IMPORTANT: /nav route serves nav.html ──────────────────
@app.route('/nav')
def nav_page():
    return send_from_directory('../frontend/pages', 'nav.html')

# ── Serve all other frontend pages ─────────────────────────
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/login')
def login_page():
    return send_from_directory('../frontend/pages', 'login.html')

@app.route('/register')
def register_page():
    return send_from_directory('../frontend/pages', 'register.html')

@app.route('/dashboard')
def dashboard_page():
    return send_from_directory('../frontend/pages', 'dashboard.html')

@app.route('/editor')
def editor_page():
    return send_from_directory('../frontend/pages', 'editor.html')

# ── Catch-all for static assets ────────────────────────────
@app.route('/<path:path>')
def static_files(path):
    full = os.path.join(app.static_folder, path)
    if os.path.exists(full):
        return send_from_directory(app.static_folder, path)
    return send_from_directory('../frontend', 'index.html')

if __name__ == '__main__':
    print("✅ NavMap starting on http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
