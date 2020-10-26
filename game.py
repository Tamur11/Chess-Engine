import chess
import chess.polyglot
import chess.svg
import chess.pgn

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget

DEPTH = 3


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.movehistory = []
        self.game = chess.pgn.Game()

        self.setGeometry(1050, 200, 500, 500)

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(0, 0, 500, 500)

        self.boardSize = min(self.widgetSvg.width(),
                             self.widgetSvg.height())
        self.squareSize = self.boardSize / 8.0
        self.pieceToMove = [None, None]

        self.board = chess.Board()

        self.drawBoard()
        

    @pyqtSlot(QWidget)
    def mousePressEvent(self, event):
        if self.board.is_game_over(claim_draw=True) is False:
            if not self.board.turn:
                move = select_move(self.board, DEPTH)
                self.board.push(move)
                self.movehistory.append(move)
            elif event.x() <= self.boardSize and event.y() <= self.boardSize:
                if event.buttons() == Qt.LeftButton:
                    file = int((event.x()) / self.squareSize)
                    rank = 7 - int((event.y()) / self.squareSize)
                    square = chess.square(file, rank)
                    piece = self.board.piece_at(square)
                    coordinates = "{}{}".format(chr(file + 97), str(rank + 1))
                    if self.pieceToMove[0] is not None:
                        move = chess.Move.from_uci("{}{}".format(self.pieceToMove[1], coordinates))
                        if move in self.board.legal_moves:
                            self.board.push(move)
                            self.movehistory.append(move)
                        piece = None
                        coordinates = None
                    self.pieceToMove = [piece, coordinates]
            self.drawBoard()
        else:
            self.game.add_line(self.movehistory)
            print(self.game, file=open("gameresult.pgn", "w"), end="\n\n")
            print("Game over")
            exit()

    def drawBoard(self):
        lastmove = self.board.peek() if self.board.move_stack else None
        self.boardSvg = chess.svg.board(board=self.board, lastmove=lastmove).encode("UTF-8")
        self.drawBoardSvg = self.widgetSvg.load(self.boardSvg)

        return self.boardSvg


def evaluate_position(board):
    pawntable = [
        0,  0,  0,  0,  0,  0,  0,  0,
        3,  3, 10, 19, 16, 19,  7, -5,
        -9, -15, 11,  15,  32, 22, 5, -22,
        -4,  -23,  6, 20, 40,  17,  4,  -8,
        13,  0, -13, 1, 11, -2,  -13,  5,
        5, -12, -7, 22, -8, -5, -15, -8,
        -7, 7, -3, -13, 5, -16, 10, -8,
        0,  0,  0,  0,  0,  0,  0,  0]

    knightstable = [
        -175, -92, -74, -73, -73, -74, -92, -175,
        -77, -41,  -27,  -15,  -15,  -27, -41, -77,
        -61,  -17, 6, 12, 12, 6,  -17, -61,
        -35,  8, 40, 49, 49, 40,  8, -35,
        -34,  13, 44, 51, 51, 44,  13, -34,
        -9,  22, 58, 53, 53, 58,  22, -9,
        -67, -27,  4,  37,  37,  4, -27, -67,
        -201, -83, -56, -26, -26, -56, -83, -201]

    bishopstable = [
        -53, -5, -8, -23, -23, -8, -5, -53,
        -15,  8,  19,  4,  4,  19,  8, -15,
        -7, 21, -5, 17, 17, -5, 21, -7,
        -5,  11, 25, 39, 39, 25,  11, -5,
        -12,  29,  22, 31, 31,  22,  29, -12,
        -16,  6,  1, 11, 11,  1,  6, -16,
        -17,  -14,  5,  0,  0,  5,  -14, -17,
        -48, 1, -14, -23, -23, -14, 1, -48]

    rookstable = [
        -31,  -20,  -14,  -5,  -5,  -14,  -20,  -31,
        -21,  -13,  -8,  6,  6,  -8,  -13, -21,
        -25,  -11,  -1,  3,  3,  -1,  -11, -25,
        -13,  -5,  -4,  -6,  -6,  -4,  -5, -13,
        -27,  -15,  -4,  3,  3,  -4,  -15, -27,
        -22,  -2,  6,  12,  12,  6,  -2, -22,
        -2, 12, 16, 18, 18, 16, 12,  -2,
        -17,  -19,  -1,  9,  9,  -1,  -19,  -17]

    queenstable = [
        3, -5, -5, 4, 4, -5, -5, 3,
        -3,  5,  8,  12,  12,  8,  5, -3,
        -3,  6,  13,  7,  7,  13,  6, -3,
        4,  5,  9,  8,  8,  9,  5, 4,
        0,  14,  12,  5,  5,  12,  14, 0,
        -4,  10,  6,  8,  8,  6,  10, -4,
        -5,  6,  10,  8,  8,  10,  6, -5,
        -2, -2, 1, -2, -2, 1, -2, -2]

    kingstable = [
        271, 327, 271,  198,  198, 271, 327, 271,
        278, 303,  234,  179,  179,  234, 303, 278,
        195, 258, 169, 120, 120, 169, 258, 195,
        164, 190, 138, 98, 98, 138, 190, 164,
        154, 179, 105, 70, 70, 105, 179, 154,
        123, 145, 81, 31, 31, 81, 145, 123,
        88, 120, 65, 33, 33, 65, 120, 88,
        59, 89, 45, -1, -1, 45, 89, 59]

    if board.is_checkmate():
        if board.turn:
            return -9999
        else:
            return 9999
    if board.is_stalemate():
        return 0
    if board.is_insufficient_material():
        return 0

    wp = len(board.pieces(chess.PAWN, chess.WHITE))
    bp = len(board.pieces(chess.PAWN, chess.BLACK))
    wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
    bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
    wb = len(board.pieces(chess.BISHOP, chess.WHITE))
    bb = len(board.pieces(chess.BISHOP, chess.BLACK))
    wr = len(board.pieces(chess.ROOK, chess.WHITE))
    br = len(board.pieces(chess.ROOK, chess.BLACK))
    wq = len(board.pieces(chess.QUEEN, chess.WHITE))
    bq = len(board.pieces(chess.QUEEN, chess.BLACK))

    material = 100*(wp-bp)+320*(wn-bn)+330*(wb-bb)+500*(wr-br)+900*(wq-bq)

    pawnsq = sum([pawntable[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
    pawnsq = pawnsq + sum([-pawntable[chess.square_mirror(i)]
                           for i in board.pieces(chess.PAWN, chess.BLACK)])
    knightsq = sum([knightstable[i]
                    for i in board.pieces(chess.KNIGHT, chess.WHITE)])
    knightsq = knightsq + sum([-knightstable[chess.square_mirror(i)]
                               for i in board.pieces(chess.KNIGHT, chess.BLACK)])
    bishopsq = sum([bishopstable[i]
                    for i in board.pieces(chess.BISHOP, chess.WHITE)])
    bishopsq = bishopsq + sum([-bishopstable[chess.square_mirror(i)]
                               for i in board.pieces(chess.BISHOP, chess.BLACK)])
    rooksq = sum([rookstable[i]
                  for i in board.pieces(chess.ROOK, chess.WHITE)])
    rooksq = rooksq + sum([-rookstable[chess.square_mirror(i)]
                           for i in board.pieces(chess.ROOK, chess.BLACK)])
    queensq = sum([queenstable[i]
                   for i in board.pieces(chess.QUEEN, chess.WHITE)])
    queensq = queensq + sum([-queenstable[chess.square_mirror(i)]
                             for i in board.pieces(chess.QUEEN, chess.BLACK)])
    kingsq = sum([kingstable[i]
                  for i in board.pieces(chess.KING, chess.WHITE)])
    kingsq = kingsq + sum([-kingstable[chess.square_mirror(i)]
                           for i in board.pieces(chess.KING, chess.BLACK)])

    eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
    if board.turn:
        return eval
    else:
        return -eval


def alphabeta(board, alpha, beta, depth_left):
    if depth_left == 0:
        return quiesce(board, alpha, beta)

    for move in board.legal_moves:
        board.push(move)
        score = -alphabeta(board, -beta, -alpha, depth_left - 1)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha


def quiesce(board, alpha, beta):
    stand_pat = evaluate_position(board)
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiesce(board, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
    return alpha


def select_move(board, depth_left):
    try:
        book_move = chess.polyglot.MemoryMappedReader(
            "leelabook.bin").weighted_choice(board).move
        return book_move
    except IndexError:
        best_move = chess.Move.null()
        best_value = -99999
        alpha = -100000
        beta = 100000
        for move in board.legal_moves:
            board.push(move)
            position_value = -alphabeta(board, -beta, -alpha, depth_left - 1)
            if position_value > best_value:
                best_value = position_value
                best_move = move
            if position_value > alpha:
                alpha = position_value
            board.pop()
    return best_move


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
