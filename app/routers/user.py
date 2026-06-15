from fastapi import FastAPI, APIRouter

router = APIRouter(prefix="/user")
from  app.routers import *
class User_request_handle():


    def HandleSignup(payload):
        data = payload
        data
        data.username



@router.get('/dashboard', methods=['GET'])

def dashboard():
    try:
        user_id = get_jwt_identity()
        files = File.query.filter_by(user_id=user_id).all()
        return jsonify({
            'files': [{
                'id': f.id,
                'filename': f.original_filename or f.filename,
                'created_at': f.created_at.isoformat()
            } for f in files]
        }), 200
    except Exception as e:
        print(f"[dashboard] Error: {e}")
        return jsonify({'error': 'Failed to fetch files'}), 500