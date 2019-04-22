from flask_restplus import Api

from .namespace1 import api as ns1
from .namespace2 import api as ns2
# ...
from .namespaceX import api as nsX

"""
REGISTERING ALL NAMESPACES

The apis.__ini__ module aggregates all namespaces. 

Alternatively, you can define custom url-prefixes for namespaces during 
registering them in your API. You don’t have to bind url-prefix while 
declaration of Namespace object.

"""

# TODO: 'app=app' should be default and can be omitted, try.
api = Api(
    title='My Title',
    version='1.0',
    description='A description',
    # All API metadatas
)

api.add_namespace(ns1, path='/prefix/of/ns1')
api.add_namespace(ns2, path='/prefix/of/ns2')
# ...
api.add_namespace(nsX, path='/prefix/of/nsX')