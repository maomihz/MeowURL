from meowurl import app

from flask import jsonify, request, g
from meowurl.dbmodels import Paste
from meowurl.extra import conv_id_str

import meowurl.captcha as captcha
import meowurl.traffic as traffic

import json

# success response
def rsuc(dat, *other):
    return (
        jsonify({ "suc": 1, "res": dat }), *other,
        { 'Content-Type': 'application/json' }
    )

# failed response
def rerr(dat, *other):
    return (
        jsonify({ "suc": 0, "res": dat }), *other,
        { 'Content-Type': 'application/json' },
    )

# need captcha
def rcap(*other):
    return (
        jsonify({ "suc": 0, "cap": captcha.reg() }), *other,
        { 'Content-Type': 'application/json' },
    )

@app.route('/api')
def api_index():
    return rerr('Please supply a method', 400)


@app.route('/api/recent')
def api_recent_pastes():
    try:
        limit = int(request.args.get('limit', 12))
        offset = int(request.args.get('offset', 0))
    except:
        return rerr('Invalid Parameter', 400)

    return rsuc([ p.as_dict() for p in Paste.get_all(limit, offset) ])

def new_url(need_captcha):
    capans = request.form.get('capans')

    # raise Exception(str(capans));

    if (not capans or not captcha.verify(**json.loads(capans))) and need_captcha:
        return rcap()

    # Assign content and password from form
    content = request.form.get('content')
    password = request.form.get('password')
    format = request.form.get('format')

    paste = None
    result = {}

    # If no content
    if not content:
        return rerr('No content')
    else:
        # Add a new paste
        try:
            paste = g.user.add_paste(content, password, format=format)
        except AssertionError as e:
            return rerr(str(e))
        else:
            return rsuc({
                'paste': paste.as_dict(),
                'html_url': request.url_root + conv_id_str(paste.id)
            })

# limit: 7 times in 3 minutes before trigerring the captcha
app.route('/api/newPaste', methods=['POST'])(traffic.limit(3 * 60, 7, new_url))
