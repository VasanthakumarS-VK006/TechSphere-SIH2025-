from werkzeug.security import generate_password_hash
from app import app, db, Admin  # replace with your filename

departments = [
    ("pwd.admin@civicconnect.gov.in", "PWD@1234", "Public Works Department"),
    ("water.admin@civicconnect.gov.in", "WATER@1234", "Water Supply Department"),
    ("electric.admin@civicconnect.gov.in", "POWER@1234", "Electricity Board"),
    ("sanitation.admin@civicconnect.gov.in", "CLEAN@1234", "Sanitation Department"),
    ("traffic.admin@civicconnect.gov.in", "TRAFFIC@1234", "Traffic Management"),
    ("parks.admin@civicconnect.gov.in", "PARKS@1234", "Parks & Recreation"),
    ("municipal.admin@civicconnect.gov.in", "MUNI@1234", "Municipal Office"),
    ("superadmin@civicconnect.gov.in", "Super@1234", "Super Admin"),
]

def seed_admins():
    with app.app_context():
        for mail, raw_password, department in departments:
            # check if already exists
            if not Admin.query.filter_by(mail=mail).first():
                hashed_password = generate_password_hash(raw_password)  # 🔒 secure
                admin = Admin(mail=mail, password=hashed_password, department=department)
                db.session.add(admin)
        db.session.commit()
        print("✅ Admin accounts inserted successfully!")

if __name__ == "__main__":
    seed_admins()

