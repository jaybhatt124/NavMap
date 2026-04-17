from flask import Blueprint, request, jsonify, current_app
from models.db import get_db
from routes.auth import token_required
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid, os

floorplans_bp = Blueprint('floorplans', __name__)
ALLOWED = {'png','jpg','jpeg','gif','webp'}

def allowed(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED

@floorplans_bp.route('/', methods=['GET'])
@token_required
def get_floorplans():
    db  = get_db()
    fps = list(db.floorplans.find({'org_id': request.user['org_id']}, {'_id':0}))
    return jsonify(fps)

@floorplans_bp.route('/', methods=['POST'])
@token_required
def upload_floorplan():
    db          = get_db()
    name        = request.form.get('name','Floor Plan').strip()
    floor_label = request.form.get('floorLabel','G').strip()
    floor_num   = int(request.form.get('floorNumber', 0))
    file        = request.files.get('image')

    if not file or not allowed(file.filename):
        return jsonify({'error': 'Valid image required (png/jpg/gif/webp)'}), 400

    ext      = file.filename.rsplit('.',1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    fp = {
        'id':           str(uuid.uuid4()),
        'name':         name,
        'floor_label':  floor_label,
        'floor_number': floor_num,
        'image_url':    f'/uploads/{filename}',
        'org_id':       request.user['org_id'],
        'org_name':     request.user['org_name'],
        'created_at':   datetime.utcnow().isoformat()
    }
    db.floorplans.insert_one(fp)
    fp.pop('_id', None)
    return jsonify(fp), 201

@floorplans_bp.route('/<fp_id>', methods=['DELETE'])
@token_required
def delete_floorplan(fp_id):
    db = get_db()
    fp = db.floorplans.find_one({'id': fp_id, 'org_id': request.user['org_id']})
    if not fp:
        return jsonify({'error': 'Not found'}), 404
    try:
        fname = fp['image_url'].replace('/uploads/','')
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], fname))
    except: pass
    db.floorplans.delete_one({'id': fp_id})
    db.markers.delete_many({'floor_plan_id': fp_id})
    return jsonify({'success': True})
