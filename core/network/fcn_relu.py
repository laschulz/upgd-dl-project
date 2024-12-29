import torch.nn as nn

# from .gate import GateLayer
import torch
from functools import partial
import collections


class ConvolutionalNetworkReLU(nn.Sequential):
    def __init__(self, n_obs=4, n_outputs=10):
        super(ConvolutionalNetworkReLU, self).__init__()
        self.name = "convolutional_network_relu"
        self.add_module(
            "conv_1", nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5)
        )
        self.add_module("pool_1", nn.MaxPool2d(kernel_size=2, stride=2))
        self.add_module(
            "conv_2", nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5)
        )
        self.add_module("pool_2", nn.MaxPool2d(kernel_size=2, stride=2))
        self.add_module("flatten", nn.Flatten())
        self.add_module("linear_1", nn.Linear(in_features=16 * 5 * 5, out_features=120))
        self.add_module("act_1", nn.ReLU())
        self.add_module("linear_2", nn.Linear(in_features=120, out_features=84))
        self.add_module("act_2", nn.ReLU())
        self.add_module("linear_3", nn.Linear(in_features=84, out_features=n_outputs))
        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.Linear):
                m.reset_parameters()

    def __str__(self):
        return self.name


# Model that we are using
class ConvolutionalNetworkReLUWithHooks(nn.Sequential):
    def __init__(self, n_obs=4, n_outputs=10):
        super(ConvolutionalNetworkReLUWithHooks, self).__init__()
        self.name = "convolutional_network_relu_with_hooks"
        self.add_module(
            "conv_1", nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5)
        )
        self.add_module("pool_1", nn.MaxPool2d(kernel_size=2, stride=2))
        self.add_module(
            "conv_2", nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5)
        )
        self.add_module("pool_2", nn.MaxPool2d(kernel_size=2, stride=2))
        self.add_module("flatten", nn.Flatten())
        self.add_module("linear_1", nn.Linear(in_features=16 * 5 * 5, out_features=120))
        self.add_module("act_1", nn.ReLU())
        self.add_module("linear_2", nn.Linear(in_features=120, out_features=84))
        self.add_module("act_2", nn.ReLU())
        self.add_module("linear_3", nn.Linear(in_features=84, out_features=n_outputs))
        self.activations = collections.defaultdict(list)
        self.n_units = 120 + 84
        for name, layer in self.named_modules():
            if isinstance(layer, nn.Conv2d) or isinstance(layer, nn.Linear):
                layer.reset_parameters()
            if isinstance(layer, nn.ReLU):
                layer.register_forward_hook(partial(self.activation_hook, name))

    def __str__(self):
        return self.name

    # Counts number of dead neurons and save it in layer
    def activation_hook(self, name, module, inp, out):
        self.activations[name] = torch.sum(out == 0.0).item()

    def __str__(self):
        return self.name


if __name__ == "__main__":
    # example of dummy input to network
    net = ConvolutionalNetworkReLU()
    inputs = torch.randn(42, 3, 32, 32)
    output = net(inputs)

    print(output.shape)
