"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import httplib
import endpoints
from datetime import date
from datetime import datetime
from protorpc import messages
from protorpc import message_types
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop


class CardCategory(messages.Enum):
    """CardCategory -- Game Card Category"""
    ONES = 0
    TWOS = 1
    THREES = 2
    FOURS = 3
    FIVES = 4
    SIXES = 5
    UPPER_SCORE = 6
    UPPER_BONUS = 7
    THREE_OF_A_KIND = 8
    FOUR_OF_A_KIND = 9
    FULL_HOUSE = 10
    SMALL_STRAIGHT = 11
    LARGE_STRAIGHT = 12
    YAHTZEE = 13
    CHANCE = 14
    LOWER_SCORE = 15
    TOTAL = 16
# CATEGORIES = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14]


# --------------------------------------------------------
# User
class User(ndb.Model):
    """User -- User profile object"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    max_score = ndb.IntegerProperty(default=-1)
    games_completed = ndb.IntegerProperty(default=0)

    def to_perf_form(self):
        """Return a user performance form"""
        form = UserPerfForm()
        form.name = self.name
        form.max_score = self.max_score
        form.games_completed = self.games_completed
        return form


class UserPerfForm(messages.Message):
    """UserPerfForm -- Show user's performance"""
    name = messages.StringField(1, required=True)
    max_score = messages.IntegerField(2, required=True)
    games_completed = messages.IntegerField(3, required=True)


class UsersRankingForm(messages.Message):
    """UsersRankingForm -- List the ranking of users"""
    items = messages.MessageField(UserPerfForm, 1, repeated=True)


# --------------------------------------------------------
# Game
class Game(ndb.Model):
    """Game -- Game object"""
    user = ndb.KeyProperty(required=True, kind='User')
    round_remain = ndb.IntegerProperty(required=True)
    roll_remain = ndb.IntegerProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    dice = ndb.IntegerProperty(repeated=True)  # list of Integer
    score_card = ndb.IntegerProperty(repeated=True)  # list of cat score
    cat_history = msgprop.EnumProperty(
                CardCategory, repeated=True)
    dice_history = ndb.StringProperty(repeated=True)

    @classmethod
    def new_game(cls, user):
        """Createes and returns a new game"""
        game = Game(
            user=user, round_remain=13, roll_remain=3, score_card=[-1]*17)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.round_remain = self.round_remain
        form.roll_remain = self.roll_remain
        form.game_over = self.game_over
        form.dice = self.dice
        form.ones = self.score_card[0]
        form.twos = self.score_card[1]
        form.threes = self.score_card[2]
        form.fours = self.score_card[3]
        form.fives = self.score_card[4]
        form.sixes = self.score_card[5]
        form.upper_score = self.score_card[6]
        form.upper_bonus = self.score_card[7]
        form.three_of_a_kind = self.score_card[8]
        form.four_of_a_kind = self.score_card[9]
        form.full_house = self.score_card[10]
        form.small_straight = self.score_card[11]
        form.large_straight = self.score_card[12]
        form.yahtzee = self.score_card[13]
        form.chance = self.score_card[14]
        form.lower_score = self.score_card[15]
        form.total = self.score_card[16]
        form.message = message
        return form

    def end_game(self):
        """Record game when it reaches the end round"""
        self.game_over = True
        self.put()
        total_score = self.score_card[16]
        score = Score(user=self.user, date=date.today(), result=total_score)
        score.put()
        user = User.query(User.key == self.user).get()
        # record max score
        if total_score > user.max_score:
            user.max_score = total_score
        # count game completed
        user.games_completed += 1
        user.put()

    def to_history_form(self):
        """Return history of the game to form"""
        form = GameHistoryForm()
        # get current history records length
        length = len(self.dice_history)
        for i in range(0, length):
            history = GameHistory()
            history.dice = self.dice_history[i]
            history.category = self.cat_history[i].name
            if i is 0:
                form_list = [history]
            else:
                form_list.append(history)
        form.items = [item for item in form_list]
        return form


class GameForm(messages.Message):
    """GameForm -- for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user_name = messages.StringField(2, required=True)
    round_remain = messages.IntegerField(3, required=True)
    roll_remain = messages.IntegerField(4, required=True)
    game_over = messages.BooleanField(5, required=True)
    dice = messages.IntegerField(6, repeated=True)
    ones = messages.IntegerField(7)
    twos = messages.IntegerField(8)
    threes = messages.IntegerField(9)
    fours = messages.IntegerField(10)
    fives = messages.IntegerField(11)
    sixes = messages.IntegerField(12)
    upper_score = messages.IntegerField(13)
    upper_bonus = messages.IntegerField(14)
    three_of_a_kind = messages.IntegerField(15)
    four_of_a_kind = messages.IntegerField(16)
    full_house = messages.IntegerField(17)
    small_straight = messages.IntegerField(18)
    large_straight = messages.IntegerField(19)
    yahtzee = messages.IntegerField(20)
    chance = messages.IntegerField(21)
    lower_score = messages.IntegerField(22)
    total = messages.IntegerField(23)
    message = messages.StringField(24)


class GameForms(messages.Message):
    """GameForms -- multiple games outbound form message"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class ChooseDiceForm(messages.Message):
    """"Used to choose the index of dice kept for next roll"""
    index_choosed = messages.IntegerField(1, repeated=True)


class ChooseCatForm(messages.Message):
    """Used to choose the category after each round"""
    category = messages.EnumField(
        'CardCategory', 1, required=True)


class GameHistory(messages.Message):
    """GameHistory -- a formatted record of a game round"""
    dice = messages.StringField(1, required=True)
    category = messages.StringField(2, required=True)


class GameHistoryForm(messages.Message):
    """GameHistoryForm -- return detailed record of the whole game"""
    items = messages.MessageField(GameHistory, 1, repeated=True)


# --------------------------------------------------------
# Score
class Score(ndb.Model):
    """Score -- record of each game"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    result = ndb.IntegerProperty(required=True)

    def to_form(self):
        """Return a score form"""
        form = ScoreForm()
        form.user_name = self.user.get().name
        form.date = str(self.date)
        form.result = self.result
        return form


class ScoreForm(messages.Message):
    """ScoreForm -- Score outbound form message"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    result = messages.IntegerField(3, required=True)


class ScoreForms(messages.Message):
    """ScoreForms -- multiple  Scores outbound form message"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


# --------------------------------------------------------
# Needed for registration
class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class ConflictException(endpoints.ServiceException):
    """ConflictException -- exception mapped to HTTP 409 response"""
    http_status = httplib.CONFLICT
