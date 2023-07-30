# Chess Analysis Scripts

This repository contains two Python scripts for analyzing chess games and positions using the Stockfish chess engine.

## Script 1: `pgn_game_analysis.py`

### Description
The `pgn_game_analysis.py` script allows users to analyze and visualize chess games stored in PGN (Portable Game Notation) files. It uses the Stockfish engine to evaluate positions and categorizes moves played by each side (White and Black) based on their quality. The script provides various statistics and plots the evaluation trends throughout the game.

### Features
- Loads a specific chess game from a PGN file.
- Evaluates moves using Stockfish to identify blunders, mistakes, inaccuracies, best moves, excellent moves, great moves, and good moves.
- Displays a tabulated representation of moves and their categories for both players.
- Plots the evaluation scores (centipawn values) over the course of the game.

### Usage
1. Modify the `run()` function call inside the `__name__ == '__main__'` block to load your desired pgn file.
2. Run the script to analyze the game.

### Example Output

_Note_: It's a little overzealous in dishing out `!` excellent moves, I'm using it for my own games and there aren't too many of them…

```
2023.04.13 40/7200:20/3600:900+30
Ding, Liren (2829) vs. Nepomniachtchi, Ian (2761)
1-0 

  Move  White    Black
------  -------  -------
     1  c4       Nf6
     2  Nc3      e5!
     3  Nf3!     Nc6!
     4  e3       Bb4!
     5  Qc2!     Bxc3!
     6  bxc3!    d6!
     7  e4!      O-O!
     8  Be2!     Nh5
     9  d4!      Nf4
    10  Bxf4!    exf4!
    11  O-O!     Qf6!
    12  Rfe1!    Re8!
    13  Bd3      Bg4!
    14  Nd2!     Na5?!
    15  c5!      dxc5!
    16  e5!      Qh6!
    17  d5!      Rad8!
    18  c4!      b6!
    19  h3       Bh5!
    20  Be4!     Re7!
    21  Qc3!     Rde8!
    22  Bf3      Nb7!
    23  Re2      f6!
    24  e6!      Nd6!
    25  Rae1!    Nf5
    26  Bxh5!    Qxh5!
    27  Re4!     Qh6!
    28  Qf3!     Nd4?
    29  Rxd4!    cxd4!
    30  Nb3!     g5?
    31  Nxd4!    Qg6!
    32  g4!      fxg3!
    33  fxg3!    h5!
    34  Nf5!     Rh7!
    35  Qe4!     Kh8?!
    36  e7!      Qf7?!
    37  d6!      cxd6!
    38  Nxd6!    Qg8?!
    39  Nxe8?!   Qxe8!
    40  Qe6?!    Kg7!
    41  Rf1!     Rh6!
    42  Rd1!     f5?
    43  Qe5+!    Kf7!
    44  Qxf5+!   Rf6!
    45  Qh7+!    Ke6!
    46  Qg7?!    Rg6!
    47  Qf8!
    
TYPE            WHITE    BLACK
------------  -------  -------
Best               30       26
Excellent           7        9
Great               5        0
Good                2        4
Inaccuracies        3        4
Mistakes            0        3
Blunders            0        0

Blunder FENs {}
Mistake FENs {'56. … Nd4': '4r1k1/p1p1r1pp/1p2Pp1q/2pP4/2PnRp2/5Q1P/P2N1PP1/4R1K1 w - - 4 29', '60. … g5': '4r1k1/p1p1r2p/1p2Pp1q/3P2p1/2Pp1p2/1N3Q1P/P4PP1/4R1K1 w - - 0 31', '84. … f5': '4q3/p3P1k1/1p2Q2r/5ppp/2P5/6PP/P7/3R2K1 w - - 0 43'}
Inaccuracies FENs {'28. … Na5': 'r3r1k1/ppp2ppp/3p1q2/n7/2PPPpb1/2PB4/P1QN1PPP/R3R1K1 w - - 8 15', '70. … Kh8': '4r2k/p1p4r/1p2Ppq1/3P1Npp/2P1Q3/6PP/P7/4R1K1 w - - 4 36', '72. … Qf7': '4r2k/p1p1Pq1r/1p3p2/3P1Npp/2P1Q3/6PP/P7/4R1K1 w - - 1 37', '76. … Qg8': '4r1qk/p3P2r/1p1N1p2/6pp/2P1Q3/6PP/P7/4R1K1 w - - 1 39', '77. Nxe8': '4N1qk/p3P2r/1p3p2/6pp/2P1Q3/6PP/P7/4R1K1 b - - 0 39', '79. Qe6': '4q2k/p3P2r/1p2Qp2/6pp/2P5/6PP/P7/4R1K1 b - - 1 40', '91. Qg7': '4q3/p3P1Q1/1p2kr2/6pp/2P5/6PP/P7/3R2K1 b - - 4 46'}
```

#### Plot
![Ding, Liren_vs_Nepomniachtchi, Ian_2023.04.13.png](evaluations%2FDing%2C%20Liren_vs_Nepomniachtchi%2C%20Ian_2023.04.13.png)

## Script 2: `stockfish_analysis.py`

### Description
The `fen_best_moves.py` script allows users to analyze a specific chess position using the Stockfish engine. It generates the top moves, their evaluation scores, and the resulting positions after each move.

### Features
- Analyzes a given chess position using Stockfish.
- Retrieves the top 5 moves, their centipawn evaluation scores, checkmate flags, and resulting lines of play.

### Usage
1. Modify the `run()` function call inside the `__name__ == '__main__'` block with your desired FEN position.
2. Run the script to analyze the specified chess position.

### Example Output

```
FEN: 2r2nk1/1p2Q1p1/p4pq1/3R3p/5B2/1P3PP1/P3PK2/8 b - - 6 37
White to move
--------
Move: g6f7
Centipawn: -48
Mate: None
Line: ['Qf7', 'Qxf7+', 'Kxf7', 'Rxh5', 'g5', 'Bd6', 'Ne6', 'Rh7+', 'Ng7', 'Rh1', 'Rc2', 'a3', 'Ne6', 'Rh7+', 'Ng7', 'b4', 'Rd2', 'Bc5', 'Ra2', 'Rh8', 'Ne6', 'Rb8', 'b5', 'Ke3', 'g4', 'fxg4', 'Rxa3+', 'Ke4', 'Rxg3', 'Kf5', 'Nxc5', 'bxc5', 'Rc3', 'Rb7+', 'Ke8', 'Kxf6']
--------
--------
Move: g6e8
Centipawn: -253
Mate: None
Line: ['Qe8', 'Qxb7', 'Qe6', 'Rd6', 'Qh3', 'Qd5+', 'Kh8', 'Kg1', 'Ng6', 'Rd8+', 'Rxd8', 'Qxd8+', 'Kh7', 'Qd3', 'Qe6', 'a4', 'f5', 'Be3', 'Ne5', 'Qc3', 'Nd7', 'Kf2', 'Nf6', 'Qd3', 'Nd5', 'Bd2', 'Kg6', 'b4', 'Qb6+', 'Kg2']
--------
--------
Move: b7b5
Centipawn: -260
Mate: None
Line: ['b5', 'Qb7', 'Qf7', 'Qxa6', 'Qxd5', 'Qxc8', 'Kf7', 'Be3', 'Qd7', 'Qxd7+', 'Nxd7', 'a4', 'bxa4', 'bxa4', 'Ke6', 'a5', 'Nb8', 'Bb6', 'Kd7', 'Ke3', 'g5', 'Bd4', 'Ke6', 'Kf2', 'Na6', 'e4']
--------
--------
Move: b7b6
Centipawn: -265
Mate: None
Line: ['b6', 'Qb7', 'Qf7', 'Qxa6', 'Qxd5', 'Qxc8', 'Kf7', 'Be3', 'Nd7', 'Qc7', 'Qe6', 'a4', 'g5', 'b4', 'h4', 'gxh4', 'gxh4', 'a5', 'bxa5', 'bxa5', 'h3', 'Bf4', 'Ke7', 'Qc2', 'Qa6', 'Qd2', 'Nf8', 'Kg3', 'Ne6', 'Be3', 'Qc8', 'Kxh3', 'Ng5+', 'Kg2']
--------
--------
Move: g6c2
Centipawn: -285
Mate: None
Line: ['Qc2', 'Qxb7', 'g5', 'Bxg5', 'Rc7', 'Qxa6', 'fxg5', 'Qf6', 'Ng6', 'Rxg5', 'Kh7', 'Rxh5+', 'Kg8', 'Qd8+', 'Kg7', 'Qd4+', 'Kf8', 'Rd5', 'Rc6', 'Rd8+', 'Kf7', 'Qd7+', 'Ne7', 'Qe8+', 'Ke6']
--------
```

