"""
Utility functions for working with Kubeflow Pipelines
"""

from typing import Any, Dict, List

try:
    from kfp.dsl import component
except ImportError as e:
    raise ImportError(
        "Kubeflow Pipelines SDK is not installed. Please install it using pip install kiwi-booster[kfp]."
    ) from e


def get_requirements(req_path: str) -> List[str]:
    """
    Get a list of requirements from requirements.txt

    Returns:
        requirements (list): List of requirements
    """
    # Get the requirements file and read it line by line, save this into a list
    with open(req_path, "r") as file:
        content = file.read()

    lines = content.splitlines()
    requirements = [line for line in lines if line and not line.startswith("#")]

    return requirements


def set_resource_constrains(kfp_op: component, config: Dict[str, Any]) -> component:
    """Set the resource constrains for a kfp operation
    Args:
        kfp_op: The kfp operation to set the resource constrains for
        config: The config dictionary. It should have "cpu" and "ram" keys.
            Optionally, it can have "gpu_type" and "gpu_limit" keys.
    Returns:
        The kfp operation with the resource constrains set
    """
    kfp_op = kfp_op.set_memory_limit(config["ram"]).set_cpu_limit(config["cpu"])
    if "gpu_type" in config:
        kfp_op = kfp_op.set_accelerator_limit(
            config.get("gpu_limit", 1)
        ).set_accelerator_type(config["gpu_type"])
    return kfp_op
