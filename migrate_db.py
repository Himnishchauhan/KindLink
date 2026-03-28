import os
from sqlalchemy import text
from app import app, db
import subprocess

def migrate():
    print("🚀 Starting Database Migration...")
    with app.app_context():
        # 1. Create all tables if they don't exist
        # This will create our NEW ImpactMetric and Reward tables automatically!
        db.create_all()
        print("✅ Core tables initialized/verified.")

        # 2. Add columns if needed (handle potential existing schema)
        alterations = [
            ("donation", "order_id", "VARCHAR(255)"),
            ("donation", "razorpay_payment_id", "VARCHAR(255)"),
            ("donation", "currency", "VARCHAR(10) DEFAULT 'INR'"),
            ("opportunity", "is_urgent", "BOOLEAN DEFAULT 0"),
            ("user", "mobile", "VARCHAR(20) DEFAULT ''"),
            ("user", "badges", "VARCHAR(200) DEFAULT ''"),
            ("user", "hours_logged", "INTEGER DEFAULT 0"),
        ]

        for table, col, col_type in alterations:
            try:
                db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                db.session.commit()
                print(f"✅ Added {col} to {table}.")
            except Exception:
                # Column likely already exists
                db.session.rollback()
                pass

        print("✨ Schema Migration Complete!")

    # 3. Prompt for seeding if credentials aren't working
    print("\n📦 Would you like to re-seed the database to ensure all demo credentials (password123) work?")
    choice = input("Run seed now? (y/n): ")
    if choice.lower() == 'y':
        print("🌱 Seeding database...")
        try:
            # Running both seed scripts
            subprocess.run(["python", "seed.py"], check=True)
            subprocess.run(["python", "seed_users.py"], check=True)
            print("✅ Seeding complete! Credentials (password123) are now active.")
        except Exception as e:
            print(f"❌ Error seeding: {e}")

if __name__ == "__main__":
    migrate()
