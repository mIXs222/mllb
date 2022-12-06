import numpy as np

class IdentityPreprocessor(object):
    def __init__(self, obs_size):
        self.obs_size = obs_size

    def reset(self):
        pass

    def preprocess(self, x):
        return x

class HistoryPreprocessor(object):
    def __init__(self, input_shape, hist_length):
        self.input_shape = input_shape
        self.hist_length = hist_length
        self.obs_size = hist_length
        self.hist = [np.zeros(input_shape, dtype=float) for _ in range(self.hist_length)]

    def reset(self):
        pass

    def preprocess(self, x):
        self.hist.append(x)
        self.hist = self.hist[-self.hist_length:]
        return np.vstack(self.hist).T
