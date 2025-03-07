# API Endpoints for Maintenance Tracking App with Database Integration

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maintenance.db'  # Change to your DB URL (e.g., PostgreSQL, MySQL)
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
    area_id = db.Column(db.Integer, db.ForeignKey('areas.area_id', ondelete='CASCADE'))
    machine_name = db.Column(db.String(100), nullable=False)
    asset_number = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(255))
    last_maintenance_date = db.Column(db.Date)

# Create the database tables
with app.app_context():
    db.create_all()


# --- MACHINES Endpoints ---
@app.route('/areas/<int:area_id>/machines', methods=['GET', 'POST'])
def manage_machines(area_id):
    if request.method == 'POST':
        # Add a new machine to the area
        data = request.get_json()
        new_machine = Machine(
            area_id=area_id,
            machine_name=data.get('machine_name'),
            asset_number=data.get('asset_number'),
            location=data.get('location'),
            last_maintenance_date=data.get('last_maintenance_date')
        )
        db.session.add(new_machine)
        db.session.commit()
        return jsonify({'message': 'Machine added', 'machine_id': new_machine.machine_id}), 201

    # Get all machines in the area
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
        # Get machine details
        return jsonify({
            'machine_id': machine.machine_id,
            'machine_name': machine.machine_name,
            'asset_number': machine.asset_number,
            'location': machine.location,
            'last_maintenance_date': machine.last_maintenance_date
        })

    elif request.method == 'PUT':
        # Update machine details
        data = request.get_json()
        machine.machine_name = data.get('machine_name', machine.machine_name)
        machine.asset_number = data.get('asset_number', machine.asset_number)
        machine.location = data.get('location', machine.location)
        machine.last_maintenance_date = data.get('last_maintenance_date', machine.last_maintenance_date)
        db.session.commit()
        return jsonify({'message': 'Machine updated'})

    elif request.method == 'DELETE':
        # Delete a machine
        db.session.delete(machine)
        db.session.commit()
        return jsonify({'message': 'Machine deleted'})

if __name__ == '__main__':
    app.run(debug=True)
