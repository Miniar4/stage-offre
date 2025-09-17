from flask import Flask, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from models import db
from routes.auth_routes import auth_bp
from routes.contact import contact_bp
from routes.offer_routes import offer_bp
from routes.admin_routes import admin_bp
from routes.rapport_routes import rapport_bp
from routes.user_routes import user_bp
from routes.attestation import attestation_bp
import logging

app = Flask(__name__)

# Configuration de base
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'cle_jwt_super_secrete'  
jwt = JWTManager(app)
app.secret_key = "votre_secret_key_ici"  

CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)


# Initialisation extensions
db.init_app(app)
bcrypt = Bcrypt(app)

# Activer logging simple pour debug
logging.basicConfig(level=logging.DEBUG)

@app.after_request
def after_request(response):
    logging.debug(f"{request.method} {request.path} - Status: {response.status}")
    return response

# Enregistrement des blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(offer_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(rapport_bp)
app.register_blueprint(user_bp)
app.register_blueprint(attestation_bp)

# Point d’entrée principal
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
