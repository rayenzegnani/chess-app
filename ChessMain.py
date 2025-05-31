import pygame as p
import ChessEngine
import ChessAI # Import the new AI module

# Constants
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
MENU_FONT_SIZE = 32
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_COLOR = p.Color("darkgray")
BUTTON_TEXT_COLOR = p.Color("white")
MENU_TITLE_COLOR = p.Color("black")

def load_images():
    """Load images for chess pieces"""
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        try:
            IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))
        except:
            print(f"Warning: Could not load image for {piece}")
            # Create a placeholder surface if image loading fails
            IMAGES[piece] = p.Surface((SQ_SIZE, SQ_SIZE))
            IMAGES[piece].fill(p.Color('red' if piece[0] == 'w' else 'blue'))

def draw_menu(screen):
    """Draws the game mode selection menu and returns button rects."""
    screen.fill(p.Color("lightgray"))
    font_title = p.font.SysFont("Helvitca", MENU_FONT_SIZE + 10, True, False)
    title_text = font_title.render("Chess Game - Select Mode", True, MENU_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(WIDTH / 2, HEIGHT / 4))
    screen.blit(title_text, title_rect)

    font_button = p.font.SysFont("Helvitca", MENU_FONT_SIZE, True, False)
    
    # Player vs Player button
    pvp_button_rect = p.Rect((WIDTH - BUTTON_WIDTH) / 2, HEIGHT / 2 - BUTTON_HEIGHT - 10, BUTTON_WIDTH, BUTTON_HEIGHT)
    p.draw.rect(screen, BUTTON_COLOR, pvp_button_rect)
    pvp_text = font_button.render("Player vs Player", True, BUTTON_TEXT_COLOR)
    pvp_text_rect = pvp_text.get_rect(center=pvp_button_rect.center)
    screen.blit(pvp_text, pvp_text_rect)

    # Player vs Computer button
    pvc_button_rect = p.Rect((WIDTH - BUTTON_WIDTH) / 2, HEIGHT / 2 + 10, BUTTON_WIDTH, BUTTON_HEIGHT)
    p.draw.rect(screen, BUTTON_COLOR, pvc_button_rect)
    pvc_text = font_button.render("Player vs Computer", True, BUTTON_TEXT_COLOR)
    pvc_text_rect = pvc_text.get_rect(center=pvc_button_rect.center)
    screen.blit(pvc_text, pvc_text_rect)
    
    p.display.flip()
    return pvp_button_rect, pvc_button_rect

def main():
    """Handles menu and calls the game loop."""
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Chess Game")
    clock = p.time.Clock()
    load_images()

    game_mode = None
    menu_active = True
    pvp_rect, pvc_rect = None, None # Initialize to None

    while menu_active:
        if pvp_rect is None or pvc_rect is None: # Draw menu only if rects are not set
             pvp_rect, pvc_rect = draw_menu(screen)

        for e in p.event.get():
            if e.type == p.QUIT:
                menu_active = False
                # Ensure game_mode remains None to exit gracefully
                game_mode = None 
            if e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = e.pos
                if pvp_rect.collidepoint(mouse_pos):
                    game_mode = "PvP"
                    menu_active = False
                elif pvc_rect.collidepoint(mouse_pos):
                    game_mode = "PvC"
                    menu_active = False
        
        # Redraw menu only if it hasn't been drawn in this iteration
        # This check is slightly redundant due to the outer check, but ensures it's drawn if needed.
        if menu_active and (pvp_rect is None or pvc_rect is None):
            pvp_rect, pvc_rect = draw_menu(screen)
        elif menu_active: # Ensure display updates if menu is still active but buttons drawn
            p.display.flip()


        clock.tick(MAX_FPS)

    if game_mode:
        run_game(screen, clock, game_mode)
    
    p.quit()


def run_game(screen, clock, game_mode):
    """Main game loop for the selected mode."""
    gs = ChessEngine.GameState()
    valid_moves = gs.getValidMoves()
    move_made = False
    
    running = True
    sq_selected = ()  # (row, col)
    player_clicks = []  # [(start_row, start_col), (end_row, end_col)]
    game_over = False
    alert_text = ""

    player_one = True  # True if White is human, False if AI
    player_two = True  # True if Black is human, False if AI

    if game_mode == "PvP":
        player_one = True
        player_two = True
    elif game_mode == "PvC":
        player_one = True  # Assume human plays White against AI
        player_two = False # AI plays Black
    
    while running:
        human_turn = (gs.whiteToMove and player_one) or (not gs.whiteToMove and player_two)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn: # Process human clicks only if it's their turn
                    location = p.mouse.get_pos()  # (x, y)
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    
                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(f"{game_mode} (Human): {move.getChessNotation()}")
                        if move in valid_moves:
                            gs.makeMove(move)
                            move_made = True
                            sq_selected = ()
                            player_clicks = []
                        else:
                            # If invalid move, check if second click was on another piece of same color
                            piece = gs.board[row][col]
                            if piece != "--" and piece[0] == ('w' if gs.whiteToMove else 'b'):
                                player_clicks = [sq_selected]
                            else:
                                player_clicks = []
            
            # Key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when 'z' is pressed
                    if game_mode == "PvP":
                        gs.undoMove()
                    elif game_mode == "PvC":

                        gs.undoMove() # Undo the last move
                        if not human_turn and len(gs.moveLog) > 0: # If it was AI's turn (meaning AI made the last move)
                                                                # and there's another move to undo (player's move)
                            gs.undoMove() # Undo player's move before AI's

                    move_made = True 
                    game_over = False 
                    alert_text = ""
                elif e.key == p.K_r:  # Reset game when 'r' is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.getValidMoves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    game_over = False
                    alert_text = ""
        
        # AI Move Logic
        if not game_over and game_mode == "PvC" and not human_turn:
            ai_move = ChessAI.find_random_move(valid_moves)
            if ai_move:
                print(f"{game_mode} (AI): {ai_move.getChessNotation()}")
                gs.makeMove(ai_move)
                move_made = True
            else: # AI has no moves (checkmate or stalemate by player)
                # This condition should ideally be caught by the checkmate/stalemate logic after player's move
                pass


        if move_made:
            valid_moves = gs.getValidMoves()
            move_made = False
            
            is_checkmate = getattr(gs, 'checkmate', False)
            is_stalemate = getattr(gs, 'stalemate', False)

            if is_checkmate:
                game_over = True
                if gs.whiteToMove: # If whiteToMove, black made the checkmating move
                    alert_text = "Black wins by checkmate"
                else: # If blackToMove, white made the checkmating move
                    alert_text = "White wins by checkmate"
            elif is_stalemate:
                game_over = True
                alert_text = "Stalemate"

        draw_game_state(screen, gs, valid_moves, sq_selected, alert_text)
        clock.tick(MAX_FPS)
        p.display.flip()


def highlight_squares(screen, gs, valid_moves, sq_selected):
    """Highlight selected square and possible moves"""
    if sq_selected:
        r, c = sq_selected
        piece = gs.board[r][c]
        if piece != "--" and piece[0] == ('w' if gs.whiteToMove else 'b'):
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Transparency
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            
            # Highlight possible moves
            s.fill(p.Color('green'))
            for move in valid_moves:
                if move.startRow == r and move.startCol == c:
                    # Different color for capture moves
                    if gs.board[move.endRow][move.endCol] != "--":
                        s.fill(p.Color('red'))
                    else:
                        s.fill(p.Color('green'))
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def draw_game_state(screen, gs, valid_moves, sq_selected, alert_text=""):
    """Draw the complete game state"""
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)
    if alert_text:
        draw_alert_text(screen, alert_text)

def draw_board(screen):
    """Draw chess board squares"""
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    """Draw chess pieces on board"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_alert_text(screen, text):
    """Draws alert text like checkmate or stalemate"""
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color('Black'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2, HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Gray')) # Shadow effect
    screen.blit(text_object, text_location.move(2,2))


if __name__ == "__main__":
    main()