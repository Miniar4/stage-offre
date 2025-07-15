from flask import Blueprint, jsonify, request, send_from_directory
from models import User, Application, Rapport, db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/comptes', methods=['GET'])
def get_comptes():
    try:
        users = User.query.all()
        return jsonify([u.serialize() for u in users]), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch users"}), 500

@admin_bp.route('/admin/candidatures', methods=['GET'])
def get_all_candidatures():
    try:
        applications = Application.query.all()
        result = []
        for app in applications:
            result.append({
                "id": app.id,
                "user_id": app.user_id,
                "offre_id": app.offer_id,
                "statut": app.statut,
                "date_candidature": app.date_candidature.isoformat() if app.date_candidature else None
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch applications"}), 500

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
            app.date_entretien = data.get("date_entretien")
            app.lieu_entretien = data.get("lieu_entretien")

        db.session.commit()
        return jsonify({"message": "Status updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update status"}), 500

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
        return jsonify({"error": "Failed to add comment"}), 500

@admin_bp.route('/admin/download/cv/<filename>', methods=['GET'])
def download_cv(filename):
    try:
        return send_from_directory('uploads/cv', filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": "File not found"}), 404

@admin_bp.route('/admin/download/motivation/<filename>', methods=['GET'])
def download_motivation(filename):
    try:
        return send_from_directory('uploads/motivation', filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": "File not found"}), 404