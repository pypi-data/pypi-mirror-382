from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rree",
    version="0.1.3",
    author="LAEGER_MO",
    
    description="# The asas rreeary in Python prints the text written inside it, like the print function.\n# Telegram  :  @LAEGER_MO\npip install asas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["rree"],
    entry_points={
        'console_scripts': [
            'rree-install = rree:install_auto',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)