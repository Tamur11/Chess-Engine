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
        5, 10, 10, -20, -20, 10, 10,  5,
        5, -5, -10,  0,  0, -10, -5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5,  5, 10, 25, 25, 10,  5,  5,
        10, 10, 20, 30, 30, 20, 10, 10,
        50, 50, 50, 50, 50, 50, 50, 50,
        0,  0,  0,  0,  0,  0,  0,  0]

    knightstable = [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20,  0,  5,  5,  0, -20, -40,
        -30,  5, 10, 15, 15, 10,  5, -30,
        -30,  0, 15, 20, 20, 15,  0, -30,
        -30,  5, 15, 20, 20, 15,  5, -30,
        -30,  0, 10, 15, 15, 10,  0, -30,
        -40, -20,  0,  0,  0,  0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50]

    bishopstable = [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10,  5,  0,  0,  0,  0,  5, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10,  0, 10, 10, 10, 10,  0, -10,
        -10,  5,  5, 10, 10,  5,  5, -10,
        -10,  0,  5, 10, 10,  5,  0, -10,
        -10,  0,  0,  0,  0,  0,  0, -10,
        -20, -10, -10, -10, -10, -10, -10, -20]

    rookstable = [
        0,  0,  0,  5,  5,  0,  0,  0,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        5, 10, 10, 10, 10, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0]

    queenstable = [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10,  0,  0,  0,  0,  0,  0, -10,
        -10,  5,  5,  5,  5,  5,  0, -10,
        0,  0,  5,  5,  5,  5,  0, -5,
        -5,  0,  5,  5,  5,  5,  0, -5,
        -10,  0,  5,  5,  5,  5,  0, -10,
        -10,  0,  0,  0,  0,  0,  0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20]

    kingstable = [
        20, 30, 10,  0,  0, 10, 30, 20,
        20, 20,  0,  0,  0,  0, 20, 20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30]

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
