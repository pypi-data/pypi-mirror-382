"""
project development variables and helpers
=========================================

this portion of the ``ae`` namespace is providing constants and helper functions to keep your projects
`DRY <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`__, in bundling all project development and
maintenance tasks, allowing you to specify and distribute all the properties of
a project without any redundancies. e.g. changing the short description/title or
the version number of a project are done in one (!)  single place.

the following Python project types are supported:

    * GUI applications
    * Django web applications
    * console app and library modules
    * console app and library packages
    * namespace library portions
    * namespace roots
    * source code parent folders
    * playgrounds

project development variables data includes:

    * project name, version, title and description
    * virtual environment (pyenv)
    * contributing author name and email
    * project documentation (README, manuals, contribution docs, license)
    * external dependencies/requirements
    * project file templates
    * repository status, branches and tags (git)
    * repository remote urls and CI (GitLab or GitHub)
    * deployment remotes (web servers, cloud storage, PyPi-release of project and its namespace children|portions)
    * setup (pip and setuptools)


determine project development variables
---------------------------------------

the :class:`ProjectDevVars` provided by this portion is a dictionary subclass that analyzes and represents project
development variables. it collects defaults, merges environment variables, inspects the filesystem, and compiles
values suitable for packaging and publishing. to collect the data of a project, create a new instance of this class.

this is done for existing projects by specifying only the path to the project's root folder. from there the project
directory tree get analyzed,  gathering the project properties - the project development variables -
into dictionary-like data structure instance.

key methods of ProjectDevVars
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :meth:`ProjectDevVars.as_dict` – export pdv values as a plain dict.
* :meth:`ProjectDevVars.copy` – create a new :class:`ProjectDevVars` with copied values.
* :meth:`ProjectDevVars.errors` – validate pdv values and return a list of errors/warnings.
* :meth:`ProjectDevVars.pdv_val` – fetch a variable’s value, falling back to defaults.

if the current working directory is the root directory of a Python project to analyze,
then the instance (assigned to the ``pdv`` variable in the following examples) can be created by the following call,
without the need to specify any arguments::

    pdv = ProjectDevVars()

to analyze a project in any other directory specify the path via the
:paramref:`~ProjectDevVars.project_path` keyword argument::

    pdv = ProjectDevVars(project_path='path/to/project_or_parent')

the project property values can be retrieved from the returned dictionary-like instance,
either via the method :meth:`~ProjectDevVars.pdv_val` (used mainly for non-string values),
or directly via getitem. the following example is retrieving a string reflecting the name of the project::

    project_name = pdv['project_name']

the type of project gets mapped by the `'project_type'` project development variable.
recognized project types are e.g. :data:`a module <MODULE_PRJ>`, :data:`a package <PACKAGE_PRJ>`,
:data:`a namespace root <ROOT_PRJ>`, or an :data:`gui application <APP_PRJ>`.

determining the project development variables of projects with the types :data:`PARENT_PRJ`
or :data:`ROOT_PRJ` will gather also the project dev vars of their containing children projects,
each of them represented by its own instance of the :class:`ProjectDevVars` class.


project introspection helpers and constants
-------------------------------------------

these standalone functions provide utilities for inspecting python source code files and project environments.
while :func:`code_file_version` determines the current version of any type of python code file, :func:`code_file_title`
does the same for the title of the code file's docstring. an optional namespace of a package gets determined and
returned as string by the function :func:`namespace_guess`.

* :func:`code_file_title`: determines the docstring title of a python code file.
* :func:`code_file_version`: reads the version number of a python code file from the `__version__` module variable.
* :func:`code_version`: determines a version number from a specified content string (e.g., file content) using a
configurable prefix and suffix.
* :func:`editable_project_root_path`: determines the project path of a package installed in an editable mode
(e.g., via `pip install -e`).
* :func:`find_extra_modules`: determines a list of additional module names within a local package,
excluding templates and `__init__.py` files.
* :func:`increment_version`: increments a semantic version string (e.g., major, minor, or patch part).
* :func:`latest_remote_version` – determine the latest or next available version tag from git remotes.
* :func:`main_file_path` – compute the expected main/version file path for a project type.
* :func:`namespace_guess`: determines and returns the optional namespace name of a python package.
* :func:`pdv_default_values` – collect default pdv values from module globals.
* :func:`pdv_env_values` – load pdv values from environment variables.
* :func:`project_owner_name_version` – split a project string into owner, name, and version.
* :func:`root_packages_masks` – return package glob masks for root packages.
* :func:`skip_files_migrations` – filter callback to exclude django migrations.
* :func:`skip_files_lean_web` – filter callback to minimize files for web deployment.
* :func:`replace_file_version` – update a file’s version string in place.

project type constants
^^^^^^^^^^^^^^^^^^^^^^

* :data:`APP_PRJ` – gui application project type.
* :data:`DJANGO_PRJ` – django web application project type.
* :data:`MODULE_PRJ` – standalone module project type.
* :data:`NO_PRJ` – marker for invalid or no project (type) detected.
* :data:`PACKAGE_PRJ` – python package project type.
* :data:`PARENT_PRJ` – pseudo-type for parent-directory initialization.
* :data:`PLAYGROUND_PRJ` – playground or scratch project type.
* :data:`ROOT_PRJ` – namespace root project type.

* :data:`ANY_PRJ_TYPE` – tuple of all real project types.
* :data:`ALL_PRJ_TYPES` – tuple of all project types, including :data:`NO_PRJ` and :data:`PARENT_PRJ`.

project development variable value constants
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  * :data:`PDV_BUILD_CONFIG_FILE`: the name of the application building configuration file (e.g., `buildozer.spec`).
  * :data:`PDV_COMMIT_MSG_FILE_NAME`: the default file name for a git commit message.
  * :data:`PDV_DOCS_FOLDER`: the default folder name for documentation (e.g., `docs`).
  * :data:`PDV_DOCS_HOST_PROTOCOL`: the default protocol for the documentation host (e.g., `https://`).
  * :data:`PDV_docs_domain`: the default dns domain for documentation (e.g., `readthedocs.io`).
  * :data:`PDV_KEYWORDS`: a list of default keywords for :pypi:`pypi` release metadata.
  * :data:`PDV_LICENSE`: the default license for the project (e.g., `gpl-3.0-or-later`, :pep:`639`).
  * :data:`PDV_MAIN_BRANCH`: the default name for the main branch in a git repository.
  * :data:`PDV_MIN_PYTHON_VERSION`: the minimum version of the python runtime required for the project (e.g., `3.9`).
  * :data:`PDV_NULL_VERSION`: the initial package version, chosen to meet :pypi:`pypi` classifier requirements.
  * :data:`PDV_PARENT_FOLDERS`: a tuple of common names for parent folders that contain python project directories.
  * :data:`PDV_PYTHON_REQUIRES`: the default required python version string for setup files (e.g., `>=3.9`).
  * :data:`PDV_RELEASE_REF_PREFIX`: the prefix for project release branch names or references.
  * :data:`PDV_REMOTE_ORIGIN`: the name of the git remote from which the local repository was cloned.
  * :data:`PDV_REMOTE_UPSTREAM`: the name of the git remote for the fork's source repository.
  * :data:`PDV_REPO_HOST_PROTOCOL`: the default protocol for the code repository host (e.g., `https://`).
  * :data:`PDV_repo_domain`: the default dns domain for the code repository (e.g., `gitlab.com`).
  * :data:`PDV_REPO_PAGES_DOMAIN`: the internet/dns domain for repository pages (e.g., `gitlab.io`).
  * :data:`PDV_REPO_GROUP_SUFFIX`: the suffix used for the default repository users group name.
  * :data:`PDV_REPO_ISSUES_SUFFIX`: the url suffix for the repository's issues page (e.g., `/-/issues`).
  * :data:`PDV_REQ_FILE_NAME`: the default filename for the main project dependencies (e.g., `requirements.txt`).
  * :data:`PDV_REQ_DEV_FILE_NAME`: the default filename for development or template-specific requirements.
  * :data:`PDV_TEMPLATES_FOLDER`: the default folder name for file templates (e.g., `templates`).
  * :data:`PDV_TESTS_FOLDER`: the default folder name for unit tests (e.g., `tests`).
  * :data:`PDV_VERSION_TAG_PREFIX`: the prefix for git version tags.

versioning constants
^^^^^^^^^^^^^^^^^^^^

these constants are used by the version introspection helper functions.

  * :data:`VERSION_QUOTE`: the quote character used for the `__version__` variable value (typically `'`).
  * :data:`VERSION_PREFIX`: the search string used to find the `__version__` variable (e.g., `__version__ = '`).
  * :data:`VERSION_MATCHER`: a pre-compiled regular expression to detect and manage version numbers conforming to
    :pep:`pep396 <396>` and python's `distutils` standards.


configure individual project development variable values
--------------------------------------------------------

this portion is providing default values for most of the project development variables.
individual default values can be configured as OS/shell/console environment variables.

for projects released at PyPI at least the author name and a contact email address should be configured,
because their default values (in :data:`PDV_AUTHOR` and :data:`PDV_AUTHOR_EMAIL`) are empty strings.

the package data resources of a project gets determined by the method :meth:`_find_package_data`. the return
value gets directly passed to the `package_data` development variable, which will be used to create
the ``setup.py`` file of your project (as kwarg passed to :func:`setuptools.setup`).
"""
# pylint: disable=too-many-lines
import getpass
import glob
import os
import re
import sys
import warnings

from collections import OrderedDict
from typing import Any, Callable, Iterable, OrderedDict as OrderedDictType, Sequence, Union, cast

from packaging.version import Version
from setuptools import find_namespace_packages, find_packages

from ae.base import (                                                                                   # type: ignore
    BUILD_CONFIG_FILE, DEF_PROJECT_PARENT_FOLDER, DOCS_FOLDER, PACKAGE_INCLUDE_FILES_PREFIX, PY_EXT, PY_INIT,
    TEMPLATES_FOLDER, TESTS_FOLDER,
    deep_dict_update, evaluate_literal, main_file_paths_parts, norm_path,
    os_path_abspath, os_path_join, os_path_isfile, os_path_dirname, os_path_basename, os_path_isdir, os_path_relpath,
    os_path_sep, os_path_splitext, project_main_file, read_file, write_file)
from ae.paths import coll_folders, path_files, path_items, skip_py_cache_files, Collector               # type: ignore
from ae.shell import (                                                                                  # type: ignore
    COMMIT_MSG_FILE_NAME, DEF_MAIN_BRANCH, GIT_FOLDER_NAME, GIT_RELEASE_REF_PREFIX, GIT_REMOTE_ORIGIN,
    GIT_REMOTE_UPSTREAM, GIT_VERSION_TAG_PREFIX, PROJECT_VERSION_SEP, PYPI_ROOT_URL, PYPI_ROOT_URL_TEST,
    GitRemotesType,
    get_domain_user_variable, get_main_app, git_remote_domain_group, git_remotes, git_tag_list, in_prj_dir_venv, sh_exec
)
from ae.templates import (                                  # type: ignore # noqa: F401 # pylint: disable=unused-import
    TEMPLATE_PLACEHOLDER_ID_PREFIX, TEMPLATE_PLACEHOLDER_ID_SUFFIX, TEMPLATE_PLACEHOLDER_ARGS_SUFFIX,
    TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID, TEMPLATE_REPLACE_WITH_PLACEHOLDER_ID,
    TemplateProjectsType)


__version__ = '0.3.5'


APP_PRJ = 'app'                                         #: gui application project
DJANGO_PRJ = 'django'                                   #: django website project
MODULE_PRJ = 'module'                                   #: module portion/project
NO_PRJ = ''                                             #: no project detected
PACKAGE_PRJ = 'package'                                 #: package portion/project
PARENT_PRJ = 'projects-parent-dir'                      #: pseudo project type for new project started in parent-dir
PLAYGROUND_PRJ = 'playground'                           #: playground project
ROOT_PRJ = 'namespace-root'                             #: namespace root project

ANY_PRJ_TYPE = (APP_PRJ, DJANGO_PRJ, MODULE_PRJ, PACKAGE_PRJ, PLAYGROUND_PRJ, ROOT_PRJ)
""" tuple of real project types (not including the pseudo-project-types: no-/incomplete-project and parent-folder) """
ALL_PRJ_TYPES = ANY_PRJ_TYPE + (NO_PRJ, PARENT_PRJ)     #: all project types (including no/parent project)

VERSION_QUOTE = "'"                                     #: quote character of the __version__ number variable value
VERSION_PREFIX = "__version__ = " + VERSION_QUOTE       #: search string to find the __version__ variable
VERSION_MATCHER = re.compile("^" + VERSION_PREFIX + r"(\d+)[.](\d+)[.](\d+)[a-z\d]*" + VERSION_QUOTE, re.MULTILINE)
""" pre-compiled regular expression to detect and change/bump the app/portion file version numbers of a version string.

The version number format has to be :pep:`conform to PEP396 <396>` and the sub-part to `Pythons distutils
<https://docs.python.org/3/distutils/setupscript.html#additional-meta-data>`__ (trailing version information indicating
sub-releases, are either “a1,a2,…,aN” (for alpha releases), “b1,b2,…,bN” (for beta releases) or “pr1,pr2,…,prN” (for
pre-releases). Note that distutils got deprecated in Python 3.12 (see package :mod:`packaging.version` as replacement)).
"""


# PDV_* constants holding default values of all user/project specific configuration  ----------------------------------

ENV_VAR_NAME_PREFIX = 'PDV_'            #: used for env var names and the constant names declared in this module

PDV_COMMIT_MSG_FILE_NAME = COMMIT_MSG_FILE_NAME         #: name of the git commit message file
PDV_BUILD_CONFIG_FILE = BUILD_CONFIG_FILE               #: app building config file
PDV_DOCS_FOLDER = DOCS_FOLDER                           #: docs folder name
PDV_DOCS_HOST_PROTOCOL = "https://"                     #: documentation host connection protocol
# pylint: disable-next=invalid-name
PDV_docs_domain = 'readthedocs.io'                      #: documentation dns domain

PDV_KEYWORDS = ['configuration', 'development', 'environment', 'productivity']  #: PyPi release keywords

# PDV_LICENSE = "OSI Approved :: GNU General Public License v3 or later (GPLv3+)"     #: project license default
PDV_LICENSE = 'GPL-3.0-or-later'                        #: project license default (:pep:`639`)
# PDV_LICENSE_FILES = ['LICENSE*.*']                    #: license files default
PDV_MAIN_BRANCH = DEF_MAIN_BRANCH                       #: default main branch name
PDV_MIN_PYTHON_VERSION = "3.9"                          #: minimum version of the Python/CPython runtime

PDV_NULL_VERSION = '0.3.0'                              #: initial package version (3==min classifier accepted by PyPI)

PDV_PARENT_FOLDERS = (
    'Projects', 'PycharmProjects', 'ae-group', 'aedev-group', 'code', 'dev', 'esc', 'old_src', 'projects', 'python',
    'repos', 'source', DEF_PROJECT_PARENT_FOLDER, 'TsT', getpass.getuser())
""" names of parent folders containing Python project directories """

PDV_PYTHON_REQUIRES = f">={PDV_MIN_PYTHON_VERSION}"     #: default required Python version of project

PDV_REPO_HOST_PROTOCOL = "https://"                     #: repo host connection protocol
# pylint: disable-next=invalid-name
PDV_repo_domain = 'gitlab.com'                          #: code repository dns domain (gitlab.com|github.com)
PDV_REPO_PAGES_DOMAIN = 'gitlab.io'                     #: repository pages internet/dns domain
PDV_REPO_GROUP_SUFFIX = "-group"                        #: repo users group name suffix (used for 'repo_group' default)
PDV_REPO_ISSUES_SUFFIX = "/-/issues"                    #: repo host URL suffix to the issues page (GitHub=="/issues")

PDV_REQ_FILE_NAME = 'requirements.txt'                  #: requirements default file name
PDV_REQ_DEV_FILE_NAME = 'dev_requirements.txt'          #: default file name for development/template requirements

PDV_TEMPLATES_FOLDER = TEMPLATES_FOLDER                 #: templates folder name
PDV_TESTS_FOLDER = TESTS_FOLDER                         #: unit tests folder name

PDV_RELEASE_REF_PREFIX = GIT_RELEASE_REF_PREFIX         #: project release branch-name/ref prefix
PDV_VERSION_TAG_PREFIX = GIT_VERSION_TAG_PREFIX         #: project version tag prefix
PDV_REMOTE_ORIGIN = GIT_REMOTE_ORIGIN                   #: name of git remote from where the local repo get cloned from
PDV_REMOTE_UPSTREAM = GIT_REMOTE_UPSTREAM               #: name of git remote from where the fork repo get forked from

# types ---------------------------------------------------------------------------------------------------------------
ChildrenType = OrderedDictType[str, 'ProjectDevVars']   #: children pdv of a project parent or a namespace root

DataFilesType = list[tuple[str, tuple[str, ...]]]       #: setup_kwargs['data_files']
PackageDataType = dict[str, list[str]]                  #: setup_kwargs['package_data']
SetupKwargsType = dict[str, Any]                        #: setuptools.setup()-kwargs

PdvVarValType = Union[str, Sequence[str], DataFilesType, GitRemotesType, SetupKwargsType, TemplateProjectsType,
                      'RemoteHost']     # type: ignore # noqa: F821 # RemoteHost is declared in aedev_project_manager
""" project development variable value types, including also types of later/externally added vars by pjm, like e.g.
'TemplateProjectsType' for the 'project_templates' variable, or 'RemoteHost' for the 'host_api' variable,
or dict[str, str] for the 'main_app_options' variable (already covered via SetupKwargsType/dict[str, Any]. """


def code_file_title(file_name: str) -> str:
    """ determine docstring title of a Python code file.

    :param file_name:           name (and optional path) of module/script file to read the docstring title number from.
    :return:                    docstring title string or empty string if file|docstring-title not found.
    """
    title = ""
    try:
        lines = read_file(file_name).split('\n')
        for idx, line in enumerate(lines):
            if line.startswith('"""'):
                title = (line[3:].strip() or lines[idx + 1].strip()).strip('"').strip()
                break
    except (FileNotFoundError, IndexError, OSError):
        pass
    return title


def code_file_version(file_name: str) -> str:
    """ read version of Python code file - from __version__ module variable initialization.

    :param file_name:           name (and optional path) of module/script file to read the version number from.
    :return:                    version number string or empty string if file or version-in-file not found.
    """
    try:
        content = read_file(file_name)
        return code_version(content)
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return ""


def code_version(content: Union[str, bytes], prefix: str = "^" + VERSION_PREFIX, suffix: str = VERSION_QUOTE) -> str:
    """ determine a version number from the specified content string.

    :param content:             content of type str or bytes to be searched for the definition/declaration of a version.
    :param prefix:              version string prefix (directly before the veesion number).
    :param suffix:              version string suffix char/string (directly after the version number string).
                                passing an empty is not allowed, and will always return an empty string.
    :return:                    version number string or empty string if version could not be not found in content.
    """
    try:
        pattern = prefix + "([^" + suffix + "]*)" + suffix
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        version_match = re.search(pattern, content, re.M)
        return version_match.group(1) if version_match else ""
    except (TypeError, UnicodeDecodeError, ValueError, Exception):  # pylint: disable=broad-exception-caught
        return ""


def editable_project_root_path(project_name: str) -> str:
    """ determine the project path of a project package installed as editable.

    :param project_name:        project|package name to search for.
    :return:                    project source root path of an editable installed package
                                or empty string, if the package is not installed as editable.
    """
    field_prefix = 'Editable project location: '
    output: list[str] = []
    if sh_exec(f"pip show {project_name}", lines_output=output) == 0:
        for line in output:
            if line.startswith(field_prefix):
                return line[len(field_prefix):]

    # fallback if pip is an older version (before 21, without PEP 660 support)
    for install_path in sys.path:
        egg_link_file = os_path_join(install_path, project_name + '.egg-link')
        if os_path_isfile(egg_link_file):
            return read_file(egg_link_file).split(os.linesep)[0]

    return ""


def find_extra_modules(package_path: str, tpls_folder: str) -> list[str]:
    """ determine additional modules of a local (namespace portion) package/project.

    :param package_path:        path to the package folder, mostly underneath the project root folder.
    :param tpls_folder:         name of the templates folder (situated in the package folder) to exclude template files.
    :return:                    list of module import name strings (without file extension and path separators as dots).
                                modules in :data:`PDV_TEMPLATES_FOLDER` as well as :data:`PY_INIT` modules are excluded.
    """
    package_path = norm_path(package_path)
    if not os_path_isdir(package_path):
        return []

    def _select_file(file_path: str) -> bool:
        return (not os_path_relpath(file_path, package_path).startswith(tpls_folder + os_path_sep)
                and os_path_basename(file_path) != PY_INIT)

    def _create_file(file_path: str) -> str:
        return os_path_relpath(file_path, package_path).replace(os_path_sep, '.')[:-len(PY_EXT)]

    return path_items(os_path_join(package_path, "**", '*' + PY_EXT), selector=_select_file, creator=_create_file)


def increment_version(version: Union[str, Iterable[str]], increment_part: int = 3) -> str:
    """ increment version number.

    :param version:             version number string or an iterable of version string parts.
    :param increment_part:      part of the version number to increment (1=mayor, 2=minor, 3=patch).
    :return:                    incremented version number.
    """
    if isinstance(version, str):
        version = version.split(".")

    return ".".join(str(int(part_str) + 1) if part_idx + 1 == increment_part else part_str
                    for part_idx, part_str in enumerate(version))


def latest_remote_version(pdv: 'ProjectDevVars', increment_part: int = 3) -> str:
    """ determine the latest or the next free origin remote repository version of the specified project.

    :param pdv:                 project development variables (project_path, project_version, VERSION_TAG_PREFIX).
    :param increment_part:      part of the version number to be incremented (1=mayor, 2=minor/namespace, 3=patch).
                                pass zero/0 to return the latest published package version.
    :return:                    the incremented latest published repository package version as a string or the first
                                version accepted by PyPI (increment_version(PDV_NULL_VERSION, increment_part) | "0.3.1")
                                if the project never published a version tag to the git origin remote.
    """
    project_path = pdv['project_path']
    tag_prefix = pdv['VERSION_TAG_PREFIX']
    latest_version = pdv['NULL_VERSION']

    if os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        for remote_name in pdv.pdv_val('remote_urls'):
            tags = git_tag_list(project_path, remote=remote_name, tag_pattern=tag_prefix + "*")
            if tags and Version(remote_version := tags[-1][len(tag_prefix):]) > Version(latest_version):
                latest_version = remote_version

    return increment_version(latest_version, increment_part=increment_part)


def main_file_path(project_path: str, project_type: str, namespace_name: str = "") -> str:
    """ return the file path of the main/version type for the specified project type.

    :param project_path:        project root folder path, including the package name as basename.
    :param project_type:        project type to determine the main/version file path for.
    :param namespace_name:      pass namespace name for namespace portion or root projects.
    :return:                    main file path and name.

    .. note::
        in contrary to :func:`~ae.base.project_main_file` this function will also work for new projects where neither
        exists the main file nor the project root folder.
    """
    main_path = norm_path(project_path)
    main_stem = os_path_basename(main_path)
    if namespace_name:
        main_path = os_path_join(main_path, namespace_name)
        main_stem = main_stem[len(namespace_name) + 1:]

    if project_type in (DJANGO_PRJ, PACKAGE_PRJ, ROOT_PRJ):
        main_path = os_path_join(main_path, namespace_name if project_type == ROOT_PRJ else main_stem)
        main_name = PY_INIT
    elif project_type == APP_PRJ:
        main_name = 'main' + PY_EXT
    else:
        main_name = main_stem + PY_EXT

    return os_path_join(main_path, main_name)


def namespace_guess(project_path: str) -> str:
    """ guess name of namespace name from the package/app/project root directory path.

    :param project_path:        path to project root folder.
    :return:                    namespace import name of the project specified via the project root directory path.
    """
    project_name = portion_name = os_path_basename(norm_path(project_path))
    namespace_name = ""
    for part in project_name.split("_"):
        for path_parts in main_file_paths_parts(portion_name):
            if os_path_isfile(os_path_join(project_path, *path_parts)):
                return namespace_name[1:]

        project_path = os_path_join(project_path, part)
        *_ns_path_parts, portion_name = portion_name.split("_", maxsplit=1)
        namespace_name += "." + part

    return ""


def pdv_default_values() -> dict[str, Any]:
    """ collect the ProjectDevVars defaults from the globals of this module.

    :return:                    dict with the pdv variable names as keys and its default values.
    """
    values = {}
    for var_name, var_val in globals().items():
        if var_name.startswith(ENV_VAR_NAME_PREFIX):
            var_name = var_name[len(ENV_VAR_NAME_PREFIX):]
        elif not var_name.startswith('TEMPLATE_'):
            continue

        values[var_name] = var_val

    return values


def pdv_env_values() -> dict[str, Any]:
    """ read pdv default values from environment variables.

    :return:                    dict with the pdv names as keys and its values loaded from the os environment variables.
    """
    values = {}
    for var_name, var_val in os.environ.items():
        if var_name.startswith(ENV_VAR_NAME_PREFIX):
            pdv_name = var_name[len(ENV_VAR_NAME_PREFIX):]
            values[pdv_name] = evaluate_literal(var_val)    # convert to var type (alt: :class:`ae.literal.Literal`)

    return values


def project_owner_name_version(project_string: str,
                               owner_default: str = "", namespace_default: str = "", version_default: str = ""
                               ) -> tuple[str, str, str]:
    """ split the specified project string into its owner user|group name, the project name, and the project version.

    :param project_string:      the string to parse and split.
    :param owner_default:       default value of the owner user|group name if not specified.
    :param namespace_default:   namespace default value, used if only portion name is specified.
    :param version_default:     default value of the version number if not specified.
    :return:                    tuple with owner name, project name and project version
    """
    if "/" in project_string:
        owner, prj_ver = project_string.rsplit("/", maxsplit=1)
    else:
        owner, prj_ver = owner_default, project_string
    if PROJECT_VERSION_SEP in prj_ver:
        project, version = prj_ver.split(PROJECT_VERSION_SEP, maxsplit=1)
    else:
        project, version = prj_ver, version_default
    if namespace_default and not project.startswith(prefix := namespace_default + '_'):
        project = prefix + project
    return owner, project, version


def replace_file_version(file_name: str, version: str = "", increment_part: int = 3) -> str:
    """ replace version number in specified project main/version file, removing any pre/alpha version subpart/suffix.

    :param file_name:           version file name to be patched/version-bumped.
    :param version:             version number to increment/bump (if the argument
                                :paramref:`~replace_file_version.increment_part` is not 0) and to replace/put into the
                                version file. defaults to the version number in the version file, if not specified.
    :param increment_part:      part of the version number to be incremented: 1=mayor, 2=minor, 3=build/revision.
                                specify 0 to not increment the version number. defaults to 3 (build) if not specified.
    :return:                    empty string on success, else error string.
    """
    msg = f"replace_file_version({file_name}) expects "
    if not os_path_isfile(file_name):
        return msg + f"existing code file path reachable from current working directory {os.getcwd()}"

    content = read_file(file_name)
    if not content:
        return msg + f"non-empty code file in {os_path_abspath(file_name)}"

    _replacement: Union[str, Callable[[re.Match[str]], str]]
    if version:
        _replacement = VERSION_PREFIX + increment_version(version, increment_part=increment_part) + VERSION_QUOTE
    else:
        def _replacement(_match: re.Match) -> str:
            return VERSION_PREFIX + increment_version((_match.group(p) for p in range(1, 4)),
                                                      increment_part=increment_part) + VERSION_QUOTE
    content, replaced = VERSION_MATCHER.subn(_replacement, content)

    if replaced != 1:
        return msg + f"single occurrence of module variable {VERSION_PREFIX}{VERSION_QUOTE}, but found {replaced} times"

    write_file(file_name, content)

    return ""


def root_packages_masks(project_packages: Iterable[str]) -> list[str]:
    """ determine root sub packages from the passed project packages and add them glob path wildcards.

    :param project_packages:    iterable with package import names, like returned from the setuptools helper functions
                                find_packages()/find_namespace_packages().
    :return:                    list of project root packages extended with glob path wildcards.
    """
    root_packages = []
    root_paths = []
    for app_import_name in sorted(project_packages):
        pkg_name_parts = app_import_name.split('.')
        if pkg_name_parts[0] not in root_packages:
            root_packages.append(pkg_name_parts[0])
            root_paths.append(os_path_join(pkg_name_parts[0], '**', '*'))
    return root_paths


def skip_files_migrations(file_path: str) -> bool:
    """ file exclusion callback for the files under the django migrations folders.

    :param file_path:       path to file to check for exclusion, relative to the project root folder.
    :return:                boolean True, if the file specified in :paramref:`~skip_files_migrations.file_path`
                            has to be excluded, else False.
    """
    return 'migrations' in file_path.split(os_path_sep)


def skip_files_lean_web(file_path: str) -> bool:
    """ file exclusion callback to reduce the deployed files on the web server to the minimum.

    :param file_path:       path to file to check for exclusion, relative to the project root folder.
    :return:                boolean True, if the file specified in :paramref:`~skip_files_lean_web.file_path`
                            has to be excluded, else False.
    """
    return (skip_py_cache_files(file_path)
            or skip_files_migrations(file_path)
            or os_path_sep + 'static' + os_path_sep in file_path
            or os_path_splitext(file_path)[1] == '.po'
            )


class ProjectDevVars(dict[str, PdvVarValType]):
    """ project development variables mapping."""
    def __init__(self, **var_values):
        """ analyze and map the environment and status of a code project into project development variables.

        :param var_values:          fixed dev var values, overwriting OS environment variables and defaults.
                                    to get the project dev variable values from an existing project pass the
                                    `project_path` kwarg with the path of the project root folder.
                                    if this `project_path` kwarg is not specified then its value defaults to
                                    the current working directory (if the `project_name`kwarg is not specified),
                                    or to the directory underneath the current working directory, specified by
                                    the `project_name` kwarg.
        :raises:                    AssertionError if `project_path` and `project_name` are specified.
        :return:                    special mapping with all the determinable project development variable values.
        """
        assert 'project_path' not in var_values or 'project_name' not in var_values, \
            f"specify either project_name or project_path not both ({var_values})"

        super().__init__()

        self.disable_non_string_fetch_warning = False  #: set to True to disable warning on access to non-str-item-value

        self._init_pdv(var_values)
        self._load_requirements()           # load info from all *requirements.txt files
        self._load_descriptions()           # load README* files
        self._compile_remote_vars()         # compile the git host remote values
        self._compile_setup_kwargs()        # compile 'setup_kwargs' variable value
        self._compile_dev_vars()            # compile development vars depending depending from other project env vars

    def __getitem__(self, var_name: str) -> str:
        """ get the string value of the project development variable with the specified var name.

        :param var_name:        project development variable name.
        :return:                string value of the specified pdv (other types are returned too, but
                                a warning will be displayed in this case).
                                or if not exists in :paramref:`~pdv_str.pdv` then the global constant/default
                                value of this module, or any empty string if no constant with this name exists.
        """
        value = self.pdv_val(var_name)
        if not self.disable_non_string_fetch_warning and not isinstance(value, str):
            warnings.warn(f" ***  value of '{var_name=}' is not of type str (got {type(value)}). use pdv_val() method!")
        return value

    def _compile_dev_vars(self):        # pylint: disable=too-many-locals
        namespace_name = self['namespace_name']
        project_path = self['project_path']
        project_type = self['project_type']
        sep = os.linesep
        ins = sep + " " * 4

        self['project_id'] = '_'.join(self[_] for _ in ('repo_domain', 'repo_group', 'project_name', 'project_version'))
        self['project_title'] = " ".join(self[_] for _ in ('project_name', 'project_type', 'project_version'))

        chi_app_options = {_o: _v for _o, _v in self.pdv_val('main_app_options').items()
                           if _v not in ('project_name', 'project_path')} \
            if 'main_app_options' in self and project_type in (PARENT_PRJ, ROOT_PRJ) else {}

        if project_type == ROOT_PRJ:
            namespace_len = len(namespace_name)

            imp_names = []
            por_vars: ChildrenType = OrderedDict()
            pypi_refs_rst = []
            pypi_refs_md = []
            pypi_test = self['parent_folder'] == 'TsT'
            for project_nam_ver in cast(list[str], self.pdv_val('portions_packages')):
                p_name = project_nam_ver.split(PROJECT_VERSION_SEP)[0]
                portion_path = os_path_join(os_path_dirname(project_path), p_name)
                portion_name = p_name[namespace_len + 1:]
                import_name = p_name[:namespace_len] + '.' + portion_name

                pypi_url = (PYPI_ROOT_URL_TEST if pypi_test else PYPI_ROOT_URL) + f"/project/{p_name}"
                pypi_refs_rst.append(f'* `{p_name} <{pypi_url}>`_')
                pypi_refs_md.append(f'* [{p_name}]({pypi_url} "{namespace_name} namespace portion {p_name}")')

                por_vars[p_name] = chi_pdv = ProjectDevVars(
                    project_path=portion_path, namespace_name=namespace_name, main_app_options=chi_app_options)

                imp_names.append(import_name)
                assert chi_pdv['package_path'] == os_path_join(portion_path, namespace_name, portion_name), \
                    f"{chi_pdv['package_path']=} != {os_path_join(portion_path, namespace_name, portion_name)=}"
                for e_mod in find_extra_modules(chi_pdv['package_path'], chi_pdv['TEMPLATES_FOLDER']):
                    imp_names.append(import_name + '.' + e_mod)

            self['children_project_vars'] = por_vars

            self['portions_pypi_refs'] = sep.join(pypi_refs_rst)  # templates/..._README.rst
            self['portions_pypi_refs_md'] = sep.join(pypi_refs_md)  # templates/..._README.md
            self['portions_import_names'] = ins.join(imp_names)  # templates/docs/..._index.rst

        elif project_type == PARENT_PRJ:
            coll = Collector(item_collector=coll_folders)
            coll.collect(project_path, select="*")
            self['children_project_vars'] = {
                os_path_basename(chi_prj_path): ProjectDevVars(project_path=chi_prj_path, **chi_app_options)
                for chi_prj_path in coll.paths}

        docs_dir = os_path_join(self['project_path'], self['DOCS_FOLDER'])
        extra_docs = path_files(os_path_join(docs_dir, 'man', "**", "*.rst"))
        self['manuals_include'] = ""    # needed by index.rst template (namespace_root_tpls/de_otf_de_tpl_index.rst)
        if extra_docs:
            self['manuals_include'] = f"manuals and tutorials{sep}" \
                                      f"*********************{sep}{sep}" \
                                      f".. toctree::{sep}{sep}" \
                                      f"    {ins.join(os_path_relpath(_, docs_dir) for _ in extra_docs)}"

        return self

    def _compile_remote_vars(self):
        project_name = self['project_name']
        group_prefix = self['namespace_name'] or project_name
        docs_prefix = self['DOCS_SUB_DOMAIN'] or group_prefix

        if 'docs_root' not in self:
            self['docs_root'] = f"{self['DOCS_HOST_PROTOCOL']}{docs_prefix}.{self['docs_domain']}"
        docs_root = self['docs_root']
        self['docs_code'] = f"{docs_root}/en/latest/_modules/{self['import_name'].replace('.', '/')}.html"
        self['docs_url'] = f"{docs_root}/en/latest/_autosummary/{self['import_name']}.html"

        if 'repo_group' not in self:
            self['repo_group'] = f"{group_prefix}{self['REPO_GROUP_SUFFIX']}"
        repo_group = self['repo_group']
        if 'repo_root' not in self:
            self['repo_root'] = f"{self['REPO_HOST_PROTOCOL']}{self['repo_domain']}/{repo_group}"   # upstream
        repo_root = self['repo_root']
        if 'repo_pages' not in self:
            self['repo_pages'] = f"{self['REPO_HOST_PROTOCOL']}{repo_group}.{self['REPO_PAGES_DOMAIN']}"
        if 'repo_url' not in self:
            self['repo_url'] = f"{repo_root}/{project_name}"

        if 'pypi_url' not in self and self['pip_name']:
            pypi_test = os_path_basename(os_path_dirname(self['project_path'])) == 'TsT'
            self['pypi_url'] = f"{PYPI_ROOT_URL_TEST if pypi_test else PYPI_ROOT_URL}/project/{self['pip_name']}"

    def _compile_setup_kwargs(self):
        """ add setup kwargs from pdv values. """
        kwargs: SetupKwargsType = self.pdv_val('setup_kwargs')  # type: ignore
        for arg_name, var_name in (
                ('author', 'AUTHOR'), ('author_email', 'AUTHOR_EMAIL'),
                ('description', 'project_desc'), ('install_requires', 'install_requires'), ('keywords', 'KEYWORDS'),
                ('license', 'LICENSE'),
                # commented because 'python setup.py check' UserWarning: Unknown distribution option: 'license-files'
                # ('license-files', 'LICENSE_FILES'),
                ('long_description_content_type', 'long_desc_type'), ('long_description', 'long_desc_content'),
                ('name', 'project_name'), ('package_data', 'package_data'), ('packages', 'project_packages'),
                ('python_requires', 'PYTHON_REQUIRES'), ('url', 'repo_url'), ('version', 'project_version'),
        ):
            if arg_name not in kwargs and var_name in self:
                kwargs[arg_name] = self.pdv_val(var_name)

        if 'classifiers' not in kwargs:     # PyPI classifiers https://pypi.org/pypi?%3Aaction=list_classifiers
            try:
                mid_version = int(self['project_version'].split('.')[1])  # minor version
            except (AttributeError, IndexError, ValueError):    # no-str-type, no-dots-in-version, no-int in [2
                mid_version = 0
            dev_status = {
                1: "Planning",
                2: "Pre-Alpha",
                3: "Alpha",
                4: "Beta",
                5: "Production/Stable",
                6: "Mature",
                7: "Inactive",
            }.get(mid_version, "Unknown")
            kwargs['classifiers'] = [
                f"Development Status :: {mid_version} - {dev_status}",
                # commented out to follow :pep:`639`: f"License :: {self['LICENSE']}",
                "Natural Language :: English",
                "Operating System :: OS Independent",
                "Programming Language :: Python",
                f"Programming Language :: Python :: {self['MIN_PYTHON_VERSION'].split('.', maxsplit=1)[0]}",
                f"Programming Language :: Python :: {self['MIN_PYTHON_VERSION']}",
                "Topic :: Software Development" + (
                    " :: Libraries :: Python Modules" if self['project_type'] in (MODULE_PRJ, PACKAGE_PRJ) else ""),
                "Typing :: Typed",
            ]

        if 'extras_require' not in kwargs:
            doc_req = cast(list[str], self.pdv_val('docs_requires'))
            tst_req = cast(list[str], self.pdv_val('tests_requires'))
            kwargs['extras_require'] = {'dev': cast(list[str], self.pdv_val('dev_requires')) + doc_req + tst_req,
                                        'docs': doc_req,
                                        'tests': tst_req, }

        if 'project_urls' not in kwargs:  # displayed on PyPI
            kwargs['project_urls'] = {'Bug Tracker': self['repo_url'] + self['REPO_ISSUES_SUFFIX'],
                                      'Documentation': self['docs_url'],
                                      'Repository': self['repo_url'],
                                      'Source': self['docs_code'],
                                      }

        if 'zip_safe' not in kwargs:
            kwargs['zip_safe'] = not bool(cast(PackageDataType, self.pdv_val('package_data'))[""])

    def _find_package_data(self) -> PackageDataType:
        """ find doc, template, kv, i18n translation text, image and sound files of an app/package.

        :return:                setuptools package_data dict, where the key is an empty string (to be included for all
                                sub-packages) and the dict item is a list of all found resource files with a relative
                                path to the :paramref:`~_find_package_data.package_path` directory. folder names with a
                                leading underscore (like e.g. the docs `_build`, the
                                :data:`~ae.base.PY_CACHE_FOLDER`|`__pycache__` and the `__enamlcache__` folders) get
                                excluded.
                                explicitly included will be any :data:`PDV_BUILD_CONFIG_FILE` file, as well as any
                                folder name starting with :data:`~ae.base.PACKAGE_INCLUDE_FILES_PREFIX` (used e.g. by
                                :mod:`ae.updater`), situated directly in the directory specified by
                                :paramref:`~_find_package_data.package_path`.
        """
        package_path = self['package_path']
        files = []

        def _add_file(file_name: str):
            if os_path_isfile(file_name):
                rel_path = os_path_relpath(file_name, package_path)
                if not any(_.startswith("_") for _ in rel_path.split(os_path_sep)):
                    files.append(rel_path)

        _add_file(os_path_join(package_path, self['BUILD_CONFIG_FILE']))

        # included folders situated in the project root folder, used e.g. by the optional ae.updater module
        for file in glob.glob(os_path_join(package_path, PACKAGE_INCLUDE_FILES_PREFIX + "*")):
            _add_file(file)  # add all files with PACKAGE_INCLUDE_FILES_PREFIX in package_path root folder
        for file in glob.glob(os_path_join(package_path, PACKAGE_INCLUDE_FILES_PREFIX + "*", "**", "*"),
                              recursive=True):
            _add_file(file)  # add all file under package_path root folder names with the PACKAGE_INCLUDE_FILES_PREFIX

        docs_path = os_path_join(package_path, self['DOCS_FOLDER'])
        for file in glob.glob(os_path_join(docs_path, "**", "*"), recursive=True):
            _add_file(file)

        tpl_path = os_path_join(package_path, self['TEMPLATES_FOLDER'])
        for file in glob.glob(os_path_join(tpl_path, "**", "*"), recursive=True):
            _add_file(file)

        for file in glob.glob(os_path_join(package_path, "**", "*.kv"), recursive=True):
            _add_file(file)

        for resource_folder in ('img', 'loc', 'snd'):
            for file in glob.glob(os_path_join(package_path, resource_folder, "**", "*"), recursive=True):
                _add_file(file)

        return {"": files}

    def _init_from_env(self, project_path: str):
        # read defaults from .git cfg, the environment variables and ``.env`` files in the project root folder and above
        env_val_ini_dir = project_path if os_path_isdir(project_path) else os_path_dirname(project_path)
        main_app = get_main_app()

        if not os_path_isdir(env_val_ini_dir):
            main_app.dpo(f"    # skipped env var loading because {project_path=} and its parent folder does not exist")
            return

        with in_prj_dir_venv(env_val_ini_dir):  # does also load_env_var_defaults() call to load env ars from .env files
            env_values = pdv_env_values()       # load early to provide mangled remote names, init after repo/web vars
            remote_domain, _remote_group = git_remote_domain_group(
                self['project_path'],
                origin_name=env_values.get('REMOTE_ORIGIN', PDV_REMOTE_ORIGIN),
                upstream_name=env_values.get('REMOTE_UPSTREAM', PDV_REMOTE_UPSTREAM),
                remote_urls=self.pdv_val('remote_urls'))

            # prepare cfg var names: repo_domain, web_domain, repo_group, repo_token, web_token, repo_user, web_user
            for var_prefix in ('repo_', 'web_'):
                is_repo_var = var_prefix == 'repo_'

                var_name = f'{var_prefix}domain'
                if var_name not in self and (
                        domain := is_repo_var and remote_domain or get_domain_user_variable(main_app, var_name)):
                    self[var_name] = domain

                # use PDV_repo_domain-default to preference/detect domain-specific user-/group-names in local .env files
                domain = self[var_name] or is_repo_var and PDV_repo_domain or ""
                user = get_domain_user_variable(main_app, var_name, domain=domain) or ""
                var_name = f'{var_prefix}user'
                if var_name not in self and user:
                    self[var_name] = user

                for var_suffix in ['token'] + (['group'] if is_repo_var else []):  # no upstream groups on web hosts
                    var_name = f'{var_prefix}{var_suffix}'
                    if var_name not in self and (
                            var_val := get_domain_user_variable(main_app, var_name, domain=domain, user=user)):
                        self[var_name] = var_val

            if env_values:
                self.disable_non_string_fetch_warning = True
                deep_dict_update(self, env_values, overwrite=False)
                self.disable_non_string_fetch_warning = False

    def _init_pdv(self, var_values: dict[str, Any]):    # pylint: disable=too-many-branches,too-many-statements
        self.update(var_values)

        project_path = self['project_path'] = norm_path(self['project_path'] or self['project_name'])
        if not self['project_name']:
            self['project_name'] = os_path_basename(project_path)
        project_name = self['project_name']
        self['parent_folder'] = os_path_basename(os_path_dirname(project_path))
        if 'remote_urls' not in self:
            self['remote_urls'] = git_remotes(project_path)  # early cache for _init_from_env/git_remote_domain_group()

        self._init_from_env(project_path)

        self.update({k: v for k, v in pdv_default_values().items() if k not in self})

        if not self['namespace_name']:
            self['namespace_name'] = namespace_guess(project_path)
        namespace_name = self['namespace_name']
        if 'portion_name' not in self:
            self['portion_name'] = project_name[len(namespace_name) + 1:] if namespace_name else ""
        portion_name = self['portion_name']
        if 'import_name' not in self:
            self['import_name'] = f"{namespace_name}.{portion_name}" if namespace_name else project_name
        import_name = self['import_name']
        if 'version_file' not in self:  # needed by _init_project_type(), so use main_file_path() on given project_type
            file_path = project_main_file(import_name, project_path=project_path)
            if not file_path and self['project_type']:
                file_path = main_file_path(project_path, self['project_type'], namespace_name=namespace_name)
            self['version_file'] = file_path
        version_file = self['version_file']
        if 'project_type' not in self:
            self['project_type'] = self._init_project_type()
        project_type = self['project_type']

        if 'project_version' not in self:
            self['project_version'] = code_file_version(version_file)
        if 'package_path' not in self:
            self['package_path'] = os_path_join(project_path, *namespace_name.split("."), portion_name)
        if 'package_data' not in self:
            self['package_data'] = self._find_package_data()
        if 'pip_name' not in self and project_type in ANY_PRJ_TYPE:
            self['pip_name'] = project_name.replace('_', '-')
        if 'project_packages' not in self:
            if namespace_name:
                find_packages_include = [namespace_name + (".*" if project_type in (PACKAGE_PRJ, ROOT_PRJ) else "")]
                self['project_packages'] = find_namespace_packages(where=project_path, include=find_packages_include)
            else:
                self['project_packages'] = find_packages(where=project_path)
        if 'project_desc' not in self:
            if namespace_name:
                project_desc = f"{namespace_name} {project_type}" if project_type == ROOT_PRJ else \
                    f"{namespace_name} namespace {project_type} portion {portion_name}"
            else:
                project_desc = f"{project_name} {project_type}"
            self['project_desc'] = f"{project_desc}: {code_file_title(version_file)}"

        if 'setup_kwargs' not in self:
            self['setup_kwargs'] = {}
        if 'name' not in self.pdv_val('setup_kwargs'):
            self.pdv_val('setup_kwargs')['name'] = project_name

    def _init_project_type(self) -> str:
        """ determine project type from project_path, project_name, namespace_name, portion_name and version_file. """
        project_name = self['project_name']
        project_path = self['project_path']
        version_file = self['version_file']
        namespace_name = self['namespace_name']

        if project_name.endswith('_playground'):
            project_type = PLAYGROUND_PRJ
        elif os_path_isfile(os_path_join(project_path, self['BUILD_CONFIG_FILE'])):
            project_type = APP_PRJ
        elif os_path_isfile(os_path_join(project_path, 'manage.py')):
            project_type = DJANGO_PRJ
        elif project_name == namespace_name + '_' + namespace_name:
            project_type = ROOT_PRJ
        elif os_path_basename(version_file) == PY_INIT:
            project_type = PACKAGE_PRJ
        elif os_path_basename(version_file) in (project_name + PY_EXT, self['portion_name'] + PY_EXT):
            project_type = MODULE_PRJ
        elif os_path_basename(project_path) in self.pdv_val('PARENT_FOLDERS'):
            project_type = PARENT_PRJ
        else:
            project_type = NO_PRJ

        return project_type

    def _load_descriptions(self):
        """ load long description from the README file of the project.

        :param self:                 dict of project development variables with a `'project_path'` key.
        """
        path = self['project_path']
        if os_path_isfile(file := os_path_join(path, 'README.rst')):
            self['long_desc_type'] = 'text/x-rst'
            self['long_desc_content'] = read_file(file)
        elif os_path_isfile(file := os_path_join(path, 'README.md')):
            self['long_desc_type'] = 'text/markdown'
            self['long_desc_content'] = read_file(file)

    def _load_requirements(self):
        """ load requirements from the available requirements.txt file(s) of this project.

        :param self:                project development variables instance with the following required project dev vars:
                                    DOCS_FOLDER, REQ_FILE_NAME, REQ_DEV_FILE_NAME, TESTS_FOLDER,
                                    namespace_name, project_name, project_path.

                                    the project env vars overwritten in this argument by this function are:
                                    dev_requires, docs_requires, install_requires, portions_packages, tests_requires.
        """

        def _package_list(req_file: str) -> list[str]:
            packages: list[str] = []
            if os_path_isfile(req_file):
                packages.extend(line.strip().split(' ')[0]      # remove options, keep version number
                                for line in read_file(req_file).split('\n')
                                if line.strip()                 # exclude empty lines
                                and not line.startswith('#')    # exclude comments
                                and not line.startswith('-')    # exclude -r/-e <req_file> lines
                                )
            return packages

        namespace_name = self['namespace_name']
        project_name = self['project_name']
        project_path = self['project_path']
        req_file_name = self['REQ_FILE_NAME']

        if 'dev_requires' not in self:
            self['dev_requires'] = _package_list(os_path_join(project_path, self['REQ_DEV_FILE_NAME']))
        dev_requires = self.pdv_val('dev_requires')

        if 'portions_packages' not in self:
            pre = f'{namespace_name}_'
            self['portions_packages'] = [_ for _ in dev_requires if _.startswith(pre) and _ != pre + namespace_name]
        if 'docs_requires' not in self:
            self['docs_requires'] = _package_list(os_path_join(project_path, self['DOCS_FOLDER'], req_file_name))
        if 'install_requires' not in self:
            self['install_requires'] = _package_list(os_path_join(project_path, req_file_name))
        if 'tests_requires' not in self:
            self['tests_requires'] = _package_list(os_path_join(project_path, self['TESTS_FOLDER'], req_file_name))
        if 'editable_project_path' not in self:
            self['editable_project_path'] = editable_project_root_path(project_name)

    # public methods ==================================================================================================

    def as_dict(self) -> dict[str, Any]:
        """ extract project development variable values as a dictionary. """
        return super().copy()

    def copy(self) -> "ProjectDevVars":
        """ create a copy of this ProjectDevVars instance. """
        dict_data = super().copy()
        dict_data.pop('project_name')
        return ProjectDevVars(**dict_data)

    def errors(self, completeness: bool = False):
        """ checks the integrity of the project development variable values.

        :return:                    a list of error/warning messages.
        """
        errors = []

        if completeness and not self['AUTHOR']:
            errors.append("author name is missing - specify via PDV_AUTHOR in OS environment or config file")
        if completeness and not self['AUTHOR_EMAIL']:
            errors.append("author email address is missing - specify aa PDV_AUTHOR_EMAIL in OS environment/config file")

        project_type = self['project_type']
        if project_type not in ALL_PRJ_TYPES:
            errors.append(f"invalid project type {project_type}; allowed types: {ALL_PRJ_TYPES}")
        if project_type == NO_PRJ:
            return errors
        if project_type not in (MODULE_PRJ, PACKAGE_PRJ, ROOT_PRJ) and self['namespace_name']:
            errors.append(f"{project_type} projects does not have/allow a {self['namespace_name']=}")

        project_path = self['project_path']
        if project_path != norm_path(project_path):
            errors.append(f"project path {project_path} is not normalized; expected {norm_path(project_path)}")

        parent_folders = self.pdv_val('PARENT_FOLDERS')
        parent_folder = os_path_basename(project_path) if project_type == PARENT_PRJ else self['parent_folder']
        if parent_folder not in parent_folders:
            errors.append(f"parent folder name {parent_folder} not in {parent_folders=}; extend via PDV_PARENT_FOLDERS")

        if project_type == ROOT_PRJ and not self['namespace_name']:
            errors.append(f"new namespace root project at {project_path=} expects --namespace_name command line option")

        if project_type != PARENT_PRJ and os_path_basename(project_path) != self['project_name']:
            errors.append(f"invalid project name {self['project_name']}; expected {os_path_basename(project_path)}")

        return errors

    def pdv_val(self, var_name: str) -> Any:
        """ determine the project development variable value from this instance of their default value.

        :param var_name:            name of the variable to determine the value of.
        :return:                    project dev var value (mostly not of type str)
                                    or an empty string if variable is not defined.
        """
        if var_name in self:
            return super().__getitem__(var_name)
        return ""
