from kataloger.data.artifact.plugin import Plugin


class TestPlugin:
    def test_plugin_to_path_should_return_path_part_from_plugin_coordinates(self):
        plugin: Plugin = Plugin(
            name="plugin",
            coordinates="com.plugin.artifact-id",
            version="1.0.0",
        )
        expected_path_part: str = "com/plugin/artifact-id/com.plugin.artifact-id.gradle.plugin"

        assert plugin.to_path() == expected_path_part
