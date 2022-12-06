import unittest
from envs import HistoryPreprocessor
import numpy as np

class TestPreprocessor(unittest.TestCase):
    def test_init(self):
        input_shape = (2, 10)
        hist_length = 10

        # Current model trained with hist length of 10
        processor = HistoryPreprocessor(input_shape, hist_length)
        self.assertEqual(len(processor.hist), hist_length)
        self.assertEqual(processor.hist[0].shape, input_shape)

    def test_preprocess(self):
        input_shape = (2, 10)
        hist_length = 10
        expected_shape = (10, 20)

        # Output shape should be (input_shape[1], input_shape[0] * hist_legnth)
        processor = HistoryPreprocessor(input_shape, hist_length)
        output = processor.preprocess(np.random.random(input_shape))
        self.assertEqual(output.shape, expected_shape)

if __name__ == '__main__':
    unittest.main()
