#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import re
import sys
import shutil
import traceback
from pathlib import Path
from setuptools import setup, find_packages

NAME = "make_colors"

def get_version():
    """
    Get the version from __version__.py file or package.
    
    The __version__.py file should contain:
    version = "2.0.0"
    """
    version = "2.0.0"  # Fallback version
    
    # Try to read from root __version__.py first
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r", encoding='utf-8') as f:
                content = f.read()
                # Use regex to find version
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except Exception as e:
        if os.getenv('TRACEBACK', '').lower() in ['1', 'true']:
            print(f"Warning: Error reading __version__.py from root: {e}")
            print(traceback.format_exc())
    
    # Try to read from make_colors/__version__.py
    try:
        version_file = Path(__file__).parent / NAME / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r", encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except Exception as e:
        if os.getenv('TRACEBACK', '').lower() in ['1', 'true']:
            print(f"Warning: Error reading __version__.py from package: {e}")
            print(traceback.format_exc())
    
    # Try to read from make_colors/__init__.py
    try:
        init_file = Path(__file__).parent / NAME / "__init__.py"
        if init_file.is_file():
            with open(init_file, "r", encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except Exception as e:
        if os.getenv('TRACEBACK', '').lower() in ['1', 'true']:
            print(f"Warning: Error reading version from __init__.py: {e}")
    
    print(f"Warning: Could not determine version, using fallback: {version}")
    return version

def get_long_description():
    """Read the README.md file for long description."""
    readme_file = Path(__file__).parent / "README.md"
    try:
        with io.open(readme_file, "rt", encoding="utf8") as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read README.md: {e}")
        return "Make command line text colored - A simple and powerful Python library for adding colors to your terminal output with cross-platform support."

def get_requirements():
    """Get requirements based on Python version."""
    requirements = []
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    # Try to read requirements.txt if it exists
    try:
        if requirements_file.is_file():
            with open(requirements_file, "r", encoding="utf-8") as f:
                requirements.extend(line.strip() for line in f if line.strip() and not line.startswith("#"))
    except Exception as e:
        print(f"Warning: Could not read requirements.txt: {e}")

    # Only add configparser for Python 2.7
    if sys.version_info < (3, 0):
        requirements.append('configparser')
    
    # argparse is built-in for Python 2.7+ and 3.2+
    if sys.version_info < (2, 7):
        requirements.append('argparse')
    
    return requirements

# Copy version file to package if it exists
try:
    version_file_in_package = os.path.join(NAME, '__version__.py')
    if os.path.exists(version_file_in_package):
        os.remove(version_file_in_package)
except Exception:
    pass

try:
    if os.path.exists('__version__.py'):
        if not os.path.exists(NAME):
            os.makedirs(NAME)
        shutil.copy2('__version__.py', NAME + '/')
except Exception:
    pass

setup(
    name="make_colors",
    version=get_version(),
    url="https://github.com/cumulus13/make_colors",
    project_urls={
        "Documentation": "https://github.com/cumulus13/make_colors",
        "Code": "https://github.com/cumulus13/make_colors",
        "Issue tracker": "https://github.com/cumulus13/make_colors/issues",
    },
    license="MIT",
    author="Hadi Cahyadi",
    author_email="cumulus13@gmail.com",
    maintainer="cumulus13",
    maintainer_email="cumulus13@gmail.com",
    description="A simple, powerful, and cross-platform Python library for adding colors, styles, and rich markup support to your terminal output. Optimized for **Windows 10+**, Linux, and macOS.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown", 
    packages=find_packages(),
    package_data={
        'make_colors': ['*.py', '*.md', '*.txt'],
    },
    include_package_data=True,
    install_requires=get_requirements(),
    python_requires=">=2.7",
    entry_points={
        'console_scripts': [
            'make_colors=make_colors.__main__:main',
        ],
    },
    keywords=['color', 'terminal', 'console', 'ansi', 'text', 'colorize', 'cli', 'markup', 'rich_markup'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Console Fonts",
        "Topic :: Terminals",
        "Topic :: Text Processing :: Markup",
    ],
)