from itertools import chain
import numpy
import scipy.signal
import mxnet as mx
import minpy.nn.init
import minpy.core as core
import minpy.numpy as np
from minpy.nn.model import ModelBase

def batch_dot(data, xs):
  prefix_shape = data.shape[:-1]
  return np.dot(data.reshape((-1, data.shape[-1])), xs).reshape((*prefix_shape, xs.shape[-1]))

class Agent(ModelBase):
    def __init__(self, input_size, act_space, config):
        super(Agent, self).__init__()
        if config:
            self.ctx = config.ctx
        self.act_space = act_space
        if config:
            self.config = config
        self.add_param('fc1', (input_size, config.hidden_size_1))
        #self.add_param('fc2', (config.hidden_size_1, config.hidden_size_2))
        self.add_param('policy_fc_last', (config.hidden_size_1, 1))
        self.add_param('vf_fc_last', (act_space, 1))
        self.add_param('vf_fc_last_bias', (1,))

        self._init_params()
        # self.params['policy_fc_last'] = numpy.identity(act_space)
        # self.params['policy_fc_last'] /= 1000

        self.optim_configs = {}
        if config:
            for p in self.param_configs:
                self.optim_configs[p] = {'learning_rate': self.config.learning_rate}

    def forward(self, Xs):
        hs = batch_dot(Xs, self.params['fc1'])
        relu1 = np.maximum(hs, 0) + np.minimum(hs * 0.01, 0)
        #hs2 = batch_dot(relu1, self.params['fc2'])
        #relu2 = np.maximum(hs2, 0) + np.minimum(hs2 * 0.01, 0)
        logits = np.sum(batch_dot(relu1, self.params['policy_fc_last']), axis=-1)
        # logits = np.vstack([-X[-1] for X in Xs])
        ps = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        ps /= np.sum(ps, axis=1, keepdims=True)
        # vs = np.dot(h.T, self.params['vf_fc_last'].T) + self.params['vf_fc_last_bias']
        vs = np.dot(logits, self.params['vf_fc_last']) + self.params['vf_fc_last_bias']
        # with np.printoptions(formatter={'all': lambda x: "{0:0.2f}".format(x)}):
        #     IDX = -1
        #     print(Xs[IDX])
        #     print(logits[IDX])
        #     print(ps[IDX])
        return ps, vs

    def loss(self, ps, as_, vs, rs, advs):
        ps = np.maximum(1.0e-5, np.minimum(1.0 - 1e-5, ps))
        policy_grad_loss = -np.sum(np.log(ps) * as_ * advs)
        vf_loss = 0.5*np.sum((vs - rs)**2)
        entropy = -np.sum(ps*np.log(ps))
        loss_ = policy_grad_loss + self.config.vf_wt*vf_loss - self.config.entropy_wt*entropy
        # print(loss_, policy_grad_loss, vf_loss, entropy)
        return loss_

    def act(self, ps):
        us = numpy.random.uniform(size=ps.shape[0])[:, np.newaxis]
        as_ = (numpy.cumsum(ps.asnumpy(), axis=1) > us).argmax(axis=1)
        return as_

    def train_step(self, env_xs, env_as, env_rs, env_vs):
        # One-hot encode the actions.
        env_xs = numpy.vstack(numpy.array(env_xs))
        env_as = mx.nd.one_hot(mx.nd.array(numpy.array(env_as).flatten(), self.ctx), self.act_space).asnumpy()

        # Compute discounted rewards and advantages.
        drs, advs = [], []
        gamma, lambda_ = self.config.gamma, self.config.lambda_
        for i in range(len(env_vs)):
            # Compute discounted rewards with a 'bootstrapped' final value.
            rs_bootstrap = [] if env_rs[i] == [] else env_rs[i] + [env_vs[i][-1]]
            drs.extend(self._discount(rs_bootstrap, gamma)[:-1])

            # Compute advantages using Generalized Advantage Estimation;
            # see eqn. (16) of [Schulman 2016].
            delta_t = env_rs[i] + gamma*numpy.array(env_vs[i][1:]) - numpy.array(env_vs[i][:-1])
            advs.extend(self._discount(delta_t, gamma * lambda_))

        drs = numpy.array(drs)[:, np.newaxis]
        advs = numpy.array(advs)[:, np.newaxis]

        assert env_xs.shape[0] == env_as.shape[0] == drs.shape[0] == advs.shape[0]
        def loss_func(*params):
            ps, vs = self.forward(env_xs)
            loss_ = self.loss(ps, env_as, vs, drs, advs)
            return loss_
            # ps, vs = self.forward(env_xs[0])
            # return self.loss(ps, env_as[0], vs, drs[0], advs[0])

        grads = self._forward_backward(loss_func)
        self._update_params(grads)

        # with np.printoptions(formatter={'all': lambda x: "{0:0.2f}".format(x)}):
        #     IDX, JDX = -1, -1
        #     ps, vs = self.forward(env_xs)
        #     print(env_xs[JDX, :, -1])
        #     print(ps[JDX])

        # with np.printoptions(precision=2, suppress=True, threshold=10, edgeitems=30, linewidth=120):
        #     print(self.params['fc1'])
        # #     # print(self.params['fc2'])
        #     print(self.params['policy_fc_last'].T)
        #     print(self.params['vf_fc_last'].T)
        #     print(self.params['vf_fc_last_bias'])
        # print(numpy.linalg.norm(self.params['policy_fc_last'].asnumpy()), numpy.linalg.norm(self.params['policy_fc_last'].asnumpy().diagonal()))

    def _discount(self, x, gamma):
        return scipy.signal.lfilter([1], [1, -gamma], x[::-1], axis=0)[::-1]

    def _forward_backward(self, loss_func):
        param_arrays = list(self.params.values())
        param_keys = list(self.params.keys())
        grad_and_loss_func = core.grad_and_loss(loss_func, argnum=range(len(param_arrays)))
        grad_arrays, loss = grad_and_loss_func(*param_arrays)
        grads = dict(zip(param_keys, grad_arrays))
        # print('param_arrays', param_arrays)
        # print('grads', grads)
        if self.config.grad_clip:
            for k, v in grads.items():
                grads[k] = numpy.clip(v, -self.config.clip_magnitude, self.config.clip_magnitude)

        return grads

    def _update_params(self, grads):
        for p, w in self.params.items():
            dw = grads[p]
            config = self.optim_configs[p]
            # print(p, ':', w, '+', dw)
            next_w, next_config = self.config.update_rule(w, dw, config)
            # print(p, ':', w, '->', next_w)
            self.params[p] = next_w
            self.optim_configs[p] = next_config

    def _init_params(self):
        for name, config in self.param_configs.items():
            init_func = minpy.nn.init.constant if name.endswith('bias') else self.config.init_func
            self.params[name] = init_func(config['shape'], self.config.init_config)
