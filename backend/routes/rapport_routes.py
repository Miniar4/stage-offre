from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from models import db, Rapport

rapport_bp = Blueprint('rapport', __name__)
UPLOAD_FOLDER = 'uploads/rapports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@rapport_bp.route('/<int:user_id>/upload', methods=['POST'])
def upload_rapport(user_id):
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file received"}), 400

    filename = secure_filename(f"rapport_user_{user_id}.pdf")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    rapport = Rapport.query.filter_by(user_id=user_id).first()
    if not rapport:
        rapport = Rapport(user_id=user_id, fichier=filename)
        db.session.add(rapport)
    else:
        rapport.fichier = filename
    db.session.commit()

    return jsonify({"message": "Report uploaded successfully"}), 200

@rapport_bp.route('/<int:user_id>/download', methods=['GET'])
def download_rapport(user_id):
    filename = f"rapport_user_{user_id}.pdf"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
