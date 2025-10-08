"""
Setup script for Agentic AI Device Attributes Analysis Demo
"""
from setuptools import setup, find_packages
import os

# Read the contents of README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name="agentic-ai-device-analysis",
    version="1.0.1",
    author="Device Analysis Team",
    author_email="team@deviceanalysis.com",
    description="Agentic AI based Device Attributes Analysis Demo for fraud prevention and device behavior analysis",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/deviceanalysis/agentic-ai-device-analysis",
    project_urls={
        "Bug Tracker": "https://github.com/deviceanalysis/agentic-ai-device-analysis/issues",
        "Documentation": "https://github.com/deviceanalysis/agentic-ai-device-analysis/wiki",
        "Source Code": "https://github.com/deviceanalysis/agentic-ai-device-analysis",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    keywords="agentic-ai, device-analysis, fraud-prevention, behavior-analysis, security, ai-demo",
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.12.0",
            "pytest-mock>=3.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentic-demo=agentic_ai_demo.server:main",
            "device-analysis-demo=agentic_ai_demo.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "agentic_ai_demo": ["templates/*.html", "static/*"],
    },
    zip_safe=False,
)