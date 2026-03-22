from flask import Flask
from model import db
from flask import render_template, redirect, url_for, session, request, flash
from model import User, CompanyProfile, StudentProfile, PlacementDrive, Application

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ppa.db'
app.config['SECRET_KEY'] = 'secret_1'

db.init_app(app)

#init
with app.app_context():
    db.create_all()
    admin_exists = User.query.filter_by(role='admin').first()
    if not admin_exists:
        admin = User(name="Admin", email="admin@gmail.com", password="admin1", role="admin")
        db.session.add(admin)
        db.session.commit()

#basic route
@app.route('/')
def index():
    return render_template('index.html')

#authenticate
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

@app.route('/logout') #logout
def logout():
    session.clear()
    return redirect(url_for('login'))

#register- student registration
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

#register- company registration
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

#dashboard (common)
@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect(url_for('login'))

    if session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif session['role'] == 'company':
        return "Company Dashboard"
    else:
        return "Student Dashboard"

#admin dashboard
@app.route('/admin')
def admin_dashboard():

    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    #stats
    companies = CompanyProfile.query.all()
    drives = PlacementDrive.query.all()
    students = StudentProfile.query.all()
    applications = Application.query.all()
    
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    return render_template('admin_dashboard.html', 
                            companies=companies, 
                            drives=drives, 
                            students=students, 
                            applications=applications,
                            total_students=total_students,
                            total_companies=total_companies,
                            total_drives=total_drives,
                            total_applications=total_applications)

#approve company
@app.route('/approve_company/<int:id>')
def approve_company(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    company = CompanyProfile.query.get_or_404(id)
    company.is_approved = True
    db.session.commit()

    return redirect(url_for('admin_dashboard'))

#reject company
@app.route('/reject_company/<int:id>')
def reject_company(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    company = CompanyProfile.query.get_or_404(id)
    company.is_approved = False
    db.session.commit()

    return redirect(url_for('admin_dashboard'))

#approve drive
@app.route('/approve_drive/<int:id>')
def approve_drive(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    drive = PlacementDrive.query.get_or_404(id)
    drive.status = "approved"
    db.session.commit()

    return redirect(url_for('admin_dashboard'))

#reject drive
@app.route('/reject_drive/<int:id>')
def reject_drive(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    drive = PlacementDrive.query.get_or_404(id)
    drive.status = "rejected"
    db.session.commit()

    return redirect(url_for('admin_dashboard'))

#search------
#search student
@app.route('/search_students')
def search_students():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    query = request.args.get('q', '')

    students = StudentProfile.query.join(User).filter(
        (User.name.contains(query)) |
        (StudentProfile.phone.contains(query)) |
        (User.id == query if query.isdigit() else False)
    ).all()

    return render_template('admin_dashboard.html', students=students, 
        companies=CompanyProfile.query.all(),
        drives=PlacementDrive.query.all(),
        applications=Application.query.all(), 
        total_students=StudentProfile.query.count(),
        total_companies=CompanyProfile.query.count(),
        total_drives=PlacementDrive.query.count(),
        total_applications=Application.query.count())

#search company
@app.route('/search_companies')
def search_companies():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    query = request.args.get('q', '')

    companies = CompanyProfile.query.filter(
        CompanyProfile.company_name.contains(query)
    ).all()

    return render_template('admin_dashboard.html',
        students=StudentProfile.query.all(),
        companies=companies,
        drives=PlacementDrive.query.all(),
        applications=Application.query.all(),
        total_students=StudentProfile.query.count(),
        total_companies=CompanyProfile.query.count(),
        total_drives=PlacementDrive.query.count(),
        total_applications=Application.query.count())

#deactivate user-------
@app.route('/deactivate_user/<int:id>')
def deactivate_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    user = User.query.get_or_404(id)
    user.is_active = False
    db.session.commit()

    return redirect(url_for('admin_dashboard'))

#activate user
@app.route('/activate_user/<int:id>')
def activate_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    user = User.query.get_or_404(id)
    user.is_active = True
    db.session.commit()

    return redirect(url_for('admin_dashboard'))

#delete
@app.route('/delete_student/<int:id>')
def delete_student(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    student = StudentProfile.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/delete_company/<int:id>')
def delete_company(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    company = CompanyProfile.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/delete_drive/<int:id>')
def delete_drive(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    drive = PlacementDrive.query.get_or_404(id)
    db.session.delete(drive)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/delete_application/<int:id>')
def delete_application(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    app_obj = Application.query.get_or_404(id)
    db.session.delete(app_obj)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

#to run
if __name__ == '__main__':
    app.run(debug=True)