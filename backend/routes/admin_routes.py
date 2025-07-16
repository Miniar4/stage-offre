import os
import uuid
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from models import User, Application, Rapport, db

admin_bp = Blueprint('admin', __name__)

UPLOAD_ATTEST = 'uploads/attestations'
os.makedirs(UPLOAD_ATTEST, exist_ok=True)

# Config logger simple
logging.basicConfig(level=logging.INFO)

# --- Récupération de tous les comptes utilisateurs ---
@admin_bp.route('/admin/comptes', methods=['GET'])
def get_comptes():
    try:
        users = User.query.all()
        return jsonify([u.serialize() for u in users]), 200
    except Exception as e:
        logging.exception("Failed to fetch users")
        return jsonify({"error": str(e)}), 500

# --- Récupération de toutes les candidatures ---
@admin_bp.route('/admin/candidatures', methods=['GET'])
def get_all_candidatures():
    try:
        applications = Application.query.all()
        result = []
        for app in applications:
            result.append({
                "id": app.id,
                "user_id": app.user_id,
                "offer_id": app.offer_id,
                "name": app.name,
                "email": app.email,
                "university": app.university,
                "education": app.education,
                "duration": app.duration,
                "motivation": app.motivation,
                "cv_filename": app.cv_filename,
                "motivation_filename": app.motivation_filename,
                "statut": app.statut,
                "date_entretien": app.date_entretien.isoformat() if app.date_entretien else None,
                "lieu_entretien": app.lieu_entretien,
                "date_candidature": app.date_candidature.isoformat() if app.date_candidature else None
            })
        return jsonify(result), 200
    except Exception as e:
        logging.exception("Failed to fetch applications")
        return jsonify({"error": str(e)}), 500

# --- Mise à jour du statut d'une candidature ---
@admin_bp.route('/admin/candidature/<int:id>/statut', methods=['PUT'])
def update_statut(id):
    try:
        data = request.json
        statut = data.get("statut")
        if not statut:
            return jsonify({"error": "Status is required"}), 400

        app = Application.query.get(id)
        if not app:
            return jsonify({"error": "Application not found"}), 404

        app.statut = statut

        if statut == "accepté":
            date_entretien = data.get("date_entretien")  # utilise _ et pas -
            lieu_entretien = data.get("lieu_entretien")
            if date_entretien:
                # convertit en datetime si nécessaire
                app.date_entretien = datetime.fromisoformat(date_entretien)
            if lieu_entretien:
                app.lieu_entretien = lieu_entretien


        db.session.commit()
        return jsonify({"message": "Status updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.exception("Failed to update status")
        return jsonify({"error": str(e)}), 500

# --- Ajouter un commentaire au rapport d'un utilisateur ---
@admin_bp.route('/admin/rapport/<int:user_id>/commentaire', methods=['POST'])
def ajouter_commentaire(user_id):
    try:
        data = request.json
        commentaire = data.get("commentaire")
        if not commentaire:
            return jsonify({"error": "Comment is required"}), 400

        rapport = Rapport.query.filter_by(user_id=user_id).first()
        if not rapport:
            return jsonify({"error": "Report not found"}), 404

        rapport.commentaire = commentaire
        db.session.commit()
        return jsonify({"message": "Comment added successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.exception("Failed to add comment")
        return jsonify({"error": str(e)}), 500

# --- Téléchargement de CV ---
@admin_bp.route('/admin/download/cv/<filename>', methods=['GET'])
def download_cv(filename):
    folder = 'uploads/cv'
    file_path = os.path.join(folder, filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(folder, filename, as_attachment=True)

# --- Téléchargement de lettre de motivation ---
@admin_bp.route('/admin/download/motivation/<filename>', methods=['GET'])
def download_motivation(filename):
    folder = 'uploads/motivation'
    file_path = os.path.join(folder, filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(folder, filename, as_attachment=True)

# --- Upload d'attestation pour un utilisateur ---
@admin_bp.route('/users/<int:user_id>/attestation', methods=['POST'])
def upload_attestation(user_id):
    try:
        file = request.files.get('attestation')
        if not file:
            return jsonify({'error': 'Aucun fichier reçu'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        path = os.path.join(UPLOAD_ATTEST, unique_filename)
        file.save(path)

        user.attestation_filename = unique_filename
        db.session.commit()

        return jsonify({'message': 'Attestation enregistrée'}), 200
    except Exception as e:
        db.session.rollback()
        logging.exception("Failed to save attestation")
        return jsonify({'error': 'Erreur lors de l\'enregistrement de l\'attestation'}), 500

# --- Téléchargement d'une attestation ---
@admin_bp.route('/admin/download/attestation/<filename>', methods=['GET'])
def download_attestation(filename):
    file_path = os.path.join(UPLOAD_ATTEST, filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(UPLOAD_ATTEST, filename, as_attachment=True)

# --- Récupération des messages contact ---
@admin_bp.route('/admin/contacts', methods=['GET'])
def get_all_contacts():
    try:
        from models import Contact
        contacts = Contact.query.all()
        return jsonify([c.serialize() for c in contacts]), 200
    except Exception as e:
        logging.exception("Failed to fetch contacts")
        return jsonify({"error": str(e)}), 500
