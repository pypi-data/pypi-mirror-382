"""Tests for join_pipelines function."""
import pytest
from dffs.utils import join_pipelines


class TestJoinPipelinesSuccess:
    """Test cases for successful pipeline execution."""

    def test_identical_output(self):
        """Test join_pipelines returns 0 when both pipelines produce identical output."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=['echo foo'],
            cmds2=['echo foo'],
            shell=True,
        )
        assert returncode == 0

    def test_multi_stage_pipeline(self):
        """Test join_pipelines with multi-stage pipelines that produce identical output."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=['echo "foo\nbar"', 'sort'],
            cmds2=['echo "bar\nfoo"', 'sort'],
            shell=True,
        )
        assert returncode == 0


class TestJoinPipelinesDifferences:
    """Test cases for pipelines with differences."""

    def test_diff_found(self):
        """Test join_pipelines returns 1 when diff finds differences."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=['echo foo'],
            cmds2=['echo bar'],
            shell=True,
        )
        assert returncode == 1


class TestJoinPipelinesErrors:
    """Test cases for error handling."""

    def test_cmd1_fails(self):
        """Test join_pipelines returns non-zero when first pipeline command fails."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=['false'],
            cmds2=['echo bar'],
            shell=True,
        )
        assert returncode != 0

    def test_cmd2_fails(self):
        """Test join_pipelines returns non-zero when second pipeline command fails."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=['echo foo'],
            cmds2=['false'],
            shell=True,
        )
        assert returncode != 0

    def test_both_cmds_fail(self):
        """Test join_pipelines returns non-zero when both pipeline commands fail."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=['false'],
            cmds2=['false'],
            shell=True,
        )
        assert returncode != 0

    def test_pipeline_error_nonexistent_file(self):
        """Test join_pipelines propagates errors from pipeline commands."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=['cat /nonexistent/file/that/does/not/exist'],
            cmds2=['echo bar'],
            shell=True,
        )
        assert returncode != 0

    def test_multi_stage_pipeline_with_error(self):
        """Test join_pipelines with multi-stage pipeline that fails."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=['echo "foo\nbar"', 'sort', 'false'],
            cmds2=['echo "bar\nfoo"', 'sort'],
            shell=True,
        )
        assert returncode != 0


class TestJoinPipelinesShellModes:
    """Test cases for different shell modes."""

    def test_shell_false_identical_output(self):
        """Test join_pipelines with shell=False returns 0 for identical output."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=[['echo', 'foo']],
            cmds2=[['echo', 'foo']],
            shell=False,
        )
        assert returncode == 0

    def test_shell_false_diff_found(self):
        """Test join_pipelines with shell=False returns 1 when diff finds differences."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=[['echo', 'foo']],
            cmds2=[['echo', 'bar']],
            shell=False,
        )
        assert returncode == 1

    def test_shell_false_cmd_fails(self):
        """Test join_pipelines with shell=False propagates command failures."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=[['false']],
            cmds2=[['echo', 'bar']],
            shell=False,
        )
        assert returncode != 0

    def test_shell_false_multi_stage(self):
        """Test join_pipelines with shell=False and multi-stage pipeline."""
        returncode = join_pipelines(
            base_cmd=['diff'],
            cmds1=[['printf', 'foo\\nbar'], ['sort']],
            cmds2=[['printf', 'bar\\nfoo'], ['sort']],
            shell=False,
        )
        assert returncode == 0
