from meowurl import app, db
from meowurl.dbmodels import InviteCode


# Since flask_migrate is used, initdb is not really useful
@app.cli.command('initdb')
def initdb():
    db.create_all()


@app.cli.command('dropdb')
def dropdb():
    db.drop_all()


# Generate public invite codes
@app.cli.command('gencode')
def gencode():
    code = InviteCode.generate_code(1)[0]
    db.session.add(code)
    db.session.commit()
    print(code)
