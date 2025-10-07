
import sys
from typing import Optional, Sequence
from mlgame.argument.cmd_argument import parse_cmd_and_get_arg_obj
from mlgame.mlgame_obj import run_mlgame
from mlgame.core.security import install_exec_killer


def main(argv: Optional[Sequence[str]] = None):
    argv = list(sys.argv[1:] if argv is None else argv)
    arg_obj = parse_cmd_and_get_arg_obj(argv)
    run_mlgame(arg_obj)

if __name__ == "__main__":
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
    install_exec_killer()
    main()