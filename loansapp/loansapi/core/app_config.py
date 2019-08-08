import os


class Config(object):
    DEBUG = False
    TESTING = False
    # DATABASE_URI = 'sqlite:///:memory:'


# class ProductionConfig(Config):
#     # DATABASE_URI = 'mysql://user@localhost/foo'
#     pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI: str = os.environ['POSTGRES_URI']
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # REDIS_URL = f"redis://:{os.environ['REDIS_PASSWD']}@" \
    #     f"{os.environ['REDIS_HOST']}:" \
    #     f"{os.environ['REDIS_PORT']}/" \
    #     f"{os.environ['REDIS_DB']}"


class TestingConfig(Config):
    TESTING = True

    DATABASE_URI: str = f"postgresql+psycopg2://test:test123@testdb/test_api"

    # TEST_REDIS_URL = "redis://:test123@redistest:6379/0"
