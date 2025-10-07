"""
Setup script for causalmma-client SDK
"""

from setuptools import setup, find_packages

setup(
    name="causalmma-client",
    version="1.0.0",
    description="Local execution SDK for CausalMMA with centralized control",
    author="Durai Rajamanickam",
    author_email="durai@infinidatum.net",
    url="https://github.com/rdmurugan/causalmma-sdk",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "requests>=2.26.0",
        "pyjwt>=2.0.0",
        "statistical-causal-inference>=4.4.0",  # Core causal inference algorithms
    ],
    extras_require={
        "full": [
            "scikit-learn>=1.0.0",
            "scipy>=1.7.0",
            "networkx>=2.6.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0",
            "mypy>=0.910",
        ]
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
