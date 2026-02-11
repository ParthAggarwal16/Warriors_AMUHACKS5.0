from flask import Blueprint, request, jsonify, render_template
from models import get_db
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/profile')
def profile():
    return render_template('profile.html')

@api_bp.route('/api/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    current_email = data.get('current_email')
    new_name = data.get('new_name')
    new_email = data.get('new_email')

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if new email is taken (if changed)
        if new_email != current_email:
            cursor.execute("SELECT * FROM users WHERE email = ?", (new_email,))
            if cursor.fetchone():
                return jsonify({'message': 'Email already in use'}), 400

        cursor.execute("UPDATE users SET name = ?, email = ? WHERE email = ?", (new_name, new_email, current_email))
        conn.commit()

    return jsonify({'message': 'Profile updated successfully', 'user': {'name': new_name, 'email': new_email}}), 200

@api_bp.route('/api/save-plan', methods=['POST'])
def save_plan():
    data = request.get_json()
    email = data.get('email')
    plan_data = data.get('plan_data') # This will be a JSON string of userData

    if not email or not plan_data:
        return jsonify({'message': 'Missing data'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        # Check if plan exists, update it; otherwise insert
        cursor.execute("SELECT id FROM plans WHERE user_email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("UPDATE plans SET plan_data = ? WHERE user_email = ?", (json.dumps(plan_data), email))
        else:
            cursor.execute("INSERT INTO plans (user_email, plan_data) VALUES (?, ?)", (email, json.dumps(plan_data)))
        conn.commit()

    return jsonify({'message': 'Plan saved successfully'}), 200

@api_bp.route('/api/get-plan', methods=['GET'])
def get_plan():
    email = request.args.get('email')
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT plan_data FROM plans WHERE user_email = ?", (email,))
        row = cursor.fetchone()
    
    if row:
        return jsonify({'plan_data': json.loads(row['plan_data'])}), 200
    return jsonify({'message': 'No plan found'}), 404