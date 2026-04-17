from flask import Blueprint, request, jsonify, send_file
from models.db import get_db
from routes.auth import token_required
import qrcode, io, base64, socket
from urllib.parse import quote

qr_bp = Blueprint('qr', __name__)

def _get_base_url():
    host = request.host
    port = host.split(':')[1] if ':' in host else '5000'
    raw  = host.split(':')[0]
    if raw in ('localhost', '127.0.0.1', '::1'):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            raw = s.getsockname()[0]
            s.close()
        except Exception:
            pass
    return f"http://{raw}:{port}"

def _qr_buf(url):
    qr = qrcode.QRCode(version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def _nav_url(marker):
    base = _get_base_url()
    return f"{base}/nav?org={quote(marker['org_id'])}&room={quote(marker['id'])}"

@qr_bp.route('/marker/<marker_id>', methods=['GET'])
@token_required
def get_qr(marker_id):
    db = get_db()
    m  = db.markers.find_one({'id': marker_id, 'org_id': request.user['org_id']}, {'_id':0})
    if not m:
        return jsonify({'error': 'Marker not found'}), 404
    url = _nav_url(m)
    buf = _qr_buf(url)
    b64 = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
    return jsonify({'qr_code': b64, 'url': url, 'label': m['label']})

@qr_bp.route('/marker/<marker_id>/download', methods=['GET'])
def download_qr(marker_id):
    db = get_db()
    m  = db.markers.find_one({'id': marker_id}, {'_id':0})
    if not m:
        return jsonify({'error': 'Marker not found'}), 404
    url = _nav_url(m)
    buf = _qr_buf(url)
    return send_file(buf, mimetype='image/png',
                     download_name=f"QR_{m['label'].replace(' ','_')}.png",
                     as_attachment=True)

@qr_bp.route('/all', methods=['GET'])
@token_required
def all_qr():
    db      = get_db()
    markers = list(db.markers.find({'org_id': request.user['org_id']}, {'_id':0}))
    result  = []
    for m in markers:
        url = _nav_url(m)
        buf = _qr_buf(url)
        b64 = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
        result.append({
            'marker_id':   m['id'],
            'label':       m['label'],
            'floor_label': m.get('floor_label',''),
            'floor_name':  m.get('floor_name',''),
            'qr_code':     b64,
            'url':         url
        })
    return jsonify(result)
