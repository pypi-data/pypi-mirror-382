import re
from setuptools import setup, Extension, find_packages
import os
import importlib.util


def parse_requirements(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line and not line.startswith("#")]


def discover_package_data():
    """
    自动发现子模块的package_data配置
    扫描所有子模块，查找package_config.py文件
    """
    package_data = {}
    # 扫描src/onescience下的所有子模块
    src_dir = os.path.join(os.path.dirname(__file__), "src", "onescience")
    
    for root, dirs, files in os.walk(src_dir):
        if "package_config.py" in files:
            try:
                # 构造模块路径
                rel_path = os.path.relpath(root, src_dir)
                module_parts = ["onescience"] + rel_path.split(os.sep) if rel_path != "." else ["onescience"]
                module_name = ".".join(module_parts)
                
                # 加载package_config.py
                config_path = os.path.join(root, "package_config.py")
                spec = importlib.util.spec_from_file_location(f"{module_name}.package_config", config_path)
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)
                
                # 获取package_data配置
                if hasattr(config_module, 'get_package_data'):
                    submodule_data = config_module.get_package_data()
                    package_data.update(submodule_data)
                    print(f"✅ Discovered package config from: {module_name}")
                    
            except Exception as e:
                print(f"⚠️  Failed to load package config from {root}: {e}")
    
    return package_data


one_deps = parse_requirements("requirements.txt") # ['numpy>=1.25.0,<2.0.0', 'tqdm>=4.65.0,<5.0.0', ...]

# {"numpy": "numpy>=1.25.0,<2.0.0",...}
deps = {re.split(r"[=<>~!]", dep)[0]: dep for dep in one_deps}  # {'numpy': 'numpy>=1.24.0,<2.0.0', ...}

basic_requires = [
    "numpy",
    "tqdm",
    "timm",
    "wandb",
    "hydra-core",
    "treelib",
    "hydra-core",
    "termcolor",
    "mlflow",
    "pytest",
    "pyyaml",
    "h5py",
    "ruamel.yaml",
    "scikit-learn",
    "scikit-image",
    "vtk",
    "pyvista",
    "einops",
    "onnx",
    "pandas",
    "omegaconf",
    "mpi4py",
    "torchdata",
    "pybind11",
    "torchmetrics",
    "torch-runstats",  # 性能分析
    "torch-ema",  #
    "opt_einsum",
    "prettytable",
    "matplotlib",
    # "torch_geometric",
    # "torch_scatter",
    # "torch_sparse",
    # "torch_cluster",
    # "torch_spline_conv",
    "megatron-core",
]


earth_requires = [
    "pytz",
    "xarray",
    "zarr",
    "s3fs",
    "netcdf4",
    "cftime",
    "dask",
    "opencv-python",
]


cfd_requires = [
    "shapely",
    "seaborn",
    "deepxde",
    "gpytorch",
]

quantum_requires = [
    "openfermion",
    "pymatgen",
]


chemistry_requires = [
    "e3nn",
    "ase",
    "xtb",
    "rdkit",
    "matscipy",
    "python-hostlist",
    "configargparse",
    "lmdb",
    "orjson",
    "pymatgen",
]

biology_requires = [
    "rdkit",
    "matplotlib",
    "contextlib2",
    "ml-collections",
    "dm-tree",
    "dm-haiku",
    "diffrax",
    "biopandas",
    "biopython",
    "pyrsistent",
    "chex",
    "flax",
    "fiddle",
    "lightning",
    "sentencepiece",
    "datasets",
    "braceexpand",
    "webdataset",
    "nemo_run",
    "tiktoken",
    "s3fs",
    "zarr",
    "zstandard",
    #"bionemo-noodles",
    "psutil",
    "transformers",
    "ftfy",
]

dev_requires = [
    "setuptools",
]


def parse_requirements_file(filename):
    """Parse a requirements file into a list of dependencies."""
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def resolve(requires, deps_dict):
    """Convert a list of dependencies to a set of requirements."""
    return [deps_dict[require] for require in requires] # select some values in deps_dict

extras = {}

install_requires = resolve(basic_requires, deps)
extras["earth"] = resolve(earth_requires, deps)
extras["bio"] = resolve(biology_requires, deps)
extras["cfd"] = resolve(cfd_requires, deps)
extras["chem"] = resolve(chemistry_requires, deps)
extras["quantum"] = resolve(quantum_requires, deps)
extras["dev"] = resolve(dev_requires, deps)
extras["all"] = one_deps

setup(
    name="onescience",
    version="0.2.0",
    author="sugon-ai4s",
    author_email="ai4s@sugon.com",
    description="First release",
    long_description="OneScience is a scientific computing toolkit built on an advanced deep learning framework",
    url="https://github.com/hpccube/OneScience",
    package_dir={"": "src"},
    packages=find_packages("src"),
    extras_require=extras,
    include_package_data=True,
    install_requires=list(install_requires),
    python_requires=">=3.10.0",
    zip_safe=False,
    license="Apache License 2.0",      # 指定 Apache 2.0
    license_files=("LICENSE",),
    # 自动发现所有子模块的package_data配置
    package_data=discover_package_data(),
)
