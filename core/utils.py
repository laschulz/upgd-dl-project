from core.task.label_permuted_cifar10 import LabelPermutedCIFAR10
from core.task.input_permuted_mnist import InputPermutedMNIST
from core.task.utility_task import UtilityTask

from core.network.fcn_relu import ConvolutionalNetworkReLU, ConvolutionalNetworkReLUWithHooks, ConvForMNSIT

from core.learner.scaled_noise_upgd import UPGDScaledWeightNormNoiseLearner,UPGDScaledGradNormNoiseLearner,UPGDScaledAdativeNormNoiseDLearner
from core.learner.usgd import USGD_withAdaptiveNoise_Learner, UPGD_DynamicclippedGradient_Learner
from core.learner.convexlearner import KernelConvexCombiLearner

from core.learner.baseline_upgd import FirstOrderGlobalUPGDLearner
from core.learner.kernel_avg import UPGD_KernelLearner
from core.learner.column_kernel_avg import UPGD_ColumnKernelLearner
from core.utilities.weight.fo_utility import FirstOrderUtility
from core.utilities.weight.so_utility import SecondOrderUtility
from core.utilities.weight.weight_utility import WeightUtility
from core.utilities.weight.oracle_utility import OracleUtility
from core.utilities.weight.grad2_utility import SquaredGradUtility

import torch
import numpy as np


tasks = {
    "weight_utils": UtilityTask,
    "feature_utils": UtilityTask,
    "label_permuted_cifar10" : LabelPermutedCIFAR10,
    "label_permuted_cifar10_stats" : LabelPermutedCIFAR10,
    "input_permuted_mnist_stats": InputPermutedMNIST,
}


networks = {
    "convolutional_network_relu": ConvolutionalNetworkReLU,
    "convolutional_network_relu_with_hooks": ConvolutionalNetworkReLUWithHooks,
    "conv_mnist": ConvForMNSIT
}

learners = {
    "weight_norm":UPGDScaledWeightNormNoiseLearner,
    "grad_norm":UPGDScaledGradNormNoiseLearner,
    "ratio_norm":UPGDScaledAdativeNormNoiseDLearner,
    "usgd": USGD_withAdaptiveNoise_Learner,
    "upgd_dynamicclippedgradient": UPGD_DynamicclippedGradient_Learner,
    "entire_kernel":UPGD_KernelLearner,
    "column_kernel": UPGD_ColumnKernelLearner,
    "baseline": FirstOrderGlobalUPGDLearner,
    "KernelConvexCombi":KernelConvexCombiLearner
}

criterions = {
    "mse": torch.nn.MSELoss,
    "cross_entropy": torch.nn.CrossEntropyLoss,
}

utility_factory = {
    "first_order": FirstOrderUtility,
    "second_order": SecondOrderUtility,
    "weight": WeightUtility,
    "g2": SquaredGradUtility,
    "oracle": OracleUtility,
}

def compute_spearman_rank_coefficient(approx_utility, oracle_utility):
    approx_list = []
    oracle_list = []
    for fo, oracle in zip(approx_utility, oracle_utility):
        oracle_list += list(oracle.ravel().numpy())
        approx_list += list(fo.ravel().numpy())

    overall_count = len(approx_list)
    approx_list = np.argsort(np.asarray(approx_list))
    oracle_list = np.argsort(np.asarray(oracle_list))

    difference = np.sum((approx_list - oracle_list) ** 2)
    coeff = 1 - 6.0 * difference / (overall_count * (overall_count**2-1))
    return coeff
  
def compute_spearman_rank_coefficient_layerwise(approx_utility, oracle_utility):
    coeffs = []
    for fo, oracle in zip(approx_utility, oracle_utility):
        overall_count = len(list(oracle.ravel().numpy()))
        if overall_count == 1:
            continue
        oracle_list = np.argsort(list(oracle.ravel().numpy()))
        approx_list = np.argsort(list(fo.ravel().numpy()))
        difference = np.sum((approx_list - oracle_list) ** 2)
        coeff = 1 - 6.0 * difference / (overall_count * (overall_count**2-1))
        coeffs.append(coeff)
    coeff_average = np.mean(np.array(coeffs))
    return coeff_average
