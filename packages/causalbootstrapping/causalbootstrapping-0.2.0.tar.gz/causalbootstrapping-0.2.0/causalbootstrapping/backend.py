from causalbootstrapping.expr import Expr
import numpy as np
import inspect
from causalbootstrapping.cb_type_defs import (
    DataDict,
    IntvDict,
    DistFunc,
    DistMap,
    WeightFunc,
    IdExpr
)
from typing import Dict, Sequence, Tuple, Union, Optional, Literal

def weight_compute(
    w_func: WeightFunc,
    data: DataDict,
    intv_dict: IntvDict,
) -> np.ndarray:
    """
    Compute causal bootstrapping weights for the given weight function and input observational data.
    
    Parameters:
        w_func (function): The causal bootstrapping weight function to be used.
        data (dict): A dictionary containing variable names as keys and their corresponding ndarray as values.
        intv_dict (dict): key: str, value: float/list(len: M)/ndarray(M,), a dictionary containing the intervention variable names and their corresponding values.
    Returns:
        numpy.ndarray: An array containing the computed causal bootstrapping weights for each data point.
    """
    N = data[list(data.keys())[0]].shape[0]
    intv_dict_expand = {}
    for intv_var in intv_dict.keys():
        if np.isscalar(intv_dict[intv_var]):
            intv_dict[intv_var] = [intv_dict[intv_var]]
        if isinstance(intv_dict[intv_var], np.ndarray):
            if intv_dict[intv_var].ndim >= 2:
                raise ValueError("intv_dict value should be 1-dimensional if numpy.ndarray.")
            intv_dict[intv_var] = intv_dict[intv_var].flatten().tolist()

        intv_dict_expand[intv_var] = np.array([intv_dict[intv_var] for i in range(N)]).reshape(N, len(intv_dict[intv_var]))
    data_for_weight_compute = {**data, **intv_dict_expand}
    weights = w_func(**data_for_weight_compute).reshape(-1)
    return weights

def build_weight_function(
    intv_prob: IdExpr,
    dist_map: DistMap,
    N: int,
    cause_intv_name_map: Dict[str, str],
    kernel: Optional[DistFunc] = None,
) -> Tuple[WeightFunc, Expr]:
    """
    Generate the causal bootstrapping weight function using the identified interventional probability and 
    corresponding distribution functions.

    Parameters:
        intv_prob (grapl.expr object): The identified interventional probability expression.
        dist_map (dict): A dictionary mapping tuples of variable combinations to their corresponding distribution functions.
        cause_intv_name_map (dict): A dictionary mapping cause variable names to their corresponding intervention variable names.
        N (int): The number of data points in the dataset.
        kernel (function, optional): The kernel function to be used in the weight computation. Defaults to None.

    Returns:
        function: The corresponding causal bootstrapping weight function.
    """

    def divide_functions(**funcs):
        def division(**kwargs):
            kwargs = {key.replace("'","_prime"): value for key, value in kwargs.items()}
            result = 1
            for nom_i in w_nom_mapped:
                func_key = ",".join(nom_i)
                param_names = inspect.signature(funcs[func_key]).parameters
                param = {key : kwargs[key] if kwargs[key].shape[0] != 1 else kwargs[key][0] for key in param_names}
                result *= funcs[func_key](**param).reshape(-1)
            for denom_i in w_denom_mapped:
                func_key = ",".join(denom_i)
                param_names = inspect.signature(funcs[func_key]).parameters
                param = {key : kwargs[key] if kwargs[key].shape[0] != 1 else kwargs[key][0] for key in param_names}
                result /= funcs[func_key](**param).reshape(-1)
            if cause_kernel_flag:
                param_names = inspect.signature(funcs["kernel"]).parameters
                param = {key : kwargs[key] for key in param_names}
                result *= funcs["kernel"](**param).reshape(-1)
            result *= (lambda n: 1/n)(N)
            return result
        return division    

    dist_map_sep = ","
    dist_map_sorted = {}
    
    for key ,value in dist_map.items():
        sorted_key = dist_map_sep.join(sorted(key.split(","))).replace(" ","")
        dist_map_sorted[sorted_key] = value
    
    cause_var = intv_prob.lhs.dov.copy()
    eff_var = intv_prob.lhs.num[0].copy()
    w_denom = intv_prob.rhs.den.copy()
    w_denom = [sorted(w_denom[i]) for i in range(len(w_denom))]
    w_nom = intv_prob.rhs.num.copy()
    w_nom = [sorted(w_nom[i]) for i in range(len(w_nom))]
    epsilo = intv_prob.rhs.mrg.copy()
    pa_var = sorted(epsilo.union(eff_var).union(cause_var))
    if pa_var in w_nom:
        w_nom.remove(pa_var)
        cause_kernel_flag = True
        if kernel is None:
            raise ValueError("Kernel function is required but not provided. E.g., kernel = lambda Y, intv_Y: np.equal(Y, intv_Y)")
        kernel_func = {"kernel": kernel}
        funcs = {**dist_map_sorted, **kernel_func}
    else:
        pa_var = set(pa_var)
        pa_var = pa_var.difference(cause_var)
        pa_var = sorted(pa_var)
        w_nom.remove(list(pa_var))
        cause_kernel_flag = False
        funcs = dist_map_sorted

    w_nom_mapped = [sorted([cause_intv_name_map.get(name, name) for name in w_nom_i]) for w_nom_i in w_nom]
    w_denom_mapped = [sorted([cause_intv_name_map.get(name, name) for name in w_denom_i]) for w_denom_i in w_denom]

    weight_func = divide_functions(**funcs)
    weight_expr = Expr(w_nom = w_nom, w_denom = w_denom, cause_var = list(cause_var)[0], kernel_flag = cause_kernel_flag)

    return weight_func, weight_expr

def gumbel_max(weights: np.ndarray) -> int:
    """
    Apply the Gumbel-max trick to sample indices based on the provided weights.
    
    Parameters:
        weights (numpy.ndarray): The weights for sampling.
    
    Returns:
        int: The index of the sampled weight.
    """
    gumbel_noise = -np.log(-np.log(np.random.rand(*weights.shape)))
    return np.argmax(np.log(weights) + gumbel_noise)

def bootstrapper(
    data: DataDict,
    w_func: WeightFunc,
    intv_var_name_in_data: Union[str, Sequence[str]],
    intv_var_name: Union[str, Sequence[str]],
    mode: Literal["fast", "robust"] = "fast",
    random_state: Optional[int] = None,
) -> Tuple[Dict[str, np.ndarray], np.ndarray]:
    """
    Perform causal bootstrapping on the input observational data using the provided weight function and given observations.
    
    Parameters:
        data (dict): A dictionary containing variable names as keys and their corresponding data arrays as values.
        w_func (function): The causal bootstrapping weight function.
        intv_var_name_in_data (str or list of str): A list of strings representing the variable names of observational data used as the interventional values.
        intv_var_name (str or list of str): The variable name for the interventional variable.
        mode (str, optional): The mode for bootstrapping. Options: 'fast' or 'robust'. Defaults to 'fast'.
        random_state (int, optional): The random state for the bootstrapping. Defaults to None.
    
    Returns:
        bootstrap_data (dict): A dictionary containing variable names as keys and their corresponding bootstrapped data arrays as values.
        weights (numpy.ndarray): An array containing the computed causal bootstrapping weights for each data point.
    """
    if isinstance(intv_var_name_in_data, str):
        intv_var_name_in_data = [intv_var_name_in_data]
    if isinstance(intv_var_name, str):
        intv_var_name = [intv_var_name]
    rng = np.random.RandomState(random_state)
    
    var_names = list(data.keys())
    N = data[var_names[0]].shape[0]

    stack_intv_data = np.hstack([data[key] if data[key].ndim == 2 else data[key].reshape(-1,1) for key in intv_var_name_in_data])
    intv_var_values_unique, counts = np.unique(stack_intv_data, axis=0, return_counts=True)
    intv_dims = [data[name].shape[1] if data[name].ndim == 2 else 1
             for name in intv_var_name_in_data]
    intv_dim_offsets = np.cumsum([0] + intv_dims)
    intv_var_slices = {
        name: slice(intv_dim_offsets[i], intv_dim_offsets[i+1])
        for i, name in enumerate(intv_var_name)
    }    
    
    causal_weights = np.zeros((N, intv_var_values_unique.shape[0]))

    bootstrap_data = {}
    for var in var_names:
        bootstrap_data[var] = np.zeros((N, data[var].shape[1]))
    for i, var in enumerate(intv_var_name):
        bootstrap_data[var] = np.zeros((N, intv_dims[i]))

    ind_pos = 0
    for i, (intv_, n) in enumerate(zip(intv_var_values_unique, counts)):
        intv_i_dict = {name: intv_[intv_var_slices[name]] for name in intv_var_name}
        weight_intv = weight_compute(w_func, data, intv_i_dict)
        causal_weights[:, i] = weight_intv
        if mode == "fast":
            sample_indices = rng.choice(range(N), p=weight_intv/np.sum(weight_intv), size=n, replace=True)
        elif mode == "robust":
            sample_indices = [gumbel_max(weight_intv) for _ in range(n)]
        else:
            raise ValueError("Invalid mode. Choose either 'fast' or 'robust'.")
        
        for var in var_names:
            bootstrap_data[var][ind_pos:ind_pos+n] = data[var][sample_indices]
        for var in intv_var_name:
            bootstrap_data[var][ind_pos:ind_pos+n] = np.array([intv_[intv_var_slices[var]] for _ in range(n)])
        ind_pos += n
        
    return bootstrap_data, causal_weights

def simu_bootstrapper(
    data: DataDict,
    w_func: WeightFunc,
    intv_dict: IntvDict,
    n_sample: int,
    mode: Literal["fast", "robust"] = "fast",
    random_state: Optional[int] = None,
) -> Tuple[Dict[str, np.ndarray], np.ndarray]:
    """
    Perform simulational causal bootstrapping on the input observational data using the provided weight function and 
    designated intervention values.

    Parameters:
        data (dict): A dictionary containing variable names as keys and their corresponding data arrays as values.
        w_func (function): The causal bootstrapping weight function.
        intv_dict (dict): key: str, value: int/list(len: M)/ndarray(M,), a dictionary containing the intervention variable names and their corresponding values.
        n_sample (int): The number of samples to be generated through bootstrapping.
        mode (str, optional): The mode for bootstrapping. Options: 'fast' or 'robust'. Defaults to 'fast'.
        random_state (int, optional): The random state for the bootstrapping. Defaults to None.

    Returns:
        bootstrap_data (dict): A dictionary containing variable names as keys and their corresponding bootstrapped data arrays as values.
        weights (numpy.ndarray): An array containing the computed causal bootstrapping weights for each data point.
    """
    rng = np.random.RandomState(random_state)
    
    causal_weights = weight_compute(w_func, data, intv_dict)
    
    var_names = list(data.keys())
    N = data[var_names[0]].shape[0]
    bootstrap_data = {}
    if mode == "fast":
        sample_indices = rng.choice(range(N), p=causal_weights/np.sum(causal_weights), size=n_sample, replace=True)
    elif mode == "robust":
        sample_indices = [gumbel_max(causal_weights) for _ in range(n_sample)]
    else:
        raise ValueError("Invalid mode. Choose either 'fast' or 'robust'.")
    
    for var in var_names:
        bootstrap_data[var.replace("'","")] = data[var][sample_indices]
    for intv_var in intv_dict.keys():
        if isinstance(intv_dict[intv_var], int):
            intv_dict[intv_var] = [intv_dict[intv_var]]
        if isinstance(intv_dict[intv_var], np.ndarray):
            if intv_dict[intv_var].ndim >= 2:
                raise ValueError("intv_dict value should be 1-dimensional if numpy.ndarray.")
            intv_dict[intv_var] = intv_dict[intv_var].flatten().tolist()
        bootstrap_data[intv_var] = np.array([intv_dict[intv_var] for _ in range(n_sample)]).reshape(n_sample, len(intv_dict[intv_var]))

    return bootstrap_data, causal_weights