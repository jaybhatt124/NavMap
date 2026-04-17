from flask import Blueprint, request, jsonify
from models.db import get_db
from routes.auth import token_required
from datetime import datetime, timedelta
from collections import defaultdict

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/scan', methods=['POST'])
def log_scan():
    db  = get_db()
    b   = request.json or {}
    org_id    = b.get('org_id','')
    marker_id = b.get('marker_id','')
    dest_id   = b.get('dest_id','')
    if not org_id:
        return jsonify({'error': 'org_id required'}), 400
    db.scan_logs.insert_one({
        'org_id':     org_id,
        'marker_id':  marker_id,
        'dest_id':    dest_id,
        'user_agent': request.headers.get('User-Agent',''),
        'ip':         request.remote_addr,
        'scanned_at': datetime.utcnow()
    })
    if marker_id:
        db.markers.update_one({'id': marker_id}, {'$inc': {'scan_count': 1}})
    if dest_id and dest_id != marker_id:
        db.markers.update_one({'id': dest_id}, {'$inc': {'dest_count': 1}})
    return jsonify({'success': True})

@analytics_bp.route('/', methods=['GET'])
@token_required
def get_analytics():
    db     = get_db()
    org_id = request.user['org_id']
    markers = list(db.markers.find({'org_id': org_id}, {'_id':0}))
    fps     = list(db.floorplans.find({'org_id': org_id}, {'_id':0}))
    total_scans   = sum(m.get('scan_count',0) for m in markers)
    total_markers = len(markers)

    # Daily scans last 14 days
    fourteen_ago = datetime.utcnow() - timedelta(days=14)
    logs = list(db.scan_logs.find(
        {'org_id': org_id, 'scanned_at': {'$gte': fourteen_ago}},
        {'_id':0, 'scanned_at':1}
    ))
    daily = defaultdict(int)
    for l in logs:
        daily[l['scanned_at'].strftime('%Y-%m-%d')] += 1
    daily_data = []
    for i in range(13,-1,-1):
        d = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
        daily_data.append({'date': d, 'scans': daily.get(d,0)})

    # Today
    today = datetime.utcnow().strftime('%Y-%m-%d')
    today_scans = daily.get(today, 0)

    # Per floor
    floor_data = []
    for fp in fps:
        fm = [m for m in markers if m['floor_plan_id'] == fp['id']]
        floor_data.append({
            'floor': fp['floor_label'],
            'name':  fp['name'],
            'scans': sum(m.get('scan_count',0) for m in fm),
            'markers': len(fm)
        })

    # Top locations
    top_scanned = sorted(markers, key=lambda m: m.get('scan_count',0), reverse=True)[:8]
    top_dest    = sorted(markers, key=lambda m: m.get('dest_count',0), reverse=True)[:8]

    # Recent logs
    marker_map = {m['id']: m for m in markers}
    recent = list(db.scan_logs.find({'org_id': org_id}, {'_id':0})
                  .sort('scanned_at',-1).limit(20))
    for l in recent:
        l['marker_label'] = marker_map.get(l.get('marker_id',''), {}).get('label','Unknown')
        l['dest_label']   = marker_map.get(l.get('dest_id',''),   {}).get('label','Unknown')
        if hasattr(l.get('scanned_at'), 'isoformat'):
            l['scanned_at'] = l['scanned_at'].isoformat()

    return jsonify({
        'total_scans':   total_scans,
        'total_markers': total_markers,
        'total_floors':  len(fps),
        'today_scans':   today_scans,
        'daily_data':    daily_data,
        'floor_data':    floor_data,
        'top_scanned':   top_scanned,
        'top_dest':      top_dest,
        'recent_logs':   recent
    })
