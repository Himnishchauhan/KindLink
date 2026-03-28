from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Add order_id column
            db.session.execute(text("ALTER TABLE donation ADD COLUMN order_id VARCHAR(255)"))
            print("Successfully added order_id column.")
        except Exception as e:
            print(f"order_id column already exists or error: {e}")

        try:
            # Add razorpay_payment_id column 
            db.session.execute(text("ALTER TABLE donation ADD COLUMN razorpay_payment_id VARCHAR(255)"))
            print("Successfully added razorpay_payment_id column.")
        except Exception as e:
            print(f"razorpay_payment_id column already exists or error: {e}")
            
        try:
            # Add currency column if missing
            db.session.execute(text("ALTER TABLE donation ADD COLUMN currency VARCHAR(10) DEFAULT 'INR'"))
            print("Successfully added currency column.")
        except Exception as e:
            print(f"currency column already exists or error: {e}")

        db.session.commit()
        print("Migration complete!")

if __name__ == "__main__":
    migrate()
