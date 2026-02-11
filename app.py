from flask import Flask, render_template
import os
from extensions import mail
from models import init_db
from auth import auth_bp
from api import api_bp

# Initialize Flask app
# We set template_folder and static_folder to 'frontend' to serve files from there
# static_url_path='' allows serving static files (css/js) from the root URL path
app = Flask(__name__, template_folder='frontend', static_folder='frontend', static_url_path='')

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') # or 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') # or 'your-app-password'

# Initialize Extensions
mail.init_app(app)

# Initialize DB
init_db()

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)