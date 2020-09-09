from sphinx_js.ir import Attribute, Exc, Function, Param, Pathname, Return
from sphinx_js.jsdoc import full_path_segments
from tests.testing import JsDocTestCase


def test_doclet_full_path():
    """Sanity-check full_path_segments(), including throwing it a non-.js filename."""
    doclet = {
        'meta': {
            'filename': 'utils.jsm',
            'path': '/boogie/smoo/Checkouts/fathom',
        },
        'longname': 'best#thing~yeah'
    }
    assert full_path_segments(doclet, '/boogie/smoo/Checkouts') == [
        './',
        'fathom/',
        'utils.',
        'best#',
        'thing~',
        'yeah',
    ]


class FunctionTests(JsDocTestCase):
    file = 'function.js'

    def test_top_level_and_function(self):
        """Test Function (and thus also TopLevel) analysis.

        This also includes exceptions, returns, params, and default values.

        """
        function = self.analyzer.get_object(['foo'], 'function')
        assert function == Function(
            name='foo',
            path=Pathname(['./', 'function.', 'foo']),
            filename='function.js',
            description=(
                'Determine any of type, note, score, and element using a callback. This\n'
                'overrides any previous call.\n'
                '\n'
                'The callback should return...\n'
                '\n'
                '* An optional :term:`subscore`\n'
                '* A type (required on ``dom(...)`` rules, defaulting to the input one on\n'
                '  ``type(...)`` rules)\n'
                '* Optional notes\n'
                '* An element, defaulting to the input one. Overriding the default\n'
                '  enables a callback to walk around the tree and say things about nodes\n'
                '  other than the input one.'),
            line=21,
            deprecated=False,
            examples=[],
            see_alsos=[],
            properties=[],
            is_private=False,
            exported_from=None,
            is_abstract=False,
            is_optional=False,
            is_static=False,
            params=[Param(name='bar',
                          description='Which bar',
                          has_default=False,
                          is_variadic=False,
                          type='String'),
                    Param(name='baz',
                          description='',
                          has_default=True,
                          default='8',
                          is_variadic=False,
                          type=None)],
            exceptions=[Exc(type=None,
                            description='ExplosionError It went boom.')],
            returns=[
                Return(type='Number',
                       description='How many things there are')])  # Test text unwrapping.


class ClassTests(JsDocTestCase):
    file = 'class.js'

    def test_class(self):
        """Test Class analysis, including members, attributes, and privacy."""
        cls = self.analyzer.get_object(['Foo'], 'class')
        assert cls.name == 'Foo'
        assert cls.path == Pathname(['./', 'class.', 'Foo'])
        assert cls.filename == 'class.js'
        assert cls.description == 'This is a long description that should not be unwrapped. Once day, I was\nwalking down the street, and a large, green, polka-dotted grand piano fell\nfrom the 23rd floor of an apartment building.'
        assert cls.line == 15  # Not ideal, as it refers to the constructor, but we'll allow it
        assert cls.examples == ['Example in constructor']  # We ignore examples and other fields from the class doclet so far. This could change someday.

        # Members:
        getter, private_method = cls.members  # default constructor not included here
        assert isinstance(private_method, Function)
        assert private_method.name == 'secret'
        assert private_method.path == Pathname(['./', 'class.', 'Foo#', 'secret'])
        assert private_method.description == 'Private method.'
        assert private_method.is_private is True
        assert isinstance(getter, Attribute)
        assert getter.name == 'bar'
        assert getter.path == Pathname(['./', 'class.', 'Foo#', 'bar'])
        assert getter.filename == 'class.js'
        assert getter.description == 'Setting this also frobs the frobnicator.'

        # Constructor:
        constructor = cls.constructor
        assert constructor.name == 'Foo'
        assert constructor.path == Pathname(['./', 'class.', 'Foo'])  # Same path as class. This might differ in different languages.
        assert constructor.filename == 'class.js'
        assert constructor.description == 'Constructor doc.'
        assert constructor.examples == ['Example in constructor']
        assert constructor.params == [Param(name='ho',
                                            description='A thing',
                                            has_default=False,
                                            is_variadic=False,
                                            type=None)]
