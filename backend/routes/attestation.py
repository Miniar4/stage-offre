from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from models import db, Stagiaire

attestation_bp = Blueprint('attestation_bp', __name__, url_prefix="/admin")

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'attestations')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload attestation
@attestation_bp.route('/upload_attestation/<int:stagiaire_id>', methods=['POST'])
def upload_attestation(stagiaire_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(f"attestation_stagiaire_{stagiaire_id}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        stagiaire = Stagiaire.query.get(stagiaire_id)
        if stagiaire:
            stagiaire.attestation_filename = filename
            db.session.commit()
            return jsonify({'message': 'Attestation uploaded successfully'}), 200
        else:
            return jsonify({'error': 'Stagiaire not found'}), 404
    else:
        return jsonify({'error': 'Invalid file type. Only PDF allowed'}), 400

# Download attestation
@attestation_bp.route('/get_attestation/<int:stagiaire_id>', methods=['GET'])
def get_attestation(stagiaire_id):
    stagiaire = Stagiaire.query.get(stagiaire_id)
    if stagiaire and stagiaire.attestation_filename:
        filepath = os.path.join(UPLOAD_FOLDER, stagiaire.attestation_filename)
        if os.path.exists(filepath):
            return send_from_directory(UPLOAD_FOLDER, stagiaire.attestation_filename, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    return jsonify({'error': 'Attestation not available'}), 404
