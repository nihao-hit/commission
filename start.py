from app import create_app,db
from app.models import Role
from app.fake import users,orders,goods

app = create_app()

@app.cli.command()
def deploy():
    db.create_all()
    Role.insert_roles()
    users()
    orders()
    goods()