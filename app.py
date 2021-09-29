from flask import Flask, render_template, url_for, request, flash, redirect, send_from_directory
from forms import LoginForm, SignupForm, CreateEventForm, EventSignupForm

from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.utils import secure_filename
import os

from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    LoginManager,
    login_user,
    logout_user,
    current_user,
    login_required,
)


app = Flask(__name__)

app.config["SECRET_KEY"] = "a714ecac84cddf5d2afc74f8cacff6ced02d0c3076f7d53a"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "user_uploads"

login = LoginManager(app)
db = SQLAlchemy(app)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def get_name(self):
        return self.name


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship("Role")
    nif = db.Column(db.String(9))
    name = db.Column(db.String(255))
    phone = db.Column(db.String(9))
    description = db.Column(db.Text(10000))
    password_hash = db.Column(db.String(128), nullable=False)
    # events = db.relationship('Event', backref='organizer', lazy='dynamic')

    def __repr__(self):
        return f"{self.id} {self.email}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password_hash):
        return check_password_hash(self.password_hash, password_hash)

    def get_role_name(self):
        return self.role.get_name()

    def is_admin(self):
        print("NotImplementWarning: User.is_admin is always returning True")
        return True


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

    # TODO Make many to many association


# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#many-to-many-relationships
# areas = db.Table(
#     "areas",
#     area_id=db.Column(db.Integer, db.ForeignKey("area.id"), primary_key=True),
#     event_id=db.Column(db.Integer, db.ForeignKey("event.id"), primary_key=True)
# )


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    # events = db.relationship(Event)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    area_id = db.Column(db.Integer, db.ForeignKey("area.id"))
    area = db.relationship("Area")

    name = db.Column(db.String(100))
    author = db.relationship("User")
    description = db.Column(db.Text(10000))
    date = db.Column(db.Date)

    def get_areas(self):
        # TODO make models support multiple areas
        return [self.area]

    def __repr__(self):
        return f"{self.id} {self.description}"

"""
When a user signs up for an event this class is instanced."""
class EventSignup(db.Model):
    user_id = db.Column(db.ForeignKey("user.id"), primary_key=True, nullable=False)
    user = db.relationship("User")

    event_id = db.Column(db.ForeignKey("event.id"), primary_key=True, nullable=False)
    event = db.relationship("Event")

    message_to_organizer = db.Column(db.Text(1000))

    # registration_time = db.Column(db.DateTime(default=...)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Email ou password errada!")
            flash("Tente novamente")

        else:
            login_user(user)
            return redirect(url_for("index"))

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


def common_password(pw):
    common_pw = (
        "123456",
        "123456789",
        "1234567890",
        "abc123",
        "000000",
        "password",
        "qwertyuop",
        "humanaethica",
        "humanalearn",
        "tecnico",
    )
    formatted_pw = pw.lower().strip()
    return any(x in formatted_pw or formatted_pw in x for x in common_pw)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm(request.form)
    pw = form.password.data

    if form.validate_on_submit():  # TODO replace all is_submitted by is_valid()
        if User.query.filter_by(email=form.email.data).first():
            flash("Já existe conta com esse email")
            return redirect(url_for("login"))

        # if len(pw) < 6:
        #     flash('Password tem de ter pelo menos 6 caracteres')
        #     return redirect(url_for('signup'))

        # if common_password(pw):
        #     flash('A password não é segura')
        #     return redirect(url_for('signup'))

        user = User(
            email=form.email.data,
            name=form.name.data,
            nif=form.nif.data,
            phone=form.phone.data,
            description=form.description.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Conta criada com sucesso.")
        return redirect(url_for("index"))
        # TODO fazer mais verificacoes e completar modelo

    return render_template("signup.html", form=form)


@app.route("/createEvent", methods=["GET", "POST"])
@login_required
# TODO refactor this function
# This is the worst code I've ever written in my life
# And I remember projecto de LP :(
def createEvent():
    form = CreateEventForm(request.form)
    if request.method == "POST":
        event = Event(
            user_id=current_user.id,
            name=form.name.data,
            description=form.description.data,
            area_id=form.area.data,
        )
        db.session.add(event)
        db.session.commit()
        # TODO Use flask-wtf built in file field
        # It doesn't work for some reason

        if request.files['photo'] and request.files['photo'].filename:  # If file exists
            photo = request.files['photo']
            # flash(os.path.join(app.instance_path, app.config["UPLOAD_FOLDER"], str(event.user_id)))
            # TODO fix this file path
            photo.save(os.path.join(os.getcwd(), "user_uploads", str(event.id)+".jpg",))

        else:
            flash("PHOTO NOT UPLOADED!!")

        """
        # f = form.photo.data
        # flash(str(request.files))
        # flash(event.id)
        # return redirect(url_for('index'))
        # flash(f)
        # if f:
        #
        #     filename = secure_filename(f)
        #     flash(filename)
        #     f.save(os.path.join(
        #         app.instance_path,
        #         app.config["UPLOAD_FOLDER"],
        #         filename
        #     ))
        #     flash(filename)
        #     flash(os.path.join(
        #         app.instance_path,
        #         app.config["UPLOAD_FOLDER"],
        #         filename
        #     ))
            # form.photo.save(os.path.join(app.instance_path, app.config["UPLOAD_FOLDER"], filename))

        """

        flash("Evento adicionado com sucesso")
        return redirect(url_for("listEvents"))

    return render_template("createEvent.html", form=form)


@app.route("/event/<int:eventID>")
@login_required
def viewEvent(eventID):

    event = Event.query.filter_by(id=eventID).first()
    author = event.author
    has_image = os.path.isfile(os.path.join(os.getcwd(), "user_uploads", str(eventID)+".jpg"))


    return render_template("viewEvent.html", event=event, user=author, has_image=has_image)

@app.route("/event-img/<int:eventID>.jpg")
@login_required
def getEventImg(eventID):
    # FIXME use correct file path
    if not os.path.isfile(os.path.join(os.getcwd(), "user_uploads", str(eventID)+".jpg")):
        return "This photo does not exist"  # FIXME What do I return here?

    return send_from_directory(os.path.join(os.getcwd(), "user_uploads"), str(eventID)+".jpg")

@app.route("/events")
@login_required
def listEvents():
    events = Event.query.all()
    return render_template("listEvents.html", events=events)


@app.route("/eventsByArea/<int:id>")
@login_required
def listEventsByArea(id):
    events = Event.query.filter_by(area_id=id).all()
    return render_template("listEvents.html", events=events)


@app.route("/profile/<int:id>")
@login_required
def showProfile(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        flash("Este utilizador não existe ou não está registado")
        return redirect(url_for("ongProfiles"))

    return render_template("profile.html", user=user)


@app.route("/organizations")
def ongProfiles():
    profiles = User.query.all()  # TODO make it filter by by colective persons
    return render_template("profiles.html", profiles=profiles)


@app.route("/editProfile", methods=["GET", "POST"])
@login_required
def editProfile():
    form = SignupForm()

    if form.is_submitted():  # can't be validate_on_submit() due to InputRequired()
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.nif = form.nif.data
        current_user.phone = form.phone.data
        current_user.description = form.description.data

        if form.password.data: # password not empty
            current_user.set_password(form.password.data)

        db.session.commit()

    elif request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.nif.data = current_user.nif
        form.phone.data = current_user.phone
        form.description.data = current_user.description

    return render_template("editProfile.html", form=form)


@app.route("/event-signup/<int:eventID>", methods=["GET", "POST"])
@login_required
def eventSignup(eventID):
    form = EventSignupForm()
    if form.validate_on_submit():
        # FIXME prevent XSS exploit on form.message_to_organizer.data
        event = EventSignup(user_id=current_user.id,
                    event_id=eventID,
                    message_to_organizer=form.message_to_organizer.data
                    )

        db.session.add(event)
        db.session.commit()

        flash("Encontra-se registado no evento")
        return redirect(url_for("viewEvent", eventID=eventID))

    return render_template("SignUpToEvent.html", form=form)


    return render_template("signupToEvent.html")


@app.route("/list-participants/<int:eventID>")
@login_required
def listParticipants(eventID):
    participants = EventSignup.query.filter_by(event_id=1).all()
    participants = EventSignup.query.all()
    flash(participants)
    flash(eventID)


    return render_template("listParticipants.html", event_signups=participants)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
