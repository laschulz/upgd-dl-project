import sys, os
from torch.nn import functional as F
sys.path.insert(1, os.getcwd())
from HesScale.hesscale import HesScale
import torch

# wasn't used by Yumi's first run, but keeping for now
class SecondOrderLocalKernelUPGD(torch.optim.Optimizer):
    method = HesScale()
    def __init__(self, params, lr=1e-5, weight_decay=0.0, beta_utility=0.0, sigma=1.0):
        names, params = zip(*params)
        defaults = dict(lr=lr, weight_decay=weight_decay, beta_utility=beta_utility, sigma=sigma, method_field=type(self).method.savefield, names=names)
        super(SecondOrderLocalKernelUPGD, self).__init__(params, defaults)

    def step(self):
        for group in self.param_groups:
            for name, p in zip(group["names"], group["params"]):
                if 'gate' in name:
                    continue
                state = self.state[p]
                if len(state) == 0:
                    state["step"] = 0
                    state["avg_utility"] = torch.zeros_like(p.data)
                state["step"] += 1
                bias_correction = 1 - group["beta_utility"] ** state["step"]
                noise = torch.randn_like(p.grad) * group["sigma"]
                avg_utility = state["avg_utility"]
                hess_param = getattr(p, group["method_field"])
                utility = 0.5 * hess_param * p.data ** 2 - p.grad.data * p.data
                avg_utility.mul_(group["beta_utility"]).add_(
                    utility, alpha=1 - group["beta_utility"]
                )
                scaled_utility = torch.sigmoid_(
                    F.normalize((avg_utility / bias_correction), dim=-1)
                )
                if len(scaled_utility.shape) == 4: # We are in convolutional layer:
                    avg = scaled_utility.mean(dim=[2, 3])  # avg shape: [out_channels, in_channels]

                    # Step 2: Inflate back to original shape
                    # First, add back the spatial dims
                    avg_expanded = avg.unsqueeze(-1).unsqueeze(-1)  # shape: [out_channels, in_channels, 1, 1]

                    # Now expand along the spatial dimensions
                    averagekernel_utility = avg_expanded.expand(-1, -1, scaled_utility.size(2), scaled_utility.size(3))  
                    # inflated shape: [out_channels, in_channels, kernel_height, kerne
                    p.data.mul_(1 - group["lr"] * group["weight_decay"]).add_(
                        (p.grad.data + noise) * (1-averagekernel_utility),
                        alpha=-2.0*group["lr"],
                    )
                else:
                    p.data.mul_(1 - group["lr"] * group["weight_decay"]).add_(
                        (p.grad.data + noise) * (1-scaled_utility),
                        alpha=-2.0*group["lr"],
                    )
                # p.data.mul_(1 - group["lr"] * group["weight_decay"]).add_(
                #     (p.grad.data + noise) * (1 - scaled_utility), alpha=-group["lr"]
                # )


class SecondOrderGlobalKernelUPGD(torch.optim.Optimizer):
    method = HesScale()
    def __init__(self, params, lr=1e-5, weight_decay=0.0, beta_utility=0.0, sigma=1.0):
        names, params = zip(*params)
        defaults = dict(lr=lr, weight_decay=weight_decay, beta_utility=beta_utility, sigma=sigma, method_field=type(self).method.savefield, names=names)
        super(SecondOrderGlobalKernelUPGD, self).__init__(params, defaults)
    def step(self):
        global_max_util = torch.tensor(-torch.inf)
        for group in self.param_groups:
            for name, p in zip(group["names"], group["params"]):
                if 'gate' in name:
                    continue
                state = self.state[p]
                if len(state) == 0:
                    state["step"] = 0
                    state["avg_utility"] = torch.zeros_like(p.data)
                state["step"] += 1
                avg_utility = state["avg_utility"]
                hess_param = getattr(p, group["method_field"])
                utility = 0.5 * hess_param * p.data ** 2 - p.grad.data * p.data
                avg_utility.mul_(group["beta_utility"]).add_(
                    utility, alpha=1 - group["beta_utility"]
                )
                current_util_max = avg_utility.max()
                if current_util_max > global_max_util:
                    global_max_util = current_util_max

        for group in self.param_groups:
            for name, p in zip(group["names"], group["params"]):
                if 'gate' in name:
                    continue
                state = self.state[p]
                bias_correction = 1 - group["beta_utility"] ** state["step"]
                noise = torch.randn_like(p.grad) * group["sigma"]
                scaled_utility = torch.sigmoid_((state["avg_utility"] / bias_correction) / global_max_util)
                if len(scaled_utility.shape) == 4: # We are in convolutional layer:
                    avg = scaled_utility.mean(dim=[2, 3])  # avg shape: [out_channels, in_channels]

                    # Step 2: Inflate back to original shape
                    # First, add back the spatial dims
                    avg_expanded = avg.unsqueeze(-1).unsqueeze(-1)  # shape: [out_channels, in_channels, 1, 1]

                    # Now expand along the spatial dimensions
                    averagekernel_utility = avg_expanded.expand(-1, -1, scaled_utility.size(2), scaled_utility.size(3))  
                    # inflated shape: [out_channels, in_channels, kernel_height, kerne
                    p.data.mul_(1 - group["lr"] * group["weight_decay"]).add_(
                        (p.grad.data + noise) * (1-averagekernel_utility),
                        alpha=-2.0*group["lr"],
                    )
                else:
                    p.data.mul_(1 - group["lr"] * group["weight_decay"]).add_(
                        (p.grad.data + noise) * (1-scaled_utility),
                        alpha=-2.0*group["lr"],
                    )
                # p.data.mul_(1 - group["lr"] * group["weight_decay"]).add_(
                #     (p.grad.data + noise) * (1 - scaled_utility), alpha=-group["lr"]
                # )