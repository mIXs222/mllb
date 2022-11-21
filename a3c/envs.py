import numpy as np

class IdentityPreprocessor(object):
    def __init__(self, obs_size):
        self.obs_size = obs_size

    def reset(self):
        pass

    def preprocess(self, x):
        return x