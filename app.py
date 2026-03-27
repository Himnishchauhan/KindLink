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
    
    volunteer = db.relationship('User', foreign_keys=[volunteer_id], backref=db.backref('applications', lazy=True))
    opportunity = db.relationship('Opportunity', backref=db.backref('applications', lazy=True))

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
        location = request.form.get('location', 'Local')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))

        new_user = User(
            role=role, 
            name=name, 
            email=email, 
            password=generate_password_hash(password)
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
        
        matches.append({'opportunity': opp, 'score': score})
    
    # Sort by score desc
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    return render_template('volunteer_dashboard.html', user=user, matches=matches[:5])

@app.route('/ngo')
def ngo_dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'ngo': return redirect(url_for('index'))
    
    opps = Opportunity.query.filter_by(ngo_id=user.id).all()
    opp_ids = [o.id for o in opps]
    applications = Application.query.filter(Application.opportunity_id.in_(opp_ids)).all() if opp_ids else []
    
    # Compute Match % for each application
    for app_rec in applications:
        u_skills = [s.strip().lower() for s in app_rec.skills.split(',')] if app_rec.skills else []
        o_skills = [s.strip().lower() for s in app_rec.opportunity.skills_required.split(',')] if app_rec.opportunity.skills_required else []
        app_rec.match_percent = len(set(u_skills).intersection(set(o_skills))) * 15 + 50
        
    return render_template('ngo_dashboard.html', user=user, opps=opps, applications=applications)

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
        
        opp = Opportunity(
            ngo_id=user.id,
            title=title,
            description=description,
            skills_required=skills_required,
            duration=duration,
            location=location
        )
        db.session.add(opp)
        db.session.commit()
        flash('Opportunity created!', 'success')
        return redirect(url_for('ngo_dashboard'))
        
    return render_template('new_opportunity.html')

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

@app.route('/log_hours', methods=['POST'])
def log_hours():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(session['user_id'])
    if user.role != 'volunteer': return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    hours = int(data.get('hours', 0))
    user.hours_logged += hours
    
    # Gamification
    badges = user.badges.split(',') if user.badges else []
    if user.hours_logged >= 50 and '50 Hours Master' not in badges:
        badges.append('50 Hours Master')
    if user.hours_logged >= 100 and '100 Hours Legend' not in badges:
        badges.append('100 Hours Legend')
    
    user.badges = ','.join([b for b in badges if b])
    db.session.commit()
    return jsonify({'success': True, 'hours': user.hours_logged, 'badges': user.badges.split(', ' if user.badges else [])})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
