from setuptools import setup, find_packages


with open("Readme.md", "r") as f:
    long_description = f.read()


setup(
    name="optimx",
    version="0.0.6",
    description="An optimization package for solving classic problems like TSP using various algorithms",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/okanyenigun/optimx",
    author="Okan Yenigün",
    author_email="okanyenigun@gmail.com",
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Documentation',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        'numpy>=1.17.4',
        'matplotlib>=3.1.2',
    ],
    extras_require={
        'dev': ['twine==5.1.1'],
        'test': ['pytest==8.2.2']
    },
    python_requires='>=3.7',
)
