from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from extensions import mail
from models import get_db
import sqlite3
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    # Input Validation
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Invalid email address format'}), 400
    
    if not password or len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
    if not name or len(name.strip()) < 2:
        return jsonify({'message': 'Name must be at least 2 characters long'}), 400

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", (email, hashed_password, name))
            conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'User already exists'}), 400
    
    return jsonify({'message': 'User created successfully', 'token': 'dummy-token', 'user': {'name': name, 'email': email}}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({'message': 'Login successful', 'token': 'dummy-token', 'user': {'name': user['name'], 'email': email}}), 200

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

    if user:
        try:
            msg = Message("Password Reset Request", sender=current_app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f"Hello {user['name']},\n\nTo reset your password, please click the link below (this is a simulation):\nhttp://localhost:5000/reset-password?email={email}\n\nIf you did not request this, please ignore this email."
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")
            
    return jsonify({'message': 'If an account exists with this email, a password reset link has been sent.'}), 200

@auth_bp.route('/reset-password')
def reset_password_page():
    return render_template('reset-password.html')

@auth_bp.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('password')
    
    if not email or not new_password:
        return jsonify({'message': 'Missing data'}), 400
        
    # Password strength validation
    if len(new_password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long'}), 400

    hashed_password = generate_password_hash(new_password)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
        conn.commit()

    return jsonify({'message': 'Password updated successfully'}), 200