from flask import Flask, render_template
from model import db, User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route("/")
def home():
    return render_template("login.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(
                name="Admin",
                email="admin@portal.com",
                password="admin123",
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
