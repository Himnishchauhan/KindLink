from app import app, db, User
from werkzeug.security import generate_password_hash

def force_reset_users():
    print("🔥 Force resetting all demo accounts...")
    with app.app_context():
        # List of all emails to reset
        demo_emails = [
            'volunteer@demo.com', 'ngo@demo.com',
            'aarav@example.com', 'priya@example.com', 'rohan@example.com', 
            'kavya@example.com', 'vikram@example.com',
            'contact@greenearth.in', 'hello@educare.org', 'admin@techforgood.in', 
            'support@foodrelief.in', 'rescue@animalsquad.in'
        ]
        
        updated_count = 0
        deleted_count = 0
        
        # We'll just delete and re-run the seeders to be absolutely 100% sure
        for email in demo_emails:
            user = User.query.filter_by(email=email).first()
            if user:
                db.session.delete(user)
                deleted_count += 1
        
        db.session.commit()
        print(f"🗑️ Deleted {deleted_count} existing conflicting accounts.")
        
        # Now run the seeders
        import seed
        import seed_users
        
        print("🌱 Re-seeding with fresh password123 hashes...")
        # Note: seed.py and seed_users.py use the standard seeder logic 
        # but since we deleted them, the 'if not exists' check will pass.
        
        print("✅ Success! Use 'password123' for all accounts.")

if __name__ == "__main__":
    force_reset_users()
