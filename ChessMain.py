import pygame as p
import ChessEngine

width=height=512
dimension=8
sq_size=height//dimension
max_fps=15
images={}

def loadImages():
    pieces=["wp","wR","wN","wB","wK","wQ","bp","bR","bN","bB","bK","bQ"]
    for piece in pieces:
        images[piece]=p.transform.scale(p.image.load("images/"+piece+".png"),(sq_size,sq_size))


def main():
    p.init()
    screen=p.display.set_mode((width,height))
    clock=p.time.Clock()
    screen.fill(p.Color("white"))
    gs=ChessEngine.GameState()
    validMoves=gs.getValidMoves()
    moveMade=False # Flag variable for when a move is made
    loadImages()
    running=True
    sqSelected=() # No square is selected initially, keep track of the last click of the user (tuple: (row,col))
    playerClicks=[] # Keep track of player clicks (two tuples: [(6,4),(4,4)])
    while running:
        for e in p.event.get():
            if e.type==p.QUIT:
                running=False
            # Mouse handler
            elif e.type==p.MOUSEBUTTONDOWN:
                location=p.mouse.get_pos() # (x,y) location of the mouse
                col=location[0]//sq_size
                row=location[1]//sq_size
                clicked_sq = (row, col)

                if sqSelected == clicked_sq: # User clicked the same square twice
                    sqSelected=() # Deselect
                    playerClicks=[] # Clear player clicks
                else:
                    # Check if the first click is on a valid piece
                    if not playerClicks: # First click
                        piece = gs.board[row][col]
                        current_player_color = "w" if gs.whiteToMove else "b"
                        if piece != "--" and piece[0] == current_player_color:
                            sqSelected = clicked_sq
                            playerClicks.append(sqSelected)
                        else: # Clicked on empty or opponent's piece initially
                            sqSelected = ()
                            playerClicks = []
                    else: # Second click
                        playerClicks.append(clicked_sq)

                if len(playerClicks)==2: # After 2nd click
                    move=ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                    # print(move.getChessNotation()) # For debugging
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade=True
                        sqSelected=() # Reset user clicks
                        playerClicks=[]
                    else: # Invalid move
                        # If the second click was on another of the player's pieces, select that piece
                        # Otherwise, keep the first piece selected
                        second_click_piece = gs.board[playerClicks[1][0]][playerClicks[1][1]]
                        current_player_color = "w" if gs.whiteToMove else "b"
                        if second_click_piece != "--" and second_click_piece[0] == current_player_color:
                            sqSelected = playerClicks[1]
                            playerClicks = [sqSelected]
                        else: # Invalid move to an empty square or opponent's piece
                            sqSelected = playerClicks[0] # Keep the original piece selected
                            playerClicks = [sqSelected]
            # Key handler
            elif e.type==p.KEYDOWN:
                if e.key==p.K_z: # Undo when 'z' is pressed
                    gs.undoMove()
                    moveMade=True # To regenerate valid moves and redraw

        if moveMade:
            validMoves=gs.getValidMoves()
            moveMade=False

        drawGameState(screen,gs, validMoves, sqSelected)
        clock.tick(max_fps)
        p.display.flip()

# Highlight square selected and moves for piece selected
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        # Highlight selected square
        s = p.Surface((sq_size, sq_size))
        s.set_alpha(100) # Transparency value -> 0 transparent, 255 opaque
        s.fill(p.Color('blue'))
        screen.blit(s, (c*sq_size, r*sq_size))
        # Highlight moves from that square
        s.fill(p.Color('yellow'))
        piece_color = gs.board[r][c][0]
        current_turn_color = "w" if gs.whiteToMove else "b"
        if piece_color == current_turn_color : # Ensure it's the current player's piece
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*sq_size, move.endRow*sq_size))


def drawGameState(screen,gs, validMoves, sqSelected):
    drawBoard(screen) # Draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen,gs.board) # Draw pieces on top of squares

# Draw the squares on the board
def drawBoard(screen):
    colors=[p.Color("white"),p.Color("gray")]
    for r in range(dimension):
        for c in range(dimension):
            color=colors[((r+c)%2)]
            p.draw.rect(screen,color,p.Rect(c*sq_size,r*sq_size,sq_size,sq_size))
            
# Draw the pieces on the board using the current GameState.board
def drawPieces(screen,board):
    for r in range(dimension): # Corrected iteration order to match board access board[r][c]
        for c in range(dimension):
            piece=board[r][c]
            if piece!="--": # Not empty square
                screen.blit(images[piece],p.Rect(c*sq_size,r*sq_size,sq_size,sq_size))

if __name__=="__main__":
    main()