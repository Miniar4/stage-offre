# cSpell:disable
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    def serialize(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            
        }
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    nb_souhaitee = db.Column(db.Integer, nullable=False, default=1)
    competences = db.Column(db.String(255), nullable=True)
    duree = db.Column(db.String(100), nullable=True)
    date_debut = db.Column(db.Date, nullable=True)
    date_fin = db.Column(db.Date, nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "nb_souhaitee": self.nb_souhaitee,
            "competences": self.competences,
            "duree": self.duree,
            "date_debut": self.date_debut.isoformat() if self.date_debut else None,
            "date_fin": self.date_fin.isoformat() if self.date_fin else None,
            "date_creation": self.date_creation.isoformat()
        }



    # etc.

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    offer_id = db.Column(db.Integer, db.ForeignKey('offer.id'))
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    university = db.Column(db.String(150))
    education = db.Column(db.String(150))
    duration = db.Column(db.String(100))
    motivation = db.Column(db.Text)
    cv_filename = db.Column(db.String(255))
    motivation_filename = db.Column(db.String(255))
    statut = db.Column(db.String(50), default="en attente")
    date_entretien = db.Column(db.DateTime, nullable=True)
    lieu_entretien = db.Column(db.String(150), nullable=True)
    date_candidature = db.Column(db.DateTime, default=datetime.utcnow)


    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "offer_id": self.offer_id,
            "name": self.name,
            "email": self.email,
            "university": self.university,
            "education": self.education,
            "duration": self.duration,
            "motivation": self.motivation,
            "cv_filename": self.cv_filename,
            "motivation_filename": self.motivation_filename,
            "statut": self.statut,
            "date_entretien": self.date_entretien.isoformat() if self.date_entretien else None,
            "lieu_entretien": self.lieu_entretien,
            "date_candidature": self.date_candidature.isoformat() if self.date_candidature else None

        }



class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "message": self.message
        }

class Rapport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fichier = db.Column(db.String(255))
    commentaire = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fichier": self.fichier,
            "commentaire": self.commentaire,
            "created_at": self.created_at.isoformat()
        }
