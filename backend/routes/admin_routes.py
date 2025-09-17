import os
import uuid
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from models import User, Application, Rapport, db, Stagiaire

admin_bp = Blueprint('admin', __name__)

UPLOAD_ATTEST = 'uploads/attestations'
os.makedirs(UPLOAD_ATTEST, exist_ok=True)

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
            app_data = {
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
            }
            result.append(app_data)
        return jsonify(result), 200
    except Exception as e:
        logging.exception("Failed to fetch applications")
        return jsonify({"error": str(e)}), 500

# --- Mise à jour du statut d'une candidature ---
@admin_bp.route('/admin/candidature/<int:application_id>/statut', methods=['PUT'])
def update_application_status(application_id):
    try:
        data = request.json
        nouveau_statut = data.get('statut')
        
        if nouveau_statut not in ['accepté', 'refusé']:
            return jsonify({"error": "Invalid status"}), 400
            
        application = Application.query.get(application_id)
        if not application:
            return jsonify({"error": "Application not found"}), 404
            
        application.statut = nouveau_statut
        db.session.commit()
        
        return jsonify({"message": f"Status updated to: {nouveau_statut}"}), 200
    except Exception as e:
        db.session.rollback()
        logging.exception("Failed to update application status")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/upload_attestation/<int:stagiaire_id>', methods=['POST'])
def upload_attestation(stagiaire_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Récupérer le stagiaire
    stagiaire = Stagiaire.query.get(stagiaire_id)
    if not stagiaire:
        return jsonify({'error': 'Intern not found'}), 404

    # Générer un nom unique pour le fichier
    filename = f"attestation_{stagiaire_id}_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(UPLOAD_ATTEST, filename)
    
    try:
        file.save(file_path)
        
        # Mettre à jour le nom du fichier dans la base de données
        stagiaire.attestation_filename = filename
        db.session.commit()
        
        return jsonify({'message': 'Certificate uploaded successfully', 'filename': filename}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to upload certificate: {str(e)}'}), 500

# --- Téléchargement de CV ---
@admin_bp.route('/admin/download/cv/<filename>', methods=['GET'])
def download_cv(filename):
    folder = os.path.abspath('uploads/cv')  
    file_path = os.path.join(folder, filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": f"File not found: {file_path}"}), 404
    return send_from_directory(folder, filename, as_attachment=True)

# --- Téléchargement de lettre de motivation ---
@admin_bp.route('/admin/download/motivation/<filename>', methods=['GET'])
def download_motivation(filename):
    folder = os.path.abspath('uploads/motivation')
    file_path = os.path.join(folder, filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": f"File not found: {file_path}"}), 404
    return send_from_directory(folder, filename, as_attachment=True)

# --- Upload d'attestation (route renommée pour éviter conflit) ---
@admin_bp.route('/admin/upload-attestation', methods=['POST'])
def upload_attestation_pdf():
    try:
        file = request.files.get('attestation')
        if not file:
            return jsonify({'error': 'No file received'}), 400

        stagiaire_id = request.form.get('stagiaire_id')
        if not stagiaire_id:
            return jsonify({'error': 'Missing intern ID'}), 400

        stagiaire = Stagiaire.query.get(stagiaire_id)
        if not stagiaire:
            return jsonify({'error': 'Intern not found'}), 404

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        path = os.path.join(UPLOAD_ATTEST, unique_filename)
        file.save(path)

        # Sauvegarde du nom de fichier dans la base pour ce stagiaire
        stagiaire.attestation_filename = unique_filename
        db.session.commit()

        return jsonify({'message': 'Certificate saved successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logging.exception("Failed to save certificate")
        return jsonify({'error': 'Error saving certificate'}), 500

# --- Téléchargement d'attestation ---
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

# --- Création d'un stagiaire ---
@admin_bp.route('/admin/stagiaire', methods=['POST'])
def create_stagiaire():
    try:
        data = request.json
        application_id = data.get('application_id')
        encadrant = data.get('encadrant')
        sujet = data.get('sujet')

        if not application_id or not encadrant or not sujet:
            return jsonify({"error": "Missing required fields"}), 400

        new_stagiaire = Stagiaire(
            application_id=application_id,
            encadrant=encadrant,
            sujet=sujet
        )
        db.session.add(new_stagiaire)

        # Mettre à jour le statut de la candidature
        application = Application.query.get(application_id)
        if application:
            application.statut = 'accepted'

        db.session.commit()
        return jsonify({"message": "Intern created successfully", "stagiaire_id": new_stagiaire.id}), 201

    except Exception as e:
        db.session.rollback()
        logging.exception("Failed to create intern")
        return jsonify({"error": "Error creating intern"}), 500

# --- Récupération des stagiaires ---
@admin_bp.route('/admin/stagiaires', methods=['GET'])
def get_stagiaires():
    try:
        user_id = request.args.get('user_id', type=int)
        result = []

        # Si user_id est fourni, on filtre
        if user_id:
            stagiaires = (
                db.session.query(Stagiaire)
                .join(Application, Stagiaire.application_id == Application.id)
                .filter(Application.user_id == user_id)
                .all()
            )
        else:
            stagiaires = Stagiaire.query.all()

        for s in stagiaires:
            stagiaire_data = s.serialize()
            application = Application.query.get(s.application_id)
            if application:
                stagiaire_data['application'] = {
                    'name': application.name,
                    'email': application.email,
                    'university': application.university,
                    'statut': application.statut
                }
                stagiaire_data['statut'] = application.statut
            result.append(stagiaire_data)

        return jsonify(result), 200

    except Exception as e:
        logging.exception("Failed to fetch interns")
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/admin/rapport/<int:user_id>/commentaire', methods=['POST'])
def commenter_rapport(user_id):
    data = request.json
    commentaire = data.get('commentaire')
    if not commentaire:
        return jsonify({"error": "Missing comment"}), 400

    rapport = Rapport(user_id=user_id, commentaire=commentaire)
    db.session.add(rapport)
    db.session.commit()

    return jsonify({"message": "Comment added"}), 201
