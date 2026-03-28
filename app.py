import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flux'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False) # 'volunteer' or 'ngo'
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String(20), default='')
    
    # Common stats
    hours_logged = db.Column(db.Integer, default=0)
    badges = db.Column(db.String(200), default='') # comma separated
    location = db.Column(db.String(100), default='Local')

    # Volunteer specifics
    skills = db.Column(db.String(255), default='') # comma separated
    interests = db.Column(db.String(255), default='')
    availability = db.Column(db.String(100), default='')
    is_available_now = db.Column(db.Boolean, default=False)

    # NGO specifics
    mission = db.Column(db.Text, default='')

class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills_required = db.Column(db.String(255), default='')
    duration = db.Column(db.String(100), default='')
    location = db.Column(db.String(100), default='Local')
    is_urgent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ngo = db.relationship('User', backref=db.backref('opportunities', lazy=True))

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunity.id'), nullable=False)
    location = db.Column(db.String(100), default='')
    skills = db.Column(db.String(255), default='')
    interests = db.Column(db.String(255), default='')
    availability = db.Column(db.String(100), default='')
    is_available_now = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending')
    
    volunteer = db.relationship('User', foreign_keys=[volunteer_id], backref=db.backref('applications', lazy=True))
    opportunity = db.relationship('Opportunity', backref=db.backref('applications', lazy=True))

class ImpactStory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), default='') # Placeholder support
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ngo = db.relationship('User', backref=db.backref('impact_stories', lazy=True, order_by='ImpactStory.created_at.desc()'))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            if user.role == 'volunteer':
                return redirect(url_for('volunteer_dashboard'))
            else:
                return redirect(url_for('ngo_dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        mobile = request.form.get('mobile', '')
        location = request.form.get('location', 'Local')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))

        new_user = User(
            role=role, 
            name=name, 
            email=email, 
            password=generate_password_hash(password),
            mobile=mobile
        )
        
        if role == 'ngo':
            new_user.mission = request.form.get('mission', '')
            new_user.location = request.form.get('location', '')

        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Logged in successfully.', 'success')
            if user.role == 'volunteer':
                return redirect(url_for('volunteer_dashboard'))
            else:
                return redirect(url_for('ngo_dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html', email=email)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route('/volunteer')
def volunteer_dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'volunteer': return redirect(url_for('index'))
    
    # Matching algorithm: simple overlap based on skills or interests
    user_skills = [s.strip().lower() for s in user.skills.split(',')] if user.skills else []
    all_opps = Opportunity.query.all()
    
    matches = []
    for opp in all_opps:
        opp_skills = [s.strip().lower() for s in opp.skills_required.split(',')] if opp.skills_required else []
        overlap = set(user_skills).intersection(set(opp_skills))
        score = len(overlap)
        
        # Boost for urgent opportunities
        if opp.is_urgent:
            score += 2 # slight base boost for urgency
            if user.is_available_now:
                score += 5 # massive prioritized boost for available volunteers
        
        matches.append({'opportunity': opp, 'score': score})
    
    # Sort by score desc
    matches.sort(key=lambda x: x['score'], reverse=True)
    # Calculate Impact Dashboard variables
    user_apps = Application.query.filter_by(volunteer_id=user.id).all()
    total_apps = len(user_apps)
    completed_apps = len([a for a in user_apps if getattr(a, 'is_completed', False)])
    pending_apps = len([a for a in user_apps if getattr(a, 'status', 'pending') == 'pending'])
    
    milestones = [1, 2, 5, 10, 50, 100]
    next_badge = next((m for m in milestones if m > user.hours_logged), 100)
    prev_badge = next((m for m in reversed(milestones) if m <= user.hours_logged), 0)
    
    if user.hours_logged >= 100:
        progress_pct = 100
    else:
        progress_pct = int(((user.hours_logged - prev_badge) / (next_badge - prev_badge)) * 100) if next_badge > prev_badge else 100

    return render_template('volunteer_dashboard.html', user=user, matches=matches[:5], total_apps=total_apps, completed_apps=completed_apps, pending_apps=pending_apps, next_badge=next_badge, progress_pct=progress_pct)

@app.route('/impact/new', methods=['GET', 'POST'])
def add_impact_story():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'ngo': return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_url = request.form.get('image_url', '')
        
        story = ImpactStory(ngo_id=user.id, title=title, description=description, image_url=image_url)
        db.session.add(story)
        db.session.commit()
        flash('Impact story added!', 'success')
        return redirect(url_for('ngo_dashboard'))
        
    return render_template('add_impact_story.html')

@app.route('/impact/delete/<int:story_id>', methods=['POST'])
def delete_impact_story(story_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    story = ImpactStory.query.get_or_404(story_id)
    if story.ngo_id != user.id: return redirect(url_for('index'))
    
    db.session.delete(story)
    db.session.commit()
    flash('Story removed from showcase.', 'info')
    return redirect(url_for('ngo_dashboard'))

@app.route('/view_ngos')
def view_ngos():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'volunteer': return redirect(url_for('index'))
    
    ngos = User.query.filter_by(role='ngo').all()
    # Prepare NGO data with active opportunity count
    ngo_list = []
    for ngo in ngos:
        # Check for count of active (non-completed) opportunities
        active_opp_count = Opportunity.query.filter_by(ngo_id=ngo.id).count()
        ngo_list.append({
            'user': ngo,
            'active_opp_count': active_opp_count
        })
    
    return render_template('view_ngos.html', ngos=ngo_list)

@app.route('/view_volunteers')
def view_volunteers():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'ngo': return redirect(url_for('index'))
    
    volunteers = User.query.filter_by(role='volunteer').all()
    # Prepare volunteer data with missions count
    vol_list = []
    for vol in volunteers:
        # Check for count of completed applications
        missions_done = Application.query.filter_by(volunteer_id=vol.id, is_completed=True).count()
        vol_list.append({
            'user': vol,
            'missions_done': missions_done
        })
    
    return render_template('view_volunteers.html', volunteers=vol_list)

@app.route('/ngo/showcase/<int:ngo_id>')
def ngo_showcase(ngo_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    ngo = User.query.get_or_404(ngo_id)
    if ngo.role != 'ngo': return redirect(url_for('index'))
    
    stories = ImpactStory.query.filter_by(ngo_id=ngo_id).order_by(ImpactStory.created_at.desc()).all()
    return render_template('ngo_showcase.html', ngo=ngo, stories=stories)

@app.route('/ngo')
def ngo_dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'ngo': return redirect(url_for('index'))
    
    opps = Opportunity.query.filter_by(ngo_id=user.id).all()
    opp_ids = [o.id for o in opps]
    applications = Application.query.filter(Application.opportunity_id.in_(opp_ids)).all() if opp_ids else []
    
    unique_volunteer_ids = {app_rec.volunteer_id for app_rec in applications}
    total_reach = len(unique_volunteer_ids)
    
    completed_missions = len([a for a in applications if getattr(a, 'is_completed', False)])
    accepted_apps = len([a for a in applications if getattr(a, 'status', 'pending') == 'accepted' or getattr(a, 'is_completed', False)])
    success_rate = int((completed_missions / accepted_apps * 100)) if accepted_apps > 0 else 0
    
    # Compute Match % for each application
    for app_rec in applications:
        u_skills = [s.strip().lower() for s in app_rec.skills.split(',')] if app_rec.skills else []
        o_skills = [s.strip().lower() for s in app_rec.opportunity.skills_required.split(',')] if app_rec.opportunity.skills_required else []
        app_rec.match_percent = len(set(u_skills).intersection(set(o_skills))) * 15 + 50
        
    # Prioritize available volunteers (especially for urgent opps)
    applications.sort(key=lambda a: (a.is_available_now and a.opportunity.is_urgent, a.is_available_now, a.match_percent), reverse=True)
        
    # Calculate trending skill (most requested globally)
    all_opps_platform = Opportunity.query.all()
    skill_counts = {}
    for o in all_opps_platform:
        if o.skills_required:
            skills = [s.strip().title() for s in o.skills_required.split(',') if s.strip()]
            for s in skills:
                skill_counts[s] = skill_counts.get(s, 0) + 1
    trending_skill = max(skill_counts, key=skill_counts.get) if skill_counts else "None yet"
    return render_template('ngo_dashboard.html', user=user, opps=opps, applications=applications, trending_skill=trending_skill, total_reach=total_reach, completed_missions=completed_missions, success_rate=success_rate)

@app.route('/opportunity/new', methods=['GET', 'POST'])
def new_opportunity():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'ngo': return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        skills_required = request.form.get('skills_required')
        duration = request.form.get('duration')
        location = request.form.get('location')
        is_urgent = True if request.form.get('is_urgent') == 'on' else False
        
        opp = Opportunity(
            ngo_id=user.id,
            title=title,
            description=description,
            skills_required=skills_required,
            duration=duration,
            location=location,
            is_urgent=is_urgent
        )
        db.session.add(opp)
        db.session.commit()
        flash('Opportunity created!', 'success')
        return redirect(url_for('ngo_dashboard'))
        
    return render_template('new_opportunity.html')

@app.route('/opportunity/edit/<int:opp_id>', methods=['GET', 'POST'])
def edit_opportunity(opp_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'ngo': return redirect(url_for('index'))
    
    opp = Opportunity.query.get_or_404(opp_id)
    if opp.ngo_id != user.id:
        flash('Unauthorized to edit this opportunity.', 'error')
        return redirect(url_for('ngo_dashboard'))
        
    if request.method == 'POST':
        opp.title = request.form.get('title')
        opp.description = request.form.get('description')
        opp.skills_required = request.form.get('skills_required')
        opp.duration = request.form.get('duration')
        opp.location = request.form.get('location')
        opp.is_urgent = True if request.form.get('is_urgent') == 'on' else False
        
        db.session.commit()
        flash('Opportunity updated successfully!', 'success')
        return redirect(url_for('ngo_dashboard'))
        
    return render_template('edit_opportunity.html', opp=opp)

@app.route('/apply', methods=['GET', 'POST'])
def make_application():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'volunteer': return redirect(url_for('index'))
    
    opps = Opportunity.query.all()
    preselected_opp = request.args.get('opp_id')
    
    if request.method == 'POST':
        opp_id = request.form.get('opportunity_id')
        location = request.form.get('location')
        skills = request.form.get('skills')
        interests = request.form.get('interests')
        availability = request.form.get('availability')
        is_available_now = True if request.form.get('is_available_now') == 'on' else False
        
        user.location = location
        user.skills = skills
        user.interests = interests
        user.availability = availability
        user.is_available_now = is_available_now
        
        app_record = Application(
            volunteer_id=user.id,
            opportunity_id=opp_id,
            location=location,
            skills=skills,
            interests=interests,
            availability=availability,
            is_available_now=is_available_now
        )
        db.session.add(app_record)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('volunteer_dashboard'))
        
    return render_template('make_application.html', user=user, opps=opps, preselected_opp=preselected_opp)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        mobile = request.form.get('mobile', '')
        location = request.form.get('location')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user.id:
            flash('Email already exists. Please use a different one.', 'error')
            return redirect(url_for('edit_profile'))

        user.name = name
        user.email = email
        user.mobile = mobile
        if location:
            user.location = location
            
        if password: # update only if provided
            user.password = generate_password_hash(password)
            
        if user.role == 'ngo':
            user.mission = request.form.get('mission', user.mission)
        else:
            user.skills = request.form.get('skills', user.skills)
            user.interests = request.form.get('interests', user.interests)
            user.availability = request.form.get('availability', user.availability)
            user.is_available_now = True if request.form.get('is_available_now') == 'on' else False
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        if user.role == 'volunteer':
            return redirect(url_for('volunteer_dashboard'))
        else:
            return redirect(url_for('ngo_dashboard'))
            
    return render_template('edit_profile.html', user=user)

@app.route('/application/accept/<int:app_id>', methods=['POST'])
def accept_application(app_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'ngo': return redirect(url_for('index'))
    
    app_record = Application.query.get_or_404(app_id)
    if app_record.opportunity.ngo_id != user.id:
        return redirect(url_for('ngo_dashboard'))
        
    app_record.status = 'accepted'
    db.session.commit()
    flash('Application accepted!', 'success')
    return redirect(url_for('ngo_dashboard'))

@app.route('/application/decline/<int:app_id>', methods=['POST'])
def decline_application(app_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'ngo': return redirect(url_for('index'))
    
    app_record = Application.query.get_or_404(app_id)
    if app_record.opportunity.ngo_id != user.id:
        return redirect(url_for('ngo_dashboard'))
        
    app_record.status = 'declined'
    db.session.commit()
    flash('Application declined.', 'info')
    return redirect(url_for('ngo_dashboard'))


@app.route('/complete_application/<int:app_id>', methods=['POST'])
def complete_application(app_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'ngo': return redirect(url_for('index'))
    
    app_record = Application.query.get_or_404(app_id)
    if app_record.opportunity.ngo_id != user.id:
        return redirect(url_for('ngo_dashboard'))
        
    if getattr(app_record, 'is_completed', False):
        flash('Already marked as completed', 'error')
        return redirect(url_for('ngo_dashboard'))
        
    if getattr(app_record, 'status', 'pending') != 'accepted':
        flash('Must accept the application first', 'error')
        return redirect(url_for('ngo_dashboard'))
        
    hours_awarded = int(request.form.get('hours', 0))
    app_record.is_completed = True
    app_record.volunteer.hours_logged += hours_awarded
    
    # Gamification
    badges = app_record.volunteer.badges.split(',') if app_record.volunteer.badges else []
    
    if app_record.volunteer.hours_logged >= 1 and "It's Just The beginning" not in badges:
        badges.append("It's Just The beginning")
    if app_record.volunteer.hours_logged >= 2 and 'Helping Hand' not in badges:
        badges.append('Helping Hand')
    if app_record.volunteer.hours_logged >= 5 and 'Rising Star' not in badges:
        badges.append('Rising Star')
    if app_record.volunteer.hours_logged >= 10 and 'Community Pillar' not in badges:
        badges.append('Community Pillar')
    if app_record.volunteer.hours_logged >= 50 and '50 Hours Master' not in badges:
        badges.append('50 Hours Master')
    if app_record.volunteer.hours_logged >= 100 and '100 Hours Legend' not in badges:
        badges.append('100 Hours Legend')
    
    app_record.volunteer.badges = ','.join([b for b in badges if b])
    db.session.commit()
    flash(f"Volunteer marked as completed. {hours_awarded} hours logged!", 'success')
    return redirect(url_for('ngo_dashboard'))

@app.route('/delete_opportunity/<int:opp_id>', methods=['POST'])
def delete_opportunity(opp_id):
    if 'user_id' not in session or session.get('role') != 'ngo':
        return redirect(url_for('login'))
        
    opp = Opportunity.query.get_or_404(opp_id)
    if opp.ngo_id != session['user_id']:
        flash('Unauthorized action', 'error')
        return redirect(url_for('ngo_dashboard'))
        
    # Delete all associated applications first
    Application.query.filter_by(opportunity_id=opp.id).delete()
    
    db.session.delete(opp)
    db.session.commit()
    flash('Opportunity deleted successfully.', 'success')
    return redirect(url_for('ngo_dashboard'))

@app.route('/withdraw_application/<int:app_id>', methods=['POST'])
def withdraw_application(app_id):
    if 'user_id' not in session or session.get('role') != 'volunteer':
        return redirect(url_for('login'))
        
    app_record = Application.query.get_or_404(app_id)
    if app_record.volunteer_id != session['user_id']:
        flash('Unauthorized action', 'error')
        return redirect(url_for('volunteer_dashboard'))
        
    db.session.delete(app_record)
    db.session.commit()
    flash('Application withdrawn successfully.', 'success')
    return redirect(url_for('volunteer_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
