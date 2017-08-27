from meowurl import app

from flask import jsonify, request, g
from meowurl.dbmodels import Paste
from meowurl.extra import conv_id_str


@app.route('/api')
def api_index():
    return jsonify({
        'success': False,
        'error': 'Please supply a method',
    }), 400, {'Content-Type': 'application/json'}


@app.route('/api/recent')
def api_recent_pastes():
    try:
        limit = int(request.args.get('limit', 12))
        offset = int(request.args.get('offset', 0))
    except:
        return jsonify({'success': False,
                        'error': 'Invalid Parameter'
                        }), 400, {'Content-Type': 'application/json'}
    return jsonify({'success': True,
                    'result': [p.as_dict() for p in Paste.get_all(limit, offset)]
                    }), {'Content-Type': 'application/json'}


@app.route('/api/newUrl', methods=['POST'])
def new_url():
    # Assign content and password from form
    content = request.form.get('content')
    password = request.form.get('password')
    paste = None
    result = {}

    # If no content
    if not content:
        result['success'] = False
        result['reason'] = 'No Content'
    else:
        # Add a new paste
        try:
            paste = g.user.add_paste(content, password)
        except AssertionError as e:
            result['success'] = False
            result['reason'] = str(e)
        else:
            result['success'] = True
            result['paste'] = paste.as_dict()
            result['html_url'] = request.url_root + conv_id_str(paste.id)
    return jsonify(result), {'Content-Type': 'application/json'}
