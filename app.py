from flask import Flask
from model import db
from flask import render_template, redirect, url_for, session, request, flash
from model import User, CompanyProfile, StudentProfile

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ppa.db'
app.config['SECRET_KEY'] = 'secret_1'

db.init_app(app)

with app.app_context():
    db.create_all()
    admin_exists = User.query.filter_by(role='admin').first()
    if not admin_exists:
        admin = User(name="Admin", email="admin@gmail.com", password="admin1", role="admin")
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student/register', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password'],
            role='student'
        )
        db.session.add(user)
        db.session.commit()

        student_profile = StudentProfile(user_id=user.id, phone=request.form['phone'])
        db.session.add(student_profile)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('stud_register.html')

@app.route('/company/register', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password'],
            role='company'
        )
        db.session.add(user)
        db.session.commit()

        company_profile = CompanyProfile(
            user_id=user.id,
            company_name=request.form['company_name']
        )
        db.session.add(company_profile)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('company_register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('password')
        
        user = User.query.filter_by(email=email, password=pwd).first()
        
        if not user:
            flash("Invalid credentials.")
            return redirect(url_for('login'))
        
        if not user.is_active:
            flash("Account deactivated by Admin.")
            return redirect(url_for('login'))

        if user.role == 'company':
            if not user.company_profile.is_approved:
                flash("Company pending admin approval.")
                return redirect(url_for('login'))

        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('dashboard'))
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect(url_for('login'))

    if session['role'] == 'admin':
        return "Admin Dashboard"
    elif session['role'] == 'company':
        return "Company Dashboard"
    else:
        return "Student Dashboard"
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)