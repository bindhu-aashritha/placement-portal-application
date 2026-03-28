from flask import Flask
from model import db
from flask import render_template, redirect, url_for, session, request, flash
from model import User, CompanyProfile, StudentProfile, PlacementDrive, Application
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ppa.db'
app.config['SECRET_KEY'] = 'secret_1'

#handling student resumes uploads
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Creating directory if not there
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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
def student_register():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password'],
            role='student'
        )
        db.session.add(user)
        db.session.flush()
       
        student_profile = StudentProfile(user_id=user.id, phone=request.form['phone'])
        db.session.add(student_profile)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('stud_register.html')

#register- company registration
@app.route('/company/register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        user = User(
            name=request.form['company_name'],
            email=request.form['email'],
            password=request.form['password'],
            role='company'
        )
        db.session.add(user)
        db.session.flush()
       
        company_profile = CompanyProfile(
            user_id=user.id,
            company_name=request.form['company_name'],
            is_approved=True
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
        return redirect(url_for('company_dashboard'))
    elif session['role'] == 'student':
        return redirect(url_for('student_dashboard'))

#admin dashboard routes
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
    drive.status = "active"
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

#company dashboard routes
@app.route('/company/dashboard')
def company_dashboard():
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    drives = PlacementDrive.query.filter_by(company_id=company.id).all()

    applications = Application.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company.id
    ).all()

    return render_template('company_dashboard.html',
                           company=company,
                           drives=drives,
                           applications=applications)

@app.route('/company/post_job', methods=['GET', 'POST'])
def post_job():
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    if not company.is_approved:
        flash("Company not approved by admin.")
        return redirect(url_for('company_dashboard'))

    if request.method == 'POST':
        drive = PlacementDrive(
            company_id=company.id,
            job_title=request.form['job_title'],
            job_description=request.form['job_description'],
            eligibility=request.form['eligibility'],
            deadline=request.form['deadline'],
            status="pending"  
        )

        db.session.add(drive)
        db.session.commit()

        flash("Job posted successfully!")
        return redirect(url_for('company_dashboard'))

    return redirect(url_for('company_dashboard'))

@app.route('/company/update_job_status/<int:id>')
def update_job_status(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    drive = PlacementDrive.query.get_or_404(id)

    if drive.status == "active":
        drive.status = "closed"
    else:
        drive.status = "active"

    db.session.commit()
    return redirect(url_for('company_dashboard'))

@app.route('/company/update_application/<int:id>/<status>')
def update_application(id, status):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    application = Application.query.get_or_404(id)
    valid_status = ["Applied", "Shortlisted", "Interview", "Selected", "Rejected", "Placed"]

    if status in valid_status:
        application.status = status
        db.session.commit()

    return redirect(url_for('company_dashboard'))

#STUDENT
#student dashboard
@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    student = StudentProfile.query.filter_by(user_id=user_id).first()
    
    query = request.args.get('q', '')
    if query:
        # Search by job title, company, or skills
        drives = PlacementDrive.query.join(CompanyProfile).filter(
            PlacementDrive.status == 'active',
            (PlacementDrive.job_title.contains(query)) |
            (CompanyProfile.company_name.contains(query)) |
            (PlacementDrive.job_description.contains(query))
        ).all()
    else:
        drives = PlacementDrive.query.filter_by(status='active').all()

    #application history for this student
    history = Application.query.filter_by(student_id=student.id).all()

    return render_template('stud_dashboard.html', student=student, drives=drives, history=history)

#update student profile
@app.route('/student/update_profile', methods=['GET', 'POST'])
def update_profile():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    student = StudentProfile.query.filter_by(user_id=session['user_id']).first()

    if request.method == 'POST':
        student.phone = request.form.get('phone')
        student.education = request.form.get('education')
        student.skills = request.form.get('skills')
        
        #to upload resume
        file = request.files.get('resume')
        if file and file.filename != '':
            #create a unique filename using student id
            filename = secure_filename(f"res_{student.id}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            student.resume = filename
            
        db.session.commit()
        flash("Profile updated successfully")
        return redirect(url_for('student_dashboard'))

    return render_template('stud_profile.html', student=student)

#apply to job
@app.route('/apply/<int:drive_id>')
def apply_job(drive_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    
    student = StudentProfile.query.filter_by(user_id=session['user_id']).first()
    
    #check if applied already
    existing = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing:
        flash("You have already applied to this job.")
        return redirect(url_for('student_dashboard'))

    new_app = Application(student_id=student.id, drive_id=drive_id, status="Applied")
    db.session.add(new_app)
    db.session.commit()
    
    flash("Applied successfully")
    return redirect(url_for('student_dashboard'))

#to delete resume
@app.route('/student/delete_resume')
def delete_resume():
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    student = StudentProfile.query.filter_by(user_id=session['user_id']).first()

    if student and student.resume:
        #constructing full path to file
        file_path = os.path.join(app.root_path, 'static/resumes', student.resume)

        #deleting physical file from the folder
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 3. Clear the filename from the database
            student.resume = None
            db.session.commit()
            flash("Resume deleted successfully.")
        except Exception as e:
            db.session.rollback()
            flash("Error deleting file from storage.")
    else:
        flash("No resume found to delete.")

    return redirect(url_for('update_profile'))

#recommended enhancements
#api integration
#get all jobs
@app.route('/api/jobs', methods=['GET'])
def api_jobs():
    drives = PlacementDrive.query.filter_by(status='active').all()

    data = []
    for d in drives:
        data.append({
            "id": d.id,
            "company": d.company_profile.company_name,
            "title": d.job_title,
            "eligibility": d.eligibility,
            "deadline": d.deadline
        })

    return jsonify(data)

#get student applications
@app.route('/api/student/<int:id>/applications', methods=['GET'])
def api_student_apps(id):
    apps = Application.query.filter_by(student_id=id).all()

    return jsonify([
        {
            "job": a.drive.job_title,
            "company": a.drive.company_profile.company_name,
            "status": a.status
        } for a in apps
    ])

#post apply
@app.route('/api/apply', methods=['POST'])
def api_apply():
    data = request.json

    student_id = data.get('student_id')
    drive_id = data.get('drive_id')

    existing = Application.query.filter_by(student_id=student_id, drive_id=drive_id).first()
    if existing:
        return jsonify({"message": "Already applied"}), 400

    app_obj = Application(student_id=student_id, drive_id=drive_id)
    db.session.add(app_obj)
    db.session.commit()

    return jsonify({"message": "Application submitted"})

#put update application
@app.route('/api/application/<int:id>', methods=['PUT'])
def api_update_application(id):
    data = request.json
    app_obj = Application.query.get_or_404(id)
    app_obj.status = data.get('status')
    db.session.commit()

    return jsonify({"message": "Updated"})

#to run
if __name__ == '__main__':
    app.run(debug=True)