import copy
import subprocess
from typing import List, Dict, Union, Optional, Any


class StockfishWrapper:
    _depth = 16
    _num_nodes = None
    _has_quit_command_been_sent = False
    _turn_perspective = None

    def __init__(self, parameters=None):
        if parameters is None:
            parameters = {}
        self._default_params = {
            "Debug Log File": "",
            "Contempt": 0,
            "Min Split Depth": 0,
            "Threads": 4,
            "Ponder": False,
            "Hash": 16,
            "MultiPV": 1,
            "Skill Level": 20,
            "Move Overhead": 10,
            "Minimum Thinking Time": 20,
            "Slow Mover": 100,
            "UCI_Chess960": False,
            "UCI_LimitStrength": False,
            "UCI_Elo": 3600,
        }

        self._stockfish = subprocess.Popen(
            "stockfish",
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        self._parameters: dict = {}
        self.update_engine_parameters(self._default_params)
        self.update_engine_parameters(parameters)

    def _prepare_for_new_position(self, send_ucinewgame_token: bool = True) -> None:
        if send_ucinewgame_token:
            self.put("ucinewgame")
        self._is_ready()
        self.info = ""

    def _is_ready(self) -> None:
        self.put("isready")
        while self._read_line() != "readyok":
            pass

    def _set_option(
            self, name: str, value: Any, update_parameters_attribute: bool = True
    ) -> None:
        str_rep_value = str(value)
        if isinstance(value, bool):
            str_rep_value = str_rep_value.lower()
        self.put(f"setoption name {name} value {str_rep_value}")
        if update_parameters_attribute:
            self._parameters.update({name: value})
        self._is_ready()

    def _read_line(self) -> str:
        if not self._stockfish.stdout:
            raise BrokenPipeError()
        if self._stockfish.poll() is not None:
            raise StockfishException("The Stockfish process has crashed")
        line = self._stockfish.stdout.readline().strip()
        # if self._debug_view:
        #     print(line)
        return line

    def _pick(self, line: list[str], value: str = "", index: int = 1) -> str:
        return line[line.index(value) + index]

    def _discard_remaining_stdout_lines(self, substr_in_last_line: str) -> None:
        """Calls _read_line() until encountering `substr_in_last_line` in the line."""
        while substr_in_last_line not in self._read_line():
            pass

    def _get_sf_go_command_output(self) -> List[str]:
        lines: List[str] = []
        while True:
            lines.append(self._read_line())
            if lines[-1].startswith("bestmove"):
                return lines

    def _get_best_move_from_sf_popen_process(self) -> Optional[str]:
        """Precondition - a "go" command must have been sent to SF before calling this function.
        This function needs existing output to read from the SF popen process."""

        lines: List[str] = self._get_sf_go_command_output()
        self.info = lines[-2]
        last_line_split = lines[-1].split(" ")
        return None if last_line_split[1] == "(none)" else last_line_split[1]

    def _go(self) -> None:
        self.put(f"go depth {self._depth}")

    def _go_nodes(self) -> None:
        self.put(f"go nodes {self._num_nodes}")

    def _go_time(self, time: int) -> None:
        self.put(f"go movetime {time}")

    def _go_remaining_time(self, wtime: Optional[int], btime: Optional[int]) -> None:
        cmd = "go"
        if wtime is not None:
            cmd += f" wtime {wtime}"
        if btime is not None:
            cmd += f" btime {btime}"
        self.put(cmd)

    def _go_perft(self, depth: int) -> None:
        self.put(f"go perft {depth}")

    def set_depth(self, depth: int = 20) -> None:
        if not isinstance(depth, int) or depth < 1 or isinstance(depth, bool):
            raise TypeError("depth must be an integer higher than 0")
        self._depth = depth

    def set_num_nodes(self, num_nodes: int = 1000000) -> None:
        if (
                not isinstance(num_nodes, int)
                or isinstance(num_nodes, bool)
                or num_nodes < 1
        ):
            raise TypeError("num_nodes must be an integer higher than 0")
        self._num_nodes: int = num_nodes

    def put(self, command: str) -> None:
        if not self._stockfish.stdin:
            raise BrokenPipeError()
        if self._stockfish.poll() is None and not self._has_quit_command_been_sent:
            # if self._debug_view:
            #     print(f">>> {command}\n")
            self._stockfish.stdin.write(f"{command}\n")
            self._stockfish.stdin.flush()
            if command == "quit":
                self._has_quit_command_been_sent = True

    def set_fen(
            self, fen: str, send_ucinewgame_token: bool = True
    ) -> None:
        self._prepare_for_new_position(send_ucinewgame_token)
        self.set_turn_perspective("w" in self.get_fen_position())
        self.put(f"position fen {fen}")

    def set_turn_perspective(self, turn_perspective: bool = True) -> None:
        if not isinstance(turn_perspective, bool):
            raise TypeError("turn_perspective must be a Boolean")
        self._turn_perspective = turn_perspective

    def get_turn_perspective(self) -> bool:
        return self._turn_perspective

    def get_turn_perspective_colour(self) -> bool:
        return f"{'White' if self._turn_perspective else 'Black'} to move"

    def get_best_move(
            self, wtime: Optional[int] = None, btime: Optional[int] = None
    ) -> Optional[str]:
        if wtime is not None or btime is not None:
            self._go_remaining_time(wtime, btime)
        else:
            self._go()
        return self._get_best_move_from_sf_popen_process()

    def get_top_moves(
            self,
            num_top_moves: int = 5,
            verbose: bool = False,
            num_nodes: int = 0,
    ) -> List[dict]:
        if num_top_moves <= 0:
            raise ValueError("num_top_moves is not a positive number.")

        old_multipv: int = self._parameters["MultiPV"]
        old_num_nodes: int = self._num_nodes

        if num_top_moves != self._parameters["MultiPV"]:
            self._set_option("MultiPV", num_top_moves)

        if num_nodes == 0:
            self._go()
        else:
            self._num_nodes = num_nodes
            self._go_nodes()

        lines: List[List[str]] = [
            line.split(" ") for line in self._get_sf_go_command_output()
        ]

        top_moves: List[dict] = []

        perspective: int = (
            1 if self.get_turn_perspective() or ("w" in self.get_fen_position()) else -1
        )

        for line in reversed(lines):
            if line[0] == "bestmove":
                if line[1] == "(none)":
                    top_moves = []
                    break
                continue

            if ("multipv" not in line) or ("depth" not in line):
                break

            if (num_nodes == 0) and (int(self._pick(line, "depth")) != self._depth):
                break

            if (num_nodes > 0) and (int(self._pick(line, "nodes")) < self._num_nodes):
                break

            move_evaluation: Dict[str, Union[str, int, None]] = {
                "Move": self._pick(line, "pv"),
                "Centipawn": int(self._pick(line, "cp")) * perspective
                if "cp" in line
                else None,
                "Mate": int(self._pick(line, "mate")) * perspective
                if "mate" in line
                else None,
                "Line": line[21:]
            }

            # add more info if verbose
            if verbose:
                move_evaluation["Time"] = self._pick(line, "time")
                move_evaluation["Nodes"] = self._pick(line, "nodes")
                move_evaluation["MultiPVLine"] = self._pick(line, "multipv")
                move_evaluation["NodesPerSecond"] = self._pick(line, "nps")
                move_evaluation["SelectiveDepth"] = self._pick(line, "seldepth")

                # add wdl if available
                # if self.does_current_engine_version_have_wdl_option():
                #     move_evaluation["WDL"] = " ".join(
                #         [
                #             self._pick(line, "wdl", 1),
                #             self._pick(line, "wdl", 2),
                #             self._pick(line, "wdl", 3),
                #         ][::perspective]
                #     )

            top_moves.insert(0, move_evaluation)

        if old_multipv != self._parameters["MultiPV"]:
            self._set_option("MultiPV", old_multipv)

        if old_num_nodes != self._num_nodes:
            self._num_nodes = old_num_nodes

        return top_moves

    def update_engine_parameters(self, parameters: Optional[dict]) -> None:
        if not parameters:
            return

        new_param_values = copy.deepcopy(parameters)

        if len(self._parameters) > 0:
            for key in new_param_values:
                if key not in self._parameters:
                    raise ValueError(f"'{key}' is not a key that exists.")

                elif key in (
                        "Ponder",
                        "UCI_Chess960",
                        "UCI_LimitStrength",
                ) and not isinstance(new_param_values[key], bool):
                    raise ValueError(
                        f"The value for the '{key}' key has been updated from a string to a bool in a new release of "
                        f"the python stockfish package."
                    )

        if ("Skill Level" in new_param_values) != (
                "UCI_Elo" in new_param_values
        ) and "UCI_LimitStrength" not in new_param_values:
            if "Skill Level" in new_param_values:
                new_param_values.update({"UCI_LimitStrength": False})
            elif "UCI_Elo" in new_param_values:
                new_param_values.update({"UCI_LimitStrength": True})

        if "Threads" in new_param_values:
            threads_value = new_param_values["Threads"]
            del new_param_values["Threads"]
            hash_value = None
            if "Hash" in new_param_values:
                hash_value = new_param_values["Hash"]
                del new_param_values["Hash"]
            else:
                hash_value = self._parameters["Hash"]
            new_param_values["Threads"] = threads_value
            new_param_values["Hash"] = hash_value

        for name, value in new_param_values.items():
            self._set_option(name, value)
        self.set_fen(self.get_fen_position(), False)

    def get_evaluation(self) -> Dict[str, Union[str, int]]:
        """Searches to the specified depth and evaluates the current position.

        Returns:
            A dictionary of two pairs: {str: str, str: int}
            - The first pair describes the type of the evaluation. The key is "type", and the value
              will be either "cp" (centipawns) or "mate".
            - The second pair describes the value of the evaluation. The key is "value", and the value
              will be an int (representing either a cp value or a mate in n value).
        """

        compare: int = (
            1 if self.get_turn_perspective() or ("w" in self.get_fen_position()) else -1
        )
        # If the user wants the evaluation specified relative to who is to move, this will be done.
        # Otherwise, the evaluation will be in terms of white's side (positive meaning advantage white,
        # negative meaning advantage black).
        self._go()
        lines = self._get_sf_go_command_output()
        split_line = [line.split(" ") for line in lines if line.startswith("info")][-1]
        score_index = split_line.index("score")
        eval_type, val = split_line[score_index + 1], split_line[score_index + 2]
        return {"type": eval_type, "value": int(val) * compare}

    def get_fen_position(self) -> str:
        """Returns current board position in Forsyth-Edwards notation (FEN).

        Returns:
            String of current board position in Forsyth-Edwards notation (FEN).

            For example: `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
        """
        self.put("d")
        while True:
            text = self._read_line()
            split_text = text.split(" ")
            if split_text[0] == "Fen:":
                self._discard_remaining_stdout_lines("Checkers")
                return " ".join(split_text[1:])

    def set_fen_position(
            self, fen_position: str, send_ucinewgame_token: bool = True
    ) -> None:
        self._prepare_for_new_position(send_ucinewgame_token)
        self.put(f"position fen {fen_position}")

    def does_current_engine_version_have_wdl_option(self) -> bool:
        """Returns whether the user's version of Stockfish has the option
           to display WDL stats.

        Returns:
            `True` if Stockfish has the `WDL` option, otherwise `False`.
        """
        self.put("uci")
        while True:
            split_text = self._read_line().split(" ")
            if split_text[0] == "uciok":
                return False
            elif "UCI_ShowWDL" in split_text:
                self._discard_remaining_stdout_lines("uciok")
                return True

    def reset_engine_parameters(self) -> None:
        self.update_engine_parameters(self._default_params)


class StockfishException(Exception):
    pass
