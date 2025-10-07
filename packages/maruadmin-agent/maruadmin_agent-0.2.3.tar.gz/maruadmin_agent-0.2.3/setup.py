"""
Setup script for MaruAdmin Agent
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = f.read().splitlines()
else:
    requirements = [
        "paramiko>=3.0.0",
        "requests>=2.28.0",
        "psutil>=5.9.0",
        "docker>=6.0.0",
    ]

setup(
    name="maruadmin-agent",
    version="0.2.3",
    description="MaruAdmin Remote Server Management Agent",
    author="MaruAdmin Team",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "maruadmin-agent=maruadmin_agent.main:main",
            "maruadmin-agent-cmd=maruadmin_agent.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)