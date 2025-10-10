from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ashclip",  # The name of your package on PyPI
    version="1.0.0",  # The initial version
    author="Heisenberg",  # <-- EDIT THIS
    author_email="heisenberg@example.com",  # <-- EDIT THIS
    description="A discreet CLI tool to fetch file content from Nexus Hub to the clipboard via a hotkey.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),  # Automatically find the 'ashclip' package folder
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[  # List of dependencies
        "keyboard",
        "pyperclip",
        "requests",
    ],
    entry_points={  # This is the magic part that makes 'ashclip' a command
        'console_scripts': [
            'ashclip=ashclip.main:main',
        ],
    },
)