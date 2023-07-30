import chess

from stockfish_wrapper import StockfishWrapper


def generate_line(fen, line):
    board = chess.Board()
    board.set_fen(fen)
    moves = []
    for coord_move in line:
        move = chess.Move.from_uci(coord_move)
        san_move = board.san(move)
        board.push(move)
        moves.append(san_move)

    return moves


def run(fen):
    print(f'FEN: {fen}')
    stockfish = StockfishWrapper()
    stockfish.set_fen_position(fen_position=fen)
    stockfish.set_depth(22)
    print(stockfish.get_turn_perspective_colour())
    for move in stockfish.get_top_moves(5):
        print('--------')
        print(f'Move: {move["Move"]}')
        print(f'Centipawn: {move["Centipawn"]}')
        print(f'Mate: {move["Mate"]}')
        print(f'Line: {generate_line(fen, move["Line"])}')
        print('--------')


if __name__ == '__main__':
    run('2r2nk1/1p2Q1p1/p4pq1/3R3p/5B2/1P3PP1/P3PK2/8 b - - 6 37')
