import os
from app import db, app, User, Event, Role, Area

try:
    os.remove("app.db")

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

u = User(
    email="mail1@gmail.com",
    name="Alice AliceLastName",
    phone="960000001",
    nif="1234567",
    description="This is a test account",
    role_id=4,
)
u.set_password("1234")

db.session.add(u)

db.session.add(
    Event(
        name="Activity 1",
        description="This is the description of the first actitivy",
        user_id=1,
        area_id=1,
    )
)

db.session.add(
    Event(
        name="Activity 2",
        description="This is the description of the first actitivy",
        user_id=1,
        area_id=3,
    )
)

# users = [
#     u,
#     User(email="mail2@gmail.com", name="User2", phone="23456", nif="12345678"),
#     User(email="mail3@gmail.com", name="User3", phone="1234568", nif="12345321"),
#     User(email="mail4@gmail.com", name="User4 ONG", phone="2456543", nif="123454")

# ]

# events = [
#     Event(name="Another event", description="Another event's decription")
# ]

# for user in users:
#     db.session.add(user)

# for event in events:
#     db.session.add(event)

db.session.commit()


app.run(debug=True, host="0.0.0.0", port=8080)
