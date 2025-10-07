import chess
def set_board():
    '''to set the board'''
    return chess.Board()
def get_legal_moves(board):
    '''to get the legal moves'''
    return str(chess.LegalMoveGenerator(board)).replace("(",")").split(")")[1].replace(" ","").split(",")
def make_move(board,move):
    '''to make move'''
    board.push_san(move)
    return board
def get_2layer_legal_moves(board):
    '''to get two layer of legal_moves'''
    legal_moves1=get_legal_moves(board)
    legal_moves2=[]
    for i in range(len(legal_moves1)):#to get the first layer of legal moves
        board.push_san(legal_moves1[i])
        lm=[]
        for x in range(len(get_legal_moves(board))):#opponent moves+get the second layer of legal moves
            board.push_san(get_legal_moves(board)[x])
            lm.append(get_legal_moves(board))
            board.pop()
        legal_moves2.append(lm)
        board.pop()
    return [legal_moves1,legal_moves2]

if __name__=="__main__":
    board=set_board()
    print(get_legal_moves(board))
    print(get_2layer_legal_moves(board))
    board=make_move(board,"e4")