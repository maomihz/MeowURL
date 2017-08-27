from flask import render_template, request, redirect, g, abort, url_for

import codecs
from uuid import uuid4
import contextlib

from meowurl import app, memcache, cache, db
from meowurl.extra import conv_id_str
from meowurl.dbmodels import Paste, User


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
    return response


@app.errorhandler(404)
def page_not_found(error):
    ''' Gives a good 404 page '''
    return render_template('error.html',
                           content='This page does not exist'), 404


@app.route('/')
def index():
    ''' Index page, just render the index.html '''
    return render_template(
        'index.html',
        recent_pastes=Paste.get_all(app.config['INDEX_PASTE_NUMBER'])
    )


@app.route('/login.do', methods=['GET', 'POST'])
def login():
    ''' Login page, if GET then just render template '''
    if request.method == 'GET':
        return render_template('login.html')

    # get and check user name
    username = request.form.get('username')
    if not username:
        memcache.flash('Please input user name')
        return redirect(url_for('login'))

    # Look up the user name in database
    user = User.get_user(username)
    if not user:
        memcache.flash('User does not exist')
        return redirect(url_for('login'))

    # get and check password
    password = request.form.get('password')
    if not password:
        memcache.flash('Please input password')
        return redirect(url_for('login'))

    # All tests passed
    if not user.check_password(password):
        memcache.flash('Incorrect password')
        return redirect(url_for('login'))

    # Set login and redirect to index page
    memcache.set_login(username.lower())
    return redirect(url_for('index'))


@app.route('/register.do', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html',
                               temp_account_info=memcache.get('temp'))

    # Get and check the user name
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    repeat_password = request.form.get('repeat_password')
    invite_code = request.form.get('invite_code')

    memcache.set('temp', {
        'username': username,
        'email': email,
        'invite_code': invite_code
    })

    if not username:
        memcache.flash('Please input user name')
    elif not email:
        memcache.flash('Please enter email address')
    elif not password or not repeat_password:
        memcache.flash('Please input passwords')
    elif password != repeat_password:
        memcache.flash('Password does not match!')
    else:
        # All checks passed
        try:
            User.add_user(username, email, password, invite_code)
        except AssertionError as e:
            memcache.flash(str(e))
            return redirect(url_for('register'))
        memcache.set_login(username)
        memcache.delete('temp')
        return redirect(url_for('index'))

    # Some tests not pass
    return redirect(url_for('register'))


@app.route('/logout.do')
def logout():
    memcache.set_logout()
    return redirect(url_for('index'))


@app.route('/account.do')
def account():
    return g.user.username


@app.route('/u/<username>')
def view_user(username):
    user = User.query.get(username.lower())
    if not user:
        return render_template('error.html', content='No such user'), 404
    else:
        recent_pastes = user.pastes.order_by(-Paste.id).all()
        return render_template('user_pastes.html', user=user, recent_pastes=recent_pastes)

@app.route('/settings.do', methods=['GET', 'POST'])
def user_settings():
    if not g.user:
        return redirect('/')

    if request.method == 'POST':
        try:
            gencode = int(request.form.get('gen'))
        except:
            pass
        else:
            g.user.generate_code(gencode)
        return redirect(request.base_url)
    else:
        return render_template('user_settings.html')


@app.route('/short.do', methods=['POST'])
def shorten():
    # Assign content and password from form
    content = request.form.get('content')
    password = request.form.get('password')
    paste = None

    # If no content
    if not content:
        error = 'No Content!'
    else:
        # Add a new paste
        try:
            paste = g.user.add_paste(content, password)
        except AssertionError as e:
            error = str(e)
        else:
            return render_template('submit.html', paste=paste)
    return render_template('error.html', content=error)


@app.route('/edit.do/<id>', methods=['GET', 'POST'])
def edit(id):
    # Try convert
    paste = Paste.get_paste(conv_id_str(id))
    # If the paste does not exist
    if not paste:
        abort(404)
    if not get_owned(paste.id):
        return render_template('error.html', content='You do not own the paste!')
    if request.method == 'GET':
        return render_template('edit.html', paste=paste)

    # Else POST
    elif request.method == 'POST':
        content = request.form.get('content')
        password = request.form.get('password')
        rmpass = request.form.get('rmpass')

        # If no content
        if not content:
            error = 'No Content!'
        else:
            try:
                paste.content = content
                if rmpass:
                    paste.password = None
                elif password:
                    paste.password = password
                db.session.commit()
            except AssertionError as e:
                error = str(e)
            else:
                return redirect(url_for('view_paste', id=id))
        return render_template('error.html', error)

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
        return render_template('all.html', pastes = recent_pastes)

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
            if paste.is_url:
                return redirect(content)
            format = 'plain'
        elif format in ['plain', 'code']:
            format = 'plain'
        elif format in ['raw']:
            return (content, {'Content-Type': 'text/plain; charset=utf-8'})
        else:
            return redirect(request.url_root + id)
    return render_template('view_message.html', paste=paste, format=format)
