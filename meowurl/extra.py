import codecs
import re

from flask import request, jsonify

from meowurl import app

URL_REGEX = re.compile(
    '(https?:\/\/(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})')

@app.template_global('conv_id_str')
def conv_id_str(id):
    '''Convert numerical ID to string or back'''
    # Define the charset to use
    charset = app.config['URL_CHARSET']
    charset_len = len(charset)

    # String to internal ID
    if type(id) is str:
        return sum(
            charset.index(char) * (charset_len ** i)
            for i, char in enumerate(reversed(id))
        )

    # Internal ID to string
    elif type(id) is int:
        result = []
        while id > 0:
            result.append(charset[id % charset_len])
            id = id // charset_len
        return ''.join(reversed(result))


@app.template_filter('decode')
def decode(text):
    return codecs.decode(text, 'utf-8')


@app.template_global('get_flashed_messages')
def get_flashed_messages():
    from meowurl import memcache
    return memcache.get_flashed_messages()

# http://flask.pocoo.org/snippets/45/
def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


def rejson(success, dat={}, *others):
    return (jsonify({'suc': success, 'dat': dat}), *others)

def rsuc(*args):
    return rejson(1, *args)

def rerr (*args):
    return rejson(0, *args)
