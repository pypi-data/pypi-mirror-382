""" unit tests for the ae.dev_ops portion. """
import os
import shutil
import sys
import warnings

from unittest.mock import patch

import pytest
import setuptools

from packaging.version import Version

from tests.conftest import skip_gitlab_ci

from ae.base import (
    BUILD_CONFIG_FILE, DEF_PROJECT_PARENT_FOLDER, DOCS_FOLDER, PACKAGE_INCLUDE_FILES_PREFIX,
    PY_CACHE_FOLDER, PY_EXT, PY_INIT, TEMPLATES_FOLDER, TESTS_FOLDER,
    in_wd, norm_path, os_path_basename, os_path_dirname, os_path_isdir, os_path_isfile, os_path_join, os_path_relpath,
    read_file, write_file)
from ae.shell import COMMIT_MSG_FILE_NAME, active_venv, in_venv, git_clone
from ae.templates import TEMPLATE_PLACEHOLDER_ID_PREFIX, template_version_option

from ae.dev_ops import (
    APP_PRJ, DJANGO_PRJ, MODULE_PRJ, NO_PRJ, PACKAGE_PRJ, PARENT_PRJ, PLAYGROUND_PRJ, ROOT_PRJ,
    ENV_VAR_NAME_PREFIX,
    PDV_MIN_PYTHON_VERSION, PDV_NULL_VERSION, PDV_PARENT_FOLDERS, PDV_repo_domain,
    PDV_REQ_FILE_NAME, PDV_REQ_DEV_FILE_NAME, PDV_TEMPLATES_FOLDER,
    VERSION_PREFIX, VERSION_QUOTE,
    ProjectDevVars,
    code_file_title, code_file_version, code_version, editable_project_root_path, find_extra_modules,
    increment_version, latest_remote_version, main_file_path, namespace_guess, pdv_env_values, pdv_default_values,
    project_owner_name_version, replace_file_version, root_packages_masks, skip_files_lean_web, skip_files_migrations)


class TestHelpers:
    """ test helper functions """
    def test_code_file_title(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_code_title.py')
        title_str = "this is an example of a code file title string"

        write_file(tst_file, f'''""" {title_str}\n\n    docstring body start here..."""\n''')
        assert code_file_title(tst_file) == title_str

        write_file(tst_file, f'''"""\n{title_str}\n====================\n    docstring body start here..."""\n''')
        assert code_file_title(tst_file) == title_str

    def test_code_file_title_invalid_file_content(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_code_title.py')
        write_file(tst_file, "")                       # empty file
        assert not code_file_title(tst_file)

        write_file(tst_file, "\n\n this is no docstring and no title")    # invalid docstring/title
        assert not code_file_title(tst_file)

    def test_code_file_title_invalid_file_name(self):
        assert not code_file_title('::invalid_file_name::')

    def test_code_file_version(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_code_version.py')
        version_str = '33.22.111pre'
        write_file(tst_file, f"{VERSION_PREFIX}{version_str}{VERSION_QUOTE}  # comment\nversion = '9.6.3'")
        assert code_file_version(tst_file) == version_str

    def test_code_file_version_invalid_file_content(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_code_version.py')
        write_file(tst_file, "")                       # empty file
        assert not code_file_version(tst_file)

        write_file(tst_file, "version__ = '1.2.3'")    # invalid version var prefix
        assert not code_file_version(tst_file)

    def test_code_file_version_invalid_file_name(self):
        assert not code_file_version('::invalid_file_name::')

    def test_code_version(self):
        version = '333.222.111dev'
        assert code_version(VERSION_PREFIX + version + VERSION_QUOTE) == version
        assert code_version(f"\n\n\n{VERSION_PREFIX}{version}{VERSION_QUOTE}\n\n\n") == version
        content = f"{VERSION_PREFIX}{version}{VERSION_QUOTE}  # comment\nversion = '9.6.3'"
        assert code_version(content) == version
        assert code_version(content.encode('utf-8')) == version

    def test_code_version_args(self):
        version = '999.333.111pre'
        assert code_version("    " + VERSION_PREFIX + version + VERSION_QUOTE) == ""
        assert code_version("    " + VERSION_PREFIX + version + VERSION_QUOTE, prefix=VERSION_PREFIX) == version

        assert code_version("\n\n    version: " + version, prefix="version: ", suffix="") == ""  # empty quote not valid
        assert code_version("\n\n    version: " + version, prefix="version: ", suffix="pre") == version[:-3]

    def test_code_version_errors(self):
        assert code_version("") == ""
        assert code_version("all but a  v-e_r.s;i:o,n") == ""

        # noinspection PyTypeChecker
        assert code_version(None) == ""

        with pytest.raises(TypeError):
            # noinspection PyArgumentList
            assert code_version() == ""

    def test_editable_project_root_path(self, tmp_path, monkeypatch):
        pkg_name = 'tst_pkg_editable'
        root_dir = 'any_prj_root_folder'
        egg_link_file = os_path_join(str(tmp_path), pkg_name + '.egg-link')
        monkeypatch.setattr(sys, 'path', [str(tmp_path)] + list(sys.path))
        write_file(egg_link_file, root_dir)

        assert editable_project_root_path(pkg_name) == root_dir

    @skip_gitlab_ci
    def test_editable_project_root_path_local(self):
        if active_venv().startswith('aedev3'):
            assert not editable_project_root_path('ae_base')
        else:
            assert not editable_project_root_path('aedev_project_tpls')
        with in_venv('ae312'):
            assert editable_project_root_path('ae_base')
        with in_venv('aedev39'):
            prj = 'aedev_project_manager'
            assert editable_project_root_path(prj) == norm_path(os_path_join("~", DEF_PROJECT_PARENT_FOLDER, prj))

    def test_find_extra_modules(self):
        assert 'setup' in find_extra_modules("", TEMPLATES_FOLDER)
        assert 'setup' in find_extra_modules(os.getcwd(), TESTS_FOLDER)
        assert 'ae.dev_ops' in find_extra_modules("", "")
        assert 'tests.test_dev_ops' in find_extra_modules("", "")
        assert 'dev_ops' in find_extra_modules(os_path_join(os.getcwd(), 'ae'), "")
        assert find_extra_modules(os_path_join(os.getcwd(), 'ae'), "") == ['dev_ops']
        assert find_extra_modules(os_path_join(os.getcwd(), 'ae', 'dev_ops'), "") == []

    def test_find_extra_modules_with_py_init(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), PDV_PARENT_FOLDERS[0])
        tst_mod = "tst_mod"
        write_file(os_path_join(parent_dir, PY_INIT), "# test __init__.py", make_dirs=True)
        write_file(os_path_join(parent_dir, tst_mod + PY_EXT), "# test module")

        assert 'setup' in find_extra_modules("", "")
        assert 'ae.dev_ops' in find_extra_modules("", "")
        assert find_extra_modules(parent_dir, "") == [tst_mod]

    def test_increment_version(self):
        assert increment_version("") == ""
        assert increment_version("0.0.1") == "0.0.2"
        assert increment_version("9999.9999.9999") == "9999.9999.10000"

        assert increment_version(PDV_NULL_VERSION, increment_part=0) == PDV_NULL_VERSION
        assert increment_version(PDV_NULL_VERSION, increment_part=1) == "1.3.0"
        assert increment_version(PDV_NULL_VERSION, increment_part=2) == "0.4.0"
        # noinspection PyArgumentEqualDefault
        assert increment_version(PDV_NULL_VERSION, increment_part=3) == "0.3.1"

        assert increment_version(("0", "1", "2"), increment_part=0) == "0.1.2"
        assert increment_version(("0", "1", "2"), increment_part=1) == "1.1.2"
        assert increment_version(("0", "1", "2"), increment_part=2) == "0.2.2"
        assert increment_version(("0", "1", "2")) == "0.1.3"

        assert increment_version(PDV_NULL_VERSION, increment_part=-1) == PDV_NULL_VERSION
        assert increment_version(PDV_NULL_VERSION, increment_part=4) == PDV_NULL_VERSION

    def test_ini_pdv_without_version_file(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, "tst_prj")

        pdv = ProjectDevVars(project_path=project_path, project_type=PACKAGE_PRJ)

        assert pdv['version_file'].endswith(PY_INIT)

    def test_ini_pdv_manuals_include(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, "tst_prj")
        docs_manual = os_path_join(project_path, DOCS_FOLDER, 'man', 'sub_dir', 'tst.rst')
        write_file(docs_manual, "# dummy RST manual", make_dirs=True)

        pdv = ProjectDevVars(project_path=project_path)

        assert 'man' + "/" + 'sub_dir' + "/" + 'tst.rst' in pdv['manuals_include']

    def test_ini_pdv_repo_user(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, "tst_prj")
        os.makedirs(project_path)

        pdv = ProjectDevVars(project_path=project_path)

        assert not pdv['repo_user']

        with patch('ae.dev_ops.get_domain_user_variable', return_value='UsaNam'):
            pdv = ProjectDevVars(project_path=project_path)

        assert pdv['repo_user'] == 'UsaNam'

    def test_latest_remote_version(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        os.makedirs(parent_dir)
        project_path = git_clone("https://gitlab.com/ae-group", 'ae_base',
                                 branch_or_tag="v0.3.60", parent_path=parent_dir)
        assert project_path
        pdv = ProjectDevVars(project_path=project_path)     # 1st clone done only to determine the latest remote version

        remote_ver = latest_remote_version(pdv, increment_part=0)

        assert Version(remote_ver)

        shutil.rmtree(project_path)                         # prepare 2nd clone with latest version
        project_path = git_clone("https://gitlab.com/ae-group", 'ae_base',
                                 branch_or_tag=f"v{remote_ver}", parent_path=parent_dir)
        assert project_path, f"git_clone-error {remote_ver=}"
        pdv = ProjectDevVars(project_path=project_path)

        assert Version(latest_remote_version(pdv)) > Version(pdv['NULL_VERSION'])
        assert Version(latest_remote_version(pdv)) > Version(pdv['project_version'])
        assert Version(remote_ver) == Version(pdv['project_version'])
        assert remote_ver == pdv['project_version']

        # test also the local version of ae.base if available in a sister project root
        if os_path_isdir(project_path := os_path_join("..", 'ae_base')):
            pdv = ProjectDevVars(project_path=project_path)

            assert Version(latest_remote_version(pdv)) > Version(pdv['NULL_VERSION'])
            assert Version(latest_remote_version(pdv)) > Version(pdv['project_version'])
            assert Version(latest_remote_version(pdv, increment_part=0)) == Version(pdv['project_version'])

    def test_main_file_path(self):
        cwd = os.getcwd()

        assert main_file_path("prj", APP_PRJ) == os_path_join(cwd, "prj", 'main' + PY_EXT)
        assert main_file_path("prj", DJANGO_PRJ) == os_path_join(cwd, "prj", "prj", PY_INIT)
        assert main_file_path("prj", MODULE_PRJ) == os_path_join(cwd, "prj", "prj" + PY_EXT)
        assert main_file_path("prj", NO_PRJ) == os_path_join(cwd, "prj", "prj" + PY_EXT)
        assert main_file_path("prj", PACKAGE_PRJ) == os_path_join(cwd, "prj", "prj", PY_INIT)
        assert main_file_path("prj", PARENT_PRJ) == os_path_join(cwd, "prj", "prj" + PY_EXT)
        assert main_file_path("prj", PLAYGROUND_PRJ) == os_path_join(cwd, "prj", "prj" + PY_EXT)
        assert main_file_path("nsn_nsn", ROOT_PRJ, "nsn") == os_path_join(cwd, "nsn_nsn", "nsn", "nsn", PY_INIT)

        assert main_file_path("prj", APP_PRJ, "nsn") == os_path_join(cwd, "prj", "nsn", 'main' + PY_EXT)
        assert main_file_path("nsn_prj", DJANGO_PRJ, "nsn") == os_path_join(cwd, "nsn_prj", "nsn", "prj", PY_INIT)
        assert main_file_path("nsn_prj", MODULE_PRJ, "nsn") == os_path_join(cwd, "nsn_prj", "nsn", "prj" + PY_EXT)
        assert main_file_path("nsn_prj", NO_PRJ, "nsn") == os_path_join(cwd, "nsn_prj", "nsn", "prj" + PY_EXT)
        assert main_file_path("nsn_prj", PACKAGE_PRJ, "nsn") == os_path_join(cwd, "nsn_prj", "nsn", "prj", PY_INIT)
        assert main_file_path("nsn_prj", PARENT_PRJ, "nsn") == os_path_join(cwd, "nsn_prj", "nsn", "prj" + PY_EXT)
        assert main_file_path("nsn_prj", PLAYGROUND_PRJ, "nsn") == os_path_join(cwd, "nsn_prj", "nsn", "prj" + PY_EXT)
        assert main_file_path("nsn_nsn", ROOT_PRJ, "nsn") == os_path_join(cwd, "nsn_nsn", "nsn", "nsn", PY_INIT)

    def test_namespace_guess_fail(self):
        assert namespace_guess(TESTS_FOLDER) == ""  # invalid project root dir
        assert namespace_guess("not_existing_project_dir") == ""

    def test_namespace_guess_portion(self, tmp_path):
        namespace = 'yz'
        portion_name = 'portion_name'
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_name = namespace + "_" + portion_name
        project_path = os_path_join(parent_dir, project_name)
        namespace_dir = os_path_join(project_path, namespace)
        os.makedirs(namespace_dir)
        main_file = os_path_join(namespace_dir, portion_name + PY_EXT)
        write_file(main_file, "# main file of module portion")

        assert namespace_guess(project_path) == namespace

        os.remove(main_file)

        portion_dir = os_path_join(namespace_dir, portion_name)
        os.makedirs(portion_dir)
        main_file = os_path_join(namespace_dir, "__init__" + PY_EXT)
        write_file(main_file, "# main file of package portion")

        assert namespace_guess(project_path) == namespace

    def test_namespace_guess_project(self):
        assert namespace_guess("") == 'ae'
        assert namespace_guess(os.getcwd()) == 'ae'

    def test_namespace_guess_root(self, tmp_path):
        namespace = 'xz'
        parent_dir = os_path_join(tmp_path, DEF_PROJECT_PARENT_FOLDER)
        project_path = por_dir = os_path_join(parent_dir, namespace + "_" + namespace)
        os.makedirs(por_dir)

        main_file = os_path_join(por_dir, namespace + PY_EXT)
        write_file(main_file, "# main file of non-namespace module")

        assert not namespace_guess(project_path)

        os.remove(main_file)

        main_file = os_path_join(por_dir, "main" + PY_EXT)
        write_file(main_file, "# main file of non-namespace project")

        assert not namespace_guess(project_path)

        os.remove(main_file)

        main_file = os_path_join(por_dir, "__init__" + PY_EXT)
        write_file(main_file, "# main file of non-namespace package")

        assert not namespace_guess(project_path)

        os.remove(main_file)

        por_dir = os_path_join(por_dir, namespace)
        os.makedirs(por_dir)

        main_file = os_path_join(por_dir, namespace + PY_EXT)
        write_file(main_file, "# main file of namespace root module")

        assert namespace_guess(project_path) == namespace

        os.remove(main_file)

        main_file = os_path_join(por_dir, "main" + PY_EXT)
        write_file(main_file, "# main file of namespace root main")

        assert namespace_guess(project_path) == namespace

        os.remove(main_file)

        por_dir = os_path_join(por_dir, namespace)
        os.makedirs(por_dir)
        main_file = os_path_join(por_dir, "__init__" + PY_EXT)
        write_file(main_file, "# main file of namespace root package")

        assert namespace_guess(project_path) == namespace

    def test_pdv_default_values(self):
        values = pdv_default_values()

        assert 'COMMIT_MSG_FILE_NAME' in values                     # from ae.shell
        assert values['COMMIT_MSG_FILE_NAME'] == COMMIT_MSG_FILE_NAME

        assert 'DOCS_FOLDER' in values                              # from ae.base
        assert values['DOCS_FOLDER'] == DOCS_FOLDER

        assert 'PARENT_FOLDERS' in values                           # from ae.dev_ops
        assert values['PARENT_FOLDERS'] == PDV_PARENT_FOLDERS

        assert 'TEMPLATE_PLACEHOLDER_ID_PREFIX' in values           # from ae.templates
        assert values['TEMPLATE_PLACEHOLDER_ID_PREFIX'] == TEMPLATE_PLACEHOLDER_ID_PREFIX

        assert 'TEMPLATE_PLACEHOLDER_ID_SUFFIX' in values
        assert 'TEMPLATE_PLACEHOLDER_ARGS_SUFFIX' in values
        assert 'TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID' in values
        assert 'TEMPLATE_REPLACE_WITH_PLACEHOLDER_ID' in values

        assert len(values) == 30  # adapted on remove, e.g. empty-vars PDV_AUTHOR, PDV_AUTHOR_EMAIL, PDV_DOCS_SUB_DOMAIN

    def test_pdv_env_values_dict(self, monkeypatch):
        dict_var = ENV_VAR_NAME_PREFIX + "DICT_VAR"
        dict_val = {'key': 1, 'key2': 'str_val'}
        monkeypatch.setenv(dict_var, repr(dict_val))

        values = pdv_env_values()

        assert values[dict_var[len(ENV_VAR_NAME_PREFIX):]] == dict_val

    def test_pdv_env_values_list(self, monkeypatch):
        list_var = ENV_VAR_NAME_PREFIX + "ListVar"
        list_val = ['item1', 2, (3, 3, 3)]
        monkeypatch.setenv(list_var, repr(list_val))

        values = pdv_env_values()

        assert values[list_var[len(ENV_VAR_NAME_PREFIX):]] == list_val

    def test_pdv_env_values_set(self, monkeypatch):
        set_var = ENV_VAR_NAME_PREFIX + "set_var"
        set_val = {'item1', 2, (3, 3, 3)}
        monkeypatch.setenv(set_var, repr(set_val))

        values = pdv_env_values()

        assert values[set_var[len(ENV_VAR_NAME_PREFIX):]] == set_val

    def test_pdv_env_values_str(self, monkeypatch):
        str_var1 = ENV_VAR_NAME_PREFIX + "StrVar1"
        str_val1 = "StrVar1-repr-Value"
        monkeypatch.setenv(str_var1, repr(str_val1))

        str_var2 = ENV_VAR_NAME_PREFIX + "str_var2"
        str_val2 = "StrVar2-Value"
        monkeypatch.setenv(str_var2, str_val2)

        values = pdv_env_values()

        assert values[str_var1[len(ENV_VAR_NAME_PREFIX):]] == str_val1
        assert values[str_var2[len(ENV_VAR_NAME_PREFIX):]] == str_val2

    def test_pdv_env_values_tuple(self, monkeypatch):
        tuple_var = ENV_VAR_NAME_PREFIX + "Tuple_var"
        tuple_val = ('item1', 2, {3, 6, 9})
        monkeypatch.setenv(tuple_var, repr(tuple_val))

        values = pdv_env_values()

        assert values[tuple_var[len(ENV_VAR_NAME_PREFIX):]] == tuple_val

    def test_project_owner_name_version(self):
        assert project_owner_name_version('project') == ("", 'project', "")
        assert project_owner_name_version("project==3.3.3") == ("", "project", "3.3.3")
        assert project_owner_name_version('prj' + "==" + '1.2.3') == ("", 'prj', '1.2.3')
        assert project_owner_name_version("owner/project==1.2.3") == ("owner", "project", "1.2.3")

        assert project_owner_name_version('prj', owner_default='ow', version_default='2.3.4') == ('ow', 'prj', '2.3.4')
        assert project_owner_name_version("prj==1.2.3", owner_default='owner') == ('owner', "prj", "1.2.3")
        assert project_owner_name_version("ow/prj==1.2.3", owner_default='owner') == ('ow', "prj", "1.2.3")
        assert project_owner_name_version("project==1.2.3", namespace_default="xyz") == ("", "xyz_project", "1.2.3")
        assert project_owner_name_version("xyz_prj==1.2.3", namespace_default="xyz") == ("", "xyz_prj", "1.2.3")

    def test_replace_file_version_invalid_file(self):
        err = replace_file_version('::invalid_file_name::')
        assert err

    def test_replace_file_version_empty_file(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_replace_file_ver' + PY_EXT)
        write_file(tst_file, "")
        err = replace_file_version(tst_file)
        assert err

    def test_replace_file_version_multi_version(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_replace_file_ver' + PY_EXT)
        write_file(tst_file, f"__version__ = '1.2.3'{os.linesep}__version__ = '2.3.4'")
        err = replace_file_version(tst_file)
        assert err

    def test_replace_file_version_major(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_replace_file_ver' + PY_EXT)
        write_file(tst_file, f"__version__ = '1.2.3'{os.linesep}")

        err = replace_file_version(tst_file, increment_part=1)

        assert not err

        content = read_file(tst_file)
        assert "__version__ = '1.2.3'" not in content
        assert "__version__ = '2.2.3'" in content

    def test_replace_file_version_minor(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_replace_file_ver' + PY_EXT)
        write_file(tst_file, f"__version__ = '1.2.3'{os.linesep}{os.linesep}version = '2.3.4'")

        err = replace_file_version(tst_file, increment_part=2)

        assert not err

        content = read_file(tst_file)
        assert "__version__ = '1.2.3'" not in content
        assert "__version__ = '1.3.3'" in content

    def test_replace_file_version_build(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_replace_file_ver' + PY_EXT)
        write_file(tst_file, f"__version__ = '1.2.3'{os.linesep}version = '2.3.4'")

        err = replace_file_version(tst_file)

        assert not err

        content = read_file(tst_file)
        assert "__version__ = '1.2.3'" not in content
        assert "__version__ = '1.2.4'" in content

    def test_replace_file_version_remove_suffix(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_replace_file_ver' + PY_EXT)
        write_file(tst_file, f"__version__ = '1.2.3pre'{os.linesep}version = '2.3.4'")

        err = replace_file_version(tst_file, increment_part=2)

        assert not err

        content = read_file(tst_file)
        assert "__version__ = '1.2.3'" not in content
        assert "__version__ = '1.3.3'" in content

    def test_replace_file_version_keeping_comment(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_replace_file_ver' + PY_EXT)
        comment_str = "  # comment string"
        write_file(tst_file, f"__version__ = '1.2.3'{comment_str}{os.linesep}version = '2.3.4'")

        err = replace_file_version(tst_file, increment_part=1)

        assert not err

        content = read_file(tst_file)
        assert f"__version__ = '2.2.3'{comment_str}" in content

    def test_replace_file_version(self, tmp_path):
        tst_file = os_path_join(str(tmp_path), 'test_replace_file_ver' + PY_EXT)
        write_file(tst_file, f"__version__ = '1.2.3'{os.linesep}")

        err = replace_file_version(tst_file, version='1.2.6')

        assert not err

        content = read_file(tst_file)
        assert "__version__ = '1.2.3'" not in content
        assert "__version__ = '1.2.7'" in content

    def test_root_packages_masks(self):
        assert root_packages_masks(['x']) == ['x/**/*']

        assert root_packages_masks(['x.y.z']) == ['x/**/*']

        assert root_packages_masks(('x.y.z', 'x.a.b.d')) == ['x/**/*']

        assert set(root_packages_masks(['x.y.z', 'a.b.d'])) == {'x/**/*', 'a/**/*'}

    def test_skip_files_migrations(self):
        assert skip_files_migrations(os_path_join('migrations'))
        assert skip_files_migrations(os_path_join('migrations', "any filename"))
        assert skip_files_migrations(os_path_join("any folder-name", 'migrations'))
        assert skip_files_migrations(os_path_join("any folder-name", 'migrations', "any filename"))

    def test_skip_files_lean_web(self):
        assert skip_files_lean_web(os_path_join("any_pkg", PY_CACHE_FOLDER, "any_filename"))
        assert skip_files_lean_web(os_path_join("any_pkg", 'migrations', "any_filename"))
        assert skip_files_lean_web(os_path_join("any_pkg", 'static', "any_filename"))
        assert skip_files_lean_web(os_path_join("any_pkg", "any_i18n_dir", "any_filename" + '.po'))

        assert not skip_files_lean_web(os_path_join('static', "any_file.ext"))


class TestProjectDevVars:
    """ test ProjectDevVars """
    def test_app_env(self, tmp_path):
        file_name = os_path_join(str(tmp_path), BUILD_CONFIG_FILE)
        write_file(file_name, "spec")

        pdv = ProjectDevVars(project_path=str(tmp_path))

        assert pdv['namespace_name'] == ""
        assert pdv['project_name'] == os_path_basename(tmp_path)
        assert pdv['project_type'] == APP_PRJ

    def test_app_options_namespace_module(self, tmp_path):
        nsn = 'abc'
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        portion_name = 'tst_ns_mod'
        project_path = os_path_join(parent_dir, nsn + '_' + portion_name)
        module_path = os_path_join(project_path, nsn, portion_name + PY_EXT)
        app_options = {'repo_group': "tst_grp",
                       template_version_option(nsn + '.' + nsn): ""}

        os.makedirs(os_path_dirname(module_path))
        write_file(module_path, f"mod_content = ''{os.linesep}__version__ = '3.3.3'{os.linesep}")

        pdv = ProjectDevVars(project_path=project_path, **app_options)

        assert pdv['namespace_name'] == nsn
        assert pdv['project_name'] == nsn + '_' + portion_name
        assert pdv['package_path'] == os_path_join(norm_path(project_path), nsn, portion_name)
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_type'] == MODULE_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert pdv['version_file'] == norm_path(module_path)

        pdv = ProjectDevVars(project_path=parent_dir, **app_options)

        assert pdv['namespace_name'] == ""
        assert pdv['project_name'] == os_path_basename(parent_dir)
        assert pdv['project_path'] == norm_path(parent_dir)
        assert pdv['project_type'] == PARENT_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert f"{nsn}_{portion_name}" in pdv.pdv_val('children_project_vars')
        assert 'portions_import_names' not in pdv

    def test_app_options_namespace_package(self, tmp_path):
        nsn = 'efg'
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        portion_name = 'tst_ns_pkg'
        project_path = os_path_join(parent_dir, nsn + '_' + portion_name)
        package_path = os_path_join(project_path, nsn, portion_name)
        app_options = {'repo_group': "tst_grp",
                       template_version_option(nsn + '.' + nsn): ""}

        os.makedirs(package_path)
        write_file(os_path_join(package_path, PY_INIT),
                   f"pkg_ini_content = ''{os.linesep}__version__ = '6.3.6'{os.linesep}")

        pdv = ProjectDevVars(project_path=project_path, **app_options)

        assert pdv['namespace_name'] == nsn
        assert pdv['project_name'] == nsn + '_' + portion_name
        assert pdv['package_path'] == norm_path(package_path)
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_type'] == PACKAGE_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert pdv['version_file'] == norm_path(os_path_join(package_path, PY_INIT))

        app_options['namespace_name'] = nsn

        pdv = ProjectDevVars(project_path=project_path, **app_options)

        assert pdv['namespace_name'] == nsn
        assert pdv['project_name'] == nsn + '_' + portion_name
        assert pdv['package_path'] == norm_path(package_path)
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_type'] == PACKAGE_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert pdv['version_file'] == norm_path(os_path_join(package_path, PY_INIT))

        app_options['namespace_name'] = ""

        pdv = ProjectDevVars(project_path=parent_dir, **app_options)

        assert pdv['namespace_name'] == ""
        assert pdv['project_name'] == os_path_basename(parent_dir)
        assert pdv['project_path'] == norm_path(parent_dir)
        assert pdv['project_type'] == PARENT_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert f"{nsn}_{portion_name}" in pdv.pdv_val('children_project_vars')
        assert 'portions_import_names' not in pdv

    def test_app_options_namespace_root(self, tmp_path):
        nsn = 'hij'
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, nsn + '_' + nsn)
        package_path = os_path_join(project_path, nsn, nsn)
        app_options = {'repo_group': "tst_grp",
                       template_version_option(nsn + '.' + nsn): ""}

        os.makedirs(package_path)
        write_file(os_path_join(package_path, PY_INIT),
                   f"root_content = ''{os.linesep}__version__ = '9.9.3'{os.linesep}")

        pdv = ProjectDevVars(project_path=project_path, **app_options)

        assert pdv['namespace_name'] == nsn
        assert pdv['project_name'] == nsn + '_' + nsn
        assert pdv['package_path'] == norm_path(package_path)
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_type'] == ROOT_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert pdv['version_file'] == norm_path(os_path_join(package_path, PY_INIT))
        assert not pdv.pdv_val('children_project_vars')
        assert not pdv.pdv_val('portions_import_names')

        app_options['namespace_name'] = nsn

        pdv = ProjectDevVars(project_path=project_path, **app_options)

        assert pdv['namespace_name'] == nsn
        assert pdv['project_name'] == nsn + '_' + nsn
        assert pdv['package_path'] == norm_path(package_path)
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_type'] == ROOT_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert pdv['version_file'] == norm_path(os_path_join(package_path, PY_INIT))
        assert not pdv.pdv_val('children_project_vars')
        assert not pdv.pdv_val('portions_import_names')

        app_options['namespace_name'] = ""

        pdv = ProjectDevVars(project_path=parent_dir, **app_options)

        assert pdv['namespace_name'] == ""
        assert pdv['project_name'] == os_path_basename(parent_dir)
        assert pdv['project_path'] == norm_path(parent_dir)
        assert pdv['project_type'] == PARENT_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert f"{nsn}_{nsn}" in pdv.pdv_val('children_project_vars')
        assert 'portions_import_names' not in pdv

    def test_app_options_namespace_root_portions(self, tmp_path):
        nsn = 'uvw'
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        root_prj_path = os_path_join(parent_dir, nsn + '_' + nsn)
        root_pkg_path = os_path_join(root_prj_path, nsn, nsn)

        project_name = 'tst_ns_pkg'
        package_prj_path = os_path_join(parent_dir, nsn + '_' + project_name)
        package_pkg_path = os_path_join(package_prj_path, nsn, project_name)
        package_extra_module_name = "extra_module_name"

        module_name = 'tst_ns_module'
        module_prj_path = os_path_join(parent_dir, nsn + '_' + module_name)
        module_path = os_path_join(module_prj_path, nsn, module_name + PY_EXT)

        app_options = {'repo_group': "tst_grp",
                       template_version_option(nsn + '.' + nsn): ""}

        os.makedirs(root_pkg_path)
        write_file(os_path_join(root_pkg_path, PY_INIT),
                   f"root_content = ''{os.linesep}__version__ = '111.33.63'{os.linesep}")
        write_file(os_path_join(root_prj_path, PDV_REQ_DEV_FILE_NAME),
                   nsn + '_' + project_name + os.linesep + nsn + '_' + module_name)

        write_file(os_path_join(package_pkg_path, PY_INIT),
                   f"pkg_content = ''{os.linesep}__version__ = '999.333.636'{os.linesep}",
                   make_dirs=True)
        write_file(os_path_join(package_pkg_path, package_extra_module_name + PY_EXT), "extra_content = ''")

        os.makedirs(os_path_dirname(module_path))
        write_file(os_path_join(module_prj_path, nsn, module_name),
                   f"mod_content = ''{os.linesep}__version__ = '6.9.699'{os.linesep}")

        pdv = ProjectDevVars(project_path=root_prj_path, **app_options)

        assert pdv['namespace_name'] == nsn
        assert pdv['project_name'] == nsn + '_' + nsn
        assert pdv['package_path'] == norm_path(root_pkg_path)
        assert pdv['project_path'] == norm_path(root_prj_path)
        assert pdv['project_type'] == ROOT_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert pdv['version_file'] == norm_path(os_path_join(root_pkg_path, PY_INIT))

        assert f"{nsn}_{project_name}" in pdv.pdv_val('children_project_vars')
        assert f"{nsn}_{project_name}.{package_extra_module_name}" not in pdv.pdv_val('children_project_vars')
        assert f"{nsn}_{module_name}" in pdv.pdv_val('children_project_vars')

        assert f"{nsn}.{project_name}" in pdv.pdv_val('portions_import_names')
        assert f"{nsn}.{project_name}.{package_extra_module_name}" in pdv['portions_import_names']
        assert f"{nsn}.{module_name}" in pdv.pdv_val('portions_import_names')

        app_options['namespace_name'] = nsn

        pdv = ProjectDevVars(project_path=root_prj_path, **app_options)

        assert pdv['namespace_name'] == nsn
        assert pdv['project_name'] == nsn + '_' + nsn
        assert pdv['package_path'] == os_path_join(norm_path(root_prj_path), nsn, nsn)
        assert pdv['project_path'] == norm_path(root_prj_path)
        assert pdv['project_type'] == ROOT_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert pdv['version_file'] == norm_path(os_path_join(root_pkg_path, PY_INIT))

        assert f"{nsn}_{project_name}" in pdv.pdv_val('children_project_vars')
        assert f"{nsn}_{project_name}.{package_extra_module_name}" not in pdv.pdv_val('children_project_vars')
        assert f"{nsn}_{module_name}" in pdv.pdv_val('children_project_vars')

        assert f"{nsn}.{project_name}" in pdv.pdv_val('portions_import_names')
        assert f"{nsn}.{project_name}.{package_extra_module_name}" in pdv.pdv_val('portions_import_names')
        assert f"{nsn}.{module_name}" in pdv.pdv_val('portions_import_names')

        app_options['namespace_name'] = ""

        pdv = ProjectDevVars(project_path=parent_dir, **app_options)

        assert pdv['namespace_name'] == ""
        assert pdv['project_name'] == os_path_basename(parent_dir)
        assert pdv['project_path'] == norm_path(parent_dir)
        assert pdv['project_type'] == PARENT_PRJ
        assert pdv['repo_group'] == app_options['repo_group']
        assert f"{nsn}_{project_name}" in pdv.pdv_val('children_project_vars')
        assert f"{nsn}_{project_name}.{package_extra_module_name}" not in pdv.pdv_val('children_project_vars')
        assert f"{nsn}_{module_name}" in pdv.pdv_val('children_project_vars')
        assert 'portions_import_names' not in pdv

    def test_app_options_in_empty_project_root(self, tmp_path):
        tmp_path = str(tmp_path)
        new_pkg_name = os_path_basename(tmp_path)

        pdv = ProjectDevVars(project_path=tmp_path)

        assert 'namespace_name' in pdv
        assert pdv['namespace_name'] == ''
        assert 'project_name' in pdv
        assert pdv['project_name'] == new_pkg_name
        assert 'project_path' in pdv
        assert pdv['project_path'] == tmp_path
        assert 'project_type' in pdv
        assert pdv['project_type'] == NO_PRJ
        assert pdv['repo_group'].startswith(new_pkg_name)

    def test_app_options_in_empty_project_root_with_namespace(self, tmp_path):
        nsn = 'nsn'
        portion = 'portion_name'
        new_pkg_name = nsn + '_' + portion
        app_options = {'namespace_name': nsn}
        tmp_path = os_path_join(str(tmp_path), new_pkg_name)
        os.makedirs(tmp_path)

        pdv = ProjectDevVars(project_path=tmp_path, **app_options)

        assert pdv['namespace_name'] == nsn
        assert pdv['portion_name'] == portion
        assert pdv['project_name'] == new_pkg_name
        assert pdv['project_path'] == tmp_path
        assert pdv['project_type'] == NO_PRJ
        assert pdv['repo_group'].startswith(nsn)

    def test_app_options_in_empty_project_root_with_nsn_and_repo_group(self, tmp_path):
        nsn = 'nsn'
        portion = 'portion_name'
        new_pkg_name = nsn + '_' + portion
        app_options = {'namespace_name': nsn, 'repo_group': "tst-group"}
        tmp_path = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER, new_pkg_name)
        os.makedirs(tmp_path)

        pdv = ProjectDevVars(project_path=tmp_path, **app_options)

        assert pdv['namespace_name'] == nsn
        assert pdv['portion_name'] == portion
        assert pdv['project_name'] == new_pkg_name
        assert pdv['project_path'] == tmp_path
        assert pdv['project_type'] == NO_PRJ
        assert pdv['repo_group'] == app_options['repo_group']

    def test_as_dict(self):
        dict_val = ProjectDevVars().as_dict()
        assert isinstance(dict_val, dict)

    def test_constants_get(self):
        pdv = ProjectDevVars()
        assert pdv['docs_domain']
        assert isinstance(pdv['docs_domain'], str)
        assert pdv.pdv_val('PARENT_FOLDERS')
        assert isinstance(pdv.pdv_val('PARENT_FOLDERS'), tuple)

    def test_copy(self, tmp_path):
        with in_wd(str(tmp_path)):  # using tmp_path to prevent read of dotenv files in local project dir or above
            pdv = ProjectDevVars()
            cop = pdv.copy()
        assert isinstance(cop, ProjectDevVars)
        assert pdv == cop
        assert pdv is not cop

    def test_django_env(self, tmp_path):
        tmp_path = str(tmp_path)
        file_name = os_path_join(tmp_path, 'manage.py')
        write_file(file_name, "any content")

        pdv = ProjectDevVars(project_path=tmp_path)

        assert pdv['namespace_name'] == ""
        assert pdv['project_name'] == os_path_basename(tmp_path)
        assert pdv['project_type'] == DJANGO_PRJ

    def test_empty_setup_kwargs_doesnt_raise(self, tmp_path):
        file_name = os_path_join(str(tmp_path), 'setup' + PY_EXT)
        write_file(file_name, "pdv = {}")

        ProjectDevVars(project_path=str(tmp_path))

    def test_errors(self):
        pdv = ProjectDevVars()

        assert not pdv.errors()

    def test_errors_author_missing(self):
        pdv = ProjectDevVars()
        pdv.pop('AUTHOR', "")           # PDV_AUTHOR not needed/available on GitLab CI
        pdv.pop('AUTHOR_EMAIL', "")

        assert len(pdv.errors(completeness=True)) == 2

        pdv['AUTHOR'] = 'author name'
        pdv['AUTHOR_EMAIL'] = 'author_email_address@host.tst'

        assert not pdv.errors(completeness=True)

    def test_errors_invalid_project_type(self):
        pdv = ProjectDevVars()
        pdv['project_type'] = "any invalid project type"

        assert pdv.errors()

        pdv['project_type'] = NO_PRJ

        assert not pdv.errors()

        # only module|package|root project types are allowed as namespace portion/root projects, only NO_PRJ skips tests

        pdv['namespace_name'] = "any_namespace"     # actually not needed because pdv has already ae namespace

        assert not pdv.errors()                     # check skipped because of NO_PRJ

        pdv['project_type'] = APP_PRJ

        assert pdv.errors()

        pdv['project_type'] = MODULE_PRJ

        assert not pdv.errors()

        pdv['project_type'] = PACKAGE_PRJ

        assert not pdv.errors()

        pdv['project_type'] = ROOT_PRJ

        assert not pdv.errors()

    def test_errors_invalid_project_path(self):
        pdv = ProjectDevVars()
        pdv['project_path'] = "."   # only absolute norm_path() allowed

        assert pdv.errors()

    def test_errors_invalid_parent_folder(self):
        pdv = ProjectDevVars()
        pdv['parent_folder'] = "parent folder not in PDV_PARENT_FOLDERS"

        assert pdv.errors()

    def test_errors_root_without_namespace(self):
        pdv = ProjectDevVars()
        pdv['project_type'] = ROOT_PRJ
        pdv['namespace_name'] = ""

        assert pdv.errors()

    def test_errors_project_path_name_mismatch(self):
        pdv = ProjectDevVars()
        pdv['project_name'] = "project name differs from root folder name"

        assert pdv.errors()

    def test_find_package_data_build_file(self, tmp_path):
        project_name = 'tst_app_with_build_file'
        pkg_path = os_path_join(str(tmp_path), project_name)
        file1 = os_path_join(pkg_path, BUILD_CONFIG_FILE)
        path2 = os_path_join(pkg_path, 'deep_dir')
        file2 = os_path_join(path2, BUILD_CONFIG_FILE)
        os.makedirs(path2)
        write_file(file1, "# build file content (included)")
        write_file(file2, "# deeper build file content (excluded)")

        pdv = ProjectDevVars(project_path=pkg_path)

        pkg_data = pdv.pdv_val('package_data')
        assert len(pkg_data) == 1
        files = pkg_data['']
        assert files[0] == os_path_relpath(file1, pkg_path)
        assert len(files) == 1

    def test_find_package_data_docs(self, tmp_path):
        project_name = 'tst_docs'
        pkg_path = os_path_join(str(tmp_path), project_name)
        doc_path = os_path_join(pkg_path, DOCS_FOLDER)
        build_path = os_path_join(doc_path, "_build")
        auto_path = os_path_join(doc_path, "_autosummary")
        img_path = os_path_join(doc_path, "img")
        file1 = os_path_join(doc_path, "conf.py")
        file2 = os_path_join(build_path, "any_build_file.py")
        file3 = norm_path(os_path_join(auto_path, "any_sum_file.rst"))
        file4 = norm_path(os_path_join(img_path, "my_included_pic.jpg"))
        os.makedirs(build_path)
        os.makedirs(auto_path)
        os.makedirs(img_path)
        write_file(file1, "# doc config file content (included)")
        write_file(file2, "# doc build file content (excluded)")
        write_file(file3, "# doc auto_summary file content (excluded)")
        write_file(file4, "# doc image resource file (included)")
        
        pdv = ProjectDevVars(project_path=pkg_path)

        files = pdv.pdv_val('package_data')[""]
        assert os_path_relpath(file1, pkg_path) in files
        assert os_path_relpath(file4, pkg_path) in files
        assert len(files) == 2

    def test_find_package_data_img(self, tmp_path):
        project_name = 'tst_pkg_with_resources'
        pkg_path = os_path_join(str(tmp_path), project_name)
        path1 = os_path_join(pkg_path, 'img')
        file1 = os_path_join(path1, 'res.ext')
        path2 = os_path_join(path1, 'res_deep')
        file2 = os_path_join(path2, 'res2.ext')
        path2d = os_path_join(path1, PY_CACHE_FOLDER)
        file2d = os_path_join(path2d, 'res2d.ext')
        file3 = os_path_join(pkg_path, 'included_widgets.kv')
        os.makedirs(path2)
        os.makedirs(path2d)
        write_file(file1, "some resource content")
        write_file(file2, "res content2")
        write_file(file2d, "res content2d (excluded)")
        write_file(file3, "kv language content")

        pdv = ProjectDevVars(project_path=pkg_path)

        files = pdv.pdv_val('package_data')[""]
        assert os_path_relpath(file1, pkg_path) in files
        assert os_path_relpath(file2, pkg_path) in files
        assert os_path_relpath(file2d, pkg_path) not in files
        assert os_path_relpath(file3, pkg_path) in files
        assert len(files) == 3

    def test_find_package_data_portion_snd(self, tmp_path):
        namespace_name = "tst_ns"
        portion_name = "ns_pkg_with_resources"
        project_name = namespace_name + "_" + portion_name
        prj_path = os_path_join(str(tmp_path), project_name)
        pkg_path = os_path_join(prj_path, namespace_name, portion_name)
        path1 = os_path_join(pkg_path, 'snd')
        file1 = os_path_join(path1, 'res.mp3')
        path2 = os_path_join(path1, 'res_deep')
        file2 = os_path_join(path2, 'res2.wav')
        file3 = os_path_join(pkg_path, 'widgets.kv')
        os.makedirs(path2)
        write_file(file1, "some resource content")
        write_file(file2, "res content2")
        write_file(file3, "kv language content")

        pdv = ProjectDevVars(project_path=pkg_path)

        files = pdv.pdv_val('package_data')[""]
        assert files[0] == os_path_relpath(file3, pkg_path)
        assert files[1] == os_path_relpath(file1, pkg_path)
        assert files[2] == os_path_relpath(file2, pkg_path)
        assert len(files) == 3

    def test_find_package_data_templates(self, tmp_path):
        project_name = 'tst_prj_with_templates'
        pkg_path = os_path_join(str(tmp_path), project_name)
        file0 = os_path_join(pkg_path, "non_tpl_file_name")
        file1 = os_path_join(pkg_path, TEMPLATES_FOLDER, "any_file_name")
        path2 = os_path_join(pkg_path, TEMPLATES_FOLDER, "deep_dir")
        file2 = os_path_join(path2, "some_other_template.ext")
        os.makedirs(path2)

        write_file(file0, "# non-template file content (not-included)")
        write_file(file1, "# root template file content (included)")
        write_file(file2, "# deeper template file content (included)")

        pdv = ProjectDevVars(project_path=pkg_path)

        files = pdv.pdv_val('package_data')[""]
        assert os_path_relpath(file1, pkg_path) in files
        assert os_path_relpath(file2, pkg_path) in files
        assert len(files) == 2

    def test_find_package_data_updater(self, tmp_path):
        project_name = 'tst_app_with_updater_or_bootstrap'
        pkg_path = os_path_join(str(tmp_path), project_name)
        file1 = os_path_join(pkg_path, PACKAGE_INCLUDE_FILES_PREFIX + "any_suffix")
        path2 = os_path_join(pkg_path, PACKAGE_INCLUDE_FILES_PREFIX + "deep_dir")
        file2 = os_path_join(path2, "some_included_file.ext")
        path2d = os_path_join(path2, "even_deeper")
        file2d = os_path_join(path2d, "other_included_file")
        path3 = os_path_join(pkg_path, "deep_not_included_dir")
        file3 = os_path_join(path3, PACKAGE_INCLUDE_FILES_PREFIX + "other_suffix")
        os.makedirs(path2d)
        os.makedirs(path3)

        write_file(file1, "# root file content (included)")
        write_file(file2, "# deeper include file content (included)")
        write_file(file2d, "# deeper include file content (included)")
        write_file(file3, "# deeper file content (excluded)")

        pdv = ProjectDevVars(project_path=pkg_path)

        files = pdv.pdv_val('package_data')[""]
        assert os_path_relpath(file1, pkg_path) in files
        assert os_path_relpath(file2, pkg_path) in files
        assert os_path_relpath(file2d, pkg_path) in files
        assert os_path_relpath(file3, pkg_path) not in files
        assert len(files) == 3

    def test_invalid_or_empty_project_doesnt_raise(self, tmp_path):
        pdv = ProjectDevVars(project_path=str(tmp_path))
        assert pdv['project_type'] == NO_PRJ

    def test_invalid_pdv_doesnt_raise(self, tmp_path):
        tmp_path = str(tmp_path)
        file_name = os_path_join(tmp_path, 'setup' + PY_EXT)

        write_file(file_name, "")
        ProjectDevVars(project_path=tmp_path)

        write_file(file_name, "pdv = ''")
        ProjectDevVars(project_path=tmp_path)

        write_file(file_name, "pdv = str")
        ProjectDevVars(project_path=tmp_path)

        write_file(file_name, "pdv = []")
        ProjectDevVars(project_path=tmp_path)

        write_file(file_name, "pdv = [str]")
        ProjectDevVars(project_path=tmp_path)

    def test_module_var_patch_local_imported(self):
        import ae.dev_ops as dc
        assert dc.PDV_REQ_FILE_NAME == 'requirements.txt'
        try:
            dc.PDV_REQ_FILE_NAME = 'new_val'
            assert dc.PDV_REQ_FILE_NAME == 'new_val'
            assert PDV_REQ_FILE_NAME == 'requirements.txt'
        finally:
            dc.PDV_REQ_FILE_NAME = 'requirements.txt'  # reset ae.dev_ops-module-var-value for subsequent tests

    def test_module_var_patch_imported_in_other_module(self):
        oth_mod = 'tst_other_module.py'
        try:
            write_file(oth_mod, "import ae.dev_ops as dc")
            # noinspection PyUnresolvedReferences
            from tst_other_module import dc
            assert dc.PDV_REQ_FILE_NAME == 'requirements.txt'

            dc.PDV_REQ_FILE_NAME = 'new_val'
            assert dc.PDV_REQ_FILE_NAME == 'new_val'
            assert PDV_REQ_FILE_NAME == 'requirements.txt'
        finally:
            if os_path_isfile(oth_mod):
                os.remove(oth_mod)
            dc.PDV_REQ_FILE_NAME = 'requirements.txt'  # reset ae.dev_ops-module-var-value for subsequent tests

    def test_module_var_patch_imported_in_other_module_as(self):
        oth_mod = 'another_tst_module.py'
        try:
            write_file(oth_mod, "from ae.dev_ops import PDV_REQ_FILE_NAME")
            # noinspection PyUnresolvedReferences
            import another_tst_module as dc
            assert dc.PDV_REQ_FILE_NAME == 'requirements.txt'

            dc.PDV_REQ_FILE_NAME = 'new_val'
            assert dc.PDV_REQ_FILE_NAME == 'new_val'
            assert PDV_REQ_FILE_NAME == 'requirements.txt'
        finally:
            if os_path_isfile(oth_mod):
                os.remove(oth_mod)

    def test_non_existent_env(self, tmp_path):
        empty_dir = str(tmp_path)

        pdv = ProjectDevVars(project_path=empty_dir)

        assert isinstance(pdv, dict)
        assert pdv['namespace_name'] == ''
        assert pdv['TEMPLATES_FOLDER'] == PDV_TEMPLATES_FOLDER == TEMPLATES_FOLDER   # == 'templates'
        assert pdv['MIN_PYTHON_VERSION'] == PDV_MIN_PYTHON_VERSION == '3.9'
        assert pdv['repo_domain'] == pdv['repo_domain'] == PDV_repo_domain == 'gitlab.com'
        assert pdv['REQ_FILE_NAME'] == PDV_REQ_FILE_NAME == 'requirements.txt'
        assert pdv['REQ_DEV_FILE_NAME'] == PDV_REQ_DEV_FILE_NAME == 'dev_requirements.txt'

        assert pdv['project_path'] == empty_dir
        assert pdv['project_type'] == NO_PRJ
        assert not pdv['project_version']
        assert pdv['repo_root']
        assert pdv['repo_pages']

        assert pdv.pdv_val('dev_requires') == []
        assert pdv.pdv_val('docs_requires') == []
        assert pdv.pdv_val('install_requires') == []
        assert pdv.pdv_val('tests_requires') == []

        assert pdv.pdv_val('portions_packages') == []
        assert not pdv.pdv_val('project_packages')
        assert pdv.pdv_val('package_data') == {'': []}

    def test_pdv_str(self, recwarn):
        pdv = ProjectDevVars(a="3")
        assert pdv["a"] == "3"
        assert pdv["tst_missing_varname"] == ""

        pdv = ProjectDevVars(a_non_str_type_var=1)

        assert pdv.pdv_val('a_non_str_type_var') == 1   # w/o warning

        assert len(recwarn) == 0

        assert pdv['a_non_str_type_var'] == 1           # with warning

        assert len(recwarn) == 1
        assert "is not of type str" in str(recwarn[0].message)

    def test_pdv_val(self):
        pdv = ProjectDevVars(a=1)

        assert pdv.pdv_val("not_existing_varname_tst") == ""
        assert pdv.pdv_val("a") == 1

    def test_project_readme_md(self, tmp_path):
        project_name = 'test_prj'
        package_dir = os_path_join(str(tmp_path), project_name)
        readme_file_name = os_path_join(package_dir, 'README.md')
        readme_content = "read me file content"
        os.makedirs(package_dir)
        write_file(readme_file_name, readme_content)

        pdv = ProjectDevVars(project_path=package_dir)

        assert pdv['long_desc_content'] == readme_content
        assert pdv['long_desc_type'] == 'text/markdown'

    def test_project_readme_rst(self, tmp_path):
        project_name = 'test_prj'
        package_dir = os_path_join(str(tmp_path), project_name)
        readme_file_name = os_path_join(package_dir, 'README.rst')
        readme_content = "read me file content"
        os.makedirs(package_dir)
        write_file(readme_file_name, readme_content)

        pdv = ProjectDevVars(project_path=package_dir)

        assert pdv['long_desc_content'] == readme_content
        assert pdv['long_desc_type'] == 'text/x-rst'

    def test_root_project_in_docs(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, "nsn")
        docs_dir = os_path_join(project_path, DOCS_FOLDER)
        common_dir = os_path_join(project_path, TEMPLATES_FOLDER)
        sphinx_conf = os_path_join(docs_dir, 'conf.py')
        os.makedirs(docs_dir)
        os.makedirs(common_dir)
        write_file(sphinx_conf, "file-content-irrelevant")

        with in_wd(docs_dir):
            pdv = ProjectDevVars(project_path='..')   # simulate call from within sphinx conf.py file

        assert pdv['project_path'] == norm_path(project_path)

    def test_root_project_project_version(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        namespace = "nsn"
        project_path = os_path_join(parent_dir, namespace)
        docs_dir = os_path_join(project_path, DOCS_FOLDER)
        tpl_dir = os_path_join(project_path, TEMPLATES_FOLDER)
        file_name = os_path_join(project_path, namespace + PY_EXT)
        project_version = "12.33.444"
        os.makedirs(docs_dir)
        os.makedirs(tpl_dir)
        write_file(file_name, f"{VERSION_PREFIX}{project_version}{VERSION_QUOTE}")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_version'] == project_version

    def test_setup_kwargs_minimum_python_version(self, tmp_path):
        pdv = ProjectDevVars(project_path=str(tmp_path))

        assert 'MIN_PYTHON_VERSION' in pdv
        assert pdv['MIN_PYTHON_VERSION'] == PDV_MIN_PYTHON_VERSION
        assert pdv['MIN_PYTHON_VERSION'] == PDV_MIN_PYTHON_VERSION

        assert pdv.pdv_val('setup_kwargs')['python_requires'].endswith(PDV_MIN_PYTHON_VERSION)
        assert any(PDV_MIN_PYTHON_VERSION in _ for _ in pdv.pdv_val('setup_kwargs')['classifiers'])

    def test_setup_pdv_via_project_local_env_file(self, tmp_path, monkeypatch):
        # w/o next line fails in "pjm check" on local machine (pjm loads PDV_AUTHOR in os.environ), but pass in PyCharm
        monkeypatch.delenv('PDV_AUTHOR', raising=False)

        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_name = "tst_pkg"
        project_path = os_path_join(parent_dir, project_name)
        env_file = os_path_join(project_path, '.env')
        author = 'App Config Author Name'
        repo_domain = "repo_url.host.domain"
        repo_url = repo_domain + "/project_name.git"
        write_file(env_file, f'PDV_AUTHOR="{author}"   # env var with comment\nPDV_repo_url={repo_url}', make_dirs=True)

        pdv = ProjectDevVars(project_path=project_path, repo_domain=repo_domain)

        assert pdv['AUTHOR'] == author
        assert pdv.pdv_val('setup_kwargs')['author'] == author

        assert pdv['repo_url'] == repo_url
        assert pdv.pdv_val('setup_kwargs')['url'] == repo_url

    def test_setuptools_find_namespace_packages(self):
        assert setuptools.find_namespace_packages(include=['ae']) == ['ae']


class TestProjectTypeAndResources:
    """ project type, modules and resources unit tests """
    def test_invalid_project_path(self):
        project_path = "invalid_project_path"

        pdv = ProjectDevVars(project_path=project_path)
        assert isinstance(pdv, dict)
        assert pdv['project_path'].endswith(os.path.sep + project_path)
        assert pdv['project_name'] == project_path
        assert pdv['namespace_name'] == ""
        assert pdv['portion_name'] == ""

    def test_no_modules(self, tmp_path):
        prj_name = 'prj_nam'
        project_path = os_path_join(str(tmp_path), prj_name)
        os.makedirs(project_path)

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == NO_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == prj_name
        assert pdv['namespace_name'] == ""

    def test_tests_folder_with_conftest(self):
        pdv = ProjectDevVars(project_path=TESTS_FOLDER)

        assert pdv['project_type'] == NO_PRJ
        assert pdv['project_path'] == norm_path(TESTS_FOLDER)
        assert pdv['project_name'] == TESTS_FOLDER
        assert pdv['namespace_name'] == ""

    def test_app_project(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_name = 'app_project'
        project_path = os_path_join(parent_dir, project_name)
        file_name = os_path_join(project_path, BUILD_CONFIG_FILE)
        os.makedirs(project_path)
        write_file(file_name, "spec content")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == APP_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == ""

    def test_app_namespace_project(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        namespace_name = 'nsn'
        portion_name = 'app_project'
        project_name = namespace_name + '_' + portion_name
        project_path = os_path_join(parent_dir, project_name)
        namespace_sub_dir = os_path_join(project_path, namespace_name)
        os.makedirs(namespace_sub_dir)
        write_file(os_path_join(namespace_sub_dir, "main" + PY_EXT), "# app main file")
        write_file(os_path_join(project_path, BUILD_CONFIG_FILE), "spec content")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == APP_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == namespace_name

    def test_app_project_no_namespace(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_name = 'appName'
        project_path = os_path_join(parent_dir, project_name)
        os.makedirs(project_path)
        write_file(os_path_join(project_path, "main" + PY_EXT), "# app main module")
        write_file(os_path_join(project_path, BUILD_CONFIG_FILE), "spec content")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == APP_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == ""

    def test_django_project(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_name = 'django_project'
        project_path = os_path_join(parent_dir, project_name)
        file_name = os_path_join(project_path, 'manage.py')
        os.makedirs(project_path)
        write_file(file_name, "any content")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == DJANGO_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == ""

    def test_module_template_project(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_name = 'project_tpls'
        project_path = os_path_join(parent_dir, project_name)
        template_path = os_path_join(project_path, TEMPLATES_FOLDER)
        os.makedirs(template_path)
        write_file(os_path_join(project_path, project_name + PY_EXT), f"{VERSION_PREFIX}1.2.3{VERSION_QUOTE}")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == MODULE_PRJ
        assert pdv['namespace_name'] == ""

    def test_package_template_project(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_name = 'project_tpls'
        project_path = os_path_join(parent_dir, project_name)
        package_path = os_path_join(project_path, project_name)
        template_path = os_path_join(project_path, TEMPLATES_FOLDER)
        os.makedirs(package_path)
        os.makedirs(template_path)
        write_file(os_path_join(package_path, PY_INIT), f"{VERSION_PREFIX}1.2.3{VERSION_QUOTE}")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == PACKAGE_PRJ
        assert pdv['namespace_name'] == ""

    def test_playground_project(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_name = 'test_project_playground'
        project_path = os_path_join(parent_dir, project_name)
        os.makedirs(project_path)

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == PLAYGROUND_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == ""

    def test_namespace_template_module_project(self, tmp_path):
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        namespace_name = 'nsn'
        portion_name = 'project_tpls'
        project_name = namespace_name + '_' + portion_name
        project_path = os_path_join(parent_dir, project_name)
        template_path = os_path_join(project_path, TEMPLATES_FOLDER)
        namespace_path = os_path_join(project_path, namespace_name)
        os.makedirs(template_path)
        os.makedirs(namespace_path)
        write_file(os_path_join(namespace_path, portion_name + PY_EXT), f"{VERSION_PREFIX}1.2.3{VERSION_QUOTE}")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == MODULE_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == namespace_name

    def test_namespace_root_project_module(self, tmp_path):
        namespace = 'rootX'  # no_underscore
        project_name = namespace + "_" + namespace
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, project_name)
        portion_path = os_path_join(project_path, namespace)
        os.makedirs(portion_path)
        write_file(os_path_join(portion_path, namespace + PY_EXT), "# namespace root main/version file")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == ROOT_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == namespace

    def test_namespace_root_project_package(self, tmp_path):
        namespace = 'namespace'
        project_name = namespace + "_" + namespace
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, project_name)
        nss_dir = os_path_join(project_path, namespace, namespace)
        os.makedirs(os_path_join(nss_dir, namespace))   # simulate root package
        write_file(os_path_join(nss_dir, PY_INIT), f"{VERSION_PREFIX}1.2.3{VERSION_QUOTE}")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == ROOT_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == namespace

    def test_one_module(self, tmp_path):
        mod_name = pkg_name = 'tst_pkg'
        project_path = os_path_join(str(tmp_path), pkg_name)
        module_path = os_path_join(project_path, mod_name + PY_EXT)
        os.makedirs(project_path)
        write_file(module_path, "v = 3")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == MODULE_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == pkg_name
        assert pdv['namespace_name'] == ""

    def test_one_namespace_module(self, tmp_path):
        namespace = 'nsn'
        mod_name = 'tst_mod1'
        pkg_name = namespace + '_' + mod_name
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, pkg_name)
        por_folder = os_path_join(project_path, namespace)
        module_path = os_path_join(por_folder, mod_name + PY_EXT)
        os.makedirs(por_folder)
        write_file(module_path, "v = 3")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == MODULE_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == pkg_name
        assert pdv['namespace_name'] == namespace

    def test_sub_package(self, tmp_path):
        project_name = 'tst_sub_pkg'
        mod_name = 'module1'
        project_path = os_path_join(str(tmp_path), project_name)
        tst_file1 = os_path_join(project_path, PY_INIT)
        tst_file2 = os_path_join(project_path, mod_name + PY_EXT)
        os.makedirs(project_path)
        write_file(tst_file1, "v = 3")
        write_file(tst_file2, "v = 6")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == PACKAGE_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == ""

    def test_namespace_sub_package(self, tmp_path):
        namespace = 'namespace'
        project_name = 'tst_sub_pkg'
        mod_name = 'module1'
        parent_dir = os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER)
        project_path = os_path_join(parent_dir, namespace + '_' + project_name)
        package_root = os_path_join(project_path, namespace, project_name)
        tst_file1 = os_path_join(package_root, PY_INIT)
        tst_file2 = os_path_join(package_root, mod_name + PY_EXT)
        os.makedirs(package_root)
        write_file(tst_file1, "v = 3")
        write_file(tst_file2, "v = 6")

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == PACKAGE_PRJ
        assert pdv['project_path'] == norm_path(project_path)
        assert pdv['project_name'] == namespace + '_' + project_name
        assert pdv['portion_name'] == project_name
        assert pdv['namespace_name'] == namespace

    def test_two_modules_package(self, tmp_path):
        tmp_path = str(tmp_path)
        prj_dir = os_path_basename(tmp_path)
        mod1 = 'mod1'
        mod2 = 'mod2'
        tst_init = os_path_join(tmp_path, PY_INIT)
        tst_file1 = os_path_join(tmp_path, mod1 + PY_EXT)
        tst_file2 = os_path_join(tmp_path, mod2 + PY_EXT)
        write_file(tst_init, "v = 3")
        write_file(tst_file1, "v = 6")
        write_file(tst_file2, "v = 99")

        pdv = ProjectDevVars(project_path=tmp_path)

        assert pdv['project_type'] == PACKAGE_PRJ
        assert pdv['project_path'] == norm_path(tmp_path)
        assert pdv['project_name'] == prj_dir
        assert pdv['namespace_name'] == ""

    def test_two_modules_no_init(self, tmp_path):
        tmp_path = str(tmp_path)
        mod1 = 'mod1'
        mod2 = 'mod2'
        tst_file1 = os_path_join(tmp_path, mod1 + PY_EXT)
        tst_file2 = os_path_join(tmp_path, mod2 + PY_EXT)
        write_file(tst_file1, "v = 3")
        write_file(tst_file2, "v = 55")

        pdv = ProjectDevVars(project_path=tmp_path)

        assert pdv['project_type'] == NO_PRJ
        assert pdv['project_path'] == norm_path(tmp_path)
        assert pdv['project_name'] == os_path_basename(tmp_path)
        assert pdv['namespace_name'] == ""

    def test_two_namespace_modules_no_init(self, tmp_path):
        tmp_path = str(tmp_path)
        mod1 = 'mod1'
        mod2 = 'mod2'
        tst_file1 = os_path_join(tmp_path, mod1 + PY_EXT)
        tst_file2 = os_path_join(tmp_path, mod2 + PY_EXT)
        write_file(tst_file1, "v = 3")
        write_file(tst_file2, "v = 55")

        pdv = ProjectDevVars(project_path=tmp_path)

        assert pdv['project_type'] == NO_PRJ
        assert pdv['project_path'] == norm_path(tmp_path)
        assert pdv['project_name'] == os_path_basename(tmp_path)
        assert pdv['namespace_name'] == ""

    def test_new_project_in_parent(self, tmp_path):
        project_name = DEF_PROJECT_PARENT_FOLDER
        parent_dir = norm_path(os_path_join(str(tmp_path), project_name))
        os.makedirs(parent_dir)

        pdv = ProjectDevVars(project_path=parent_dir)

        assert pdv['project_type'] == PARENT_PRJ
        assert pdv['project_path'] == parent_dir
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == ""

    def test_new_project_under_parent(self, tmp_path):
        project_name = 'new_prj'
        parent_dir = norm_path(os_path_join(str(tmp_path), DEF_PROJECT_PARENT_FOLDER))
        project_path = os_path_join(parent_dir, project_name)
        os.makedirs(project_path)

        pdv = ProjectDevVars(project_path=project_path)

        assert pdv['project_type'] == NO_PRJ
        assert pdv['project_path'] == project_path
        assert pdv['project_name'] == project_name
        assert pdv['namespace_name'] == ""
