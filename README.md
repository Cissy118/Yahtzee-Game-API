#Yahtzee Game API

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver, and ensure it's running by visiting the API Explorer 
 - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
Yahtzee Game is a dice game. The object of the game is to score points by
rolling five dice to make certain combinations. 
Each game begin with 'roll_dice'. The dice can be rolled up to three times in a 
turn to try to make various scoring combinations. Each time you can choose which
 dice to be kept before next turn.
A game consists of thirteen rounds. After each round the player
 'choose_category' to determine which scoring category is to be used for that 
 round. Once a category has been used in the game, it cannot be used again. 
The scoring categorieshave varying point values. A Yahtzee is five-of-a-kind and scores 50 points; the highest of any category. The winner is the player who scores the most points.
Many different Yahtzee games ca be played by many different Users at any time. 
Each game can be retrieved by using the path parameter 'urlsafe_game_key'.


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
    - Method: POST
    - Parameters: urlsafe_game_key
    - Returns: Message confirming the cancellation of the Game.
    - Description: Delete an incompleted game of the user. A warning message 
    will be sent if the game is completed or the game is not found or the game 
    is not belonging to the user.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_active_game_count**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts remaining for all games
    from a previously cached memcache key.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.