# -*- coding: utf-8 -*-

import unittest
from brainiak import prefixes
from brainiak.prefixes import expand_uri, prefix_to_slug, safe_slug_to_prefix, shorten_uri, slug_to_prefix, MemorizeContext, uri_to_slug, prefix_from_uri, PrefixError, extract_prefix, is_compressed_uri


class PrefixesTestCase(unittest.TestCase):

    def test_prefix_contains_obligatory_keys(self):
        existing_keys = sorted(prefixes._MAP_SLUG_TO_PREFIX.keys())
        expected_keys = ['base', 'dbpedia', 'dc', 'dct', 'ego', 'esportes',
                         'eureka', 'event', 'foaf', 'g1', 'geo', 'glb', 'organization',
                         'owl', 'person', 'place', 'rdf', 'rdfs', 'schema', 'time', 'tvg',
                         'upper', 'xsd']
        self.assertEqual(len(existing_keys), 23)
        self.assertEqual(existing_keys, expected_keys)

    def test_prefix_to_slug(self):
        self.assertEqual(prefix_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 'rdf')

    def test_uri_to_slug(self):
        self.assertEqual(uri_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), 'rdf')

    def test_safe_slug_to_prefix_when_prefix_is_defined(self):
        self.assertEqual(safe_slug_to_prefix('rdf'), 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    def test_safe_slug_to_prefix_when_prefix_is_not_defined(self):
        self.assertEqual(safe_slug_to_prefix('bigoletinha'), 'bigoletinha')

    def test_slug_to_prefix_when_prefix_is_defined(self):
        self.assertEqual(slug_to_prefix('dct'), 'http://purl.org/dc/terms/')

    def test_slug_to_prefix_when_prefix_is_not_defined(self):
        self.assertRaises(PrefixError, slug_to_prefix, 'alchueyr')

    def test_shorten_uri_success(self):
        self.assertEqual(shorten_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), "rdf:type")

    def test_shorten_uri_fails(self):
        self.assertEqual(shorten_uri("http://some/invalid/uri"), "http://some/invalid/uri")

    def test_prefix_from_uri(self):
        self.assertEqual("http://test/person/", prefix_from_uri("http://test/person/Person"))

    def test_expand_uri(self):
        self.assertEqual("http://www.w3.org/2003/01/geo/wgs84_pos#Brasil", expand_uri("geo:Brasil"))

    def test_expand_another_uri(self):
        self.assertEqual("http://schema.org/whatever", expand_uri("schema:whatever"))

    def test_expand_uri_that_is_already_a_uri(self):
        self.assertEqual("http://oi", expand_uri("http://oi"))

    def test_expand_uri_that_is_already_a_uri_with_https(self):
        self.assertEqual("https://secure", expand_uri("https://secure"))

    def test_is_compressed_uri_given_a_literal(self):
        self.assertEqual(is_compressed_uri("oi"), False)


class ExtractPrefixTestCase(unittest.TestCase):

    def setUp(self):
        self.original_prefix_to_slug = prefixes._MAP_PREFIX_TO_SLUG
        prefixes._MAP_PREFIX_TO_SLUG = {}

    def tearDown(self):
        prefixes._MAP_PREFIX_TO_SLUG = self.original_prefix_to_slug

    def test_prefix_is_substring_of_other_prefix(self):
        # Mock
        prefixes._MAP_PREFIX_TO_SLUG["http://some"] = None
        prefixes._MAP_PREFIX_TO_SLUG["http://someprefix/place/"] = "place"
        prefixes._MAP_PREFIX_TO_SLUG["http://someprefix/place/City"] = "place"
        self.assertEqual("http://someprefix/place/City", extract_prefix("http://someprefix/place/City"))


class MemorizeContextTestCase(unittest.TestCase):

    def setUp(self):
        self.context = MemorizeContext()

    def test_unique_object_properties(self):
        self.context.add_object_property("ctx:field_name", "upper:Entity")
        self.assertIn('ctx:field_name', self.context.object_properties)

    def test_prefix_to_slug(self):
        self.assertEqual(self.context.prefix_to_slug('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 'rdf')
        self.assertIn('rdf', self.context.context)
        self.assertEqual(self.context.context['rdf'], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    def test_shorten_uri(self):
        self.assertEqual(self.context.shorten_uri('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), 'rdf:type')
        self.assertIn('rdf', self.context.context)
        self.assertEqual(self.context.context['rdf'], 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
