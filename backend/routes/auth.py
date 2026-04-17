from flask import Blueprint, request, jsonify
from models.db import get_db
import bcrypt, jwt, os, uuid
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__)
SECRET  = os.getenv('JWT_SECRET', 'navmap_dev_secret')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization','').replace('Bearer ','').strip()
        if not token:
            return jsonify({'error': 'No token'}), 401
        try:
            request.user = jwt.decode(token, SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    db  = get_db()
    b   = request.json or {}
    email    = b.get('email','').strip().lower()
    password = b.get('password','')
    org_name = b.get('orgName','').strip()
    org_type = b.get('orgType','college')

    if not all([email, password, org_name]):
        return jsonify({'error': 'All fields required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password min 6 characters'}), 400
    if db.users.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 409

    org = db.organizations.find_one({'name': org_name})
    if not org:
        org_id = str(uuid.uuid4())
        db.organizations.insert_one({
            'id': org_id, 'name': org_name, 'type': org_type,
            'admin_email': email, 'created_at': datetime.utcnow()
        })
    else:
        org_id = org['id']

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db.users.insert_one({
        'id': str(uuid.uuid4()), 'email': email,
        'password': hashed, 'org_id': org_id,
        'org_name': org_name, 'created_at': datetime.utcnow()
    })

    token = jwt.encode({
        'email': email, 'org_id': org_id, 'org_name': org_name,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, SECRET, algorithm='HS256')

    return jsonify({'token': token, 'org_id': org_id, 'org_name': org_name})

@auth_bp.route('/login', methods=['POST'])
def login():
    db  = get_db()
    b   = request.json or {}
    email    = b.get('email','').strip().lower()
    password = b.get('password','')
    user = db.users.find_one({'email': email})
    if not user or not bcrypt.checkpw(password.encode(), user['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    token = jwt.encode({
        'email': user['email'], 'org_id': user['org_id'], 'org_name': user['org_name'],
        'exp': datetime.utcnow() + timedelta(days=7)
    }, SECRET, algorithm='HS256')
    return jsonify({'token': token, 'org_id': user['org_id'], 'org_name': user['org_name']})
