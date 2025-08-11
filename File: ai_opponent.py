import random
from .ai_strategy import AIStrategy, EasyAIStrategy, MediumAIStrategy, HardAIStrategy


class AIStrategyFactory:
    """Factory for creating AI strategy objects based on difficulty"""
    
    def create_strategy(self, difficulty):
        """
        Create and return an AI strategy based on difficulty
        
        Args:
            difficulty (str): Difficulty level ('easy', 'medium', 'hard')
            
        Returns:
            AIStrategy: The appropriate strategy object
            
        Raises:
            ValueError: If an invalid difficulty is provided
        """
        if difficulty.lower() == 'easy':
            return EasyAIStrategy()
        elif difficulty.lower() == 'medium':
            return MediumAIStrategy()
        elif difficulty.lower() == 'hard':
            return HardAIStrategy()
        else:
            raise ValueError(f"Invalid difficulty level: {difficulty}")


class AIPersonality:
    """
    Defines the "personality" of the AI by occasionally making suboptimal moves
    to increase engagement and provide a more human-like opponent
    """
    
    def __init__(self, randomness_factor=0.1):
        """
        Initialize the AI personality
        
        Args:
            randomness_factor (float): Probability (0-1) of making suboptimal moves
        """
        self.randomness_factor = max(0.0, min(1.0, randomness_factor))  # Clamp between 0 and 1
        
        # Define move preferences (can be used to make AI favor certain positions)
        self.move_preferences = {
            # Map positions to preference weights
            (0, 0): 1.2,  # Corners
            (0, 2): 1.2,
            (2, 0): 1.2,
            (2, 2): 1.2,
            (1, 1): 1.5,  # Center
            (0, 1): 1.0,  # Edges
            (1, 0): 1.0,
            (1, 2): 1.0,
            (2, 1): 1.0
        }
    
    def should_make_suboptimal_move(self):
        """
        Determine if AI should make a suboptimal move in this turn
        
        Returns:
            bool: True if should make suboptimal move, False otherwise
        """
        return random.random() < self.randomness_factor
    
    def adjust_move(self, suggested_move, board):
        """
        Potentially adjust the suggested move to a suboptimal one
        
        Args:
            suggested_move (Move): Optimal move suggested by strategy
            board (Board): Current board state
            
        Returns:
            Move: Either the original move or a suboptimal alternative
        """
        empty_cells = board.get_empty_cells()
        if len(empty_cells) <= 1:
            return suggested_move  # Only one option, can't be suboptimal
        
        # Remove the suggested (optimal) move from candidates
        suboptimal_candidates = [move for move in empty_cells if move != suggested_move]
        
        if not suboptimal_candidates:
            return suggested_move
        
        # Weight the candidates by position preference
        weighted_candidates = []
        for move in suboptimal_candidates:
            weight = self.move_preferences.get((move.x, move.y), 1.0)
            weighted_candidates.append((move, weight))
        
        # Choose based on weights
        total_weight = sum(w for _, w in weighted_candidates)
        r = random.uniform(0, total_weight)
        upto = 0
        for move, weight in weighted_candidates:
            upto += weight
            if upto >= r:
                return move
        
        # Fallback
        return random.choice(suboptimal_candidates)


class AIOpponent:
    """AI Opponent that makes moves based on difficulty level"""
    
    def __init__(self, difficulty='medium', player_mark='X'):
        """
        Initialize the AI opponent
        
        Args:
            difficulty (str): Difficulty level ('easy', 'medium', 'hard')
            player_mark (str): The mark used by the player ('X' or 'O')
        """
        self.difficulty_level = difficulty
        self.player_mark = player_mark
        self.ai_mark = 'O' if player_mark == 'X' else 'X'
        self.strategy_factory = AIStrategyFactory()
        self.strategy = self.strategy_factory.create_strategy(difficulty)
        self.personality = AIPersonality(randomness_factor=0.1)
    
    def make_move(self, board):
        """
        Determine the best move based on current difficulty
        
        Args:
            board (Board): Current game board state
            
        Returns:
            Move: The chosen move (x, y coordinates)
        """
        # Get the optimal move from strategy
        suggested_move = self.strategy.find_best_move(board, self.ai_mark)
        
        # Personality might modify the move
        if self.personality.should_make_suboptimal_move():
            return self.personality.adjust_move(suggested_move, board)
        
        return suggested_move
    
    def set_difficulty(self, difficulty):
        """
        Change the AI difficulty level
        
        Args:
            difficulty (str): New difficulty level ('easy', 'medium', 'hard')
        """
        self.difficulty_level = difficulty
        self.strategy = self.strategy_factory.create_strategy(difficulty)
    
    def set_personality(self, randomness_factor):
        """
        Update the AI personality settings
        
        Args:
            randomness_factor (float): Value between 0-1 determining chance of suboptimal moves
        """
        self.personality = AIPersonality(randomness_factor=randomness_factor)