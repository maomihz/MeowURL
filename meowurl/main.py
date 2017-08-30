from flask import render_template, request, redirect, g, abort, url_for, jsonify

import codecs
from uuid import uuid4
import contextlib

from meowurl import app, memcache, db
from meowurl.extra import conv_id_str, request_wants_json
from meowurl.api import rsuc, rerr
from meowurl.dbmodels import Paste, User, InviteCode

from meowurl.forms import LoginForm, RegisterForm, UserSettingsForm
from meowurl.forms import PasteForm, EditPasteForm

db.create_all()


@app.template_global('get_authorized')
def get_authorized(id):
    ''' One of the template globals, check whether an item id is authorized by
    the current user. Authorized means the item is view only.
    '''
    return memcache.get_authorized(id)


@app.template_global('get_owned')
def get_owned(id):
    ''' One of the template globals, check whether an item id is owned by the
    current user. Owned means the item is both viewable and editable. '''
    paste = Paste.get_paste(id)
    with contextlib.suppress(AttributeError):
        return paste.owner is g.user
    return False


# Before request set up the session IDs
@app.before_request
def check_session():
    ''' Before request, assign a session id if there is no session id.
    Then determine the username and try to associate the user name with an
    actual name. '''
    g.session_id = request.cookies.get('session_id') or str(uuid4())
    login = memcache.get_login()
    # if the user is already logged in then retrieve the user object from database
    # Otherwise retrieve the anonymous user
    if login:
        g.user = User.get_user(login)
    else:
        g.user = User.get_user(g.session_id)

    # If user does not exist then create an anonymous user
    if not g.user:
        g.user = User.add_anonymous_user(g.session_id)


# After request reply the cookie
@app.after_request
def set_session(response):
    ''' After request, set the session ID as cookie '''
    response.set_cookie('session_id', g.session_id)
    print(response.data)
    return response


@app.errorhandler(404)
def page_not_found(error):
    ''' Gives a good 404 page '''
    return render_template('error.html',
                           content='This page does not exist'), 404


@app.route('/')
def index():
    ''' Index page, just render the index.html '''
    return render_template('index.html')


@app.route('/login.do', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        memcache.set_login(form.username.data)
        if request_wants_json():
            return rsuc()
        return redirect(url_for('index'))

    if request_wants_json():
        return rerr({
            error: [a for b in form.errors.values() for a in b]
        })
    memcache.flash_form_errors(form)
    return render_template('login.html', form=form)


@app.route('/register.do', methods=['GET', 'POST'])
def register():
    # User already logged in, do not show the page
    if not g.user.anonymous:
        return redirect(url_for('index'))

    form = RegisterForm()

    # Temporarily store user names
    memcache.set('temp', {
        'name': request.form.get('name', ''),
        'email': request.form.get('email', ''),
        'invite_code': request.form.get('invite_code', '')
    })

    if form.validate_on_submit():
        User.add_user(form.name.data,
                      form.email.data,
                      form.password.data,
                      form.invite_code.data)
        memcache.set_login(form.name.data.lower())
        memcache.delete('temp')
        return redirect(url_for('index'))

    memcache.flash_form_errors(form)
    return render_template('register.html',
                           temp_account_info=memcache.get('temp'),
                           invite_code=request.args.get('i'),
                           form=form)


@app.route('/logout.do')
def logout():
    memcache.set_logout()
    return rsuc()


@app.route('/settings.do', methods=['GET', 'POST'])
def user_settings():
    if g.user.anonymous:
        return redirect(url_for('index'))

    form = UserSettingsForm()
    if form.validate_on_submit():
        codes = g.user.generate_code(form.gencode.data)
        if request_wants_json():
            return rsuc({
                codes: [c.code for c in codes],
                left: g.user.invites_left})
        return redirect(request.base_url)

    if request_wants_json():
        return rerr({
            error: [a for b in form.errors.values() for a in b]
        })
    return render_template('user_settings.html', form=form)


@app.route('/short.do', methods=['POST'])
def shorten():
    form = PasteForm()
    if form.validate_on_submit():
        paste = g.user.add_paste(form.content.data, form.password.data)
        return rsuc({
            'html_url': request.url_root + conv_id_str(paste.id)
        })
    return rerr({
        'error': [a for b in form.errors.values() for a in b]
    })


@app.route('/edit.do/<id>', methods=['GET', 'POST'])
def edit(id):
    form = EditPasteForm()
    if form.validate_on_submit():
        if not get_owned(form.paste.id):
            return rerr({error: "You do not own the paste!"})
            form.paste.content = content
            form.paste.password = None if rmpass else password
            db.session.commit()
            return rsuc()
    return 'b'


@app.route('/u/<username>')
def view_user(username):
    user = User.query.get(username.lower())
    if not user:
        return render_template('error.html', content='No such user'), 404
    recent_pastes = user.pastes.order_by(-Paste.id).all()
    return render_template('user_pastes.html', user=user, recent_pastes=recent_pastes)


@app.route('/<id>', defaults={'format': 'redir'})
@app.route('/<id>/<format>')
def view_paste(id, format):
    paste = None
    try:
        paste_id = conv_id_str(id)
    except:
        abort(404)

    # Request 100 recent paste list
    if paste_id <= 0:
        recent_pastes = Paste.get_all(app.config['MORE_PASTE_NUMBER'])
        return render_template('all.html', pastes=recent_pastes)

    else:
        paste = Paste.get_paste(conv_id_str(id))
        # If paste not found
        if not paste:
            abort(404)

        # If a authorization request
        auth = request.args.get('auth')
        if auth:
            if paste.check_password(auth):
                memcache.add_authorized(paste.id)
            return redirect(request.base_url)
        content = codecs.decode(paste.content, 'utf-8')
        if paste.password and not get_authorized(paste.id):
            format = 'need auth'
        elif format in ['md', 'markdown']:
            format = 'markdown'
        elif format in ['redir']:
            if paste.format == 'url':
                return redirect(content)
            format = 'plain'
        elif format in ['plain', 'code']:
            format = 'plain'
        elif format in ['raw']:
            return (content, {'Content-Type': 'text/plain; charset=utf-8'})
        else:
            return redirect(request.url_root + id)
    return render_template('view_message.html', paste=paste, format=format)


@app.route('/invites.do')
def invites():
    invite_codes = InviteCode.query.filter(InviteCode.owner == None).all()
    return render_template('invites.html', invite_codes=invite_codes)
