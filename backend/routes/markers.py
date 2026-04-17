from flask import Blueprint, request, jsonify
from models.db import get_db
from routes.auth import token_required
from datetime import datetime
import uuid

markers_bp = Blueprint('markers', __name__)

@markers_bp.route('/floor/<fp_id>', methods=['GET'])
def get_by_floor(fp_id):
    db = get_db()
    markers = list(db.markers.find({'floor_plan_id': fp_id}, {'_id':0}))
    return jsonify(markers)

@markers_bp.route('/org/<org_id>', methods=['GET'])
def get_by_org(org_id):
    db = get_db()
    markers = list(db.markers.find({'org_id': org_id}, {'_id':0}))
    return jsonify(markers)

@markers_bp.route('/', methods=['POST'])
@token_required
def add_marker():
    db  = get_db()
    b   = request.json or {}
    label   = b.get('label','').strip()
    fp_id   = b.get('floorPlanId','')
    if not label or not fp_id:
        return jsonify({'error': 'label and floorPlanId required'}), 400
    fp = db.floorplans.find_one({'id': fp_id, 'org_id': request.user['org_id']})
    if not fp:
        return jsonify({'error': 'Floor plan not found'}), 404
    m = {
        'id':           str(uuid.uuid4()),
        'label':        label,
        'category':     b.get('category','General'),
        'icon':         b.get('icon','📍'),
        'x_pct':        float(b.get('xPct', 50)),
        'y_pct':        float(b.get('yPct', 50)),
        'floor_plan_id':fp_id,
        'floor_label':  fp.get('floor_label',''),
        'floor_number': fp.get('floor_number', 0),
        'floor_name':   fp.get('name',''),
        'org_id':       request.user['org_id'],
        'org_name':     request.user['org_name'],
        'scan_count':   0,
        'dest_count':   0,
        'created_at':   datetime.utcnow().isoformat()
    }
    db.markers.insert_one(m)
    m.pop('_id', None)
    return jsonify(m), 201

@markers_bp.route('/<marker_id>', methods=['PUT'])
@token_required
def update_marker(marker_id):
    db = get_db()
    b  = request.json or {}
    b.pop('_id', None)
    db.markers.update_one(
        {'id': marker_id, 'org_id': request.user['org_id']},
        {'$set': b}
    )
    return jsonify(db.markers.find_one({'id': marker_id}, {'_id':0}))

@markers_bp.route('/<marker_id>', methods=['DELETE'])
@token_required
def delete_marker(marker_id):
    db = get_db()
    db.markers.delete_one({'id': marker_id, 'org_id': request.user['org_id']})
    return jsonify({'success': True})
