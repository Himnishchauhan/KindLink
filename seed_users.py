import os
from app import app, db, User
from werkzeug.security import generate_password_hash

volunteers = [
    {"name": "Aarav Sharma", "email": "aarav@example.com", "mobile": "+91 9876543210", "password": "password123", "role": "volunteer", "location": "Mumbai, Maharashtra", "skills": "teaching, mentoring", "availability": "Weekends"},
    {"name": "Priya Patel", "email": "priya@example.com", "mobile": "+91 9876543211", "password": "password123", "role": "volunteer", "location": "Delhi, NCR", "skills": "planting, cleaning", "availability": "Evenings"},
    {"name": "Rohan Gupta", "email": "rohan@example.com", "mobile": "+91 9876543212", "password": "password123", "role": "volunteer", "location": "Bangalore, Karnataka", "skills": "coding, web development", "availability": "Flexible"},
    {"name": "Kavya Singh", "email": "kavya@example.com", "mobile": "+91 9876543213", "password": "password123", "role": "volunteer", "location": "Chennai, Tamil Nadu", "skills": "cooking, distribution", "availability": "Weekdays mornings", "is_available_now": True},
    {"name": "Vikram Desai", "email": "vikram@example.com", "mobile": "+91 9876543214", "password": "password123", "role": "volunteer", "location": "Pune, Maharashtra", "skills": "event management, speaking", "availability": "Weekends", "is_available_now": True}
]

ngos = [
    {"name": "Green Earth India", "email": "contact@greenearth.in", "mobile": "+91 8876543210", "password": "password123", "role": "ngo", "location": "Mumbai, Maharashtra", "mission": "Promoting afforestation and reducing carbon footprint across major cities."},
    {"name": "EduCare Foundation", "email": "hello@educare.org", "mobile": "+91 8876543211", "password": "password123", "role": "ngo", "location": "Delhi, NCR", "mission": "Providing free education and educational resources to underprivileged children."},
    {"name": "Tech for Good", "email": "admin@techforgood.in", "mobile": "+91 8876543212", "password": "password123", "role": "ngo", "location": "Bangalore, Karnataka", "mission": "Building digital solutions and websites for rural health organizations."},
    {"name": "Food Relief Network", "email": "support@foodrelief.in", "mobile": "+91 8876543213", "password": "password123", "role": "ngo", "location": "Chennai, Tamil Nadu", "mission": "Distributing surplus food to homeless shelters and managing food banks."},
    {"name": "Animal Rescue Squad", "email": "rescue@animalsquad.in", "mobile": "+91 8876543214", "password": "password123", "role": "ngo", "location": "Pune, Maharashtra", "mission": "Rescuing and rehabilitating stray and injured animals."}
]

with app.app_context():
    count = 0
    # Seed Volunteers
    for v in volunteers:
        if not User.query.filter_by(email=v['email']).first():
            new_v = User(
                role=v['role'],
                name=v['name'],
                email=v['email'],
                password=generate_password_hash(v['password']),
                mobile=v['mobile'],
                location=v['location'],
                skills=v['skills'],
                availability=v['availability'],
                is_available_now=v.get('is_available_now', False)
            )
            db.session.add(new_v)
            count += 1
            
    # Seed NGOs
    for n in ngos:
        if not User.query.filter_by(email=n['email']).first():
            new_n = User(
                role=n['role'],
                name=n['name'],
                email=n['email'],
                password=generate_password_hash(n['password']),
                mobile=n['mobile'],
                location=n['location'],
                mission=n['mission']
            )
            db.session.add(new_n)
            count += 1
            
    db.session.commit()
    print(f"Successfully seeded {count} new users!")
