from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Volunteer
    v = User.query.filter_by(email='volunteer@demo.com').first()
    if not v:
        v = User(
            role='volunteer',
            name='John Doe',
            email='volunteer@demo.com',
            password=generate_password_hash('password123'),
            location='New York, NY',
            skills='Teaching, Mentoring',
            interests='Education',
            availability='Weekends'
        )
        db.session.add(v)
    
    # NGO
    n = User.query.filter_by(email='ngo@demo.com').first()
    if not n:
        n = User(
            role='ngo',
            name='Global Education Outreach',
            email='ngo@demo.com',
            password=generate_password_hash('password123'),
            location='New York, NY',
            mission='Providing free education and mentorship to underprivileged kids.'
        )
        db.session.add(n)
        
    db.session.commit()
    print("Seed successful")
