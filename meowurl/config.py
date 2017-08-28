class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    # These are essential configuration
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/meowurl'

    MEMCACHEDCLOUD_SERVERS = [
        '127.0.0.1:11211'
    ]
    MEMCACHEDCLOUD_PASSWORD = None
    MEMCACHEDCLOUD_USERNAME = None

    DB_PREFIX = 'mu_'
    MEMCACHE_PREFIX = 'mu'

    # App configurations
    MAX_CONTENT_LENGTH = 65536
    MAX_PASSWORD_LENGTH = 63
    MIN_PASSWORD_LENGTH = 6

    # Display content
    VERSION = '0.1'
    INTRO = 'MeowURL'
    TITLE = 'MeowURL Shortener'

    # URL & Page
    INDEX_PASTE_NUMBER = 8
    MORE_PASTE_NUMBER = 100
    URL_CHARSET = '0123456789abcdefghijklmnopqrstuvwxyz'
    ALT_URL_CHARSET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    # User
    OPEN_REGISTRATION = True
    USER_INVITES = 5
    RESERVED_USERNAMES = [
        'anonymous',
    ]


class DebugConfig(Config):
    DEBUG = True
    TEMPLATE_AUTO_RELOAD = True
