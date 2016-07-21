#Yahtzee Game API

## Products
- [App Engine][1]

## Language
- [Python][2]

## APIs
- [Google Cloud Endpoints][3]

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1. Update the values at the top of `settings.py` to
   reflect the respective client IDs you have registered in the
   [Developer Console][4].
1. Run the app with the devserver using `dev_appserver.py DIR`, and ensure it's running by visiting
   your local server's address (by default [localhost:8080][5].)
1. (Optional) Generate your client library(ies) with the endpoints tool.
1. Deploy your application.

[1]: https://developers.google.com/appengine
[2]: http://python.org
[3]: https://developers.google.com/appengine/docs/python/endpoints/
[4]: https://console.developers.google.com/
[5]: https://localhost:8080/
 
##Game Description:
- Yahtzee Game is a dice game. The object of the game is to score points by
rolling five dice to make certain combinations. 
- A game consists of thirteen rounds. Each round begins with 'roll_dice'. The dice 
can be rolled up to three times in a turn to try to make various scoring 
combinations. Each time you can choose which dice to be kept before next turn.
- After each round the player 'choose_category' to determine which scoring 
category is to be used for that round. Once a category has been used in the game, 
it cannot be used again. 
- The scoring categories have varying point values. A Yahtzee is five-of-a-kind and
 scores 50 points; the highest of any category. The winner is the player who 
 scores the most points. [Scoring rule is here][6].
- Many different Yahtzee games can be played by many different Users at any time. 
Each game can be retrieved by using the path parameter 'urlsafe_game_key'.

[6]:https://en.wikipedia.org/wiki/Yahtzee#Rules
##How to play/test the game:
1. Create as a user. May need Oauth login first.
1. Create a new game, or retrieve an incompleted game to continue via
  'urlsafe_game_key'.
1. Start the first round of game by rolling the dice. You have three times to roll the dice in each round.
- 
 - ONES: Get as many ones as possible.  Points = count(ONES) * 1
 - TWOS: Get as many twos as possible.  Points = count(TWOS) * 2
 - THREES: Get as many threes as possible.  Points = count(THREES) * 3
 - FOURS: Get as many fours as possible.  Points = count(FOURS) * 4
 - FIVES: Get as many fives as possible.  Points = count(FIVES) * 5
 - SIXES: Get as many sixes as possible.  Points = count(SIXES) * 6
 - THREE_OF_A_KIND: Get three dice with the same number. Points = sum of all dice (not just the three of a kind).
 - FOUR_OF_A_KIND: Get four dice with the same number. Points = sum of all dice (not just the four of a kind).
 - FULL_HOUSE: Get three of a kind and a pair, e.g. 1,1,3,3,3 or 3,3,3,6,6. Scores 25 points.
 - SMALL_STRAIGHT: Get four sequential dice, 1,2,3,4 or 2,3,4,5 or 3,4,5,6. Scores 30 points.
 - LARGE_STRAIGHT: Get five sequential dice, 1,2,3,4,5 or 2,3,4,5,6. Scores 40 points.
 - CHANCE: You can put anything into chance, it's basically like a garbage can when you don't have anything else you can use the dice for. Points = sum of all dice.
 - YAHTZEE: Five of a kind. Scores 50 points.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - play.py: Helper functions for play the game.
 - settings.py: User settings.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: None
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. A user must use oauth to login and 
    register. Will raise an UnauthorizedException if user doesn't login.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: None
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user must login as an existing user. 
    Will raise an UnauthorizedException if user doesn't login and a 
    NotFoundException if user hasn't registered.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

- **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: Message confirming the cancellation of the Game.
    - Description: Delete an incompleted game of the user. A warning message 
    will be sent if the game is completed or the game is not found or the game 
    is not belonging to the user.
    
- **get_user_games**
    - Method: GET
    - Parameters: None
    - Returns: GameForms
    - Description: Return all of a User's active games.

- **get_game_historys**
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForm
    - Description: Return the history record of a game. It inculdes dice 
    combination and points earned of each round of the game.

- **get_high_scores**
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms
    - Description: Return the list of high scores, top 3 as default.

- **get_user_rankings**
    - Method: GET
    - Parameters: None
    - Returns: UsersRankingForm
    - Description: Return the rankings of users. Order by max scores users got.

- **roll_dice**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: ChooseDiceForm, urlsafe_game_key
    - Returns: GameForm
    - Description: Accept a 'kept_dice' if user chooses to keep some of the dice
     before next turn and return a new rolling dice result.

- **choose_category**
    - Path: 'game/{urlsafe_game_key}'
    - Method: POST
    - Parameters: ChooseCatForm, urlsafe_game_key
    - Returns: GameForm
    - Description: Accept a 'choosed_category' and record the corresponding 
    points earned in this round. Update the dice and category information to 
    the game history. Calculate the sum points if game ends and end game.

##Models Included:
 - **User**
    - Stores unique users and email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **UserPerfForm**
    - Representation of a User's performance(name, max_score, games_completed)

 - **UsersRankingForm**
    - Multiple UserPerfForm container.

 - **GameForm**
    - Representation of a Game's state.

 - **GameForms**
    - Multiple GameForm container.
 
 - **ChooseDiceForm**
    - Inbound the list of index of each dice kept for next turn.
 
 - **ChooseCatForm**
    - Inbound the Enum field of CardCategory choosed.

 - **GameHistory**
    - Game history includes dice result and corresponded category.

 - **GameHistoryForm**
    - Multiple GameHistory container.

 - **ScoreForm**
    - Representation of a completed game's Score (user, date, result).

 - **ScoreForms**
    - Multiple ScoreForm container.

 - **StringMessage**
    - General purpose String container.

##Others Included:
 - **CardCategory**
    - Enum the game card category.

 - **ConflictException**
    - Exception mapped to HTTP 409 response.

