# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crispr_millipede_helper',
 'crispr_millipede_helper.models',
 'crispr_millipede_helper.pipeline']

package_data = \
{'': ['*']}

install_requires = \
['PyMuPDF==1.24.7',
 'biopython>=1.81,<2.0',
 'google-cloud-storage==3.1.0',
 'matplotlib>=3.7.1,<4.0.0',
 'numpy==1.24.4',
 'pandarallel>=1.6.4,<2.0.0',
 'pandas>=1.5.3,<2.0.0',
 'scipy>=1.10.1,<2.0.0',
 'typeguard>=3.0.2,<4.0.0']

setup_kwargs = {
    'name': 'crispr-millipede-helper',
    'version': '0.1.18',
    'description': '',
    'long_description': '',
    'author': 'Basheer Becerra',
    'author_email': 'bbecerr@outlook.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
