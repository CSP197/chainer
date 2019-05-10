import numpy as np
import unittest

from chainer import testing
from chainer.dataset import TabularDataset

from .test_tabular_dataset import DummyDataset


@testing.parameterize(*testing.product_dict(
    testing.product({
        'mode': [tuple, dict],
        'integer': [int, np.int32],
        'seq': [list, np.array],
    }),
    [
        {'indices': slice(None), 'expected_len': 10,
         'expected_indices': slice(0, 10, 1)},
        {'indices': [3, 1], 'expected_len': 2, 'expected_indices': [3, 1]},
        {'indices': [11, 1], 'exception': IndexError},
        {'indices': slice(3, None, -2), 'expected_len': 2,
         'expected_indices': slice(3, -1, -2)},
    ],
    [
        {'keys': None, 'expected_keys': ('a', 'b', 'c'),
         'expected_key_indices': None},
        {'keys': (1,), 'expected_keys': ('b',),
         'expected_key_indices': (1,)},
        {'keys': ('c',), 'expected_keys': ('c',),
         'expected_key_indices': (2,)},
        {'keys': ('c', 0), 'expected_keys': ('c', 'a'),
         'expected_key_indices': (2, 0)},
    ],
))
class TestSlice(unittest.TestCase):

    def setUp(self):
        if isinstance(self.indices, list):
            self.indices = self.seq(
                [self.integer(index) for index in self.indices])

    def test_slice(self):
        def callback(indices, key_indices):
            self.assertEqual(indices, self.expected_indices)
            self.assertEqual(key_indices, self.expected_key_indices)

        dataset = DummyDataset(self.mode, callback)

        if hasattr(self, 'exception'):
            with self.assertRaises(self.exception):
                if self.keys is None:
                    dataset.slice[self.indices]
                else:
                    dataset.slice[self.indices, self.keys]
            return

        if self.keys is None:
            view = dataset.slice[self.indices]
            data = dataset.data[:, self.indices]
        else:
            view = dataset.slice[self.indices, self.keys]
            key_indices = [{'a': 0, 'b': 1, 'c': 2}.get(key, key)
                           for key in self.keys]
            data = dataset.data[key_indices][:, self.indices]

        self.assertIsInstance(view, TabularDataset)
        self.assertEqual(len(view), self.expected_len)
        self.assertEqual(view.keys, self.expected_keys)
        self.assertEqual(view.mode, self.mode)

        if self.mode is tuple:
            expected_output = tuple(list(d) for d in data)
        elif self.mode is dict:
            expected_output = dict(zip(
                self.expected_keys, (list(d) for d in data)))

        self.assertEqual(view.fetch(), expected_output)


testing.run_module(__name__, __file__)
