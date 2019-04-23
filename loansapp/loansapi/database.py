from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

"""
This is a declarative approach. The Models are being built on pre-existing
database tables.
[ http://flask.pocoo.org/docs/1.0/patterns/sqlalchemy/#declarative ]

"""


engine = create_engine("postgresql://flask:flaskdb@postgres/flask_api")
# Provides scoped management of :class:`.Session` objects.
# linking the scope of a Session with that of a web request
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
# Returns .Query` object against the current :class:`.Session` when called.
# Basically connects the mapper() with the current Session
# NOTE: This allows for direct querying through the Model objects !!
Base.query = db_session.query_property()


# TODO: What does init_db do? Why is it needed if database exist already?
# This function is most likely optional in case a db creation is needed
# (e.g. for testing) < assumption, needs to be verified
def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import loansapi.models
    Base.metadata.create_all(bind=engine)
