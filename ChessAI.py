import random

def find_random_move(valid_moves):
    """
    Picks a random valid move. Prioritizes capture moves.
    """
    if not valid_moves:
        return None

    capture_moves = []
    for move in valid_moves:
        # Assuming Move object has pieceCaptured attribute from ChessEngine
        # and "--" means an empty square.
        if hasattr(move, 'pieceCaptured') and move.pieceCaptured != "--":
            capture_moves.append(move)
    
    if capture_moves:
        return random.choice(capture_moves)
    
    # If no capture moves, pick any random valid move
    return random.choice(valid_moves)

