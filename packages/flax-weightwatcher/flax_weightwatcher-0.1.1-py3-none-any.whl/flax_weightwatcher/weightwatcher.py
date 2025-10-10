import numpy as np
import pandas as pd
from typing import *
from powerlaw import Fit

from flax import nnx
from jax import Array
from jaxtyping import *
import jax.numpy as jnp


class FlaxWeightWatcher():
    def __init__(self, model: nnx.Module, details_format: str = "df"):
        self.model = model
        assert details_format in ["df", "dict"], "Unsupported `details_format` provided."
        self.details_format = details_format
        self.supported_layers = ["linear", "lineargeneral"]


    def is_supported(self, layer: nnx.Module) -> bool:
        layer_class_name = type(layer).__name__.lower()
        if layer_class_name in self.supported_layers:
            return True
        return False


    def compute_esd(self, X: Float[Array, "n n"]) -> Float[Array, "n"]:
        if X.shape[0] != X.shape[1]:
            eigenvalues = jnp.linalg.svd(X, compute_uv=False)
        else:
            eigenvalues = jnp.linalg.eigvalsh(X @ X.T)
            eigenvalues = jnp.sqrt(jnp.abs(eigenvalues))
        
        return jnp.sort(eigenvalues)[::-1]


    def fit_powerlaw_for_matrix(self, matrix: Float[Array, "m n"]) -> List:
        corr = matrix.T @ matrix
        evs = self.compute_esd(corr)
        eigenvalues_np = np.array(evs)

        fit = Fit(eigenvalues_np, discrete=False, verbose=False)
        eigenvalues_used = eigenvalues_np[eigenvalues_np >= fit.xmin]
        
        if fit.xmax:
            eigenvalues_used = eigenvalues_used[eigenvalues_used <= fit.xmax]
        
        alpha = getattr(fit, 'alpha')
        return [alpha, eigenvalues_used, eigenvalues_np]
    

    def get_weight_from_path(self, path: str) -> Union[nnx.Module, Float[Array, "m n"]]:
        N = len(path)
        obj = self.model

        for i in range(N):
            if isinstance(path[i], int):
                obj = obj[path[i]]
            else:
                obj = getattr(obj, path[i])

        if hasattr(obj, "kernel"): # should be the case
            return obj.kernel.value
        return obj


    def analyze(self) -> Union[Dict, pd.DataFrame]:
        data = {
            "layer_index": [], 
            "layer_name": [], 
            "weight_shape": [], 
            "alpha": [], 
            "num_eigenvals_fit": [],
            "num_eigenvals": [],
            "stable_ranks": [],
            "effective_ranks": [],
            "ranks": []
        }

        for idx, (path, module) in enumerate(nnx.iter_graph(self.model)):
            # my work mainly tests uses HTSR on transformers, so linear layers supported currently
            # if isinstance(module, nnx.Linear) or isinstance(module, nnx.LinearGeneral):
            
            if self.is_supported(module): 
                data["layer_index"].append(idx)
                layer_path = ".".join([str(item) for item in path])
                data["layer_name"].append(layer_path)

                weight = self.get_weight_from_path(path)

                if len(weight.shape) > 2:
                    N = weight.shape[0]
                    weight = weight.reshape((N, -1))
                
                weight_shape = ",".join([str(item) for item in weight.shape])
                data["weight_shape"].append(weight_shape)
                data["ranks"].append(np.linalg.matrix_rank(weight).item())

                stable_rank = jnp.linalg.norm(weight, ord='fro') / jnp.linalg.norm(weight, ord=2)
                data["stable_ranks"].append(stable_rank.item())

                [alpha, evals_eff, evals] = self.fit_powerlaw_for_matrix(weight)
                data["alpha"].append(alpha.item())
                data["num_eigenvals_fit"].append(len(evals_eff))
                data["num_eigenvals"].append(len(evals))

                p = evals / np.linalg.norm(evals, ord=1)
                entropy = -1 * (p * np.log(p)).sum()
                effective_rank = np.exp(entropy)
                data["effective_ranks"].append(effective_rank.item())

            
        if self.details_format == "df":
            data = pd.DataFrame.from_dict(data)
        return data
