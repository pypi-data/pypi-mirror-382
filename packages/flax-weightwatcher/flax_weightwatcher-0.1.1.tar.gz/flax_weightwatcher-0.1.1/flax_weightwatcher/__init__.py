from flax import nnx
from .weightwatcher import FlaxWeightWatcher


def run_simple_test():
    model = nnx.Sequential(*[nnx.Linear(28*28, 128, rngs=nnx.Rngs(0)), nnx.Linear(128, 10, rngs=nnx.Rngs(0))])
    ww = FlaxWeightWatcher(model=model, details_format="df")
    d = ww.analyze()
    print(d.head())
