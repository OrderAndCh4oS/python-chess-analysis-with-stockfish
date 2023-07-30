import chess
import chess.pgn


def load_games(pgn):
    games = []
    while True:
        game = chess.pgn.read_game(pgn)
        if not game:
            break
        games.append(game)

    return games


def get_headers(game):
    print()
    game_times = game.headers['TimeControl'].split('+')
    time = int(float(game_times[0]) / 60)
    increment = '+' + game_times[1] if len(game_times) > 1 else ''
    return f"\n-----\n{game.headers['Date']} Time: {time}m{increment}\n" \
           f"{game.headers['White']} ({game.headers['WhiteElo']}) vs. " \
           f"{game.headers['Black']} ({game.headers['BlackElo']})\n" \
           f"{game.headers['Result']} {game.headers['Termination']}\n-----"


def run(pgn_file):
    pgn = open(pgn_file)
    games = load_games(pgn)
    for i, game in enumerate(games):
        print(i, get_headers(game))


if __name__ == '__main__':
    run('games/chess_com_games_2023-07-23.pgn')

