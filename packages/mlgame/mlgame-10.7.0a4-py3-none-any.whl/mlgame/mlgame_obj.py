from __future__ import annotations

import sys

from mlgame.core.security import install_exec_killer
sys.path.append('.')

import time
from typing import Optional, Sequence

from mlgame.argument.cmd_argument import parse_cmd_and_get_arg_obj
from mlgame.argument.tool import revise_ai_clients
from mlgame.core.process import create_process_of_az_uploader_and_start
from mlgame.executor.game import GameExecutor
from mlgame.executor.manual import GameManualExecutor
from mlgame.game.paia_game import get_paia_game_obj
from mlgame.utils.logger import logger
from mlgame.view.audio_model import MusicInitSchema, SoundInitSchema
from mlgame.view.sound_controller import SoundController
from mlgame.argument.model import MLGameArgument
from mlgame.argument.game_argument import GameConfig

from mlgame.core.communication import GameCommManager
from mlgame.core.process import (
    create_process_of_ai_clients_and_start,
    create_process_of_ws_and_start,
    create_process_of_recorder_and_start,
    terminate,
)
from mlgame.view.view import PygameView, DummyPygameView


class MLGameObj:
    def __init__(self, args: MLGameArgument):
        self.args = args

        self._ai_processes: list = []
        self._ws_proc = None
        self._record_proc = None
        self._az_upload_proc = None
        self._game_executor: Optional[GameExecutor | GameManualExecutor] = None
        self._game_comm: Optional[GameCommManager] = None


        game_config = GameConfig(game_folder=self.args.game_folder.__str__())
        parsed_game_params = game_config.parse_game_params(game_params=self.args.game_params)

        ai_clients = revise_ai_clients(
            ai_clients=self.args.group_ai,
            user_num_config=game_config.user_num_config
        )
        user_num = len(ai_clients)
        game = get_paia_game_obj(
            game_cls=game_config.game_cls,
            parsed_game_params=parsed_game_params,
            user_num=user_num,
            group_ai_list=ai_clients
        )

        self._game_config = game_config
        self._parsed_game_params = parsed_game_params
        self._ai_clients = ai_clients
        self._game = game

        if getattr(self.args, "is_debug", False):
            logger.remove()
            logger.add(
                sys.stdout,
                level="DEBUG",
                format="<green>{time:YYYY-MM-DD HH:mm:ss.SSSSS}</green> | "
                       "<level>{level: <8}</level> | <cyan>{name}</cyan>:"
                       "<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                       "<level>{message}</level>"
            )
            logger.add(
                "debug.log",
                level="DEBUG",
                rotation="10 MB",
                retention=1,
                compression=None,
            )

        self._setup_runtime()

    def _setup_runtime(self):
        logger.info("===========Game is started ===========")
        self._game_comm = GameCommManager()

        if self.args.ws_url:
            self._ws_proc = create_process_of_ws_and_start(self._game_comm, str(self.args.ws_url))

        if self.args.record_folder:
            self._record_proc = create_process_of_recorder_and_start(
                self._game_comm, self.args.record_folder, self.args.progress_frame_frequency
            )

        if self.args.az_upload_url:
            self._az_upload_proc = create_process_of_az_uploader_and_start(
                self._game_comm, self.args.az_upload_url
            )

        init_data = self._game.get_scene_init_data()



        if self.args.is_manual:
            game_view = PygameView(
                init_data,
                caption=f"PAIA Game: {self._game_config.game_name} v{self._game_config.game_version}",
                icon=self._game_config.logo,
            )
            self._game_executor = GameManualExecutor(
                self._game,
                game_view,
                self._game_comm,
                fps=getattr(self.args, "fps", 30),
                one_shot_mode=getattr(self.args, "one_shot_mode", False),
            )
        else:
            sound_controller = SoundController(
                is_sound_on=self.args.is_sound_on,
                music_objs=[MusicInitSchema(**obj) for obj in init_data.get("musics", [])],
                sound_objs=[SoundInitSchema(**obj) for obj in init_data.get("sounds", [])],
            )
            if self.args.no_display:
                logger.warning("Game will not be displayed.")
                game_view = DummyPygameView(init_data)
            else:
                game_view = PygameView(
                    init_data,
                    caption=f"PAIA Game: {self._game_config.game_name} v{self._game_config.game_version}",
                    icon=self._game_config.logo,
                    sound_controller=sound_controller,
                )

            self._ai_processes = create_process_of_ai_clients_and_start(
                game_comm=self._game_comm,
                ai_clients=self._ai_clients,
                game_params=self._parsed_game_params,
            )
            self._game_executor = GameExecutor(
                self._game,
                self._game_comm,
                game_view,
                fps=getattr(self.args, "fps", 30),
                one_shot_mode=getattr(self.args, "one_shot_mode", False),
                no_display=self.args.no_display,
                output_folder=getattr(self.args, "output_folder", None),
            )

    def run(self):
        install_exec_killer()

        if not self._game_executor:
            raise RuntimeError("Game executor not initialized.")
        time.sleep(0.1)
        try:
            self._game_executor.run()
        except Exception as e:
            logger.exception(e)
            raise
        finally:
            self.close()

    def close(self):
        if self._game_comm is None:
            return
        terminate(self._game_comm, self._ai_processes, self._ws_proc, self._record_proc, self._az_upload_proc)
        self._game_comm = None
        logger.info("===========All process is terminated ===========")


def run_mlgame(arg_obj: MLGameArgument):
    logger.info("===========Game is started ===========")
    install_exec_killer()
    game = MLGameObj(arg_obj)
    game.run()

def main(argv: Optional[Sequence[str]] = None):
    argv = list(sys.argv[1:] if argv is None else argv)
    arg_obj = parse_cmd_and_get_arg_obj(argv)
    run_mlgame(arg_obj)

if __name__ == "__main__":
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

    main()