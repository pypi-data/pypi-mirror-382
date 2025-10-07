"""Tests for utility functions."""
import pytest
from pathlib import Path
from dffs.utils import get_git_root, get_dir_path


class TestGitHelpers:
    """Test cases for Git helper functions."""

    def test_get_git_root(self):
        """Test get_git_root returns a valid path."""
        root = get_git_root()
        assert root
        assert Path(root).exists()
        assert Path(root, '.git').exists()

    def test_get_git_root_cached(self):
        """Test get_git_root uses cache."""
        root1 = get_git_root()
        root2 = get_git_root()
        assert root1 is root2  # Same object due to @cache

    def test_get_dir_path(self):
        """Test get_dir_path returns relative path from git root."""
        dir_path = get_dir_path()
        assert isinstance(dir_path, str)
        # Should not start with / (it's relative)
        assert not dir_path.startswith('/')

    def test_get_dir_path_cached(self):
        """Test get_dir_path uses cache."""
        path1 = get_dir_path()
        path2 = get_dir_path()
        assert path1 is path2  # Same object due to @cache
