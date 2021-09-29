import os
import shutil
from app import db, app, User, Event, Role, Area

try:
    os.remove("app.db")
    shutil.rmtree("user_uploads")
    os.mkdir("user_uploads")

except:
    pass

db.create_all()


db.session.add(Role(name="ONG"))
db.session.add(Role(name="Instituição Púlbica"))
db.session.add(Role(name="Instituição Privada"))
db.session.add(Role(name="Utilizador particular"))

db.session.add(Area(name="Outras"))
db.session.add(Area(name="Saúde"))
db.session.add(Area(name="Educação"))

db.session.commit()
