from flask import Blueprint, request, jsonify
from models.db import get_db
import jwt, os

navigate_bp = Blueprint('navigate', __name__)
SECRET = os.getenv('JWT_SECRET', 'navmap_dev_secret')

def _auth_user():
    token = request.headers.get('Authorization','').replace('Bearer ','').strip()
    try:
        return jwt.decode(token, SECRET, algorithms=['HS256'])
    except:
        return None

def _build_nav_data(org_id, db):
    markers  = list(db.markers.find({'org_id': org_id}, {'_id':0}))
    fps      = list(db.floorplans.find({'org_id': org_id}, {'_id':0}))
    org      = db.organizations.find_one({'id': org_id}, {'_id':0, 'admin_email':0})
    entrance = db.entrance_gates.find_one({'org_id': org_id}, {'_id':0})
    return {
        'markers':       markers,
        'floor_plans':   fps,
        'org':           org,
        'entrance_gate': entrance
    }

@navigate_bp.route('/room/<room_id>', methods=['GET'])
def get_room(room_id):
    db     = get_db()
    marker = db.markers.find_one({'id': room_id}, {'_id':0})
    if not marker:
        return jsonify({'error': 'Room not found'}), 404
    data = _build_nav_data(marker['org_id'], db)
    data['scanned_room'] = marker
    return jsonify(data)

@navigate_bp.route('/org/<org_id>', methods=['GET'])
def get_org(org_id):
    db = get_db()
    if not db.organizations.find_one({'id': org_id}):
        return jsonify({'error': 'Organization not found'}), 404
    return jsonify(_build_nav_data(org_id, db))

@navigate_bp.route('/entrance', methods=['GET'])
def get_entrance():
    org_id = request.args.get('org_id','')
    if not org_id:
        return jsonify({'error': 'org_id required'}), 400
    db   = get_db()
    gate = db.entrance_gates.find_one({'org_id': org_id}, {'_id':0})
    return jsonify(gate or {})

@navigate_bp.route('/entrance', methods=['POST'])
def set_entrance():
    user = _auth_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    db  = get_db()
    b   = request.json or {}
    gate = {
        'org_id':        user['org_id'],
        'org_name':      user['org_name'],
        'label':         b.get('label', 'Main Entrance'),
        'icon':          '🚪',
        'floor_plan_id': b.get('floor_plan_id',''),
        'floor_label':   b.get('floor_label','G'),
        'floor_name':    b.get('floor_name','Ground Floor'),
        'x_pct':         float(b.get('x_pct', 50)),
        'y_pct':         float(b.get('y_pct', 95)),
        'is_entrance':   True
    }
    db.entrance_gates.update_one({'org_id': user['org_id']}, {'$set': gate}, upsert=True)
    return jsonify({'success': True, 'gate': gate})

@navigate_bp.route('/entrance', methods=['DELETE'])
def delete_entrance():
    user = _auth_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    get_db().entrance_gates.delete_one({'org_id': user['org_id']})
    return jsonify({'success': True})
