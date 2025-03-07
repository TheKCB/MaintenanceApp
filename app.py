# API Endpoints for Maintenance Tracking App with Database Integration

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maintenance.db'  # Change to PostgreSQL/MySQL if needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Models ---
class Area(db.Model):
    __tablename__ = 'areas'
    area_id = db.Column(db.Integer, primary_key=True)
    area_name = db.Column(db.String(100), nullable=False)

class Machine(db.Model):
    __tablename__ = 'machines'
    machine_id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.area_id', ondelete='CASCADE'), nullable=False)
    machine_name = db.Column(db.String(100), nullable=False)
    asset_number = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(255), nullable=True)
    last_maintenance_date = db.Column(db.String(50), nullable=True)  # Changed to String to avoid Date issues

# Ensure tables are created before first use
def setup_database():
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")

setup_database()

# --- AREAS Endpoint ---
@app.route('/areas', methods=['GET', 'POST'])
def manage_areas():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'area_name' not in data:
            return jsonify({"error": "Missing 'area_name' field"}), 400

        new_area = Area(area_name=data['area_name'])
        db.session.add(new_area)
        db.session.commit()
        return jsonify({"message": "Area added successfully!", "area_id": new_area.area_id}), 201

    areas = Area.query.all()
    areas_list = [{"area_id": area.area_id, "area_name": area.area_name} for area in areas]
    return jsonify({"areas": areas_list})

# --- MACHINES Endpoints ---
@app.route('/areas/<int:area_id>/machines', methods=['GET', 'POST'])
def manage_machines(area_id):
    if request.method == 'POST':
        data = request.get_json()
        if not data or "machine_name" not in data or "asset_number" not in data:
            return jsonify({"error": "Missing required fields: 'machine_name' and 'asset_number'"}), 400

        new_machine = Machine(
            area_id=area_id,
            machine_name=data.get('machine_name'),
            asset_number=data.get('asset_number'),
            location=data.get('location', None),
            last_maintenance_date=data.get('last_maintenance_date', None)
        )
        db.session.add(new_machine)
        db.session.commit()
        return jsonify({'message': 'Machine added successfully!', 'machine_id': new_machine.machine_id}), 201

    machines = Machine.query.filter_by(area_id=area_id).all()
    machines_list = [
        {
            'machine_id': machine.machine_id,
            'machine_name': machine.machine_name,
            'asset_number': machine.asset_number,
            'location': machine.location,
            'last_maintenance_date': machine.last_maintenance_date
        } for machine in machines
    ]
    return jsonify({'machines': machines_list})

@app.route('/machines/<int:machine_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_machine(machine_id):
    machine = Machine.query.get_or_404(machine_id)

    if request.method == 'GET':
        return jsonify({
            'machine_id': machine.machine_id,
            'machine_name': machine.machine_name,
            'asset_number': machine.asset_number,
            'location': machine.location,
            'last_maintenance_date': machine.last_maintenance_date
        })

    elif request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        machine.machine_name = data.get('machine_name', machine.machine_name)
        machine.asset_number = data.get('asset_number', machine.asset_number)
        machine.location = data.get('location', machine.location)
        machine.last_maintenance_date = data.get('last_maintenance_date', machine.last_maintenance_date)
        db.session.commit()
        return jsonify({'message': 'Machine updated successfully!'})

    elif request.method == 'DELETE':
        db.session.delete(machine)
        db.session.commit()
        return jsonify({'message': 'Machine deleted successfully!'})

# --- Run Flask App ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's assigned port or default to 5000
    print(f"🚀 Running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port)
