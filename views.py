from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from .models import Board, Move, UserPreference
from .game_engine import GameEngine


def index(request):
    """
    Main game page view
    """
    context = {
        'title': 'Tic-Tac-Toe Game',
        'difficulties': [
            {'value': 'easy', 'label': 'Easy'},
            {'value': 'medium', 'label': 'Medium'},
            {'value': 'hard', 'label': 'Hard'},
        ]
    }
    
    # If user is logged in, get their preferences
    if request.user.is_authenticated:
        try:
            prefs = UserPreference.objects.get(user=request.user)
            context['user_preferences'] = {
                'difficulty': prefs.preferred_difficulty,
                'mark': prefs.preferred_mark
            }
        except UserPreference.DoesNotExist:
            # Create default preferences
            prefs = UserPreference(user=request.user)
            prefs.save()
            context['user_preferences'] = {
                'difficulty': prefs.preferred_difficulty,
                'mark': prefs.preferred_mark
            }
    
    return render(request, 'tictactoe/index.html', context)


@csrf_exempt
def new_game(request):
    """
    API endpoint to start a new game
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player_mark = data.get('player_mark', 'X')
            difficulty = data.get('difficulty', 'medium')
            
            # Create and store game engine in session
            game_engine = GameEngine()
            game_state = game_engine.start_new_game(
                player_mark=player_mark,
                difficulty=difficulty
            )
            
            # Store engine in session
            request.session['game_engine'] = game_engine.__dict__
            
            # If user is authenticated, update preferences
            if request.user.is_authenticated:
                UserPreference.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'preferred_mark': player_mark,
                        'preferred_difficulty': difficulty
                    }
                )
            
            return JsonResponse({
                'success': True,
                'game_state': game_state
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error