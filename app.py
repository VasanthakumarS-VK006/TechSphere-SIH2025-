from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# PostgreSQL config (replace with your actual user/password/db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:vasanth@localhost:5432/civicdb'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='citizen')
    phone = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# User model
class Reports(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    def __init__(self, id, title, description, category, location, lat, lon, status, time, department):
        self.id = id
        self.title = title
        self.description = description 
        self.category = category
        self.location = location
        self.lat = lat
        self.lon = lon
        self.status = status
        self.time = time
        self.department = department

# --- Initialize DB tables once ---
with app.app_context():
    db.create_all()


# Registration
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email', '').lower()

    if not data.get('name') or not email or not data.get('password') or not data.get('phone'):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    new_user = User(
        name=data['name'],
        email=email,
        role=data.get('role', 'citizen'),
        phone=data['phone']
    )
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully',
        'user': {
            'id': new_user.id,
            'name': new_user.name,
            'email': new_user.email,
            'role': new_user.role
        }
    }), 201


# Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route("/report/post", methods=["POST"])
def InsertReport():
    report = request.get_json()

    rp = Reports(report["id"], report["title"], report["description"], report["category"], report["location"], report["lat"], report["lon"], report["status"], report["time"],  report["department"])
    db.session.add(rp)
    db.session.commit()
    return jsonify({"message" : "Success"})

if __name__ == '__main__':
    app.run(debug=True)
