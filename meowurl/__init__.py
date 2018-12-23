from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from mistune import markdown
from bleach import linkify, clean
from meowurl.whitelist import tags, attrs

from meowurl.config import Config

# Initialize app object
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
app.config.from_pyfile('config.cfg')

CSRFProtect(app)

# Setup jinja environment
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.filters['markdown'] = markdown

@app.template_filter('bleach')
def bleach_filter(html):
    '''The bleach filter is a wrapper of bleach's clean and linkify.
    It also adds some custom functions when processing the markdown HTML.
    '''
    html = clean(html, tags, attrs)
    html = linkify(html)
    return html.replace('<table>','<table class="table table-striped">')


# Setup database environment
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
