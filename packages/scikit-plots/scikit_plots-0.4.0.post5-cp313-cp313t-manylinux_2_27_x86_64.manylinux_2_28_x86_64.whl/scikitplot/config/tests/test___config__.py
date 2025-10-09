# pylint: disable=no-name-in-module

"""Check the SciPy config is valid."""

from unittest.mock import patch

import pytest

from .. import __config__  # type: ignore[reportMissingModuleSource]

pytestmark = pytest.mark.skipif(
    not hasattr(__config__, "_built_with_meson"),
    reason="Requires Meson builds",
)


class TestScikitPlotsConfigs:
    REQUIRED_CONFIG_KEYS = ["Compilers", "Machine Information", "Python Information"]

    @pytest.mark.thread_unsafe
    @patch("scikitplot.config.__config__._check_pyyaml")
    def test_pyyaml_not_found(self, mock_yaml_importer):
        mock_yaml_importer.side_effect = ModuleNotFoundError()
        with pytest.warns(UserWarning):
            __config__.show_config()

    def test_dict_mode(self):
        config = __config__.show_config(mode="dicts")

        assert config is None or isinstance(config, dict)
        # assert all([key in config for key in self.REQUIRED_CONFIG_KEYS]), (
        #     "Required key missing,"
        #     " see index of `False` with `REQUIRED_CONFIG_KEYS`"
        # )

    def test_invalid_mode(self):
        with pytest.raises(AttributeError):
            __config__.show_config(mode="foo")

    def test_warn_to_add_tests(self):
        assert (
            len(__config__.DisplayModes) == 2
        ), "New mode detected, please add UT if applicable and increment this count"
