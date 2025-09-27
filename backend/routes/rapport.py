from flask import Blueprint, request, jsonify, send_from_directory, send_file
import os
from werkzeug.utils import secure_filename
from models import db, Rapport
from datetime import datetime

rapport_bp = Blueprint('rapport_bp', __name__)
UPLOAD_FOLDER = 'uploads/rapports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -----------------------------
# Upload rapport par userId
# -----------------------------
@rapport_bp.route('/user/<int:user_id>/rapport/upload', methods=['POST'])
def upload_rapport(user_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF allowed'}), 400

    filename = secure_filename(f"{user_id}.pdf")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({'error': f'Cannot save file: {str(e)}'}), 500

    # Mettre à jour la BDD
    rapport = Rapport.query.filter_by(user_id=user_id).first()
    if not rapport:
        rapport = Rapport(user_id=user_id, fichier=filename)
        db.session.add(rapport)
    else:
        rapport.fichier = filename
    db.session.commit()

    return jsonify({'message': 'Rapport uploaded successfully'}), 200


# -----------------------------
# Télécharger rapport par userId
# -----------------------------
@rapport_bp.route('/user/<int:user_id>/rapport/download', methods=['GET'])
def download_rapport(user_id):
    # Récupérer le dernier rapport
    rapport = Rapport.query.filter_by(user_id=user_id).order_by(Rapport.created_at.desc()).first()
    if rapport:
        filepath = os.path.join(UPLOAD_FOLDER, rapport.fichier)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    return jsonify({'error': 'No rapport found'}), 404

# -----------------------------
# Vérifier si le rapport existe
# -----------------------------
@rapport_bp.route('/user/<int:user_id>/rapport/exists', methods=['GET'])
def rapport_exists(user_id):
    exists = Rapport.query.filter_by(user_id=user_id).first() is not None
    return jsonify({'exists': exists}), 200

# -----------------------------
# Télécharger rapport (admin)
# -----------------------------
@rapport_bp.route('/admin/<int:user_id>/rapport/download', methods=['GET'])
def admin_download_rapport(user_id):
    rapport = Rapport.query.filter_by(user_id=user_id).order_by(Rapport.created_at.desc()).first()
    if rapport:
        filepath = os.path.join(UPLOAD_FOLDER, rapport.fichier)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    return jsonify({'error': 'No rapport found'}), 404

# -----------------------------
# Vérifier rapport (admin)
# -----------------------------
@rapport_bp.route('/admin/<int:user_id>/rapport/exists', methods=['GET'])
def admin_rapport_exists(user_id):
    exists = Rapport.query.filter_by(user_id=user_id).first() is not None
    return jsonify({'exists': exists}), 200

# -----------------------------
# Commentaire rapport (admin)
# -----------------------------
@rapport_bp.route('/admin/<int:user_id>/rapport/commentaire', methods=['POST'])
def admin_commenter_rapport(user_id):
    data = request.json
    commentaire = data.get('commentaire')
    if not commentaire:
        return jsonify({"error": "Missing comment"}), 400

    # Ajouter commentaire au dernier rapport
    rapport = Rapport.query.filter_by(user_id=user_id).order_by(Rapport.created_at.desc()).first()
    if not rapport:
        return jsonify({'error': 'No rapport found'}), 404

    rapport.commentaire = commentaire
    db.session.commit()
    return jsonify({"message": "Comment added", "rapport": rapport.serialize()}), 201
