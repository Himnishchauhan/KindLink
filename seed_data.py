from app import app, db, User
from werkzeug.security import generate_password_hash

def seed():
    with app.app_context():
        # High-security hashed password for all (can be changed later)
        default_pwd = generate_password_hash('password123')

        # 10 Diverse Volunteers
        volunteers = [
            ("Arjun Mehta", "arjun.m@example.com", "+91 98765 43210", "UI/UX, Figma, Product Design", "Design Thinking", "Weekends", "Mumbai, Maharashtra"),
            ("Sara Khan", "sara.k@example.com", "+91 98765 43211", "Data Analysis, Python, SQL", "Education, Analytics", "Flexible", "Delhi, NCR"),
            ("Vikram Singh", "vikram.s@example.com", "+91 98765 43212", "Content Writing, SEO, Blogs", "Journalism", "Part-time", "Chandigarh, Punjab"),
            ("Priya Nair", "priya.n@example.com", "+91 98765 43213", "Social Media, Marketing, Ads", "Public Awareness", "Evenings", "Bangalore, Karnataka"),
            ("Rohan Gupta", "rohan.g@example.com", "+91 98765 43214", "Web Dev, React, Node.js", "Open Source", "Full-time", "Pune, Maharashtra"),
            ("Ananya Das", "ananya.d@example.com", "+91 98765 43215", "Graphic Design, Branding", "Art, Culture", "Project-based", "Kolkata, West Bengal"),
            ("Karthik Raja", "karthik.r@example.com", "+91 98765 43216", "Event Management, Logistics", "Disaster Relief", "On-call", "Chennai, Tamil Nadu"),
            ("Meera Joshi", "meera.j@example.com", "+91 98765 43217", "Public Relations, Networking", "Community Building", "Weekdays", "Ahmedabad, Gujarat"),
            ("Rahul Verma", "rahul.v@example.com", "+91 98765 43218", "Legal Advocacy, Research", "Human Rights", "Evenings", "Lucknow, Uttar Pradesh"),
            ("Ishita Roy", "ishita.r@example.com", "+91 98765 43219", "Psychology, Counseling", "Mental Health", "Flexible", "Hyderabad, Telangana")
        ]

        # 10 Impact-Driven NGOs
        ngos = [
            ("Green Earth Foundation", "green.earth@example.org", "+91 90000 11111", "Preserving biodiversity through community reforestation projects.", "Mumbai, MH"),
            ("Education for All", "edu.forall@example.org", "+91 90000 11112", "Bridging the digital divide for underprivileged children in rural areas.", "Delhi, NCR"),
            ("Clean Water India", "clean.water@example.org", "+91 90000 11113", "Implementing sustainable water filtration systems in drought-prone regions.", "Jaipur, RJ"),
            ("Tech Empower", "tech.empower@example.org", "+91 90000 11114", "Providing coding workshops and equipment to aspiring youth in small towns.", "Bangalore, KA"),
            ("Healthy Hearts", "healthy.hearts@example.org", "+91 90000 11115", "Offering affordable healthcare and nutritional support to urban slums.", "Hyderabad, TG"),
            ("Wildlife Guardians", "wildlife.g@example.org", "+91 90000 11116", "Protecting endangered species through technology and anti-poaching patrols.", "Guwahati, AS"),
            ("Art for Change", "art.change@example.org", "+91 90000 11117", "Using creative expression to drive social awareness and mental wellness.", "Kolkata, WB"),
            ("Disaster Ready", "disaster.r@example.org", "+91 90000 11118", "Training local communities in rapid response and emergency first aid.", "Chennai, TN"),
            ("Women Rise", "women.rise@example.org", "+91 90000 11119", "Empowering women through vocational training and micro-entrepreneurship.", "Ahmedabad, GJ"),
            ("Peace Builders", "peace.b@example.org", "+91 90000 11120", "Promoting social harmony through cross-cultural education and dialogue.", "Srinagar, JK")
        ]

        # Invalidate and add Volunteers
        for name, email, mobile, skills, interests, availability, location in volunteers:
            if not User.query.filter_by(email=email).first():
                vol = User(name=name, email=email, password=default_pwd, role='volunteer', 
                           mobile=mobile, skills=skills, interests=interests, 
                           availability=availability, location=location)
                db.session.add(vol)

        # Invalidate and add NGOs
        for name, email, mobile, mission, location in ngos:
            if not User.query.filter_by(email=email).first():
                ngo = User(name=name, email=email, password=default_pwd, role='ngo', 
                           mobile=mobile, mission=mission, location=location)
                db.session.add(ngo)

        db.session.commit()
        print("Successfully seeded 20 new records (10 Volunteers, 10 NGOs)!")

if __name__ == "__main__":
    seed()
