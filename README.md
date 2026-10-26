# Placement Portal Application
## Web application designed for institutions to manage placements with role-based login and dashboards. It provides an easy way to select, reject and shortlist students for companies. It also gives clear information to students about available placement drives, companies and status of their application. Admin can supervise the process and also select or reject companies and students when required.

## •	Tech Stack: 
### Python, Flask, SQLite, Flask-Login, Bootstrap, Chart.js, Werkzeug
* Overview: Architected a role-based web application with dedicated dashboards for Admins, Companies, and Students to streamline campus recruitment and drive management.
* Key Technical Highlights:
* o	Implemented Role-Based Access Control (RBAC) using Flask-Login and session authorization to secure approval pipelines and enforce company blacklisting logic.
* o	Enforced SQLAlchemy unique constraints and rigorous backend validation to block duplicate drive applications and preserve relational database integrity.
* o	Engineered secure file upload handling via Werkzeug (secure_filename) and integrated dynamic Chart.js analytics for administrative placement statistics.
---
## Project Outputs
* Main dashboard with Role Based Access for Student, Admin and Companies
<img width="945" height="480" alt="image" src="https://github.com/user-attachments/assets/01e4ae03-9a42-4b43-9839-36e44e86502a" />

* Admin Dashboard with admin metrics view powered by Chart.js
<img width="945" height="457" alt="image" src="https://github.com/user-attachments/assets/3e46d86e-44ba-4e25-a8f5-df4f7d634a3e" />

* Placement Drives with status of candidate approval
<img width="945" height="463" alt="image" src="https://github.com/user-attachments/assets/a7732b77-f191-4d04-9b97-d1083624fcb1" />

* Status of student applications with ready to view Resume and Updates
<img width="945" height="454" alt="image" src="https://github.com/user-attachments/assets/7d909b87-baf8-44b4-ae1f-4a67a52c3c7f" />

## Issues encountered and solutions
## Milestone 0: GitHub Setup

### Issues: README was not displaying on github and didn't include all required files in .gitignore.
### Solution: Added files properly and learnt correct Git commands.

## Milestone: Database Models and Schema Setup

### Issues: Integrity errors and missing field errors came due to only some fields being marked non-nullable and confusion if name was referring to student name or company name.
### Solution: Designed a unified User model with role-based extensions. Uniformly made fields non-nullable and checked the naming.

## Milestone: Authentication and Role-Based Access

### Issues: Restricting access for different roles didn't work at first.
### Solution: Added session checks and used Flask-Login to implement role-based access control.

## Milestone: Admin Dashboard

### Issues: Global stats weren't being passed to the filtered routes. Missing data in templates and first the html page loaded without data.
### Solution: Put queries into a centralized get_admin_stats() helper function and used python dictionary,helper functions and fixed the data passing to make it work.

## Milestone: Company Dashboard

### Issues: Companies accessing features without approval and managing job posting. And if an Admin deactivated a company, their active drives were still visible to student.
### Solution: Added approval system (is_approved) which is default false and job status controls so that company can't login. Updated the deactivation route so that placement drives are inactive when the company is blacklisted.


## Milestone: Student Dashboard

### Issues: Resume upload handling was difficult because first the file was not getting uploaded and didn't check where the file was storing.
### Solution: Used secure file handling using werkzeug.utils.secure_filename and prefixed files with the student ID (res_{id}_{filename}) and also option to physically delete files from the server when a user removes their resume.

## Milestone: Job Application Tracking

### Issues: Students could submit multiple applications for same placement drive.
### Solution: Added a unique constraint in the Application part of database(between student_id and drive_id) and added backend validation checks.

## Optional Enhancements
## Milestone: API Integration

### Issues: Structuring APIs for handling responses.
### Solution: Creating endpoints which have consistent JSON responses.

## Milestone: Charts & Visualization

### Issues: Data not passing correctly and charts breaking with empty data. Charts stretched to 100% width. Pie charts defaulted to similar color schemes.
### Solution: Used |tojson and fixed chart styling. Wrapped the <canvas> in a max-width container with mx-auto. Used arrays of RGBA colors for pie charts.

## Milestone: Responsive UI

### Issues: CSS was conflicting with bootstrap and components were not aligning.
### Solution: Adjusted use of Bootstrap grid/flex and avoided overriding default styles by use of important.

