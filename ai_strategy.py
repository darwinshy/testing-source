import random
from abc import ABC, abstractmethod

class AIStrategy(ABC):
    """Abstract base class for AI strategies"""
    
    @abstractmethod
    def find_best_move(self, board, mark):
        """
        Find the best move according to this strategy
        
        Args:
            board (Board): Current game board
            mark (str): AI's mark ('X' or 'O')
            
        Returns:
            Move: Best move according to this strategy
        """
        pass


class EasyAIStrategy(AIStrategy):
    """Implementation of easy difficulty AI that makes random moves"""
    
    def find_best_move(self, board, mark):
        """
        Find a random valid move
        
        Args:
            board (Board): Current game board
            mark (str): AI's mark ('X' or 'O')
            
        Returns:
            Move: A random valid move
        """
        empty_cells = board.get_empty_cells()
        if not empty_cells:
            return None
        
        # Choose a random empty cell
        return random.choice(empty_cells)


class MediumAIStrategy(AIStrategy):
    """
    Medium difficulty AI that blocks obvious wins and 
    tries to make winning moves when possible
    """
    
    def find_best_move(self, board, mark):
        """
        Find best move with medium difficulty logic:
        1. Try to win if possible
        2. Block opponent from winning
        3. Take center if available
        4. Take a random move
        
        Args:
            board (Board): Current game board
            mark (str): AI's mark ('X' or 'O')
            
        Returns:
            Move: Best move according to medium difficulty strategy
        """
        # Get opponent's mark
        opponent_mark = 'O' if mark == 'X' else 'X'
        
        # Check if AI can win in the next move
        winning_move = self._find_winning_move(board, mark)
        if winning_move:
            return winning_move
        
        # Check if opponent can win in the next move and block it
        blocking_move = self._find_winning_move(board, opponent_mark)
        if blocking_move:
            return blocking_move
        
        # Take center if available
        center = Move(1, 1)
        if board.is_cell_empty(center.x, center.y):
            return center
        
        # Take a random move
        empty_cells = board.get_empty_cells()
        if empty_cells:
            return random.choice(empty_cells)
        
        return None
    
    def _find_winning_move(self, board, mark):
        """
        Find a move that would lead to immediate win
        
        Args:
            board (Board): Current game board
            mark (str): Mark to check win condition for
            
        Returns:
            Move or None: Winning move if exists, None otherwise
        """
        # Try each empty cell and see if it results in a win
        for move in board.get_empty_cells():
            # Make the move
            board.make_move(move, mark)
            
            # Check if this results in a win
            is_win = board.check_win(mark)
            
            # Undo the move
            board.undo_move(move)
            
            if is_win:
                return move
        
        return None


class HardAIStrategy(AIStrategy):
    """
    Hard difficulty AI using the minimax algorithm with alpha-beta pruning
    for optimal move selection
    """
    
    def find_best_move(self, board, mark):
        """
        Find optimal move using minimax algorithm with alpha-beta pruning
        
        Args:
            board (Board): Current game board
            mark (str): AI's mark ('X' or 'O')
            
        Returns:
            Move: Optimal move
        """
        # Get opponent's mark
        opponent_mark = 'O' if mark == 'X' else 'X'
        
        best_score = float('-inf')
        best_move = None
        
        # Try each empty cell
        for move in board.get_empty_cells():
            # Make the move
            board.make_move(move, mark)
            
            # Recursively evaluate the position
            score = self._minimax(board, 0, False, mark, opponent_mark, float('-inf'), float('inf'))
            
            # Undo the move
            board.undo_move(move)
            
            # Update best score and move
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _minimax(self, board, depth, is_maximizing, ai_mark, opponent_mark, alpha, beta):
        """
        Minimax algorithm with alpha-beta pruning
        
        Args:
            board (Board): Current game board state
            depth (int): Current depth in the search tree
            is_maximizing (bool): Whether current player is maximizing
            ai_mark (str): AI's mark
            opponent_mark (str): Opponent's mark
            alpha (float): Alpha value for pruning
            beta (float): Beta value for pruning
            
        Returns:
            int: Evaluation score of the position
        """
        # Terminal state checks
        if board.check_win(ai_mark):
            return 10 - depth  # Win is good, quicker wins are better
        
        if board.check_win(opponent_mark):
            return depth - 10  # Loss is bad, but later losses are better
        
        if board.check_draw():
            return 0  # Draw
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in board.get_empty_cells():
                board.make_move(move, ai_mark)
                eval = self._minimax(board, depth + 1, False, ai_mark, opponent_mark, alpha, beta)
                board.undo_move(move)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.get_empty_cells():
                board.make_move(move, opponent_mark)
                eval = self._minimax(board, depth + 1, True, ai_mark, opponent_mark, alpha, beta)
                board.undo_move(move)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval