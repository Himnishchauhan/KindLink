from app import app, db, User, ImpactStory

def seed_impact():
    with app.app_context():
        # Find the NGO
        target_name = "Global Education Outreach Impact Center"
        ngo = User.query.filter(User.name.like(f"%{target_name}%")).first()
        
        if not ngo:
            # Maybe it is just Global Education Outreach
            ngo = User.query.filter(User.name.like("%Global Education Outreach%")).first()
            if not ngo:
                # Last try: search for "Education" and pick the first
                ngo = User.query.filter(User.name.like("%Education%")).first()
        
        if not ngo:
            print("NGO not found. Please ensure the organization is registered.")
            return

        print(f"Adding stories for NGO: {ngo.name} (ID: {ngo.id})")

        stories = [
            ("Digital Literacy Milestone", "Successfully trained 150 local students in core computing skills and digital safety.", "https://images.unsplash.com/photo-1509062522246-3755977927d7?q=80&w=2104&auto=format&fit=crop"),
            ("Rural Scholarship Success", "Two of our top scholarship students have been admitted to national universities with full funding.", "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?q=80&w=2070&auto=format&fit=crop"),
            ("New Community Library Opened", "Our 12th community library is officially open, providing 2000+ books to local youth.", "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?q=80&w=2070&auto=format&fit=crop"),
            ("Women In STEM Workshop", "Concluded a 4-week coding bootcamp specifically for young women interested in engineering.", "https://images.unsplash.com/photo-1573164060897-39031ca39c38?q=80&w=2069&auto=format&fit=crop"),
            ("Primary Literacy Boost", "A record 85% of our primary students reached advanced reading levels this semester.", "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=2022&auto=format&fit=crop"),
            ("Teacher Training Program", "Completed intensive pedagogical training for 50 local educators in modern STEM teaching methods.", "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=2070&auto=format&fit=crop"),
            ("Precision Tutoring Impact", "Our personalized tutoring pilot showed a 40% improvement in student math scores.", "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?q=80&w=2070&auto=format&fit=crop"),
            ("Mobile Science Lab Launch", "Our mobile science lab is now visiting 20 remote schools every month, reaching 5000 students.", "https://images.unsplash.com/photo-1532094349884-543bc11b234d?q=80&w=2070&auto=format&fit=crop"),
            ("Community Learning Center Renewal", "Renovated all five of our main learning centers with modern equipment and solar power.", "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?q=80&w=2073&auto=format&fit=crop"),
            ("Global Exchange Success", "Facilitated our first virtual classroom exchange between our students and a school in London.", "https://images.unsplash.com/photo-1588196749597-9ff075ee6b5b?q=80&w=1974&auto=format&fit=crop")
        ]

        # Add stories
        for title, desc, img in stories:
            new_story = ImpactStory(ngo_id=ngo.id, title=title, description=desc, image_url=img)
            db.session.add(new_story)

        db.session.commit()
        print(f"Successfully added 10 impact stories to {ngo.name}!")

if __name__ == "__main__":
    seed_impact()
