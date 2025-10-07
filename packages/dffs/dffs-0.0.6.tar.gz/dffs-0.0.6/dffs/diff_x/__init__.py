from __future__ import annotations

import subprocess
from typing import Tuple

from click import option, command

from dffs.cli import args, shell_exec_opt, no_shell_opt, verbose_opt, exec_cmd_opt
from dffs.utils import join_pipelines

color_opt = option('-c', '--color', is_flag=True, help='Colorize the output')
unified_opt = option('-U', '--unified', type=int, help='Number of lines of context to show (passes through to `diff`)')
ignore_whitespace_opt = option('-w', '--ignore-whitespace', is_flag=True, help="Ignore whitespace differences (pass `-w` to `diff`)")


@command('diff-x', short_help='Diff two files after running them through a pipeline of other commands', no_args_is_help=True)
@color_opt
@shell_exec_opt
@no_shell_opt
@unified_opt
@verbose_opt
@ignore_whitespace_opt
@exec_cmd_opt
@args
def main(
    color: bool,
    shell_executable: str | None,
    no_shell: bool,
    unified: int | None,
    verbose: bool,
    ignore_whitespace: bool,
    exec_cmds: Tuple[str, ...],
    args: Tuple[str, ...],
):
    """Diff two files after running them through a pipeline of other commands."""
    if len(args) < 2:
        raise ValueError('Must provide at least two files to diff')

    *cmds, path1, path2 = args
    cmds = list(exec_cmds) + cmds
    diff_args = [
        *(['-w'] if ignore_whitespace else []),
        *(['-U', str(unified)] if unified is not None else []),
        *(['--color=always'] if color else []),
    ]
    if cmds:
        first, *rest = cmds
        returncode = join_pipelines(
            base_cmd=['diff', *diff_args],
            cmds1=[ f'{first} {path1}', *rest ],
            cmds2=[ f'{first} {path2}', *rest ],
            verbose=verbose,
            shell=not no_shell,
            executable=shell_executable,
        )
        raise SystemExit(returncode)
    else:
        result = subprocess.run(['diff', *diff_args, path1, path2])
        raise SystemExit(result.returncode)
