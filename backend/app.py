from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt

from models import db
from routes.auth_routes import auth_bp
from routes.contact import contact_bp
from routes.offer_routes import offer_bp
from routes.admin_routes import admin_bp
from routes.rapport_routes import rapport_bp
from routes.user_routes import user_bp

app = Flask(__name__)

# CORS : autoriser toutes les origines pour le dev (à restreindre en prod !)
CORS(app, resources={r"/*": {"origins": "*"}})

# Config Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "votre_secret_key_ici"  # à sécuriser en prod

# Initialisation extensions
db.init_app(app)
bcrypt = Bcrypt(app)

# Enregistrement des blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(offer_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(rapport_bp)
app.register_blueprint(user_bp)

# Point d’entrée principal
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crée toutes les tables si elles n'existent pas
    app.run(debug=True)
