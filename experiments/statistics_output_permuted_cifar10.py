from core.grid_search import GridSearch
from core.learner.weight_upgd import FirstOrderGlobalUPGDLearner, FirstOrderNonprotectingGlobalUPGDLearner
from core.learner.sgd import SGDLearner
from core.learner.shrink_and_perturb import ShrinkandPerturbLearner
from core.learner.adam import AdamLearner
from core.learner.ewc import EWCLearner
from core.learner.synaptic_intelligence import SynapticIntelligenceLearner

from core.network.fcn_relu import ConvolutionalNetworkReLUWithHooks
from core.runner import Runner
from core.run.run_stats import RunStats
from core.utils import create_script_generator, create_script_runner, tasks

exp_name = "label_permuted_cifar10_stats"
task = tasks[exp_name]()

n_steps = 1000000
n_seeds = 20

upgd1_grid = GridSearch(
               seed=[i for i in range(0, n_seeds)],
               lr=[0.01],
               beta_utility=[0.99],
               sigma=[0.01],
               weight_decay=[0.001],
               network=[ConvolutionalNetworkReLUWithHooks()],
               n_samples=[n_steps],
    )

upgd2_grid = GridSearch(
               seed=[i for i in range(0, n_seeds)],
               lr=[0.01],
               beta_utility=[0.999],
               sigma=[0.001],
               weight_decay=[0.0],
               network=[ConvolutionalNetworkReLUWithHooks()],
               n_samples=[n_steps],
    )



sgd_grid = GridSearch(
               seed=[i for i in range(0, n_seeds)],
               lr=[0.01],
               weight_decay=[0.001],
               network=[ConvolutionalNetworkReLUWithHooks()],
               n_samples=[n_steps],
    )

sp_grid = GridSearch(
               seed=[i for i in range(0, n_seeds)],
               lr=[0.01],
               sigma=[0.005],
               decay=[0.001],
               network=[ConvolutionalNetworkReLUWithHooks()],
               n_samples=[n_steps],
    )

adam_grid = GridSearch(
               seed=[i for i in range(0, n_seeds)],
               lr=[0.001],
               weight_decay=[0.01],
               beta1=[0.0],
               beta2=[0.9999],
               eps=[1e-8],
               network=[ConvolutionalNetworkReLUWithHooks()],
               n_samples=[n_steps],
    )

ewc_grid = GridSearch(
               seed=[i for i in range(0, n_seeds)],
               lr=[0.01],
               beta_weight=[0.999],
               beta_fisher=[0.9999],
               lamda=[10.0],
               network=[ConvolutionalNetworkReLUWithHooks()],
               n_samples=[n_steps],
    )


si_grid = GridSearch(
                seed=[i for i in range(0, n_seeds)],
                lr=[0.001],
                beta_weight=[0.999],
                beta_importance=[0.9],
                lamda=[1.0],
                network=[ConvolutionalNetworkReLUWithHooks()],
                n_samples=[n_steps],
    )



grids = [
         upgd1_grid,
         upgd2_grid,
         sgd_grid,
         sp_grid,
         adam_grid,
         ewc_grid,
         si_grid,
]

learners = [
    FirstOrderNonprotectingGlobalUPGDLearner(),
    FirstOrderGlobalUPGDLearner(),
    SGDLearner(),
    ShrinkandPerturbLearner(),
    AdamLearner(),
    EWCLearner(),
    SynapticIntelligenceLearner(),
]

for learner, grid in zip(learners, grids):
    runner = Runner(RunStats, learner, grid, exp_name, learner.name)
    runner.write_cmd("generated_cmds")
    create_script_generator(f"generated_cmds/{exp_name}", exp_name)
    create_script_runner(f"generated_cmds/{exp_name}")