from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    email = EmailField(
        "Endereço de email",
        validators=[InputRequired()],
        render_kw={"placeholder": "Endereço de email"},
    )
    password = PasswordField(
        "Password", validators=[InputRequired()], render_kw={"placeholder": "Password"}
    )


class SignupForm(FlaskForm):
    email = EmailField(
        "Endereço de email",
        validators=[InputRequired()],
        render_kw={"placeholder": "Endereço de email"},
    )
    password = PasswordField(
        "Password", validators=[InputRequired()], render_kw={"placeholder": "Password"}
    )
    name = StringField(
        "Name", validators=[InputRequired()], render_kw={"placeholder": "Nome completo"}
    )
    nif = StringField(
        "NIF/NIPC", validators=[InputRequired()], render_kw={"placeholder": "NIF/NIPC"}
    )
    phone = StringField(
        "Contacto telefónico",
        validators=[InputRequired()],
        render_kw={"placeholder": "Contacto telefónico"},
    )
    description = TextAreaField(
        "Descrição (opcional)",
        render_kw={"placeholder": "Descrição - Preenchimento facultativo"},
    )


class CreateEventForm(FlaskForm):
    name = StringField(
        "Nome", validators=[InputRequired()], render_kw={"placeholder": "Nome"}
    )
    area = SelectField(
        "Área",
        choices=[("2", "Saúde"), ("3", "Educação"), ("1", "Outras")],
    )
    description = TextAreaField(
        "Descrição",
        validators=[InputRequired()],
        render_kw={
            "placeholder": "#TODO Escrever aqui o que é necessário escrever na descrição"
        },
    )
    photo = FileField("Imagem associada ao evento (opcional)", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'avif', 'heic'])],
                      render_kw={"accept": "image/*"})

    date = DateField(
        "Dia em que a atividade será realizada", validators=[InputRequired()]
    )

""" This is a placeholder form
events may require extra information
Here we are only asking for comments or special info from the user"""
class EventSignupForm(FlaskForm):
    message_to_organizer = TextAreaField("Mensagem para o organizador")


# Fixme later - add placeholder
# render_kw={"placeholder", "Indique se precisa de alguma acomodação espacial"})
