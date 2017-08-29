from meowurl import app, db
from meowurl.dbmodels import InviteCode

@app.cli.command('initdb')
def initdb():
    db.create_all()


@app.cli.command('dropdb')
def dropdb():
    db.drop_all()

@app.cli.command('gencode')
def gencode():
    code = InviteCode.generate_code(1)[0]
    db.session.add(code)
    db.session.commit()
    print(code)
