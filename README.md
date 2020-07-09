# Chess Engine

KNOWN ISSUES:
- "Picking up" and "putting down" a piece on the same square during your turn will cause game to crash.

Built on the [python-chess](https://python-chess.readthedocs.io/en/latest/index.html) library.

Chess evaluation inspired by [Stockfish Evaluation Guide](https://hxim.github.io/Stockfish-Evaluation-Guide/) and [Stockfish Github](https://github.com/official-stockfish/Stockfish/blob/master/src/evaluate.cpp).

Rule-based decision making based on [Alphabeta pruning](https://www.chessprogramming.org/Alpha-Beta) and [Quiescene search documentation](https://www.chessprogramming.org/Quiescence_Search).

Uses [Cerebellum polyglot books](https://zipproth.de/Brainfish/cerebellum/) for openings moves.
