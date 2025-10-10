"""
Cirquit - Quantum Computing Platform
Setup configuration for PyPI distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    # Basic metadata
    name="cirquit",
    version="1.0.0",
    description="Quantum circuits, simplified. A developer-first quantum computing platform.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Author information
    author="Cirquit Team",
    author_email="hello@cirquit.io",
    url="https://cirquit.io",

    # Project URLs
    project_urls={
        "Homepage": "https://cirquit.io",
        "Documentation": "https://docs.cirquit.io",
        "Source Code": "https://github.com/cirquit/cirquit",
        "Bug Tracker": "https://github.com/cirquit/cirquit/issues",
        "Discord": "https://discord.gg/cirquit",
        "Twitter": "https://twitter.com/cirquit_io",
    },

    # License
    license="MIT",

    # Package discovery
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),

    # Python version requirement
    python_requires=">=3.11",

    # Dependencies
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
    ],

    # Optional dependencies
    extras_require={
        # Development tools
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "pylint>=2.17.0",
            "flake8>=6.1.0",
            "pre-commit>=3.3.0",
        ],

        # Documentation
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
            "myst-parser>=2.0.0",
        ],

        # Visualization
        "viz": [
            "matplotlib>=3.7.0",
            "plotly>=5.15.0",
        ],

        # Performance
        "performance": [
            "cupy-cuda11x>=12.0.0",  # GPU acceleration (CUDA 11.x)
            "numba>=0.57.0",          # JIT compilation
        ],

        # Cloud features
        "cloud": [
            "requests>=2.31.0",
            "websockets>=11.0.0",
            "python-dotenv>=1.0.0",
        ],

        # Full installation
        "all": [
            "numpy>=1.24.0",
            "scipy>=1.10.0",
            "matplotlib>=3.7.0",
            "plotly>=5.15.0",
            "requests>=2.31.0",
            "websockets>=11.0.0",
            "python-dotenv>=1.0.0",
        ],
    },

    # Entry points (CLI commands)
    entry_points={
        "console_scripts": [
            "cirquit=cirquit.cli:main",
        ],
    },

    # Package data
    package_data={
        "cirquit": [
            "py.typed",  # PEP 561 - indicate package supports type checking
            "data/*.json",
        ],
    },

    # Classifiers for PyPI
    classifiers=[
        # Development status
        "Development Status :: 4 - Beta",

        # Intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",

        # Topics
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules",

        # License
        "License :: OSI Approved :: MIT License",

        # Python versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",

        # Operating systems
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",

        # Typing
        "Typing :: Typed",
    ],

    # Keywords for PyPI search
    keywords=[
        "quantum",
        "quantum-computing",
        "quantum-circuits",
        "qubits",
        "quantum-algorithms",
        "quantum-simulation",
        "quantum-programming",
        "qaas",
        "quantum-cloud",
        "quantum-sdk",
    ],

    # Additional metadata
    platforms=["any"],
    zip_safe=False,  # Don't install as a zip file
    include_package_data=True,
)

# Post-installation message
print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🎉  Cirquit installed successfully!                        ║
║                                                               ║
║   Get started:                                                ║
║   ------------                                                ║
║                                                               ║
║   >>> from cirquit import QuantumCircuit                      ║
║   >>> circuit = QuantumCircuit(2)                             ║
║   >>> circuit.h(0).cnot(0, 1).measure_all()                   ║
║   >>> result = circuit.run(shots=1000)                        ║
║                                                               ║
║   Documentation: https://docs.cirquit.io                      ║
║   Examples:      https://github.com/cirquit/cirquit/examples  ║
║   Discord:       https://discord.gg/cirquit                   ║
║                                                               ║
║   Happy quantum computing! ⚛️                                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")