from app import create_app,db
from app.models import Role,Town
from app.fake import users,orders,goods,reports

app = create_app()


@app.cli.command()
def deploy():
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    Town.insert_towns()
    users()
    orders()
    goods()
    reports()