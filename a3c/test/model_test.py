import unittest
from config import Config
from model import Agent
from envs import HistoryPreprocessor
import numpy as np

class TestModel(unittest.TestCase):
    def test_forward(self):
        num_features = 20
        act_space = 10

        # can be anything else
        batch_size = 32

        # batch size * act space * num_features
        input_shape = (batch_size, act_space, num_features)

        agent = Agent(num_features, act_space, Config(None))

        # Test shape of forward output
        ps, vs = agent.forward(np.random.random(input_shape))
        self.assertEqual(ps.shape, (batch_size, act_space))
        self.assertEqual(vs.shape, (batch_size, 1))

        # Test shape of act output
        action = agent.act(ps)
        self.assertEqual(action.shape, (batch_size,))


if __name__ == '__main__':
    unittest.main()
