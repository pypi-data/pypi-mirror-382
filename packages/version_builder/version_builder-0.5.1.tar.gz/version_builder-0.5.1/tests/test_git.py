import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from semver import Version

from src.version_builder.git import GitHelper


class MockTag:
    def __init__(self, name):
        self.name = name


class TestGitHelper:
    @pytest.mark.parametrize(
        "tags_return, expected_version",
        [
            ([], None),
            ([MockTag(name="1.0.0"), MockTag(name="1.0.1")], Version.parse("1.0.1")),
        ],
    )
    @patch("src.version_builder.git.Repo.init")
    def test_get_version(
        self,
        mock_repo,
        tags_return: list,
        expected_version: Version | None,
    ):
        """Test that get_version() returns the latest tag or None if no tags exist."""
        mock_repo.return_value.tags = tags_return

        version = GitHelper().get_version()
        assert version == expected_version

    @patch("git.repo.base.Repo.index")
    @patch("src.version_builder.git.Repo.init")
    def test_commit(self, mock_repo, mock_index):
        with (
            tempfile.NamedTemporaryFile() as temp_file,
            tempfile.NamedTemporaryFile() as temp_file2,
        ):
            GitHelper().commit(
                version="1.0.1",
                files=[Path(temp_file.name), Path(temp_file2.name)],
            )

            assert ".index.add" in str(mock_repo.mock_calls[2])
            assert temp_file.name in str(mock_repo.mock_calls[2])
            assert temp_file2.name in str(mock_repo.mock_calls[2])

            assert ".index.commit('Bump version to 1.0.1')" in str(
                mock_repo.mock_calls[3],
            )

    @patch("git.repo.base.Repo.create_tag")
    @patch("src.version_builder.git.Repo.init")
    def test_create_tag(self, mock_repo, mock_create_tag):
        """Test that create_tag() calls the Git repository's create_tag method."""
        tag = "1.2.0"
        GitHelper().create_tag(tag=tag)

        mock_repo.return_value.create_tag.assert_called_once_with(tag)
