from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect

from mistune import markdown
import bleach
from meowurl.whitelist import tags, attrs

from meowurl.config import Config

# Initialize app object
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
app.config.from_pyfile('config.cfg')

CsrfProtect(app)

# Setup jinja environmenta
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.filters.update({
    'bleach': lambda md_html: bleach.linkify(
        bleach.clean(md_html, tags, attrs)).replace('<table>','<table class="table table-striped">'),
})

@app.template_filter('markdown')
def filter_markdown(*args, **kwargs):
    md = markdown(*args, **kwargs)
    return md

# Setup database environment
db = SQLAlchemy(app)

from .cache import Client
# Set up Memcache cache environment
memcache = Client(
    app.config['MEMCACHEDCLOUD_SERVERS'],
    username=app.config['MEMCACHEDCLOUD_USERNAME'],
    password=app.config['MEMCACHEDCLOUD_PASSWORD'],
    binary=True,
    behaviors={'tcp_nodelay': True,
               'ketama': True}
)


# Register Cli interface
import meowurl.cli

# Register view functions
import meowurl.main

# Register APIs
import meowurl.api
