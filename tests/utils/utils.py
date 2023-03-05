import io
from unittest import TestCase
from engine.utils.utils import DotDict
from tests.utils.data import Data


class RunAllTestCase(TestCase):
    """Expand TestCase class. Substitute original assertion
       methods with custom ones using subTest to run all multiple
       assertions in a test class"""
    def expectEqual(self, obj, template):
        with self.subTest():
            self.assertEqual(obj, template)

    def expectTrue(self, obj):
        with self.subTest():
            self.assertTrue(obj)

    def expectFalse(self, obj):
        with self.subTest():
            self.assertFalse(obj)

    def expectIsNone(self, obj):
        with self.subTest():
            self.assertIsNone(obj)

    def expectNotEqual(self, obj, template):
        with self.subTest():
            self.assertNotEqual(obj, template)


class Message(Data):
    """Model the structure of
       a Telegram message/call."""
    num = 0
    text = ''

    @property
    def message(self):
        return DotDict({'from_user': DotDict({'id': self.num, 'first_name': f'Name{self.num}'}),
                        'text': f'{self.text}',
                        'location': DotDict({'latitude': self.data_point_polygon_location[0],
                                             'longitude': self.data_point_polygon_location[1]}),
                        'survey': f'survey{self.num}'})


class TestID:
    """Setting static IDs in the
       testing mode."""
    def transit_process(self, transit):
        test_id = [37, 38, 39, 40]

        for i in range(4):
            transit[i][0] = test_id[i]

        return transit

    def elem_process(self, elem, index):
        test_id = [22, 23, 24, 25]

        elem['id'] = test_id[index]

        return elem


class ShpProcess:
    """Process shp
       binaries."""
    def shp_value(self, shp):
        shp['shp'] = shp['shp'].getvalue()
        shp['shx'] = shp['shx'].getvalue()
        shp['dbf'] = shp['dbf'].getvalue()[31:]

        return shp

    def shp_bytes(self, shp):
        shp['shp'] = io.BytesIO(shp['shp'])
        shp['shx'] = io.BytesIO(shp['shx'])
        shp['dbf'] = io.BytesIO(shp['dbf'])

        return shp
