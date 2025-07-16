from flask import Blueprint, request, jsonify
from models import db, Offer,Application
from datetime import datetime
import logging

offer_bp = Blueprint('offer_bp', __name__)

@offer_bp.route('/offres', methods=['GET'])
def get_offres():
    try:
        print("=== GET /offres appelé ===")
        offres = Offer.query.all()
        print(f"Nombre d'offres trouvées: {len(offres)}")
        
        # Sérialisation avec gestion des dates
        offres_serialized = []
        for offre in offres:
            try:
                serialized = offre.serialize()
                print(f"Offre sérialisée: {serialized['titre']}")
                offres_serialized.append(serialized)
            except Exception as e:
                print(f"Erreur sérialisation offre {offre.id}: {e}")
                continue
        
        print(f"Offres sérialisées: {len(offres_serialized)}")
        
        response = jsonify(offres_serialized)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response, 200
    except Exception as e:
        print(f"Erreur dans get_offres: {e}")
        return jsonify({"error": "Failed to fetch offers"}), 500

@offer_bp.route('/offres', methods=['POST'])
def create_offre():
    try:
        print("=== POST /offres appelé ===")
        data = request.json
        print(f"Données reçues: {data}")
        
        if not data or not data.get('titre') or not data.get('description'):
            return jsonify({"error": "Fields 'titre' and 'description' are required"}), 400

        # Gestion des dates
        date_debut = None
        date_fin = None
        
        if data.get('date_debut'):
            try:
                date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
            except ValueError:
                print(f"Format date_debut invalide: {data['date_debut']}")
        
        if data.get('date_fin'):
            try:
                date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
            except ValueError:
                print(f"Format date_fin invalide: {data['date_fin']}")

        offre = Offer(
            titre=data['titre'],
            description=data['description'],
            nb_souhaitee=data.get('nb_souhaitee', 1),
            competences=data.get('competences'),
            duree=data.get('duree'),
            date_debut=date_debut,
            date_fin=date_fin
        )
        
        db.session.add(offre)
        db.session.commit()
        
        print(f"Offre créée avec ID: {offre.id}")
        
        return jsonify({
            "message": "Offer created successfully", 
            "id": offre.id,
            "offre": offre.serialize()
        }), 201
    except Exception as e:
        print(f"Erreur dans create_offre: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to create offer"}), 500

@offer_bp.route('/offres/<int:id>', methods=['PUT'])
def update_offre(id):
    try:
        print(f"=== PUT /offres/{id} appelé ===")
        data = request.json
        offre = Offer.query.get(id)
        if not offre:
            return jsonify({"error": "Offer not found"}), 404

        # Mise à jour des champs
        if 'titre' in data:
            offre.titre = data['titre']
        if 'description' in data:
            offre.description = data['description']
        if 'nb_souhaitee' in data:
            offre.nb_souhaitee = data['nb_souhaitee']
        if 'competences' in data:
            offre.competences = data['competences']
        if 'duree' in data:
            offre.duree = data['duree']
        
        # Gestion des dates
        if 'date_debut' in data and data['date_debut']:
            try:
                offre.date_debut = datetime.strptime(data['date_debut'], '%Y-%m-%d').date()
            except ValueError:
                print(f"Format date_debut invalide: {data['date_debut']}")
        
        if 'date_fin' in data and data['date_fin']:
            try:
                offre.date_fin = datetime.strptime(data['date_fin'], '%Y-%m-%d').date()
            except ValueError:
                print(f"Format date_fin invalide: {data['date_fin']}")

        db.session.commit()
        print(f"Offre {id} mise à jour")
        return jsonify({"message": "Offer updated successfully"}), 200
    except Exception as e:
        print(f"Erreur dans update_offre: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to update offer"}), 500

@offer_bp.route('/offres/<int:id>', methods=['DELETE'])
def delete_offre(id):
    try:
        print(f"=== DELETE /offres/{id} appelé ===")
        offre = Offer.query.get(id)
        if not offre:
            return jsonify({"error": "Offer not found"}), 404

        db.session.delete(offre)
        db.session.commit()
        print(f"Offre {id} supprimée")
        return jsonify({"message": "Offer deleted successfully"}), 200
    except Exception as e:
        print(f"Erreur dans delete_offre: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to delete offer"}), 500

# Route de debug pour vérifier les données
@offer_bp.route('/debug/offres', methods=['GET'])
def debug_offres():
    try:
        offres = Offer.query.all()
        debug_info = {
            'total_offres': len(offres),
            'offres_details': []
        }
        
        for offre in offres:
            debug_info['offres_details'].append({
                'id': offre.id,
                'titre': offre.titre,
                'description': offre.description[:50] + '...' if len(offre.description) > 50 else offre.description,
                'date_creation': offre.date_creation.isoformat(),
                'date_debut': offre.date_debut.isoformat() if offre.date_debut else None,
                'date_fin': offre.date_fin.isoformat() if offre.date_fin else None
            })
        
        return jsonify(debug_info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@offer_bp.route('/offres/<int:id>/apply', methods=['POST'])
def postuler_offre(id):
    try:
        print(f"POST /offres/{id}/apply - Candidature reçue")
        name = request.form.get('name')
        email = request.form.get('email')
        university = request.form.get('university')
        education = request.form.get('education')
        duration = request.form.get('duration')
        motivation = request.form.get('motivation')
        cv = request.files.get('cv')
        motivation_letter = request.files.get('motivationLetter')

        if not all([name, email, university, education, duration, motivation, cv, motivation_letter]):
            return jsonify({"error": "Tous les champs sont requis"}), 400

        # Sauvegarde des fichiers
        cv_filename = f"cv_{email}.pdf"
        lettre_filename = f"lettre_{email}.pdf"
        cv.save(f"uploads/cv/{cv_filename}")
        motivation_letter.save(f"uploads/motivation/{lettre_filename}")

        # Enregistrement dans la base de données
        candidature = Application(
            offer_id=id,
            name=name,
            email=email,
            university=university,
            education=education,
            duration=duration,
            motivation=motivation,
            cv_filename=cv_filename,
            motivation_filename=lettre_filename
        )
        db.session.add(candidature)
        db.session.commit()

        print(f"Candidature de {name} enregistrée.")
        return jsonify({"message": "Candidature reçue avec succès"}), 201
    except Exception as e:
        print(f"Erreur dans postuler_offre: {e}")
        db.session.rollback()
        return jsonify({"error": "Erreur serveur"}), 500
