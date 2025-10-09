""" ae.base unit tests """
import datetime
import os
import socket
import ssl
import string
import sys
import tempfile
import textwrap
import time
import timeit
import warnings

from collections import OrderedDict
from configparser import ConfigParser
# noinspection PyProtectedMember
from http.client import HTTPMessage
from types import ModuleType
from typing import cast, Any, Optional
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from tests.conftest import skip_gitlab_ci

# noinspection PyProtectedMember
from ae.base import (
    ASCII_TO_UNICODE, ASCII_UNICODE, BUILD_CONFIG_FILE, DOTENV_FILE_NAME, DOTENV_VAR_IN_VAL_MATCHER,
    PY_EXT, PY_INIT, PY_MAIN, TESTS_FOLDER, UNICODE_TO_ASCII, UNSET, URI_SEP_STR, URI_SEP_UNICODE_CHAR,
    app_name_guess, ascii_str, build_config_variable_values, camel_to_snake,
    dedefuse, deep_dict_update, defuse, dummy_function, duplicates, env_str, evaluate_literal,
    force_encoding, format_given, full_stack_trace, import_module, instantiate_config_parser, in_wd,
    late_env_var_resolver, load_env_var_defaults, load_dotenvs, main_file_paths_parts, mask_secrets, mask_url,
    module_attr, module_file_path, module_name, norm_line_sep, norm_name, norm_path, now_str, on_ci_host,
    os_host_name, os_local_ip, _os_platform, os_user_name,
    parse_dotenv, project_main_file, read_file, round_traditional, sign, snake_to_camel, stack_frames, stack_var,
    stack_vars, str_ascii, sys_env_dict, sys_env_text, to_ascii, url_failure, utc_datetime, write_file,
    ErrorMsgMixin)

tst_uri1 = "schema://user:pwd@domain/path_root/path_sub\\path+file% Üml?ä|ït.path_ext*\"<>|*'()[]{}#^;&=$,~" + chr(127)
tst_fna1 = "schema⫻user﹕pwd﹫domain⁄path_root⁄path_sub﹨path﹢file﹪␣Üml﹖ä।ït.path_ext﹡＂⟨⟩।﹡‘⟮⟯⟦⟧﹛﹜﹟＾﹔﹠﹦﹩﹐~␡"
tst_uri2 = "test control chars" + "".join(chr(_) for _ in range(1, 32))
tst_fna2 = "test␣control␣chars␁␂␃␄␅␆␇␈␉␊␋␌␍␎␏␐␑␒␓␔␕␖␗␘␙␚␛␜␝␞␟"

DOTENV_VAR_NAME = 'env_var_nam1'
DOTENV_VAR_VAL = 'value of env var'
DOTENV_LATE_VAR_PRE = 'late_var_nam'
DOTENV_LATE_VAL_PRE = '-late Pre Val'
DOTENV_DIR_NAME = 'fdr'
DOTENV_FULL_DIRS = (0, 1, 3)
DOTENV_DIR_RANGE = 6
DOTENV_LIT_VALUES = {}
DOTENV_LATE_VALUES = {}
for _level in range(DOTENV_DIR_RANGE):
    if _level in DOTENV_FULL_DIRS:
        _val_lit = "".join("$" + ("{" if _ % 2 else "") + DOTENV_LATE_VAR_PRE + str(_) + ("}" if _ % 2 else "")
                           for _ in range(_level) if _ in DOTENV_FULL_DIRS)
        DOTENV_LIT_VALUES[_level] = DOTENV_LATE_VAL_PRE + _val_lit + "  " + str(_level)
        DOTENV_LATE_VALUES[_level] = DOTENV_LATE_VAL_PRE + "".join(
                DOTENV_LATE_VALUES[_var_level] for _var_level in range(_level) if _var_level in DOTENV_FULL_DIRS
            ) + "  " + str(_level)


@pytest.fixture
def os_env_test_env():
    """ create .env files to test and backup os.environ. """
    with tempfile.TemporaryDirectory() as tmp_path:
        for level in range(DOTENV_DIR_RANGE):
            file_path = os.path.join(tmp_path, *((DOTENV_DIR_NAME, ) * level))
            os.makedirs(file_path, exist_ok=True)
            if level in DOTENV_FULL_DIRS:
                content = (os.linesep + DOTENV_VAR_NAME + "='" + DOTENV_VAR_VAL + str(level) + "'" +
                           os.linesep + DOTENV_LATE_VAR_PRE + str(level) + '="' + DOTENV_LIT_VALUES[level] + '"' +
                           os.linesep + "RecursiveWithLowerCase = $RecursiveWithLowerCase")
                write_file(os.path.join(file_path, DOTENV_FILE_NAME), content)

        old_env = os.environ
        os.environ = old_env.copy()

        yield tmp_path

        os.environ = old_env


module_test_var = 'module_test_var_val'   # used for stack_var()/try_exec() tests


def test_unset_truthiness_and_null_length():
    assert not UNSET
    assert bool(UNSET) is False

    assert len(UNSET) == 0


def test_proof_os_path_shortcuts_performance_win():
    att_call_setup = textwrap.dedent("""
    import os
    path1, path2, path3 = "folder1", "folder2", "file.tst"
    """)
    sho_call_setup = att_call_setup + textwrap.dedent("""
    os_path_join = os.path.join
    """)

    att_call_code = "os.path.join(path1, path2, path3)"
    sho_call_code = "os_path_join(path1, path2, path3)"

    time_att = timeit.timeit(att_call_code, setup=att_call_setup, number=3_000_000)
    time_sho = timeit.timeit(sho_call_code, setup=sho_call_setup, number=3_000_000)

    assert time_sho < time_att
    print(f"\n¡!¡!¡! os_path_* shortcuts are ~{((time_att - time_sho) / time_att) * 100:.2f}% faster")


class TestErrorMsgMixin:
    def test_instantiation(self):
        ins = ErrorMsgMixin()
        assert ins
        assert ins.main_app is None     # in test env is no console/gui app available
        assert ins.po is ins.dpo is ins.vpo is print

        with patch('ae.core.main_app_instance', lambda: None):
            ins = ErrorMsgMixin()
            assert ins
            assert ins.main_app is None
            assert ins.po is ins.dpo is ins.vpo is print

        class _AppMock(ErrorMsgMixin):
            main_app = None

            @staticmethod
            def po():
                """ po() mock """
                return "po"

            @staticmethod
            def dpo():
                """ dpo() mock """
                return "dpo"

            @staticmethod
            def vpo():
                """ vpo() mock """
                return "vpo"

        app_ins = _AppMock()

        with patch('ae.core.main_app_instance', lambda: app_ins):
            ins = ErrorMsgMixin()
            assert ins.main_app is app_ins
            assert ins.po is not print
            assert ins.po() == "po"
            assert ins.dpo is not print
            assert ins.dpo() == "dpo"
            assert ins.vpo is not print
            assert ins.vpo() == "vpo"

    def test_error_message_property(self):
        ins = ErrorMsgMixin()
        assert ins.error_message == ""

        err_msg = "set new error message"
        ins.error_message = err_msg
        assert ins.error_message == err_msg

        err_msg2 = "added error message"
        ins.error_message = err_msg2
        assert err_msg in ins.error_message
        assert err_msg2 in ins.error_message

        ins.error_message = ""
        assert ins.error_message == ""

    def test_error_message_property_for_warnings(self):
        ins = ErrorMsgMixin()

        err_msg = "error message with the word warning"
        ins.error_message = err_msg
        ins.error_message = "another message"
        assert err_msg in ins.error_message


class TestBaseHelpers:
    def test_app_name_guess(self):
        assert app_name_guess()     # app.exe name in pytest returning '_jb_pytest_runner'(PyCharm)/'__main__'(console)
        assert app_name_guess() != 'main'
        assert app_name_guess() == 'unguessable'

    def test_ascii_str(self):
        assert isinstance(ascii_str(""), str)

        uni_str = "äÄßéÉíÍñÑòÒùÙ"
        assert all(ord(_) >= 128 for _ in uni_str)
        assert all(ord(_) < 128 for _ in ascii_str(uni_str))

        uni_str = "".join(_uco for _asc, _uco in ASCII_UNICODE)
        assert any(ord(_) >= 128 for _ in uni_str)
        assert all(ord(_) < 128 for _ in ascii_str(uni_str))

        asc_str = "".join(_asc for _asc, _uco in ASCII_UNICODE)
        assert any(ord(_) < 128 for _ in asc_str)
        assert all(ord(_) < 128 for _ in ascii_str(asc_str))

    def test_str_ascii(self):
        assert isinstance(str_ascii(ascii_str("tst")), str)

        assert str_ascii(ascii_str("tst")) == "tst"
        uni_str = "äÄßéÉíÍñÑòÒùÙ"
        assert str_ascii(ascii_str(uni_str)) == uni_str

        uni_str = "".join(_uco for _asc, _uco in ASCII_UNICODE)
        assert str_ascii(ascii_str(uni_str)) == uni_str

        asc_str = "".join(_asc for _asc, _uco in ASCII_UNICODE)
        assert str_ascii(ascii_str(asc_str)) == asc_str

    def test_str_ascii_errors(self):
        with pytest.raises(SyntaxError):
            str_ascii("")

        with pytest.raises(SyntaxError):
            str_ascii("any tst string not encoded/converted via ascii_str()")

    def test_build_config_variable_values_with_spec(self):
        try:
            with open(BUILD_CONFIG_FILE, "w") as file_handle:
                file_handle.write("""[app]\nexisting = tst""")
            existing, not_existing = build_config_variable_values(
                ('existing', ""),
                ('not_existing', "default_value")
            )
            assert existing == "tst"
            assert not_existing == "default_value"
        finally:
            if os.path.exists(BUILD_CONFIG_FILE):
                os.remove(BUILD_CONFIG_FILE)

    def test_build_config_variable_values_no_spec(self):
        assert not os.path.exists(BUILD_CONFIG_FILE)
        existing, not_existing = build_config_variable_values(
            ('not_existing1', "default_value1"),
            ('not_existing2', "default_value2")
        )
        assert existing == "default_value1"
        assert not_existing == "default_value2"

    def test_camel_to_snake(self):
        assert camel_to_snake("AnyCamelCaseName") == "_Any_Camel_Case_Name"
        assert camel_to_snake("anyCamelCaseName") == "any_Camel_Case_Name"

        assert camel_to_snake("_under_score") == "_under_score"
        assert camel_to_snake("any_name") == "any_name"
        assert camel_to_snake("@special/chars!") == "@special/chars!"

    def test_deep_dict_update_empty(self):
        str_val = "str_val"
        upd = {'setup_kwargs': {'entry_points': {'console_scripts': str_val}}}

        ori = {}
        deep_dict_update(ori, upd)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == str_val

        ori = {}
        deep_dict_update(ori, upd, overwrite=False)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == str_val

    def test_deep_dict_update_half_empty_ordered(self):
        str_val = "str_val"
        lst_val = [str_val]
        upd = {'setup_kwargs': {'entry_points': {'console_scripts': lst_val}}}

        ori: dict[str, Any] = OrderedDict({'setup_kwargs': {'untouched_key1': "untouched val 1"},
                                           'untouched_key2': "untouched val 2"})
        deep_dict_update(ori, upd)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == lst_val
        assert ori['setup_kwargs']['entry_points']['console_scripts'][0] == str_val
        assert ori['untouched_key2'] == "untouched val 2"
        assert ori['setup_kwargs']['untouched_key1'] == "untouched val 1"
        assert list(ori.keys()) == ['setup_kwargs', 'untouched_key2']
        assert list(ori['setup_kwargs'].keys()) == ['untouched_key1', 'entry_points']

        ori: dict[str, Any] = OrderedDict({'setup_kwargs': {'untouched_key1': "untouched val 1"},
                                           'untouched_key2': "untouched val 2"})
        deep_dict_update(ori, upd, overwrite=False)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == lst_val
        assert ori['setup_kwargs']['entry_points']['console_scripts'][0] == str_val
        assert ori['untouched_key2'] == "untouched val 2"
        assert ori['setup_kwargs']['untouched_key1'] == "untouched val 1"
        assert list(ori.keys()) == ['setup_kwargs', 'untouched_key2']
        assert list(ori['setup_kwargs'].keys()) == ['untouched_key1', 'entry_points']

    def test_deep_dict_update_full(self):
        str_old = "old_val"
        str_new = "new_val"
        lst_val = [str_new]
        upd = {'setup_kwargs': {'entry_points': {'console_scripts': lst_val}}}

        ori = {'setup_kwargs': {'entry_points': {'console_scripts': str_old}}}
        deep_dict_update(ori, upd)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == lst_val
        assert ori['setup_kwargs']['entry_points']['console_scripts'][0] == str_new

        ori = {'setup_kwargs': {'entry_points': {'console_scripts': str_old}}}
        deep_dict_update(ori, upd, overwrite=False)
        assert ori
        assert 'setup_kwargs' in ori
        assert 'entry_points' in ori['setup_kwargs']
        assert 'console_scripts' in ori['setup_kwargs']['entry_points']
        assert ori['setup_kwargs']['entry_points']['console_scripts'] == str_old
        assert ori['setup_kwargs']['entry_points']['console_scripts'][0] == str_old[0]

    def test_dedefuse_file_name(self):
        assert dedefuse(tst_fna1) == tst_uri1
        assert dedefuse(tst_fna2) == tst_uri2

        assert dedefuse(defuse(tst_uri1)) == tst_uri1
        assert dedefuse(defuse(tst_uri2)) == tst_uri2

    def test_defuse_file_name(self):
        assert defuse(tst_uri1) == tst_fna1
        assert defuse(tst_uri2) == tst_fna2

        assert defuse(dedefuse(tst_fna1)) == tst_fna1
        assert defuse(dedefuse(tst_fna2)) == tst_fna2

    def test_defuse_os_file_name(self):
        try:
            write_file(tst_fna1, "tst uri file content1")
            assert os.path.exists(tst_fna1)
            write_file(tst_fna2, "tst uri file content2")
            assert os.path.exists(tst_fna2)
        finally:
            if os.path.exists(tst_fna1):
                os.remove(tst_fna1)
            if os.path.exists(tst_fna2):
                os.remove(tst_fna2)

    def test_defuse_maps_integrity(self):
        assert len(ASCII_TO_UNICODE) == len(ASCII_UNICODE)      # duplicates check in ASCII_UNICODE map
        assert len(UNICODE_TO_ASCII) == len(ASCII_UNICODE) + 1  # -"-, having also the ord(URI_SEP_UNICODE_CHAR) key
        assert ord(URI_SEP_UNICODE_CHAR) in UNICODE_TO_ASCII
        assert UNICODE_TO_ASCII[ord(URI_SEP_UNICODE_CHAR)] == URI_SEP_STR

    def test_defuse_maps_not_touching_chars_allowed_as_slug_and_filename(self):
        assert ord('-') not in ASCII_TO_UNICODE
        assert ord('_') not in ASCII_TO_UNICODE
        assert ord('.') not in ASCII_TO_UNICODE
        assert ord('~') not in ASCII_TO_UNICODE
        for char in string.ascii_letters + string.digits:
            assert ord(char) not in ASCII_TO_UNICODE

    def test_dummy_function(self):
        assert dummy_function() is None
        assert dummy_function(999, "any_args") is None
        assert dummy_function(3, kw_arg1=3, kw_arg2="6") is None

    def test_duplicates(self):
        lst = ['a', 3, 'bb', 3, 'ccc', 3]
        assert duplicates(lst) == [3, 3]

    def test_env_var_unconverted(self):
        ev = 'PATH'
        assert env_str(ev)

    def test_env_var_case_conversions(self):
        ev = 'path'
        assert env_str(ev, convert_name=True)

        ev = 'camelCase'
        vv = "test variable value"
        os.environ['CAMEL_CASE'] = vv
        assert env_str(ev, convert_name=True) == vv

        ev = 'CamelCase'
        vv = "test variable value"
        os.environ['_CAMEL_CASE'] = vv
        assert env_str(ev, convert_name=True) == vv

    def test_env_var_non_alpha_num_conversions(self):
        ev = 'non\talpha\\num/chars-69'
        vv = "test variable value"
        os.environ['NON_ALPHA_NUM_CHARS_69'] = vv
        assert env_str(ev, convert_name=True) == vv

    def test_evaluate_literal(self):
        tst_str = "unquoted string"

        assert evaluate_literal(tst_str) == tst_str                 # actually: evaluate_literal(tst_str) is tst_str

        assert evaluate_literal("'" + tst_str + "'") == tst_str

        tst_dict = dict(a=1, b=[dict(b3=3), (1, 2, 3), set()])

        assert evaluate_literal(repr(tst_dict)) == tst_dict

    def test_evaluate_literal_errors(self):
        assert evaluate_literal("") == ""

        # noinspection PyTypeChecker
        assert evaluate_literal(None) is None                       # raising ValueError: malformed node or string: None

        tst = dict(a=1, b=[dict(b3=3), (1, "22", 333), set()])

        assert evaluate_literal("    " + repr(tst) + "    ") == "    " + repr(tst) + "    "  # raising IndentationError

        assert evaluate_literal(repr(tst) + "    ") == tst          # trailing white space chars are ok

        # noinspection PyTypeChecker
        assert evaluate_literal(tst) is tst

    def test_force_encoding_bytes(self):
        s = 'äöü'

        assert s.encode('ascii', errors='replace') == b'???'
        ba = s.encode('ascii', errors='backslashreplace')   # == b'\\xe4\\xf6\\xfc'
        assert force_encoding(ba, encoding='ascii') == str(ba, encoding='ascii')
        assert force_encoding(ba) == str(ba, encoding='ascii')

        bw = s.encode('cp1252')                             # == b'\xe4\xf6\xfc'
        assert force_encoding(bw, encoding='cp1252') == s
        with pytest.raises(UnicodeDecodeError):
            force_encoding(bw)

    def test_force_encoding_umlaut(self):
        s = 'äöü'
        assert force_encoding(s) == '\\xe4\\xf6\\xfc'

        assert force_encoding(s, encoding='utf-8') == s
        assert force_encoding(s, encoding='utf-16') == s
        assert force_encoding(s, encoding='cp1252') == s

        assert force_encoding(s, encoding='utf-8', errors='strict') == s
        assert force_encoding(s, encoding='utf-8', errors='replace') == s
        assert force_encoding(s, encoding='utf-8', errors='backslashreplace') == s
        assert force_encoding(s, encoding='utf-8', errors='xmlcharrefreplace') == s
        assert force_encoding(s, encoding='utf-8', errors='ignore') == s
        assert force_encoding(s, encoding='utf-8', errors='') == s

        with pytest.raises(TypeError):
            # noinspection PyInvalidCast
            assert force_encoding(s, encoding=cast(str, None)) == '\\xe4\\xf6\\xfc'

    def test_format_given(self):
        assert format_given("test text with {placeholder}", {}) == "test text with {placeholder}"
        assert format_given("test text with {placeholder:.2e}", {}) == "test text with {placeholder:.2e}"
        assert format_given("a {placeholder} {{test}}", {}) == "a {placeholder} {test}"

        assert format_given("test text with {placeholder}", {'placeholder': "replaced"}) == "test text with replaced"
        assert format_given("test text with {placeholder:.2e}", {'placeholder': 3.14159}) == "test text with 3.14e+00"

        assert format_given("a {ph} {{test}}", {'ph': "rep"}) == "a rep {test}"
        assert format_given("a {{ph}} {test}", {'ph': "rep"}) == "a {ph} {test}"
        assert format_given("a {{ph} {test}}", {'ph': "rep"}) == "a {{ph} {test}}"

        assert format_given("a non-ph}", {'ph': "rep"}) == "a non-ph}"
        assert format_given("a non-{ph", {'ph': "rep"}) == "a non-{ph"

    def test_format_given_err(self):
        with pytest.raises(ValueError):
            format_given("test text with {placeholder", {}, strict=True)     # missing closing curly bracket
        with pytest.raises(ValueError):
            format_given("test text with placeholder}", {}, strict=True)     # missing opening curly bracket

    def test_import_module_ae_base(self):
        mod_ref = import_module('ae.base')
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'TESTS_FOLDER') == TESTS_FOLDER

    def test_import_module_built_ins(self):
        assert import_module('os') is None
        assert import_module('textwrap') is None

    def test_import_module_local_module(self, monkeypatch, tmp_path):
        module = "mod_2_tst"
        mod_file = cast(str, os.path.join(str(tmp_path), module + PY_EXT))
        write_file(mod_file, "mod_var = 'mod_var_val'")

        mod_ref = import_module(module, path=mod_file)
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

        mod_ref = import_module(str(tmp_path) + '.' + module)
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

        mod_ref = import_module(module)
        assert mod_ref is None

        monkeypatch.chdir(str(tmp_path))

        mod_ref = import_module(module, path=module + PY_EXT)
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

        mod_ref = import_module(module)
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'mod_var') == 'mod_var_val'

    def test_import_module_local_package(self, monkeypatch, tmp_path):
        namespace = "zy"
        portion = "por_2_tst"
        pkg_root = os.path.join(str(tmp_path), namespace)
        pkg_path = os.path.join(pkg_root, portion)
        pkg_file = os.path.join(pkg_path, PY_INIT)

        os.makedirs(pkg_path)
        write_file(pkg_file, "pkg_var = 'pkg_var_val'")

        mod_ref = import_module(portion, path=pkg_file)
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        mod_ref = import_module(namespace + '.' + portion, path=pkg_file)
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        mod_ref = import_module(str(tmp_path) + '.' + namespace + '.' + portion, path=pkg_file)
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        mod_ref = import_module(str(tmp_path) + '.' + namespace + '.' + portion)
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        monkeypatch.chdir(str(tmp_path))

        mod_ref = import_module(namespace + '.' + portion)
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

        mod_ref = import_module(namespace + '.' + portion, path=os.path.relpath(pkg_file, str(tmp_path)))
        assert isinstance(mod_ref, ModuleType)
        assert getattr(mod_ref, 'pkg_var') == 'pkg_var_val'

    def test_import_module_not_exists(self):
        assert import_module('not_existing_import_name') is None

    def test_instantiate_config_parser(self):
        cfg_parser = instantiate_config_parser()
        assert isinstance(cfg_parser, ConfigParser)
        assert cfg_parser.optionxform is str

    def test_in_wd(self, tmp_path):
        old_dir = os.getcwd()
        tst_dir = str(tmp_path)
        with in_wd(tst_dir):
            assert os.getcwd() == tst_dir
        assert os.getcwd() == old_dir

    def test_late_env_var_resolver_errors_and_warnings(self):
        # all branches in this follow-up/resolve function are already covered by the test_load_env_var_defaults*() tests
        late_env_var_resolver({}, {}, {})

        with warnings.catch_warnings(record=True) as warnings_list:

            late_env_var_resolver({}, {}, {'unresolvable_var': [('', '$', '{NOT_EXISTENT_VAR}', 'NOT_EXISTENT_VAR')]})

            assert len(warnings_list) == 1
            assert "has unresolved environment variables in its value" in str(warnings_list[0].message)

        with warnings.catch_warnings(record=True) as warnings_list:
            var_nam = "RECURSIVE_VAR_Name"
            var_val = "infinite-val-grow$" + var_nam
            late_resolved = {var_nam: DOTENV_VAR_IN_VAL_MATCHER.findall(var_val)}
            env_vars = {var_nam: var_val}

            late_env_var_resolver(env_vars, env_vars, late_resolved)

            assert len(warnings_list) == 1
            assert "ignoring recursive environment variable" in str(warnings_list[0].message)

    def test_load_dotenvs(self, os_env_test_env):
        assert DOTENV_VAR_NAME not in os.environ
        load_dotenvs()
        assert DOTENV_VAR_NAME not in os.environ

    def test_load_dotenvs_from_module_path(self, os_env_test_env):
        assert DOTENV_VAR_NAME not in os.environ
        load_dotenvs(from_module_path=True)
        assert DOTENV_VAR_NAME not in os.environ

    def test_load_env_var_defaults_errors(self):
        with pytest.raises(TypeError):
            # noinspection PyArgumentList
            load_env_var_defaults()

        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            load_env_var_defaults(None, None)   # STRANGE: raising TypeError in Python 3.9.21/local but not in 3.9.23/CI
            # noinspection PyArgumentList
            load_env_var_defaults(None)         # HOTFIX ensuring failure - could not find any changelog notes

        # noinspection PyTypeChecker
        load_env_var_defaults("inv:_ file path", ())  # NO ERROR EXCEPTIONS on these invalid arg values!!!

    def test_load_env_var_defaults_not_loaded(self):
        env_vars = {}

        load_env_var_defaults('/', env_vars)
        assert DOTENV_VAR_NAME not in env_vars

        load_env_var_defaults('.', env_vars)
        assert DOTENV_VAR_NAME not in env_vars

    def test_load_env_var_defaults_not_loaded_in_os_environ(self, os_env_test_env):
        assert DOTENV_VAR_NAME not in os.environ

        load_env_var_defaults('/', os.environ)
        assert DOTENV_VAR_NAME not in os.environ

        load_env_var_defaults('.', os.environ)
        assert DOTENV_VAR_NAME not in os.environ

        load_env_var_defaults(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME,) * 5)), os.environ)
        assert DOTENV_VAR_NAME not in os.environ

        load_env_var_defaults(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME,) * 6)), os.environ)  # too-deep path
        assert DOTENV_VAR_NAME not in os.environ

    def test_load_env_var_defaults_load_start_parent_first_no_chain(self, monkeypatch, os_env_test_env):
        monkeypatch.chdir(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME,) * 4)))

        loaded = load_env_var_defaults("", os.environ)

        assert DOTENV_VAR_NAME in loaded
        assert loaded[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '3'
        assert DOTENV_VAR_NAME in os.environ
        assert os.environ[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '3'

    def test_load_env_var_defaults_load_start_first_no_chain(self, os_env_test_env):
        loaded = load_env_var_defaults(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME,) * 3)), os.environ)

        assert DOTENV_VAR_NAME in loaded
        assert loaded[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '3'
        assert DOTENV_VAR_NAME in os.environ
        assert os.environ[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '3'

    def test_load_env_var_defaults_load_start_parent_first_in_chain(self, os_env_test_env):
        loaded = load_env_var_defaults(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME,) * 2)), os.environ)

        assert DOTENV_VAR_NAME in loaded
        assert loaded[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '1'
        assert DOTENV_VAR_NAME in os.environ
        assert os.environ[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '1'

    def test_load_env_var_defaults_load_start_no_parent_first_in_chain(self, os_env_test_env):
        loaded = load_env_var_defaults(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME,) * 1)), os.environ)

        assert DOTENV_VAR_NAME in loaded
        assert loaded[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '1'
        assert DOTENV_VAR_NAME in os.environ
        assert os.environ[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '1'

    def test_load_env_var_defaults_load_start_on_second_within_chain(self, os_env_test_env):
        loaded = load_env_var_defaults(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME,) * 0)), os.environ)

        assert DOTENV_VAR_NAME in loaded
        assert loaded[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '0'
        assert DOTENV_VAR_NAME in os.environ
        assert os.environ[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '0'

    def test_load_env_var_defaults_resolve_vars_late(self, os_env_test_env):
        loaded = load_env_var_defaults(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME,) * 1)), os.environ)

        assert DOTENV_LATE_VAR_PRE + '0' in loaded
        assert DOTENV_LATE_VAR_PRE + '0' in os.environ
        assert DOTENV_LATE_VAR_PRE + '1' in loaded
        assert DOTENV_LATE_VAR_PRE + '1' in os.environ
        assert DOTENV_LATE_VAR_PRE + '3' not in loaded
        assert DOTENV_LATE_VAR_PRE + '3' not in os.environ
        assert loaded[DOTENV_LATE_VAR_PRE + '0'] == DOTENV_LATE_VALUES[0]
        assert os.environ[DOTENV_LATE_VAR_PRE + '0'] == DOTENV_LATE_VALUES[0]
        assert loaded[DOTENV_LATE_VAR_PRE + '1'] == DOTENV_LATE_VALUES[1]
        assert os.environ[DOTENV_LATE_VAR_PRE + '1'] == DOTENV_LATE_VALUES[1]

    def test_load_env_var_defaults_resolve_vars_late_with_gap_and_closed_gap(self, os_env_test_env):
        empty_env = {}

        loaded = load_env_var_defaults(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME, ) * 3)), empty_env)

        assert DOTENV_LATE_VAR_PRE + '0' not in loaded
        assert DOTENV_LATE_VAR_PRE + '0' not in empty_env
        assert DOTENV_LATE_VAR_PRE + '1' not in loaded
        assert DOTENV_LATE_VAR_PRE + '1' not in empty_env
        assert DOTENV_LATE_VAR_PRE + '3' in loaded
        assert DOTENV_LATE_VAR_PRE + '3' in empty_env
        assert loaded[DOTENV_LATE_VAR_PRE + '3'] == DOTENV_LIT_VALUES[3]
        assert empty_env[DOTENV_LATE_VAR_PRE + '3'] == DOTENV_LIT_VALUES[3]

        write_file(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME, ) * 2), DOTENV_FILE_NAME), "# closing level 2 gap")

        loaded = load_env_var_defaults(os.path.join(os_env_test_env, *((DOTENV_DIR_NAME, ) * 3)), os.environ)

        assert DOTENV_LATE_VAR_PRE + '0' in loaded
        assert DOTENV_LATE_VAR_PRE + '0' in os.environ
        assert DOTENV_LATE_VAR_PRE + '1' in loaded
        assert DOTENV_LATE_VAR_PRE + '1' in os.environ
        assert DOTENV_LATE_VAR_PRE + '3' in loaded
        assert DOTENV_LATE_VAR_PRE + '3' in os.environ
        assert loaded[DOTENV_LATE_VAR_PRE + '3'] == DOTENV_LATE_VALUES[3]
        assert os.environ[DOTENV_LATE_VAR_PRE + '3'] == DOTENV_LATE_VALUES[3]

    def test_main_file_paths_parts(self):
        assert isinstance(main_file_paths_parts(""), tuple)
        assert len(main_file_paths_parts(""))
        assert isinstance(main_file_paths_parts("")[0], tuple)

        assert any("main" + PY_EXT in _ for _ in main_file_paths_parts(""))
        assert any(PY_MAIN in _ for _ in main_file_paths_parts(""))
        assert any(PY_INIT in _ for _ in main_file_paths_parts(""))
        por_name = "portion_tst_name"
        assert any(por_name in _ for _ in main_file_paths_parts(por_name))
        assert any(por_name + PY_EXT in _ for _ in main_file_paths_parts(por_name))

        assert ('main', PY_INIT) in main_file_paths_parts("")
        assert (por_name, PY_INIT) in main_file_paths_parts(por_name)

    def test_mask_secrets(self):
        assert mask_secrets({}) == {}
        assert mask_secrets([]) == []
        assert mask_secrets(tuple()) == ()
        assert mask_secrets("") == ""

        assert mask_secrets({'password': "secret"}) == {'password': "sec*********"}
        assert mask_secrets({'PASSWORD': "secret"}) == {'PASSWORD': "sec*********"}
        assert mask_secrets([{'pwd': "secret"}, "any"]) == [{'pwd': "sec*********"}, "any"]
        assert mask_secrets([{'Pwd': "secret"}, "Any"]) == [{'Pwd': "sec*********"}, "Any"]

        assert mask_secrets({'secret': "secret"}, fragments=('token', 'secret')) == {'secret': "sec*********"}
        assert mask_secrets({'_token': "secret"}, fragments=('token', 'secret')) == {'_token': "sec*********"}
        assert mask_secrets({'_token': "secret"}, fragments=('TOKEN', 'secret')) == {'_token': "secret"}

        untouched = 'untouched_Pw_d_p_a_s_s_word'
        dat = {'key1': {'subKey1': (
                                    {'host_Pwd': "secret"},
                                    untouched,
                                    ),
                        'passWord___': "secRet",
                        },
               'any_PASSWORD_to_hide': "Se",
               untouched: untouched,
               }
        assert mask_secrets(dat) is dat
        assert dat['key1']['subKey1'][0]['host_Pwd'] == "sec*********"
        assert dat['key1']['passWord___'] == "sec*********"
        assert dat['any_PASSWORD_to_hide'] == "Se*********"

        assert dat['key1']['subKey1'][1] == untouched
        assert dat[untouched] == untouched

    def test_mask_url(self):
        assert mask_url("") == ""

        password, domain, path = "toBeMaskedPassword", "any-not_existing-host_domain.zzz", "any/not/existing/url/path"

        url = f"https://username:{password}@{domain}/{path}"
        assert password not in mask_url(url)
        assert domain in mask_url(url)
        assert path in mask_url(url)

        url = f"https://username@{domain}:8081/{path}"
        assert mask_url(url) == url

    def test_norm_line_sep(self):
        assert norm_line_sep('a\r\nb') == 'a\nb'
        assert norm_line_sep('a\rb') == 'a\nb'

    def test_norm_name(self):
        assert norm_name("AnyCamelCaseName") == "AnyCamelCaseName"
        assert norm_name("anyCamelCaseName") == "anyCamelCaseName"
        assert norm_name("NoUnderScoreOnNone") == "NoUnderScoreOnNone"
        assert norm_name("any_name") == "any_name"
        # noinspection SpellCheckingInspection
        assert norm_name("äáßñìÄÏÜ") == "äáßñìÄÏÜ"
        assert norm_name("@special/chars!:;-`¡'´") == "_special_chars________"
        assert norm_name("abc123") == "abc123"
        assert norm_name("123abc") == "_23abc"
        assert norm_name("123abc", allow_num_prefix=True) == "123abc"

    def test_norm_path(self):
        new_folder = "non_existent_folder"
        
        assert norm_path(".") == os.getcwd()
        assert norm_path(".", resolve_sym_links=False) == os.getcwd()
        assert norm_path(".", make_absolute=False) == os.getcwd()
        assert norm_path(".", make_absolute=False, remove_base_path=os.getcwd()) == "."

        assert norm_path(new_folder) == os.path.join(os.getcwd(), new_folder)
        assert norm_path(new_folder, resolve_sym_links=False) == os.path.join(os.getcwd(), new_folder)
        assert norm_path(new_folder, make_absolute=False) == os.path.join(os.getcwd(), new_folder)
        assert norm_path(new_folder, make_absolute=False, remove_base_path=os.getcwd()) == new_folder

        assert norm_path(os.path.join(TESTS_FOLDER, "..")) == os.getcwd()
        assert norm_path(os.path.join(TESTS_FOLDER, ".."), resolve_sym_links=False) == os.getcwd()
        assert norm_path(os.path.join(TESTS_FOLDER, ".."), make_absolute=False) == os.getcwd()
        assert norm_path(os.path.join("ae", ".."), make_absolute=False, remove_base_path=os.getcwd()) == "."

        assert norm_path("~") != ""
        assert norm_path(os.path.join("~", new_folder)).endswith(new_folder)
        assert norm_path(os.path.join("~", new_folder), remove_base_path="~").endswith(new_folder)

    def test_now_str(self):
        assert len(now_str()) == 20
        assert len(now_str("_")) == 23

    @skip_gitlab_ci
    def test_on_ci_host_local(self):
        assert not on_ci_host()

    def test_on_ci_host_on_gitlab(self):
        assert on_ci_host() == ('CI_PROJECT_ID' in os.environ)

    @skip_gitlab_ci
    def test_on_ci_host_with_ci_var(self, monkeypatch):
        assert not on_ci_host()

        monkeypatch.setenv('CI', "any value")
        assert on_ci_host()

    @skip_gitlab_ci
    def test_on_ci_host_with_ci_project_id(self, monkeypatch):
        assert not on_ci_host()

        monkeypatch.setenv('CI_PROJECT_ID', "any value")
        assert on_ci_host()

    def test_os_host_name(self):
        print(os_host_name())
        assert os_host_name()

    def test_os_local_ip(self):
        assert os_local_ip() or os_local_ip() == ""

    def test_os_platform_android(self):
        try:
            os.environ['ANDROID_ARGUMENT'] = 'tst'
            assert _os_platform() == 'android'
        finally:
            os.environ.pop('ANDROID_ARGUMENT', None)

        # noinspection PyUnreachableCode
        try:
            os.environ['KIVY_BUILD'] = 'android'
            assert _os_platform() == 'android'
        finally:
            os.environ.pop('KIVY_BUILD', None)

    def test_os_platform_cygwin(self):
        old_platform = sys.platform
        try:
            sys.platform = 'cygwin'
            assert _os_platform() == 'cygwin'
        finally:
            sys.platform = old_platform

    def test_os_platform_darwin(self):
        old_platform = sys.platform
        try:
            sys.platform = 'darwin'
            assert _os_platform() == 'darwin'
        finally:
            sys.platform = old_platform

    def test_os_platform_freebsd(self):
        old_platform = sys.platform
        try:
            sys.platform = 'freebsd'
            assert _os_platform() == 'freebsd'
        finally:
            sys.platform = old_platform

    def test_os_platform_ios(self):
        try:
            os.environ['KIVY_BUILD'] = 'ios'
            assert _os_platform() == 'ios'
        finally:
            os.environ.pop('KIVY_BUILD', None)

    def test_os_platform_win32(self):
        old_platform = sys.platform
        try:
            sys.platform = 'win32'
            assert _os_platform() == 'win32'
        finally:
            sys.platform = old_platform

    def test_os_user_name(self):
        print(os_user_name())
        assert os_user_name()

    def test_parse_dotenv_dollar_char_does_not_cutoff_value(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write('declaredVar = DeclaredValue\n')
            fp.write('replacedVar = beforeTheDollar$declaredVar\n')
            fp.write('uncutVar=beforeTheDollar$afterTheDollar\n')
            fp.seek(0)
            late_resolved = {}

            loaded = parse_dotenv(fp.name, late_resolved)

            assert 'replacedVar' in loaded
            assert 'uncutVar' in loaded
            late_env_var_resolver(loaded, loaded, late_resolved)
            assert loaded['replacedVar'] == "beforeTheDollarDeclaredValue"
            assert loaded['uncutVar'] == "beforeTheDollar$afterTheDollar"

    def test_parse_dotenv_double_quoted_value(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write('var_nam="var val"')
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' in loaded
            assert loaded['var_nam'] == "var val"

    def test_parse_dotenv_double_quote_in_single_value(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("""var_nam='"var val"'""")
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' in loaded
            assert loaded['var_nam'] == '"var val"'

    def test_parse_dotenv_exclude_vars_dict_arg(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("exc_var0=var val\nvar_nam=var val\nexc_var1='excluded var val'")
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {}, exclude_vars={'exc_var0': "not overwritten value", 'exc_var1': ""})

            assert 'exc_var0' not in loaded
            assert 'exc_var1' not in loaded
            assert 'var_nam' in loaded

    def test_parse_dotenv_exclude_vars_tuple_arg(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("exc_var0=var val\nvar_nam=var val\nexc_var1='excluded var val'")
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {}, exclude_vars=('exc_var0', 'exc_var1'))

            assert 'exc_var0' not in loaded
            assert 'exc_var1' not in loaded
            assert 'var_nam' in loaded

    def test_parse_dotenv_error_space_prefixed_var_name(self, recwarn):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write(' var_nam="var val"')
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' not in loaded
            assert len(recwarn) == 1
            assert f"doesn't match {DOTENV_FILE_NAME} format" in str(recwarn[0].message)

    def test_parse_dotenv_literal_dict_with_list(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            var_val = "{'key': {'sub-key': ['list-item', 'list-item with = char', ]}}"
            fp.write("var_nam=" + var_val)
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' in loaded
            assert loaded['var_nam'] == var_val

    def test_parse_dotenv_literal_dict_with_list_quoted(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            var_val = "{'key': {'sub-key': ['list-item', 'list-item with = char']}}"
            fp.write('var_nam="' + var_val + '"')
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' in loaded
            assert loaded['var_nam'] == var_val

    def test_parse_dotenv_multi_line_var_value(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            var_val = "{'key': {'sub-key':\\\n    ['list-item',\\\n     'list-item with = char', ]}}"
            fp.write("var_nam=" + var_val)
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' in loaded
            assert loaded['var_nam'] == var_val.replace('\\\n', "")

    def test_parse_dotenv_single_in_double_quoted_value(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write('''var_nam="'var val'"''')
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' in loaded
            assert loaded['var_nam'] == "'var val'"

    def test_parse_dotenv_single_value(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("var_nam='var val'")
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' in loaded
            assert loaded['var_nam'] == "var val"

    def test_parse_dotenv_start_parent_first_in_chain(self, os_env_test_env):
        assert DOTENV_VAR_NAME not in os.environ
        file_path = os.path.join(os_env_test_env, DOTENV_DIR_NAME, DOTENV_FILE_NAME)

        loaded = parse_dotenv(file_path, {})

        assert DOTENV_VAR_NAME in loaded
        assert loaded[DOTENV_VAR_NAME] == DOTENV_VAR_VAL + '1'

    def test_parse_dotenv_space_surrounded_value(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("var_nam   =   var val   ")
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' in loaded
            assert loaded['var_nam'] == "var val"

    def test_parse_dotenv_unquoted_value(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("var_nam=var val")
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' in loaded
            assert loaded['var_nam'] == "var val"

    def test_parse_dotenv_var_escaped_double_quote(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write('var_nam="escaped\\"val"')
            fp.seek(0)
            late_resolved = {}

            loaded = parse_dotenv(fp.name, late_resolved)

            assert 'var_nam' in loaded
            late_env_var_resolver(loaded, loaded, late_resolved)
            assert loaded['var_nam'] == 'escaped"val'

    def test_parse_dotenv_var_empty_value(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("var_nam=")
            fp.seek(0)
            late_resolved = {}

            loaded = parse_dotenv(fp.name, late_resolved)

            assert 'var_nam' in loaded
            late_env_var_resolver(loaded, loaded, late_resolved)
            assert loaded['var_nam'] == ""

    def test_parse_dotenv_var_expands_variables_found_in_values(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("env_var=var val\nvar_nam=$env_var")
            fp.seek(0)
            late_resolved = {}

            loaded = parse_dotenv(fp.name, late_resolved)

            assert 'var_nam' in loaded
            late_env_var_resolver(loaded, loaded, late_resolved)
            assert loaded['var_nam'] == "var val"
            assert 'env_var' in loaded
            assert loaded['env_var'] == "var val"

    def test_parse_dotenv_var_expands_variable_wrapped_in_brackets(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("env_var=var val\n\n\nvar_nam=${env_var} tst")
            fp.seek(0)
            late_resolved = {}

            loaded = parse_dotenv(fp.name, late_resolved)

            assert 'var_nam' in loaded
            late_env_var_resolver(loaded, loaded, late_resolved)
            assert loaded['var_nam'] == "var val tst"
            assert 'env_var' in loaded
            assert loaded['env_var'] == "var val"

    def test_parse_dotenv_var_expands_not_an_undefined_variable_to_empty_string(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("var_nam=$env_var")
            fp.seek(0)
            late_resolved = {}

            loaded = parse_dotenv(fp.name, late_resolved)

            assert 'env_var' not in loaded
            assert 'var_nam' in loaded
            late_env_var_resolver(loaded, loaded, late_resolved)
            assert loaded['var_nam'] == "$env_var"

    def test_parse_dotenv_var_expands_in_double_quoted_values(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("env_var=tst\nvar_nam=\"var val $env_var\"")
            fp.seek(0)
            late_resolved = {}

            loaded = parse_dotenv(fp.name, late_resolved)

            assert 'var_nam' in loaded
            late_env_var_resolver(loaded, loaded, late_resolved)
            assert loaded['var_nam'] == "var val tst"

    def test_parse_dotenv_var_export_keyword(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("export var_nam=var val")
            fp.seek(0)

            loaded = parse_dotenv(fp.name, {})

            assert 'var_nam' in loaded
            assert loaded['var_nam'] == "var val"

    def test_parse_dotenv_var_not_expands_in_single_quoted_values(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("var_nam='var val $env_var'")
            fp.seek(0)
            late_resolved = {}

            loaded = parse_dotenv(fp.name, late_resolved)

            assert 'var_nam' in loaded
            late_env_var_resolver(loaded, loaded, late_resolved)
            assert loaded['var_nam'] == "var val $env_var"

    def test_parse_dotenv_var_not_expands_escaped_variables(self):
        with tempfile.NamedTemporaryFile(mode="w") as fp:
            fp.write("var_nam=var val \\$env_var \\${env_var}")
            fp.seek(0)
            late_resolved = {}

            loaded = parse_dotenv(fp.name, late_resolved)

            assert 'var_nam' in loaded
            late_env_var_resolver(loaded, loaded, late_resolved)
            assert loaded['var_nam'] == "var val $env_var ${env_var}"

    def test_project_main_file(self, tmp_path):
        assert project_main_file("not_existing_xy.tst") == ""

        ae_base_main_file = norm_path(os.path.join("ae", "base" + PY_EXT))
        assert project_main_file("ae.base") == ae_base_main_file
        assert project_main_file("ae.base", norm_path("")) == ae_base_main_file

        local_project_dir = os.path.join(str(tmp_path), "ae_base")
        local_main_file = norm_path(os.path.join(local_project_dir, "main.py"))

        os.makedirs(local_project_dir)
        write_file(local_main_file, "# main file content")
        assert project_main_file("ae.base") == ae_base_main_file
        assert project_main_file("ae.base", norm_path("")) == ae_base_main_file
        assert project_main_file("ae.base", local_project_dir) == local_main_file
        assert project_main_file("ae.base", norm_path(local_project_dir)) == local_main_file

    def test_read_file(self):
        with open(__file__) as file_handle:
            content = file_handle.read()
        assert read_file(__file__) == content
        assert read_file(__file__, extra_mode="b") == bytes(content, 'utf8')

    def test_round_traditional(self):
        assert round_traditional(1.01) == 1
        assert round_traditional(10.1, -1) == 10
        assert round_traditional(1.123, 1) == 1.1
        assert round_traditional(0.5) == 1
        assert round_traditional(0.5001, 1) == 0.5

        assert round_traditional(0.075, 2) == 0.08
        assert round(0.075, 2) == 0.07

    def test_sign_with_float_arg(self):
        assert sign(1.11) == 1
        assert sign(-0.000003) == -1
        assert sign(0.0000000) == 0
        assert sign(-0.0) == 0

    def test_sign_with_int_arg(self):
        assert sign(3) == 1
        assert sign(-6) == -1
        assert sign(0) == 0
        assert sign(-0) == 0

    def test_sign_with_invalid_arg(self):
        with pytest.raises(TypeError):
            # noinspection PyArgumentList
            sign()

        with pytest.raises(TypeError):
            # noinspection PyArgumentList,PyTypeChecker
            sign(None)

        with pytest.raises(TypeError):
            # noinspection PyArgumentList,PyTypeChecker
            sign(UNSET)

    def test_snake_to_camel(self):
        assert snake_to_camel("_Any_Camel_Case_Name") == "AnyCamelCaseName"
        assert snake_to_camel("any_Camel_Case_Name") == "AnyCamelCaseName"
        assert snake_to_camel("any_Camel_Case_Name", back_convertible=True) == "anyCamelCaseName"

        assert snake_to_camel("houseMen") == "Housemen"
        assert snake_to_camel("any_name") == "AnyName"
        assert snake_to_camel("any_name", back_convertible=True) == "anyName"
        assert snake_to_camel("@special/chars!") == "@special/chars!"

    def test_sys_env_dict(self):
        assert sys_env_dict().get('python ver')
        assert sys_env_dict().get('cwd')
        assert sys_env_dict().get('frozen') is False

        assert sys_env_dict().get('bundle_dir') is None
        sys.frozen = True
        assert sys_env_dict().get('bundle_dir')
        # noinspection PyUnresolvedReferences
        del sys.__dict__['frozen']      # sys.__dict__.pop('frozen')
        assert sys_env_dict().get('bundle_dir') is None

    def test_sys_env_text(self):
        assert isinstance(sys_env_text(), str)
        assert 'python ver' in sys_env_text()
        ret = sys_env_text(extra_sys_env_dict=dict(test_add='TstAdd'))
        assert 'test_add' in ret
        assert 'TstAdd' in ret

    def test_to_ascii(self):
        assert to_ascii('áéí óú') == 'aei ou'
        assert to_ascii('ÁÉÍ ÓÚ') == 'AEI OU'

        assert to_ascii('àèì òù') == 'aei ou'
        assert to_ascii('ÀÈÌ ÒÙ') == 'AEI OU'

        assert to_ascii('äëï öü') == 'aei ou'
        assert to_ascii('ÄËÏ ÖÜ') == 'AEI OU'

        assert to_ascii('âêî ôû') == 'aei ou'
        assert to_ascii('ÂÊÎ ÔÛ') == 'AEI OU'

        assert to_ascii('ß') == 'ss'
        assert to_ascii('€') == 'Euro'

    @staticmethod
    def url_failure_httpbin_50x_retryer(url: str, timeout: Optional[float] = None) -> tuple[str, str]:
        """ retry if httpbin is unavailable with 503 error (sometimes 502) """
        retries = 9
        while True:
            err_msg = url_failure(url, timeout=timeout)
            if not err_msg or int(err_msg[:3]) not in (502, 503) or retries == 0:
                break
            time.sleep(3)
            retries -= 1
        return err_msg, f"url_failure({url=}, {timeout=}) httpbin is sometimes unavailable/503. retry later; {err_msg=}"

    def test_url_failure(self):
        assert not url_failure("https://gitlab.com/ae-group/ae_base")

        assert not url_failure("https://gitlab.com/ae-group/ae_base.git")

        assert not url_failure("https://gitlab.com/ae-group/ae_base", git_repo=True)

        assert not url_failure("https://www.google.com")

        if not on_ci_host():
            ret, message = self.url_failure_httpbin_50x_retryer("https://httpbin.org/status/200")
            assert not ret, message

    def test_url_failure_authentication_errors(self):
        password, domain, path = "toBeMaskedPassword", "any-not_existing-host_domain.zzz", "any/not/existing/url/path"
        url = f"https://username:{password}@{domain}/{path}"
        err_msg = "raised exception error message"

        ret = url_failure(url, token=password)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret

        ret = url_failure(url, username="any user name", password=password)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret

        ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret

        # noinspection PyInvalidCast
        mocked_headers = cast(HTTPMessage, {})

        def mock_raise_http_error404(*_args, **_kwargs):
            raise HTTPError(url=url, code=404, msg=err_msg, hdrs=mocked_headers, fp=None)

        with patch('ae.base.urlopen', mock_raise_http_error404):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def mock_raise_http_error503(*_args, **_kwargs):
            raise HTTPError(url=url, code=503, msg=err_msg, hdrs=mocked_headers, fp=None)

        with patch('ae.base.urlopen', mock_raise_http_error503):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def mock_raise_gai_error(*_args, **_kwargs):
            raise URLError(reason=socket.gaierror(err_msg))

        with patch('ae.base.urlopen', mock_raise_gai_error):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def mock_raise_timeout(*_args, **_kwargs):
            raise URLError(reason=socket.timeout(err_msg))

        with patch('ae.base.urlopen', mock_raise_timeout):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def mock_raise_socket_timeout(*_args, **_kwargs):
            raise socket.timeout(err_msg)

        with patch('ae.base.urlopen', mock_raise_socket_timeout):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert f"{mask_url(url)} raised socket-timeout exception" in ret

        def mock_raise_ssl_error(*_args, **_kwargs):
            raise URLError(reason=ssl.SSLCertVerificationError(1, err_msg))

        with patch('ae.base.urlopen', mock_raise_ssl_error):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def mock_raise_generic_url_error(*_args, **_kwargs):
            raise URLError(reason=err_msg)

        with patch('ae.base.urlopen', mock_raise_generic_url_error):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret
        assert err_msg in ret

        def mock_raise_unexpected_error(*_args, **_kwargs):
            raise ValueError(err_msg)

        with patch('ae.base.urlopen', mock_raise_unexpected_error):
            ret = url_failure(url)

        assert ret
        assert int(ret[:3]) > 0
        assert password not in ret
        assert domain in ret
        assert path in ret

    def test_url_failure_ssl_errors(self):
        ret = url_failure(f"https://expired.badssl.com")

        assert ret
        assert int(ret[:3]) > 0

    @skip_gitlab_ci
    def test_url_failure_timeout_errors(self):
        ret, message = self.url_failure_httpbin_50x_retryer("https://httpbin.org/delay/3", timeout=0.9)

        assert ret, message
        assert ret[:3] == '997', message

    @skip_gitlab_ci
    def test_url_failure_url_errors(self):
        assert url_failure("")

        ret, message = self.url_failure_httpbin_50x_retryer(url2 := "https://httpbin.org/status/504")

        assert ret, message
        assert ret[:3] == '504', message
        assert ret[4:].startswith(mask_url(url2)), message

        with pytest.raises(AttributeError):
            # noinspection PyInvalidCast
            url_failure(cast(str, 123456))

    def test_utc_datetime(self):
        dt1 = utc_datetime()
        dt2 = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        assert dt2 - dt1 < datetime.timedelta(seconds=1)

    def test_write_file_as_text(self, tmp_path):
        test_file = os.path.join(str(tmp_path), 'tst_file_written.ext')
        content = "any content"
        assert not os.path.exists(test_file)

        write_file(test_file, content)
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_file(test_file) == content

    def test_write_file_as_binary(self, tmp_path):
        test_file = os.path.join(str(tmp_path), 'bin_file_written.ext')
        content = b"any content"
        assert not os.path.exists(test_file)

        write_file(test_file, content, extra_mode="b")
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_file(test_file, extra_mode="b") == content

        write_file(test_file, content)      # 'b' in extra_mode arg is optional because content is bytes array
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_file(test_file, extra_mode="b") == content

    def test_write_file_make_dirs(self, tmp_path):
        root_dir = os.path.join(str(tmp_path), 'root path of file')
        test_dir = os.path.join(root_dir, '1st sub dir of file', 'subDir2')
        test_file = os.path.join(test_dir, 'file in sub dir.ext')
        content = "any content"
        assert not os.path.exists(test_dir)
        assert not os.path.exists(test_file)

        with pytest.raises(FileNotFoundError):
            write_file(test_file, content)
        write_file(test_file, content, make_dirs=True)
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)
        assert os.path.exists(test_file)
        assert os.path.isfile(test_file)
        assert read_file(test_file) == content


class TestModuleHelpers:
    def test_module_attr_callable_with_args(self):
        namespace = TESTS_FOLDER
        mod_name = 'test_module_name'
        att_name = 'test_module_func'
        module_file = cast(str, os.path.join(namespace, mod_name + PY_EXT))
        try:
            write_file(module_file, f"def {att_name}(*args, **kwargs):\n    return args, kwargs\n")
            args = (1, '2')
            kwargs = dict(kwarg1=1, kwarg2='2')

            ret = module_attr(namespace + '.' + mod_name, attr_name=att_name)
            assert ret
            assert callable(type(ret))

            call_ret = ret(*args, **kwargs)
            assert call_ret
            assert call_ret[0] == args
            assert call_ret[1] == kwargs

        finally:
            if os.path.exists(module_file):
                os.remove(module_file)

        # test already imported module
        # noinspection PyUnreachableCode
        callee = module_attr('textwrap', attr_name='indent')
        assert callable(callee)
        assert callee is textwrap.indent

    def test_module_attr_callable_wrong_args(self):
        namespace = TESTS_FOLDER
        mod_name = 'test_module_name'
        att_name = 'test_module_func'
        module_file = cast(str, os.path.join(namespace, mod_name + PY_EXT))
        try:
            write_file(module_file, f"def {att_name}(arg1, args2, kwarg1='default'):\n    return arg1, arg2, kwarg1\n")

            callee = module_attr(namespace + '.' + mod_name, attr_name=att_name)
            assert callable(callee)

            args = (1, '2')
            kwargs = dict(kwarg1=1, kwarg2='2')
            with pytest.raises(TypeError):
                callee(*args, **kwargs)

        finally:
            if os.path.exists(module_file):
                os.remove(module_file)

    def test_module_attr_imported(self):
        """ test with module w/ and w/o namespace. """
        assert isinstance(module_attr('os'), ModuleType)
        assert isinstance(module_attr('textwrap'), ModuleType)
        assert isinstance(module_attr('ae.base'), ModuleType)

    def test_module_attr_module_ref(self, monkeypatch, tmp_path):
        namespace = str(tmp_path)
        mod_name = 'test_module_name'
        module_file = cast(str, os.path.join(namespace, mod_name + PY_EXT))

        write_file(module_file, "# empty module")

        ret = module_attr(namespace + '.' + mod_name)
        assert isinstance(ret, ModuleType)

        monkeypatch.chdir(namespace)

        ret = module_attr(mod_name)
        assert isinstance(ret, ModuleType)

    def test_module_attr_not_exists_attr(self, monkeypatch, tmp_path):
        """ first test with a non-existing module, second test with a non-existing function. """
        namespace = str(tmp_path)
        mod_name = 'test_module_name'
        att_name = 'test_module_func'
        module_file = cast(str, os.path.join(namespace, mod_name + PY_EXT))
        write_file(module_file, f"""def {att_name}(*args, **kwargs):\n    pass\n""")

        ret = module_attr(namespace + '.' + mod_name, attr_name="not_existing_func_or_attr")
        assert ret is UNSET

        ret = module_attr(namespace + '.' + mod_name, attr_name=att_name)
        assert callable(ret)

        monkeypatch.chdir(namespace)

        ret = module_attr(mod_name)
        assert ret
        assert type(ret) is ModuleType

    def test_module_attr_not_exists_module(self):
        """ first test with a non-existing module, second test with a non-existing function. """
        mod_name = 'non_existing_test_module_name'
        att_name = 'non_existing_test_module_func'
        assert module_attr(mod_name, attr_name=att_name) is None

    def test_module_file_path(self):
        assert module_file_path() == __file__
        assert module_file_path(lambda: 0) == __file__

    def test_module_name(self):
        assert module_name() == 'test_base'
        assert module_name('') == 'test_base'
        # noinspection PyInvalidCast
        assert module_name(cast(str, None)) == 'test_base'
        assert module_name('_invalid_module_name') == 'test_base'
        assert module_name('ae.base') == 'test_base'
        assert module_name(depth=-30) == 'test_base'
        assert module_name(depth=-2) == 'test_base'
        assert module_name(depth=-1) == 'test_base'
        # assert module_name(depth=0) == 'test_base'   # depth=0 is default value
        # assert module_name(depth=1) == '_pytest.python'

        assert module_name(__name__, depth=-30) == 'ae.base'
        assert module_name(__name__, depth=-2) == 'ae.base'
        assert module_name(__name__, depth=-1) == 'ae.base'

        # assert module_name(__name__) == '_pytest.python'                  # depth=0 is the default
        # assert module_name('test_base') == '_pytest.python'
        # assert module_name(__name__, depth=1) == '_pytest.python'


class TestStackHelpers:
    def test_full_stack_trace(self):
        try:
            raise ValueError
        except ValueError as ex:
            # print(full_stack_trace(ex))
            assert full_stack_trace(ex)

    def test_stack_frames(self):
        for frame in stack_frames():
            assert frame
            assert getattr(frame, 'f_globals')
            # if pytest runs from terminal, then f_locals is missing in the highest frame:
            # assert getattr(frame, 'f_locals')

    def test_stack_var_module(self):
        assert module_test_var
        assert stack_var('module_test_var', depth=-1) == 'module_test_var_val'
        assert stack_var('module_test_var', depth=0) == 'module_test_var_val'
        assert stack_var('module_test_var', scope='globals', depth=0) == 'module_test_var_val'
        assert stack_var('module_test_var', 'ae.base', depth=0) == 'module_test_var_val'

        assert stack_var('module_test_var') is UNSET      # depth==1 (def)
        assert stack_var('module_test_var', depth=2) is UNSET
        assert stack_var('module_test_var', scope='locals', depth=0) is UNSET
        assert stack_var('module_test_var', scope='locals') is UNSET
        assert stack_var('module_test_var', 'test_base') is UNSET
        assert stack_var('module_test_var', 'ae.base', 'test_base') is UNSET

    def test_stack_var_func(self):
        _func_var = 'func_var_val'

        assert stack_var('_func_var', 'ae.base', scope='locals', depth=0) == 'func_var_val'
        assert stack_var('_func_var', depth=0) == 'func_var_val'
        assert stack_var('_func_var', scope='locals', depth=0) == 'func_var_val'

        # assert stack_var('_func_var', scope='locals', depth=1) is UNSET
        assert stack_var('_func_var') is UNSET
        assert stack_var('_func_var', scope='globals', depth=0) is UNSET
        assert stack_var('_func_var', 'test_base', scope='locals') is UNSET
        assert stack_var('_func_var', 'ae.base', 'test_base', scope='locals') is UNSET
        assert stack_var('_func_var', scope='locals', depth=3) is UNSET

    def test_stack_var_inner_func(self):
        def _inner_func():
            _inner_var = 'inner_var_val'
            assert stack_var('_inner_var', depth=-1) == 'inner_var_val'
            assert stack_var('_inner_var', depth=0) == 'inner_var_val'
            assert stack_var('_inner_var', scope='locals', depth=0) == 'inner_var_val'
            assert stack_var('_inner_var', 'ae.base', scope='locals', depth=0) == 'inner_var_val'
            assert stack_var('_inner_var', 'ae.base', 'xxx yyy', scope='locals', depth=0) == 'inner_var_val'

            assert stack_var('_inner_var') is UNSET     # depth==1 (def)
            assert stack_var('_inner_var', depth=2) is UNSET
            assert stack_var('_inner_var', scope='globals', depth=0) is UNSET
            assert stack_var('_inner_var', 'test_base', scope='locals', depth=0) is UNSET

            assert stack_var('_outer_var') == 'outer_var_val'
            assert stack_var('_outer_var', depth=0) == 'outer_var_val'
            assert stack_var('_outer_var', 'ae.base', scope='locals') == 'outer_var_val'
            assert stack_var('_outer_var', scope='locals') == 'outer_var_val'
            assert stack_var('_outer_var', scope='locals', depth=0) == 'outer_var_val'

            assert stack_var('_outer_var', scope='locals', depth=2) is UNSET
            assert stack_var('_outer_var', 'test_base', scope='locals') is UNSET
            assert stack_var('_outer_var', 'ae.base', 'test_base', scope='locals') is UNSET

            assert stack_var('module_test_var') == 'module_test_var_val'
            assert stack_var('module_test_var', scope='globals') == 'module_test_var_val'

            assert stack_var('module_test_var', depth=2) is UNSET
            assert stack_var('module_test_var', scope='locals') is UNSET
            assert stack_var('module_test_var', 'test_base') is UNSET
            assert stack_var('module_test_var', 'ae.base', 'test_base') is UNSET

        _outer_var = 'outer_var_val'
        _inner_func()

        assert stack_var('_outer_var', depth=0) == 'outer_var_val'
        assert stack_var('_outer_var', 'ae.base', scope='locals', depth=0) == 'outer_var_val'
        assert stack_var('_outer_var', scope='locals', depth=0) == 'outer_var_val'

        assert stack_var('_outer_var') is UNSET
        assert stack_var('_outer_var', scope='locals') is UNSET
        assert stack_var('_outer_var', scope='locals', depth=2) is UNSET
        assert stack_var('_outer_var', 'test_base') is UNSET

        assert stack_var('module_test_var', depth=0) == 'module_test_var_val'
        assert stack_var('module_test_var', depth=0, scope='globals') == 'module_test_var_val'

        assert stack_var('module_test_var') is UNSET
        assert stack_var('module_test_var', depth=2) is UNSET
        assert stack_var('module_test_var', depth=3) is UNSET
        assert stack_var('module_test_var', scope='locals', depth=0) is UNSET
        assert stack_var('module_test_var', 'test_base') is UNSET
        assert stack_var('module_test_var', 'ae.base', 'test_base') is UNSET

    def test_stack_vars(self):
        local_var = "loc_var_val"
        glo, loc, deep = stack_vars(min_depth=0, max_depth=1)
        assert deep == 1
        assert 'local_var' in loc
        assert loc['local_var'] == local_var

        glo, loc, deep = stack_vars(max_depth=3)
        assert deep == 3

        glo, loc, deep = stack_vars(min_depth=0, find_name='module_test_var')    # min_depth needed for this stack frame
        assert glo.get('module_test_var') == 'module_test_var_val'

        glo, loc, deep = stack_vars(find_name='module_test_var')                 # min_depth default == 1
        assert glo.get('module_test_var') is None

        glo, loc, deep = stack_vars(min_depth=2, find_name='module_test_var')    # min_depth needed for this stack frame
        assert glo.get('module_test_var') is None
