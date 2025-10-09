# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src']

package_data = \
{'': ['*']}

install_requires = \
['fortitudo-tech>=1.1.11,<2.0.0', 'notebook']

setup_kwargs = {
    'name': 'cvar-optimization-benchmarks',
    'version': '0.1',
    'description': 'Conditional Value-at-Risk (CVaR) portfolio optimization benchmark problems in Python.',
    'long_description': "# CVaR optimization benchmark problems\nThis repository contains Conditional Value-at-Risk (CVaR) portfolio optimization benchmark problems for fully general Monte Carlo distributions and derivatives portfolios.\n\nThe starting point is the [next-generation investment framework's market representation](https://youtu.be/4ESigySdGf8?si=yWYuP9te1K1RBU7j&t=46) given by the matrix $R\\in \\mathbb{R}^{S\\times I}$ and associated joint scenario probability vectors $p,q\\in \\mathbb{R}^{S}$.\n\nThe [CVaROptBenchmarks notebook](https://github.com/fortitudo-tech/cvar-optimization-benchmarks/blob/main/CVaROptBenchmarks.ipynb) illustrates how the benchmark problems can be solved using Fortitudo Technologies' Investment Analysis module.\n\nThe [OptimizationExample notebook](https://github.com/fortitudo-tech/cvar-optimization-benchmarks/blob/main/OptimizationExample.ipynb) shows how you can replicate the results using the [fortitudo.tech open-source Python package](https://github.com/fortitudo-tech/fortitudo.tech) for the efficient frontier optimizations of long-only cash portfolios, which are the easiest problems to solve.\n\nYou can read much more about the next-generation investment framework in the [Portfolio Construction and Risk Management book](https://antonvorobets.substack.com/p/pcrm-book).",
    'author': 'Fortitudo Technologies',
    'author_email': 'software@fortitudo.tech',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://fortitudo.tech',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.14',
}


setup(**setup_kwargs)
