# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.project_tpls v0.3.58
""" setup of ae namespace module portion dev_ops: project development variables and helpers. """
# noinspection PyUnresolvedReferences
import sys
print(f"SetUp {__name__=} {sys.executable=} {sys.argv=} {sys.path=}")

# noinspection PyUnresolvedReferences
import setuptools

setup_kwargs = {
    'author': 'AndiEcker',
    'author_email': 'aecker2@gmail.com',
    'classifiers': [       'Development Status :: 3 - Alpha', 'Natural Language :: English', 'Operating System :: OS Independent',
        'Programming Language :: Python', 'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9', 'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed'],
    'description': 'ae namespace module portion dev_ops: project development variables and helpers',
    'extras_require': {       'dev': [       'aedev_project_tpls', 'ae_ae', 'anybadge', 'coverage-badge', 'aedev_project_manager', 'flake8',
                       'mypy', 'pylint', 'pytest', 'pytest-cov', 'pytest-django', 'typing', 'types-setuptools'],
        'docs': [],
        'tests': [       'anybadge', 'coverage-badge', 'aedev_project_manager', 'flake8', 'mypy', 'pylint', 'pytest',
                         'pytest-cov', 'pytest-django', 'typing', 'types-setuptools']},
    'install_requires': ['packaging', 'setuptools', 'ae_base', 'ae_paths', 'ae_shell', 'ae_templates'],
    'keywords': ['configuration', 'development', 'environment', 'productivity'],
    'license': 'GPL-3.0-or-later',
    'long_description': ('<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project ae.ae v0.3.100 -->\n'
 '<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.namespace_root_tpls v0.3.21 -->\n'
 '# dev_ops 0.3.5\n'
 '\n'
 '[![GitLab develop](https://img.shields.io/gitlab/pipeline/ae-group/ae_dev_ops/develop?logo=python)](\n'
 '    https://gitlab.com/ae-group/ae_dev_ops)\n'
 '[![LatestPyPIrelease](\n'
 '    https://img.shields.io/gitlab/pipeline/ae-group/ae_dev_ops/release0.3.5?logo=python)](\n'
 '    https://gitlab.com/ae-group/ae_dev_ops/-/tree/release0.3.5)\n'
 '[![PyPIVersions](https://img.shields.io/pypi/v/ae_dev_ops)](\n'
 '    https://pypi.org/project/ae-dev-ops/#history)\n'
 '\n'
 '>ae namespace module portion dev_ops: project development variables and helpers.\n'
 '\n'
 '[![Coverage](https://ae-group.gitlab.io/ae_dev_ops/coverage.svg)](\n'
 '    https://ae-group.gitlab.io/ae_dev_ops/coverage/index.html)\n'
 '[![MyPyPrecision](https://ae-group.gitlab.io/ae_dev_ops/mypy.svg)](\n'
 '    https://ae-group.gitlab.io/ae_dev_ops/lineprecision.txt)\n'
 '[![PyLintScore](https://ae-group.gitlab.io/ae_dev_ops/pylint.svg)](\n'
 '    https://ae-group.gitlab.io/ae_dev_ops/pylint.log)\n'
 '\n'
 '[![PyPIImplementation](https://img.shields.io/pypi/implementation/ae_dev_ops)](\n'
 '    https://gitlab.com/ae-group/ae_dev_ops/)\n'
 '[![PyPIPyVersions](https://img.shields.io/pypi/pyversions/ae_dev_ops)](\n'
 '    https://gitlab.com/ae-group/ae_dev_ops/)\n'
 '[![PyPIWheel](https://img.shields.io/pypi/wheel/ae_dev_ops)](\n'
 '    https://gitlab.com/ae-group/ae_dev_ops/)\n'
 '[![PyPIFormat](https://img.shields.io/pypi/format/ae_dev_ops)](\n'
 '    https://pypi.org/project/ae-dev-ops/)\n'
 '[![PyPILicense](https://img.shields.io/pypi/l/ae_dev_ops)](\n'
 '    https://gitlab.com/ae-group/ae_dev_ops/-/blob/develop/LICENSE.md)\n'
 '[![PyPIStatus](https://img.shields.io/pypi/status/ae_dev_ops)](\n'
 '    https://libraries.io/pypi/ae-dev-ops)\n'
 '[![PyPIDownloads](https://img.shields.io/pypi/dm/ae_dev_ops)](\n'
 '    https://pypi.org/project/ae-dev-ops/#files)\n'
 '\n'
 '\n'
 '## installation\n'
 '\n'
 '\n'
 'execute the following command to install the\n'
 'ae.dev_ops module\n'
 'in the currently active virtual environment:\n'
 ' \n'
 '```shell script\n'
 'pip install ae-dev-ops\n'
 '```\n'
 '\n'
 'if you want to contribute to this portion then first fork\n'
 '[the ae_dev_ops repository at GitLab](\n'
 'https://gitlab.com/ae-group/ae_dev_ops "ae.dev_ops code repository").\n'
 'after that pull it to your machine and finally execute the\n'
 'following command in the root folder of this repository\n'
 '(ae_dev_ops):\n'
 '\n'
 '```shell script\n'
 'pip install -e .[dev]\n'
 '```\n'
 '\n'
 'the last command will install this module portion, along with the tools you need\n'
 'to develop and run tests or to extend the portion documentation. to contribute only to the unit tests or to the\n'
 'documentation of this portion, replace the setup extras key `dev` in the above command with `tests` or `docs`\n'
 'respectively.\n'
 '\n'
 'more detailed explanations on how to contribute to this project\n'
 '[are available here](\n'
 'https://gitlab.com/ae-group/ae_dev_ops/-/blob/develop/CONTRIBUTING.rst)\n'
 '\n'
 '\n'
 '## namespace portion documentation\n'
 '\n'
 'information on the features and usage of this portion are available at\n'
 '[ReadTheDocs](\n'
 'https://ae.readthedocs.io/en/latest/_autosummary/ae.dev_ops.html\n'
 '"ae_dev_ops documentation").\n'),
    'long_description_content_type': 'text/markdown',
    'name': 'ae_dev_ops',
    'package_data': {'': []},
    'packages': ['ae'],
    'project_urls': {       'Bug Tracker': 'https://gitlab.com/ae-group/ae_dev_ops/-/issues',
        'Documentation': 'https://ae.readthedocs.io/en/latest/_autosummary/ae.dev_ops.html',
        'Repository': 'https://gitlab.com/ae-group/ae_dev_ops',
        'Source': 'https://ae.readthedocs.io/en/latest/_modules/ae/dev_ops.html'},
    'python_requires': '>=3.9',
    'url': 'https://gitlab.com/ae-group/ae_dev_ops',
    'version': '0.3.5',
    'zip_safe': True,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    pass
