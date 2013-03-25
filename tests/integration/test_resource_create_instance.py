import json

from mock import patch

from brainiak.instance import create_resource
from brainiak.instance.delete_resource import QUERY_DELETE_INSTANCE
from brainiak.instance.get_resource import QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE
from brainiak.schema import resource as schema_resource
from brainiak.utils import sparql
from tests import TornadoAsyncHTTPTestCase, MockRequest
from tests.sparql import QueryTestCase


JSON_CITY_GLOBOLAND = {
    "@context": {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "place": "http://semantica.globo.com/place/",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "base": "http://semantica.globo.com/base/",
        "upper": "http://semantica.globo.com/upper/"
    },
    "upper:name": "Globoland",
    "upper:fullName": "Globoland (RJ)",
    "rdfs:comment": "City of Globo's companies. Historically known as PROJAC.",
    "place:partOfState": "base:UF_RJ",
    "place:latitude": "-22.958314",
    "place:longitude": "-43.407133"
}


class CollectionResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None
    allow_triplestore_connection = True
    graph_uri = 'http://semantica.globo.com/sample-place/'
    fixtures = []

    def setUp(self):
        self.original_create_instance_uri = sparql.create_instance_uri
        self.original_schema_resource_get_schema = schema_resource.get_schema
        super(CollectionResourceTestCase, self).setUp()

    def tearDown(self):
        #query_string = QUERY_DELETE_INSTANCE % {
        #    "graph_uri": 'http://semantica.globo.com/sample-place/',
        #    "instance_uri": 'http://semantica.globo.com/sample-place/City/unique-id'
        #}
        #self.query(query_string)
        sparql.create_instance_uri = self.original_create_instance_uri
        schema_resource.get_schema = self.original_schema_resource_get_schema
        super(CollectionResourceTestCase, self).tearDown()

    def checkInstanceExistance(self, class_uri, instance_uri):
        query_string = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % {
            "class_uri": class_uri,
            "instance_uri": instance_uri
        }
        response = self.query(query_string)
        return response['results']['bindings'] != []

    def assertInstanceExist(self, class_uri, instance_uri):
        return self.checkInstanceExistance(class_uri, instance_uri)

    def assertInstanceDoesNotExist(self, class_uri, instance_uri):
        return not self.checkInstanceExistance(class_uri, instance_uri)

    @patch("brainiak.handlers.log")
    def test_create_instance_500_internal_error(self, log):
        def raise_exception():
            raise Exception()
        schema_resource.get_schema = lambda params: raise_exception()
        response = self.fetch('/person/Person',
            method='POST',
            body=json.dumps({}))
        self.assertEqual(response.code, 500)
        body = json.loads(response.body)
        self.assertIn("HTTP error: 500\nException:\n", body["error"])

    @patch("brainiak.handlers.log")
    def test_create_instance_500_internal_error(self, log):
        response = self.fetch('/place/City',
            method='POST',
            body="invalid input")
        self.assertEqual(response.code, 400)
        body = json.loads(response.body)
        self.assertEquals(body["error"], 'HTTP error: 400\nNo JSON object could be decoded')

    @patch("brainiak.handlers.log")
    def test_create_instance_404_inexistant_class(self, log):
        payload = {}
        response = self.fetch('/xubiru/X',
            method='POST',
            body=json.dumps(payload))
        self.assertEqual(response.code, 404)
        body = json.loads(response.body)
        self.assertEqual(body["error"], u"HTTP error: 404\nClass X doesn't exist in context xubiru.")

    @patch("brainiak.handlers.log")
    def test_create_instance_201(self, log):
        schema_resource.get_schema = lambda params: True
        sparql.create_instance_uri = lambda class_uri: "http://unique-id"
        payload = JSON_CITY_GLOBOLAND
        response = self.fetch('/sample-place/City',
            method='POST',
            body=json.dumps(payload))
        self.assertEqual(response.code, 201)
        self.assertEqual(response.headers['Location'], "http://unique-id")
        self.assertEqual(response.body, "")
        self.assertInstanceExist('http://semantica.globo.com/sample-place/City', "http://unique-id")

    def test_query(self):
        self.graph_uri = "http://fofocapedia.org/"
        self.assertInstanceDoesNotExist('criatura', 'fulano')
        query = create_resource.QUERY_INSERT_TRIPLES % {"triples": '<fulano> a <criatura>; <gosta-de> <ciclano>', "prefix": "", "graph_uri": self.graph_uri}
        expected_response = {
            u'head': {u'link': [], u'vars': [u'callret-0']},
            u'results': {u'bindings': [{u'callret-0': {u'type': u'literal',
                                            u'value': u'Insert into <http://fofocapedia.org/>, 2 (or less) triples -- done'}}],
            u'distinct': False,
            u'ordered': True}}
        self.query(query)
        self.assertInstanceExist('criatura', 'fulano')