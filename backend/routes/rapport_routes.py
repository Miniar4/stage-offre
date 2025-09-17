from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from models import db, Rapport

rapport_bp = Blueprint('rapport', __name__)
UPLOAD_FOLDER = 'uploads/rapports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Upload rapport par userId
@rapport_bp.route('/user/<int:user_id>/rapport/upload', methods=['POST'])
def upload_rapport(user_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    filename = f"{user_id}.pdf"  # on force le nom pour un seul fichier par user
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # TODO: Mettre à jour la BDD si nécessaire (ex: marquer rapport reçu)
    return jsonify({'message': 'Rapport uploaded successfully'}), 200


# Download rapport par userId
@rapport_bp.route('/user/<int:user_id>/rapport/download', methods=['GET'])
def download_rapport(user_id):
    filepath = os.path.join(UPLOAD_FOLDER, f"{user_id}.pdf")
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    return send_file(filepath, as_attachment=True)


# Vérifier si le rapport existe
@rapport_bp.route('/user/<int:user_id>/rapport/exists', methods=['GET'])
def rapport_exists(user_id):
    filepath = os.path.join(UPLOAD_FOLDER, f"{user_id}.pdf")
    return jsonify({'exists': os.path.exists(filepath)}), 200
# Téléchargement du rapport de n'importe quel utilisateur (admin)
@rapport_bp.route('/admin/<int:user_id>/rapport/download', methods=['GET'])
def admin_download_rapport(user_id):
    filepath = os.path.join(UPLOAD_FOLDER, f"{user_id}.pdf")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Report not found'}), 404
    return send_file(filepath, as_attachment=True)

# Vérifier si un utilisateur a un rapport
@rapport_bp.route('/admin/<int:user_id>/rapport/exists', methods=['GET'])
def admin_rapport_exists(user_id):
    filepath = os.path.join(UPLOAD_FOLDER, f"{user_id}.pdf")
    return jsonify({'exists': os.path.exists(filepath)}), 200

# (Optionnel) Ajouter un commentaire sur le rapport d'un user
@rapport_bp.route('/admin/<int:user_id>/rapport/commentaire', methods=['POST'])
def admin_commenter_rapport(user_id):
    data = request.json
    commentaire = data.get('commentaire')
    if not commentaire:
        return jsonify({"error": "Missing comment"}), 400

    # ici tu peux enregistrer dans ta base (exemple modèle Rapport)
    rapport = Rapport(user_id=user_id, commentaire=commentaire)
    db.session.add(rapport)
    db.session.commit()

    return jsonify({"message": "Comment added"}), 201