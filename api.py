# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from models import User
from models import UserPerfForm
from models import UsersRankingForm
from models import Game
from models import GameForm
from models import GameForms
from models import ChooseDiceForm
from models import ChooseCatForm
from models import CardCategory
from models import Score
from models import ScoreForm
from models import ScoreForms
from models import StringMessage
from models import ConflictException
from models import GameHistoryForm

from utils import get_by_urlsafe
from utils import get_user_id
from play import choose_dice
from play import roll
from play import find_score
from settings import WEB_CLIENT_ID

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
ROLL_REQUEST = endpoints.ResourceContainer(
        ChooseDiceForm,
        urlsafe_game_key=messages.StringField(1),)
CATEGORY_REQUEST = endpoints.ResourceContainer(
        ChooseCatForm,
        urlsafe_game_key=messages.StringField(1),)


@endpoints.api(name='yahtzee', version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
               scopes=[EMAIL_SCOPE])
class YahtzeeGameApi(remote.Service):
    """Yahtzee Game API"""

    # Create User
    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User."""
        cur_user = endpoints.get_current_user()
        if not cur_user:
            raise endpoints.UnauthorizedException('Authourization required')
        user_id = get_user_id(cur_user)
        p_key = ndb.Key(User, user_id)
        user = p_key.get()
        if not user:
            user = User(
                key=p_key,
                name=cur_user.nickname(),
                email=cur_user.email(),
            )
            user.put()
            return StringMessage(message='User {} created!'.format(
                cur_user.nickname()))
        return StringMessage(message='User already created!')

    # New Game
    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Create new game"""
        # preload user data
        user = self._get_user()
        game = Game.new_game(user.key)
        return game.to_form('Roll the Dice! Good Luck!')

    # Get Game
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the selected game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            user = self._get_user()
            if game.user.get() is not user:
                raise endpoints.NotFoundException(
                    'You cannot get the game not belonging to you.')
            else:
                return game.to_form('Let us roll!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    # Remove the incompleted game
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        """Delete the selected game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            user = self._get_user()
            if game.user.get() is not user:
                return StringMessage(
                    message="You cannot cancel the game not belonging to you.")
            if not game.game_over:
                game.key.delete()
                return StringMessage(message="The game is cancelled.")
            else:
                return StringMessage(
                    message="You cannot cancel completed games.")
        else:
            raise endpoints.NotFoundException('Game not found!')

    # Return all active games of the user
    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=GameForms,
                      http_method='POST',
                      name='get_user_games')
    def get_user_games(self, request):
        """Return all of a User's active games."""
        user = self._get_user()
        games = Game.query(Game.user == user.key).filter(
            Game.game_over == False).order(Game.round_remain)
        # return set of GameForm object per game
        return GameForms(
            items=[game.to_form('%s remaining rounds.' % game.round_remain)
                   for game in games])

    # Return the history record of the game
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameHistoryForm,
                      http_method='GET',
                      name='get_game_history')
    def get_game_history(self, request):
        """Return history of the game"""
        user = self._get_user()
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.user.get() is user:
            return game.to_history_form()

    # Return a leader-board
    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=ScoreForms,
                      http_method='GET',
                      name='get_high_scores')
    def get_high_scores(self, request):
        """Return a list of high scores"""
        high_scores = Score.query().order(-Score.result).fetch(3)
        return ScoreForms(
            items=[score.to_form() for score in high_scores])

    # Return the ranking of users
    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=UsersRankingForm,
                      http_method='GET',
                      name='get_user_rankings')
    def get_user_rankings(self, request):
        """Return the rankings of users"""
        ranking_users = User.query().order(-User.max_score).order(
            User.games_completed).fetch()
        return UsersRankingForm(
            items=[user.to_perf_form() for user in ranking_users])

    # Roll Dice
    @endpoints.method(request_message=ROLL_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='roll_dice',
                      http_method='PUT')
    def roll_dice(self, request):
        """Roll a dice -- Three chances each round"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')
        # for the first roll you cannot choose dice to keep
        if not game.dice and request.index_chosen:
            return game.to_form('Cannot choose index now.')
        if game.roll_remain < 1:
            return game.to_form('You have to choose the category, \
                no more roll chance.')
        else:
            dice_kept = choose_dice(game.dice, request.index_chosen)
            game.dice = roll(dice_kept)
            game.roll_remain -= 1
            game.put()
            return game.to_form('%s chances remain to roll in this round.'
                                % game.roll_remain)

    # Category Round
    @endpoints.method(request_message=CATEGORY_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='choose_category',
                      http_method='POST')
    def choose_category(self, request):
        """Choose a category to earn points for each round"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')
        card = game.score_card
        index = int(request.category)  # cast category Enum to int as the index
        if not game.dice:
            return game.to_form('Roll the dice first!')
        if card[index] is not -1:
            return game.to_form(
                'You have already chosen this category.')
        # Record score to the category
        points = find_score(game.dice, index)
        card[index] = points
        game.round_remain -= 1
        # Record game history
        dice_str = ''.join(str(num) for num in game.dice)
        game.dice_history.append(dice_str)
        game.cat_history.append(request.category)
        # Check the sum and add bonus if any
        if -1 not in card[0:6]:
            card[6] = sum(card[0:6])
            card[7] = 35 if card[6] >= 63 else 0
        # Check if game end and add sum
        if -1 not in card[0:15]:
            card[15] = sum(card[8:15])
            card[16] = sum(card[6:15])
            total = card[16]
            game.end_game()
            msg = 'You got total %s ! Game End.' % total
            return game.to_form(msg)
        else:
            # Reset dice
            game.roll_remain = 3
            game.dice[:] = []
            game.put()
        return game.to_form('You got %s points.' % points)

    # Get game user information
    def _get_user(self):
        """helper -- get user"""
        cur_user = endpoints.get_current_user()
        if not cur_user:
            raise endpoints.UnauthorizedException('Authourization required')
        user_id = get_user_id(cur_user)
        p_key = ndb.Key(User, user_id)
        user = p_key.get()
        if not user:
            raise endpoints.NotFoundException('Please create as a user first')
        return user


api = endpoints.api_server([YahtzeeGameApi])
