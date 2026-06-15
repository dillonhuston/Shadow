from fastapi import FastAPI, APIRouter


router = APIRouter(prefix="/file")



@router.post('/upload')
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()
    file = request.files.get('file')

    if not file or file.filename == '':
        return jsonify({'error': 'No file provided'}), 400

    file.seek(0, os.SEEK_END)
    if file.tell() > 10 * 1024 * 1024:
        return jsonify({'error': 'File too large'}), 400
    file.seek(0)

    filename = secure_filename(file.filename)
    file_data = file.read()
    encoded_data = base64.b64encode(file_data).decode('utf-8')

    user = User.query.get(user_id)
    try:
        print(f"[upload] User: {user_id}, File: {filename}")
        encrypted_filename = EncryptionService.encrypt(encoded_data, filename, user_id, user.get_key())
        encrypted_path = os.path.join(Config.ENCRYPTED_FILE_PATH, encrypted_filename)

        new_file = File(
            user_id=user_id,
            filename=encrypted_filename,
            filepath=encrypted_path,
            original_filename=filename
        )

        db.session.add(new_file)
        db.session.commit()

        print(f"[upload] Saved: {new_file.id} as {encrypted_filename}")
        return jsonify({'message': f'{filename} uploaded'}), 201

    except EncryptionService.EncryptionError as e:
        print(f"[upload] Encryption error: {e}")
        return jsonify({'error': str(e)}), 500

    except Exception as e:
        print(f"[upload] General error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Upload failed'}), 500

@router.get('/files')
@jwt_required()
def list_files():
    try:
        user_id = get_jwt_identity()
        files_info = []

        for name in os.listdir(Config.ENCRYPTED_FILE_PATH):
            path = os.path.join(Config.ENCRYPTED_FILE_PATH, name)
            if os.path.isfile(path):
                entry = File.query.filter_by(user_id=user_id, filename=name).first()
                if entry:
                    files_info.append({
                        'filename': entry.original_filename or entry.filename,
                        'size': os.path.getsize(path),
                        'created_at': entry.created_at.isoformat() if entry.created_at else None
                    })

        return jsonify({'files': files_info}), 200

    except Exception as e:
        print(f"[files] Error: {e}")
        return jsonify({'error': 'Failed to list files'}), 500

@router.get('/download/<file_id>')
@jwt_required()
def download_file(file_id):
    try:
        user_id = get_jwt_identity()
        file_entry = File.query.filter_by(id=file_id, user_id=user_id).first()

        if not file_entry:
            return jsonify({'error': 'File not found or unauthorized'}), 404

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        path = file_entry.filepath.replace('/', os.sep)
        if not os.path.exists(path):
            return jsonify({'error': 'File not found on server'}), 404

        print(f"[download] Decrypting {file_entry.filename} for user {user_id}")
        decrypted_b64 = EncryptionService.decrypt(file_entry.filename, user_id, user.get_key())
        decrypted_data = base64.b64decode(decrypted_b64)

        filename = file_entry.original_filename or file_entry.filename
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'txt'
        mimetypes = {
            'txt': 'text/plain',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

        return send_file(
            BytesIO(decrypted_data),
            download_name=filename,
            mimetype=mimetypes.get(ext, 'application/octet-stream'),
            as_attachment=True
        )
    
    except Exception as e:
        print(f"[download] Error: {e}")
        return jsonify({'error': 'Download failed'}), 500

@router.delete('/delete/<file_id>')
@jwt_required()
def delete_file(file_id):
    try:
        user_id = get_jwt_identity()
        file = File.query.filter_by(id=file_id, user_id=user_id).first()
        if not file:
            return jsonify({'error': 'File not found or unauthorized'}), 404

        File.deletefile(file)
        print(f"[delete] File {file_id} deleted for user {user_id}")
        return jsonify({'message': 'File deleted successfully'}), 200

    except Exception as e:
        print(f"[delete] Error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete file'}), 500

with app.app_context():
    db.create_all()
