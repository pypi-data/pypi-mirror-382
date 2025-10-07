from __future__ import annotations

from functools import cache
from os import environ as env, getcwd
from os.path import relpath
from subprocess import Popen

from utz import err, named_pipes, pipeline, process


@cache
def get_git_root() -> str:
    return process.line('git', 'rev-parse', '--show-toplevel', log=False)


@cache
def get_dir_path() -> str:
    return relpath(getcwd(), get_git_root())


def join_pipelines(
    base_cmd: list[str],
    cmds1: list[str],
    cmds2: list[str],
    verbose: bool = False,
    executable: str | None = None,
    **kwargs,
) -> int:
    """Run two sequences of piped commands, pass their outputs as inputs to a ``base_cmd``.

    Args:
        base_cmd: Top=level command that takes two positional args (named pipes with the outputs
            of the ``cmds1`` and ``cmds2`` pipelines).
        cmds1: First sequence of commands to pipe together
        cmds2: Second sequence of commands to pipe together
        verbose: Whether to print commands being executed
        executable: Shell to use for executing commands; defaults to $SHELL
        **kwargs: Additional arguments passed to subprocess.Popen

    Returns:
        Exit code: 0 if all processes succeeded, otherwise the first non-zero exit code

    Each command sequence will be piped together before being compared.
    For example, if cmds1 = ['cat foo.txt', 'sort'], the function will
    execute 'cat foo.txt | sort' before comparing with cmds2's output.

    Adapted from https://stackoverflow.com/a/28840955"""
    if executable is None:
        executable = env.get('SHELL')

    with named_pipes(n=2) as pipes:
        (pipe1, pipe2) = pipes
        join_cmd = [
            *base_cmd,
            pipe1,
            pipe2,
        ]
        proc = Popen(join_cmd)
        processes = [proc]

        for pipe, cmds in ((pipe1, cmds1), (pipe2, cmds2)):
            if verbose:
                err(f"Running pipeline: {' | '.join(cmds)}")

            processes += pipeline(
                cmds,
                pipe,
                wait=False,
                executable=executable,
                **kwargs,
            )

        for p in processes:
            p.wait()

        # Check pipeline processes first (all except base_cmd which is processes[0])
        # Pipeline commands should succeed (returncode 0)
        for p in processes[1:]:
            if p.returncode != 0:
                return p.returncode

        # Return base_cmd exit code (may be 0, 1 for diff, or error code)
        return processes[0].returncode


