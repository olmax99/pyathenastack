import os


class Config(object):
    DEBUG = False
    TESTING = False
    # DATABASE_URI = 'sqlite:///:memory:'


# TODO: Production will be configured along with CloudFormation
# class ProductionConfig(Config):
#     # DATABASE_URI = 'mysql://user@localhost/foo'
#     pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI: str = os.getenv('POSTGRES_URI', None)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URI: str = os.getenv('REDIS_URI', None)


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI: str = f"postgresql+psycopg2://test:test123@postgres.testing/test_api"
    TEST_REDIS_URI: str = "redis://:test456@redis.testing:6379/0"
