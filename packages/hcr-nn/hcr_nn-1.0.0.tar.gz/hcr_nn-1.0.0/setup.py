from setuptools import setup, find_packages

setup(
    name='hcr_nn',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.26.4',
        'matplotlib>=3.10.1',
        'scipy>=1.13.1',
        'torch>=2.7.0',
    ],
    entry_points={
        "console_scripts": [
            "hcr_nn_info = hcr_nn:layers.hcr_nn_info",
        ],
    },
)
