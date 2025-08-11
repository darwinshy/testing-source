import random
from abc import ABC, abstractmethod
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Move:
    """Represents a position on the game board"""
    
    def __init__(self, x, y):
        """
        Initialize a move with coordinates
        
        Args:
            x (int): X coordinate (0-2)
            y (int): Y coordinate (0-2)
        """
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        """
        Check if two moves are equal (same coordinates)
        
        Args:
            other (Move): Move to compare with
            
        Returns:
            bool: True if moves are equal, False otherwise
        """
        if not isinstance(other, Move):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        """
        Generate hash for use in dictionaries and sets
        
        Returns:
            int: Hash value
        """
        return hash((self.x, self.y))
    
    def __str__(self):
        """
        String representation of move
        
        Returns:
            str: String in format '(x, y)'
        """
        return f"({self.x}, {self.y})"
    
    def to_json(self):
        """
        Convert move to JSON-serializable format
        
        Returns:
            dict: JSON representation of the move
        """
        return {
            'x': self.x,
            'y': self.y
        }
    
    @classmethod
    def from_json(cls, data):
        """
        Create a move from JSON data
        
        Args:
            data (dict): JSON data with 'x' and 'y' fields
            
        Returns:
            Move: New move instance
        """
        return cls(data['x'], data['y'])


class Board:
    """Represents the Tic-Tac-Toe game board state"""
    
    def __init__(self, grid=None):
        """
        Initialize the board with an empty grid or provided state
        
        Args:
            grid (list[list[str]], optional): 3x3 grid with cell values
        """
        # Initialize empty grid if none provided
        if grid is None:
            self.grid = [[''] * 3 for _ in range(3)]
        else:
            # Validate and copy the provided grid
            if len(grid) != 3 or any(len(row) != 3 for row in grid):
                raise ValueError("Grid must be 3x3")
            self.grid = [row[:] for row in grid]  # Deep copy
    
    def get_empty_cells(self):
        """
        Get all empty cells on the board
        
        Returns:
            list[Move]: List of empty cell positions
        """
        empty_cells = []
        for x in range(3):
            for y in range(3):
                if self.grid[x][y] == '':
                    empty_cells.append(Move(x, y))
        return empty_cells
    
    def is_cell_empty(self, x, y):
        """
        Check if a cell is empty
        
        Args:
            x (int): X coordinate (0-2)
            y (int): Y coordinate (0-2)
            
        Returns:
            bool: True if the cell is empty, False otherwise
            
        Raises:
            ValueError: If coordinates are out of bounds
        """
        if not (0 <= x < 3 and 0 <= y < 3):
            raise ValueError(f"Coordinates ({x}, {y}) out of bounds")
        
        return self.grid[x][y] == ''
    
    def make_move(self, move, mark):
        """
        Place a mark on the board at the specified position
        
        Args:
            move (Move): Position to place mark
            mark (str): Mark to place ('X' or 'O')
            
        Returns:
            bool: True if move was valid and made, False otherwise
            
        Raises:
            ValueError: If coordinates are out of bounds or cell is occupied
        """
        if not (0 <= move.x < 3 and 0 <= move.y < 3):
            raise ValueError(f"Coordinates ({move.x}, {move.y}) out of bounds")
        
        if self.grid[move.x][move.y] != '':
            raise ValueError(f"Cell ({move.x}, {move.y}) is already occupied")
        
        self.grid[move.x][move.y] = mark
        return True
    
    def undo_move(self, move):
        """
        Undo a move by clearing the specified cell
        
        Args:
            move (Move): Position to clear
            
        Raises:
            ValueError: If coordinates are out of bounds
        """
        if not (0 <= move.x < 3 and 0 <= move.y < 3):
            raise ValueError(f"Coordinates ({move.x}, {move.y}) out of bounds")
        
        self.grid[move.x][move.y] = ''
    
    def check_win(self, mark):
        """
        Check if the specified mark has won
        
        Args:
            mark (str): Mark to check ('X' or 'O')
            
        Returns:
            bool: True if the mark has won, False otherwise
        """
        # Check rows
        for row in self.grid:
            if all(cell == mark for cell in row):
                return True
        
        # Check columns
        for col in range(3):
            if all(self.grid[row][col] == mark for row in range(3)):
                return True
        
        # Check diagonals
        if all(self.grid[i][i] == mark for i in range(3)):
            return True
        
        if all(self.grid[i][2-i] == mark for i in range(3)):
            return True
        
        return False
    
    def check_draw(self):
        """
        Check if the game is a draw (all cells filled with no winner)
        
        Returns:
            bool: True if game is a draw, False otherwise
        """
        # If board is full and no one has won, it's a draw
        return all(self.grid[x][y] != '' for x in range(3) for y in range(3))
    
    def is_game_over(self):
        """
        Check if the game is over (win or draw)
        
        Returns:
            bool: True if game is over, False otherwise
        """
        return self.check_win('X') or self.check_win('O') or self.check_draw()
    
    def get_winning_line(self):
        """
        Get the winning line if there is one
        
        Returns:
            list[Move] or None: List of positions forming winning line, or None if no win
        """
        # Check rows
        for row in range(3):
            if self.grid[row][0] != '' and self.grid[row][0] == self.grid[row][1] == self.grid[row][2]:
                return [Move(row, 0), Move(row, 1), Move(row, 2)]
        
        # Check columns
        for col in range(3):
            if self.grid[0][col] != '' and self.grid[0][col] == self.grid[1][col] == self.grid[2][col]:
                return [Move(0, col), Move(1, col), Move(2, col)]
        
        # Check diagonals
        if self.grid[0][0] != '' and self.grid[0][0] == self.grid[1][1] == self.grid[2][2]:
            return [Move(0, 0), Move(1, 1), Move(2, 2)]
        
        if self.grid[0][2] != '' and self.grid[0][2] == self.grid[1][1] == self.grid[2][0]:
            return [Move(0, 2), Move(1, 1), Move(2, 0)]
        
        return None
    
    def get_cell(self, x, y):
        """
        Get the value of a cell
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            str: Cell value ('X', 'O', or '')
        """
        if not (0 <= x < 3 and 0 <= y < 3):
            raise ValueError(f"Coordinates ({x}, {y}) out of bounds")
        
        return self.grid[x][y]
    
    def to_json(self):
        """
        Convert board to JSON-serializable format
        
        Returns:
            dict: JSON representation of the board
        """
        return {
            'grid': [row[:] for row in self.grid]
        }
    
    @classmethod
    def from_json(cls, data):
        """
        Create a board from JSON data
        
        Args:
            data (dict): JSON data with 'grid' field
            
        Returns:
            Board: New board instance
        """
        return cls(grid=data['grid'])


class UserPreference(models.Model):
    """User preferences including AI difficulty settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_difficulty = models.CharField(
        max_length=10, 
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium'
    )
    randomness_factor = models.FloatField(
        default=0.1,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Determines the likelihood of AI making suboptimal moves (0.0-1.0)"
    )
    preferred_mark = models.CharField(
        max_length=1,
        choices=[('X', 'X'), ('O', 'O')],
        default='X'
    )
    
    def __str__(self):
        return f"{self.user.username}'s preferences"