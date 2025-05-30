class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self.getPawnMoves,
                            'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves,
                            'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
    
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # Reset checkmate and stalemate flags
            self.checkmate = False
            self.stalemate = False

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        
        if self.inCheck:
            if len(self.checks) == 1: # Single check
                moves = self.getAllPossibleMoves() # Default for_attack_check=False
                # filter out moves that don't resolve the check
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = [] # Squares that block the check or capture the checking piece
                if pieceChecking[1] == "N": # Knight check
                    validSquares = [(checkRow, checkCol)]
                else: # Rook, Bishop, Queen check
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: # Reached the checking piece
                            break
                
                # Remove moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != "K": # Non-king moves
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: # Move doesn't block or capture
                            moves.remove(moves[i])
            else: # Double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves) # Default for_attack_check=False
        else: # Not in check
            moves = self.getAllPossibleMoves() # Default for_attack_check=False
        
        # After generating all moves, determine if it's checkmate or stalemate
        if len(moves) == 0: # No valid moves
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else: # Valid moves exist
            self.checkmate = False
            self.stalemate = False
            
        return moves

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        enemyMoves = self.getAllPossibleMoves(for_attack_check=True) # Pass True here
        self.whiteToMove = not self.whiteToMove
        for move in enemyMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self, for_attack_check=False): # Add for_attack_check parameter
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    # Pass for_attack_check to specific move functions
                    self.moveFunctions[piece](r, c, moves, for_attack_check=for_attack_check)
        return moves

    def getPawnMoves(self, r, c, moves, for_attack_check=False): # Add for_attack_check
        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else: # black pawn moves
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r+1, c+1), self.board))

    def getRookMoves(self, r, c, moves, for_attack_check=False): # Add for_attack_check
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                newRow = r + d[0] * i
                newCol = c + d[1] * i
                if 0 <= newRow < 8 and 0 <= newCol < 8:
                    if self.board[newRow][newCol] == "--":
                        moves.append(Move((r, c), (newRow, newCol), self.board))
                    elif self.board[newRow][newCol][0] == enemyColor:
                        moves.append(Move((r, c), (newRow, newCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves, for_attack_check=False): # Add for_attack_check
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves, for_attack_check=False): # Add for_attack_check
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                newRow = r + d[0] * i
                newCol = c + d[1] * i
                if 0 <= newRow < 8 and 0 <= newCol < 8:
                    if self.board[newRow][newCol] == "--":
                        moves.append(Move((r, c), (newRow, newCol), self.board))
                    elif self.board[newRow][newCol][0] == enemyColor:
                        moves.append(Move((r, c), (newRow, newCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves, for_attack_check=False): # Add for_attack_check
        self.getRookMoves(r, c, moves, for_attack_check=for_attack_check)
        self.getBishopMoves(r, c, moves, for_attack_check=for_attack_check)

    def getKingMoves(self, r, c, moves, for_attack_check=False): # Add for_attack_check
        kingMoves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        allyColor = "w" if self.whiteToMove else "b"
        
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Not an allied piece
                    if for_attack_check: # If called for attack check, don't validate safety recursively
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    else: # Normal call, validate safety
                        # Temporarily make the move to check if king would be in check
                        originalPieceAtStart = self.board[r][c]
                        originalPieceAtEnd = self.board[endRow][endCol]
                        
                        self.board[r][c] = "--"
                        self.board[endRow][endCol] = originalPieceAtStart # Move king to new square
                        
                        originalKingLoc = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
                        if self.whiteToMove:
                            self.whiteKingLocation = (endRow, endCol)
                        else:
                            self.blackKingLocation = (endRow, endCol)

                        is_safe_square = not self.squareUnderAttack(endRow, endCol)
                        
                        self.board[r][c] = originalPieceAtStart
                        self.board[endRow][endCol] = originalPieceAtEnd
                        if self.whiteToMove:
                            self.whiteKingLocation = originalKingLoc
                        else:
                            self.blackKingLocation = originalKingLoc
                        
                        if is_safe_square:
                            moves.append(Move((r, c), (endRow, endCol), self.board))

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == "R") or \
                                (4 <= j <= 7 and type == "B") or \
                                (i == 1 and type == "p" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                                (type == "Q") or (i == 1 and type == "K"):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
              
         
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        
        return inCheck, pins, checks


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
    
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]