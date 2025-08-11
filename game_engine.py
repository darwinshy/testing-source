from .models import Board, Move
from .ai_opponent import AIOpponent

class GameEngine:
    """
    Game engine that coordinates the game flow, maintains board state,
    and manages interactions between player and AI opponent
    """
    
    def __init__(self):
        """Initialize a new game engine with default values"""
        self.board = None
        self.current_player = None
        self.ai_opponent = None
        self.game_status = "not_started"  # Options: not_started, in_progress, player_win, ai_win, draw
        self.player_mark = None
        self.ai_mark = None
    
    def start_new_game(self, player_mark='X', difficulty='medium'):
        """
        Start a new game with the specified parameters
        
        Args:
            player_mark (str): Mark for the human player ('X' or 'O')
            difficulty (str): AI difficulty level ('easy', 'medium', 'hard')
            
        Returns:
            dict: Game initialization information
        """
        # Validate inputs
        if player_mark not in ['X', 'O']:
            raise ValueError("Player mark must be 'X' or 'O'")
            
        # Initialize game state
        self.board = Board()
        self.player_mark = player_mark
        self.ai_mark = 'O' if player_mark == 'X' else 'X'
        self.ai_opponent = AIOpponent(difficulty=difficulty, player_mark=player_mark)
        
        # X always goes first in Tic-Tac-Toe
        self.current_player = 'X'
        self.game_status = "in_progress"
        
        # If AI is X, it makes the first move
        ai_move = None
        if self.ai_mark == 'X':
            ai_move = self._process_ai_move()
        
        return {
            'board': self.board.grid,
            'current_player': self.current_player,
            'player_mark': self.player_mark,
            'ai_mark': self.ai_mark,
            'game_status': self.game_status,
            'ai_move': ai_move.to_json() if ai_move else None
        }
    
    def player_move(self, x, y):
        """
        Process a player's move
        
        Args:
            x (int): X coordinate of the move
            y (int): Y coordinate of the move
            
        Returns:
            dict: Updated game state after the move
            
        Raises:
            ValueError: If the move is invalid or the game is over
        """
        # Check if game is in progress
        if self.game_status != "in_progress":
            raise ValueError(f"Game is not in progress. Current status: {self.game_status}")
        
        # Check if it's the player's turn
        if self.current_player != self.player_mark:
            raise ValueError(f"It's not the player's turn. Current player: {self.current_player}")
        
        # Create and validate the move
        move = Move(x, y)
        
        # Try to make the move
        try:
            self.board.make_move(move, self.player_mark)
        except ValueError as e:
            raise ValueError(f"Invalid move: {e}")
        
        # Update game state
        self._update_game_status_after_move(self.player_mark)
        
        # If game continues, it's AI's turn
        ai_move = None
        if self.game_status == "in_progress":
            ai_move = self._process_ai_move()
        
        return {
            'board': self.board.grid,
            'current_player': self.current_player,
            'game_status': self.game_status,
            'winning_line': self._get_winning_line(),
            'ai_move': ai_move.to_json() if ai_move else None
        }
    
    def _process_ai_move(self):
        """
        Process the AI's move
        
        Returns:
            Move: The move made by the AI, or None if no move was made
        """
        # Check if game is in progress and it's AI's turn
        if self.game_status != "in_progress" or self.current_player != self.ai_mark:
            return None
        
        # Get AI's move
        ai_move = self.ai_opponent.make_move(self.board)
        
        # Make the move on the board
        if ai_move:
            self.board.make_move(ai_move, self.ai_mark)
            
            # Update game state
            self._update_game_status_after_move(self.ai_mark)
            
            return ai_move
        
        return None
    
    def _update_game_status_after_move(self, mark):
        """
        Update game status after a move
        
        Args:
            mark (str): Mark of the player who just moved
        """
        # Check for win
        if self.board.check_win(mark):
            if mark == self.player_mark:
                self.game_status = "player_win"
            else:
                self.game_status = "ai_win"
        # Check for draw
        elif self.board.check_draw():
            self.game_status = "draw"
        # Game continues, switch current player
        else:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
    
    def _get_winning_line(self):
        """
        Get the winning line if there is one
        
        Returns:
            list or None: List of positions in the winning line, or None if no win
        """
        winning_line = self.board.get_winning_line()
        if winning_line:
            return [move.to_json() for move in winning_line]
        return None
    
    def get_board(self):
        """
        Get the current board state
        
        Returns:
            Board: Current game board
        """
        return self.board
    
    def get_game_status(self):
        """
        Get the current game status
        
        Returns:
            str: Current game status
        """
        return self.game_status
    
    def get_current_player(self):
        """
        Get the current player's mark
        
        Returns:
            str: Current player's mark ('X' or 'O')
        """
        return self.current_player
    
    def change_difficulty(self, difficulty):
        """
        Change the AI difficulty level
        
        Args:
            difficulty (str): New difficulty level ('easy', 'medium', 'hard')
        """
        if self.ai_opponent:
            self.ai_opponent.set_difficulty(difficulty)
            return True
        return False
    
    def set_ai_personality(self, randomness_factor):
        """
        Update the AI personality settings
        
        Args:
            randomness_factor (float): Value between 0-1 determining chance of suboptimal moves
        """
        if self.ai_opponent:
            self.ai_opponent.set_personality(randomness_factor)
            return True
        return False