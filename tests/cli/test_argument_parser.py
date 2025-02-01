from pathlib import Path
from typing import Optional

from kataloger.cli.argument_parser import parse_arguments
from kataloger.data.catalog import Catalog
from kataloger.data.configuration_data import ConfigurationData
from kataloger.data.kataloger_arguments import KatalogerArguments


class TestArgumentParser:

    def test_should_return_empty_arguments_when_no_arguments_passed(self):
        expected_arguments: KatalogerArguments = self.__create_arguments(
            configuration_path=None,
            catalogs=None,
            verbose=None,
            suggest_unstable_updates=None,
            fail_on_updates=None,
        )
        actual_arguments: KatalogerArguments = parse_arguments()

        assert actual_arguments == expected_arguments

    def test_should_return_arguments_with_configuration_path_when_valid_configuration_path_argument_passed(
        self,
        tmp_conf: Path,
    ):
        expected_arguments: KatalogerArguments = self.__create_arguments(
            configuration_path=tmp_conf,
            catalogs=None,
            verbose=None,
            suggest_unstable_updates=None,
            fail_on_updates=None,
        )
        actual_short_form_arguments: KatalogerArguments = parse_arguments("-c", str(tmp_conf))
        actual_long_form_arguments: KatalogerArguments = parse_arguments("--configuration", str(tmp_conf))

        assert actual_short_form_arguments == expected_arguments
        assert actual_long_form_arguments == expected_arguments

    def test_should_return_arguments_with_catalogs_when_valid_catalog_paths_arguments_passed(self, tmp_catalog: Path):
        expected_arguments: KatalogerArguments = self.__create_arguments(
            configuration_path=None,
            catalogs=[Catalog.from_path(tmp_catalog)],
            verbose=None,
            suggest_unstable_updates=None,
            fail_on_updates=None,
        )
        actual_short_form_arguments: KatalogerArguments = parse_arguments("-p", str(tmp_catalog))
        actual_long_form_arguments: KatalogerArguments = parse_arguments("--path", str(tmp_catalog))

        assert actual_short_form_arguments == expected_arguments
        assert actual_long_form_arguments == expected_arguments

    def test_should_return_arguments_with_true_verbose_flag_when_verbose_argument_passed(self):
        expected_arguments: KatalogerArguments = self.__create_arguments(
            configuration_path=None,
            catalogs=None,
            verbose=True,
            suggest_unstable_updates=None,
            fail_on_updates=None,
        )
        actual_short_form_arguments: KatalogerArguments = parse_arguments("-v")
        actual_long_form_arguments: KatalogerArguments = parse_arguments("--verbose")

        assert actual_short_form_arguments == expected_arguments
        assert actual_long_form_arguments == expected_arguments

    def test_should_return_arguments_with_true_suggest_unstable_flag_when_suggest_unstable_argument_passed(self):
        expected_arguments: KatalogerArguments = self.__create_arguments(
            configuration_path=None,
            catalogs=None,
            verbose=None,
            suggest_unstable_updates=True,
            fail_on_updates=None,
        )
        actual_short_form_arguments: KatalogerArguments = parse_arguments("-u")
        actual_long_form_arguments: KatalogerArguments = parse_arguments("--suggest-unstable")

        assert actual_short_form_arguments == expected_arguments
        assert actual_long_form_arguments == expected_arguments

    def test_should_return_arguments_with_true_fail_on_updates_flag_when_fail_on_updates_argument_passed(self):
        expected_arguments: KatalogerArguments = self.__create_arguments(
            configuration_path=None,
            catalogs=None,
            verbose=None,
            suggest_unstable_updates=None,
            fail_on_updates=True,
        )
        actual_short_form_arguments: KatalogerArguments = parse_arguments("-f")
        actual_long_form_arguments: KatalogerArguments = parse_arguments("--fail-on-updates")

        assert actual_short_form_arguments == expected_arguments
        assert actual_long_form_arguments == expected_arguments

    @staticmethod
    def __create_arguments(
        configuration_path: Optional[Path],
        catalogs: Optional[list[Catalog]],
        verbose: Optional[bool],
        suggest_unstable_updates: Optional[bool],
        fail_on_updates: Optional[bool],
    ) -> KatalogerArguments:
        return KatalogerArguments(
            configuration_path=configuration_path,
            configuration_data=ConfigurationData(
                catalogs=catalogs,
                library_repositories=None,
                plugin_repositories=None,
                verbose=verbose,
                suggest_unstable_updates=suggest_unstable_updates,
                fail_on_updates=fail_on_updates,
            ),
        )
