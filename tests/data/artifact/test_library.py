from kataloger.data.artifact.library import Library


class TestLibrary:
    def test_library_to_path_should_return_path_part_from_library_coordinates(self):
        library: Library = Library(
            name="library",
            coordinates="com.library.group:library-artifact-id",
            version="1.0.0",
        )
        expected_path_part: str = "com/library/group/library-artifact-id"

        assert library.to_path() == expected_path_part
