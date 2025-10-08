#!/usr/bin/env python

from os import path, walk

import sys
from setuptools import setup, find_packages

NAME = "Orange3-MLflow-Export"

VERSION = "0.6.0"

AUTHOR = "NIRLAB AG"
AUTHOR_EMAIL = 'dev@nirlab.com'

URL = 'https://github.com/NIRLab-com/mlflow-model-widget'
DESCRIPTION = "Export Orange3 models with preprocessing pipelines to MLflow format for production deployment."
LONG_DESCRIPTION = open(path.join(path.dirname(__file__), 'README.pypi'),
                        'r', encoding='utf-8').read()

LICENSE = "GPL-3.0-only"

KEYWORDS = [
    # [PyPi](https://pypi.python.org) packages with keyword "orange3 add-on"
    # can be installed using the Orange Add-on Manager
    'orange3 add-on',
    'mlflow',
    'machine learning',
    'model export',
    'data science',
    'deployment',
    'preprocessing',
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Plugins',
    'Programming Language :: Python',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
]

PYTHON_REQUIRES = '>=3.8'

PACKAGES = find_packages()

PACKAGE_DATA = {
    'orangecontrib.mlflowexport.widgets': ['icons/*'],
}

DATA_FILES = [
    # Data files that will be installed outside site-packages folder
]

INSTALL_REQUIRES = [
    'Orange3',
    'mlflow',
    'cloudpickle',
    'scikit-learn',
]

ENTRY_POINTS = {
    # Entry points that marks this package as an orange add-on. If set, addon will
    # be shown in the add-ons manager even if not published on PyPi.
    'orange3.addon': (
        'mlflowexport = orangecontrib.mlflowexport',
    ),

    # Entry point used to specify packages containing widgets.
    'orange.widgets': (
        # Syntax: category name = path.to.package.containing.widgets
        # Widget category specification can be seen in
        #    orangecontrib/example/widgets/__init__.py
        'MLFlow = orangecontrib.mlflowexport.widgets',
    ),
}



def include_documentation(local_dir, install_dir):
    global DATA_FILES
    if 'bdist_wheel' in sys.argv and not path.exists(local_dir):
        print("Directory '{}' does not exist. "
              "Please build documentation before running bdist_wheel."
              .format(path.abspath(local_dir)))
        sys.exit(0)

    doc_files = []
    for dirpath, dirs, files in walk(local_dir):
        doc_files.append((dirpath.replace(local_dir, install_dir),
                          [path.join(dirpath, f) for f in files]))
    DATA_FILES.extend(doc_files)


if __name__ == '__main__':
    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        license=LICENSE,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        install_requires=INSTALL_REQUIRES,
        entry_points=ENTRY_POINTS,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        python_requires=PYTHON_REQUIRES,
        zip_safe=False,
        project_urls={
            'Bug Reports': 'https://github.com/NIRLab-com/mlflow-model-widget/issues',
            'Source': 'https://github.com/NIRLab-com/mlflow-model-widget',
            'Documentation': 'https://github.com/NIRLab-com/mlflow-model-widget/blob/main/README_MLFLOW_WIDGET.md',
        },
    )
