import chess
import chess.pgn
import numpy as np
from stockfish import Stockfish
import matplotlib.pyplot as plt
from ansi_colours import AnsiColours as Colour
from tabulate import tabulate


def load_game(pgn, index):
    i = 0
    while i < index:
        chess.pgn.skip_game(pgn)
        i += 1

    return chess.pgn.read_game(pgn)


def get_headers(game):
    time_control = game.headers['TimeControl'] if 'TimeControl' in game.headers else ''
    termination = game.headers['Termination'] if 'Termination' in game.headers else ''
    return f"{game.headers['Date']} {time_control}\n" \
           f"{game.headers['White']} ({game.headers['WhiteElo']}) vs. " \
           f"{game.headers['Black']} ({game.headers['BlackElo']})\n" \
           f"{game.headers['Result']} {termination}"


def mate_value(eval_value, is_white_move):
    if eval_value == 0:
        return -1 if not is_white_move else 1
    return -1 if eval_value < 0 else 1


def get_san(fen, coord_move):
    board = chess.Board()
    board.set_fen(fen)
    move = chess.Move.from_uci(coord_move)
    return board.san(move)


def get_move_counts_dict():
    return {
        "blunders": 0,
        "mistakes": 0,
        "inaccuracies": 0,
        "best_moves": 0,
        "excellent_moves": 0,
        "great_moves": 0,
        "good_moves": 0,
    }


def run(pgn_file, index=0, depth=16, threads=8):
    pgn = open(pgn_file)
    game = load_game(pgn, index)
    # print(game)
    print(get_headers(game))
    stockfish = Stockfish(parameters={"Threads": threads})
    stockfish.set_depth(depth)
    board = game.board()

    evaluations = []
    last_cp = 0
    white_moves = []
    black_moves = []

    white_move_counts = get_move_counts_dict()
    black_move_counts = get_move_counts_dict()

    inaccuracy_fens = {}
    mistake_fens = {}
    blunder_fens = {}

    for i, move in enumerate(game.mainline_moves()):
        is_white_move = board.turn

        great_moves_san = []
        excellent_moves_san = []
        fen = board.fen()
        evaluation = stockfish.get_evaluation()
        cp = evaluation["value"]
        top_moves = stockfish.get_top_moves(5)
        best_move_san = get_san(fen, top_moves[0]['Move'])
        for top_move in top_moves:
            san = get_san(fen, top_move['Move'])
            top_move_cp = top_move['Centipawn']
            if top_move_cp is None:
                excellent_moves_san.append(san)
                break
            if abs(cp - top_move_cp) < 10:
                excellent_moves_san.append(san)
            elif abs(cp - top_move_cp) < 25:
                great_moves_san.append(san)

        # print('w' if is_white_move else 'b', 'bt', best_move_san)
        # print('w' if is_white_move else 'b', 'ex', excellent_moves_san)
        # print('w' if is_white_move else 'b', 'gd', great_moves_san)

        san = board.san(move)
        board.push(move)
        fen = board.fen()
        stockfish.set_fen_position(fen_position=fen)
        evaluation = stockfish.get_evaluation()
        cp = evaluation["value"]

        move_str = san

        current_move_counts = white_move_counts if is_white_move else black_move_counts

        if abs(last_cp - cp) > 300:
            current_move_counts["blunders"] += 1
            blunder_fens[f'{i + 1}. {san}' if is_white_move else f'{i + 1}. … {san}'] = fen
            move_str = Colour.red(move_str + '??')
        elif abs(last_cp - cp) > 100:
            current_move_counts["mistakes"] += 1
            mistake_fens[f'{i + 1}. {san}' if is_white_move else f'{i + 1}. … {san}'] = fen
            move_str = Colour.purple(move_str + '?')
        elif abs(last_cp - cp) > 50:
            current_move_counts["inaccuracies"] += 1
            inaccuracy_fens[f'{i + 1}. {san}' if is_white_move else f'{i + 1}. … {san}'] = fen
            move_str = Colour.yellow(move_str + '?!')
        elif san == best_move_san:
            current_move_counts["best_moves"] += 1
            move_str = Colour.green(move_str + '!')
        elif san in excellent_moves_san:
            current_move_counts["excellent_moves"] += 1
            move_str = Colour.cyan(move_str + '!')
        elif san in great_moves_san:
            current_move_counts["great_moves"] += 1
            move_str = Colour.blue(move_str)
        else:
            current_move_counts["good_moves"] += 1

        last_cp = cp

        eval_value = float(evaluation["value"]) / 1530
        if is_white_move:
            white_moves.append(move_str)
        else:
            black_moves.append(move_str)

        evaluations.append(eval_value if evaluation["type"] != "mate" else mate_value(eval_value, is_white_move))

    data = {
        "white_moves": white_moves,
        "black_moves": white_moves,
        "white_move_counts": white_move_counts,
        "black_move_counts": black_move_counts
    }

    if len(black_moves) != len(white_moves):
        black_moves.append('')

    print(tabulate(
        [(f"{i + 1}.", white_moves[i], black_moves[i]) for i in range(len(white_moves))],
        headers=("Move", "White", "Black")
    ))

    print(tabulate((
        ('Best', white_move_counts["best_moves"], black_move_counts["best_moves"]),
        ('Excellent', white_move_counts["excellent_moves"], black_move_counts["excellent_moves"]),
        ('Great', white_move_counts["great_moves"], black_move_counts["great_moves"]),
        ('Good', white_move_counts["good_moves"], black_move_counts["good_moves"]),
        ('Inaccuracies', white_move_counts["inaccuracies"], black_move_counts["inaccuracies"]),
        ('Mistakes', white_move_counts["mistakes"], black_move_counts["mistakes"]),
        ('Blunders', white_move_counts["blunders"], black_move_counts["blunders"]),
    ), headers=('TYPE', 'WHITE', 'BLACK')))

    print('Blunder Lines', blunder_fens)
    print('Mistake Lines', mistake_fens)
    print('Inaccuracies Lines', inaccuracy_fens)

    evaluations = np.array(evaluations)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(evaluations, color='#e0e0e0', linewidth=0.5)

    ax.set_title(get_headers(game), fontdict={'fontsize': 9})
    ax.set_ylabel('Centipawn')
    ax.set_xlabel('Move')

    min_val, max_val = min(evaluations), max(evaluations)
    abs_max = max(abs(min_val), abs(max_val))
    plt.ylim(-abs_max, abs_max)

    fig.patch.set_facecolor('#F5F5E8')
    ax.set_facecolor('#F5F5FE')

    x = range(len(evaluations))
    plt.fill_between(x=x, y1=10, y2=evaluations, interpolate=True,
                     color='black', edgecolor=None)
    plt.fill_between(x=x, y1=-10, y2=evaluations,
                     interpolate=True, color='white', edgecolor=None)

    ax.margins(x=0)

    ax.axhline(0, color='#cccccc', linewidth=0.5, dashes=[6, 12])

    # plt.show()

    plt.savefig('./evaluations/' + pgn_file[6:-4] + '.png')


if __name__ == '__main__':
    run('games/Ding, Liren_vs_Nepomniachtchi, Ian_2023.04.13.pgn', depth=20)
