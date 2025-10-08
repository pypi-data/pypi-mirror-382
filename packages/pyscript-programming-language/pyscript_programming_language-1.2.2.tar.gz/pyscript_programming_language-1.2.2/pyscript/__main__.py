from .core.buffer import PysFileBuffer
from .core.constants import DEFAULT, OPTIMIZE
from .core.handlers import handle_execute
from .core.highlight import HLFMT_HTML, HLFMT_ANSI, pys_highlight
from .core.runner import pys_runner, pys_shell
from .core.utils import normalize_path, build_symbol_table
from .core.version import __version__

from argparse import ArgumentParser

import sys

parser = ArgumentParser(
    prog='pyscript',
    description="PyScript Launcher for Python Version {}".format('.'.join(map(str, sys.version_info)))
)

parser.add_argument(
    'file',
    type=str,
    nargs='?',
    default=None,
    help="file path"
)

parser.add_argument(
    '-v', '-V', '--version',
    action='version',
    version="PyScript {}".format(__version__),
)

parser.add_argument(
    '-c', '--command',
    type=str,
    default=None,
    help="execute PyScript from argument",
)

parser.add_argument(
    '-O', '--optimize',
    action='store_true',
    help="set optimize flag"
)

parser.add_argument(
    '-i', '--inspect',
    action='store_true',
    help="inspect interactively after running a file",
)

parser.add_argument(
    '-l', '--highlight',
    choices=('html', 'ansi'),
    default=None,
    help='generate PyScript highlight code from a file'
)

args = parser.parse_args()

if args.highlight and args.file is None:
    parser.error("file path require")

flags = DEFAULT

if args.optimize:
    flags |= OPTIMIZE

if args.file is not None:
    args.file = normalize_path(args.file)

    try:
        with open(args.file, 'r') as file:
            file = PysFileBuffer(file.read(), args.file)

    except FileNotFoundError:
        parser.error("can't open file {!r}: No such file or directory".format(args.file))

    except PermissionError:
        parser.error("can't open file {!r}: Permission denied.".format(args.file))

    except IsADirectoryError:
        parser.error("can't open file {!r}: Path is not a file.".format(args.file))

    except NotADirectoryError:
        parser.error("can't open file {!r}: Attempting to access directory from file.".format(args.file))

    except (OSError, IOError):
        parser.error("can't open file {!r}: Attempting to access a system directory or file.".format(args.file))

    except UnicodeDecodeError:
        parser.error("can't read file {!r}: Bad file.".format(args.file))

    except BaseException as e:
        parser.error("file {!r}: Unexpected error: {}".format(args.file, e))

    if args.highlight:
        try:
            print(pys_highlight(file, HLFMT_HTML if args.highlight == 'html' else HLFMT_ANSI))
        except BaseException as e:
            parser.error("file {!r}: Tokenize error: {}".format(args.file, e))

    else:
        symtab = build_symbol_table(file)
        symtab.set('__name__', '__main__')

        result = pys_runner(
            file=file,
            mode='exec',
            symbol_table=symtab,
            flags=flags
        )

        code = handle_execute(result)

        if args.inspect:
            pys_shell(flags=flags, future=result.future, symbol_table=result.context.symbol_table)
        else:
            exit(code)

elif args.command is not None:
    file = PysFileBuffer(args.command)

    symtab = build_symbol_table(file)
    symtab.set('__name__', '__main__')

    exit(
        handle_execute(
            pys_runner(
                file=file,
                mode='exec',
                symbol_table=symtab,
                flags=flags
            )
        )
    )

else:
    pys_shell(flags=flags)