"""
CLWE - Color Lattice Learning With Errors
Post-Quantum Cryptography Library v1.0.4

CLWE is a revolutionary post-quantum cryptographic system that combines
lattice-based cryptography with color transformations for unparalleled
security, performance, and features.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
def read_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    requirements = []
    try:
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        # Default requirements if file doesn't exist
        requirements = [
            'numpy>=1.21.0',
            'cryptography>=3.4.0',
            'Pillow>=8.0.0',
        ]
    return requirements

setup(
    name="clwe",
    version="1.0.4",
    author="Cryptopix Development Team",
    author_email="support@cryptopix.in",
    description="CLWE - Revolutionary Post-Quantum Cryptography with Color Transformations",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/cryptopix-dev/clwe",
    project_urls={
        "Homepage": "https://www.cryptopix.in",
        "Documentation": "https://github.com/cryptopix-dev/clwe",
        "Source": "https://github.com/cryptopix-dev/clwe",
        "Tracker": "https://github.com/cryptopix-dev/clwe/issues",
    },
    packages=find_packages(where="Code"),
    package_dir={"": "Code"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="cryptography post-quantum lattice-based color-transformation security encryption",
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.800",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
        "gpu": [
            "cupy>=9.0.0",
        ],
        "full": [
            "numpy>=1.21.0",
            "cryptography>=3.4.0",
            "Pillow>=8.0.0",
            "cupy>=9.0.0",
            "scipy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clwe=clwe.cli:main",
            "clwe-benchmark=clwe.cli:benchmark",
            "clwe-test=clwe.cli:test",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    test_suite="tests",
    tests_require=[
        "pytest>=6.0.0",
        "pytest-cov>=2.0.0",
    ],
)