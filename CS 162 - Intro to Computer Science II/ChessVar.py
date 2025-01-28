# Author: Stefan Law
# GitHub username: stefan-law
# Date: 03/04/2024
# Description: Creates a Hunter-Falcon Chess variant implemented using
# OOP. Has separate classes for the game itself, the board, for each player,
# and for each piece which defines their respective states and unique actions
# available. Parses input chess moves and determines if input is valid or not.
# If valid, the game state is updated and a new board representation is output
# to the console. If a win is achieved, input is no longer accepted and a relevant
# message is printed to the console.

class ChessVar:
    """
    This class represents the overall state of the chess game being played.
    On initialization, it will set up game state, track whose turn it is, create all
    necessary objects for the game and set up the board for play before printing it to
    the screen for reference.

    By nature of running the game, it will communicate with all Board, Player, and Piece objects and will
    set in motion their instantiation and manage their activities.
    """

    def __init__(self):
        """
        Init method for Chess Var
        Parameters: none
        Returns: None

        Creates private data members to track turn, gamestate, creates a Board instance, Black/White
        players. Also contains a column_index dictionary to translate algebraic chess notation of columns to a numbered
        index that various methods can use.

        Sets up pieces on board (i.e. creates all Pieces and assigns starting locations to each Piece)
        Prints initial board representation to console
        """
        self._turn = "WHITE"
        self._game_state = "UNFINISHED"
        self._gameboard = Board()
        self._white = Player("WHITE")
        self._black = Player("BLACK")

        self._gameboard.set_board(self._black, self._white)
        self._gameboard.draw_board()

        self._column_index = {'a': 0,
                              'b': 1,
                              'c': 2,
                              'd': 3,
                              'e': 4,
                              'f': 5,
                              'g': 6,
                              'h': 7}

    def get_game_state(self):
        """
        Parameters: none
        Returns: self._game_state (string: UNFINISHED, WHITE_WON, BLACK_WON flags only)

        Helper method for to determine current game state
        Utilized by ChessVar.make_move()
        """
        return self._game_state

    def set_game_state(self, state):
        """
        Parameters: state (string: UNFINISHED, WHITE_WON, BLACK_WON flags only)
        Returns: None

        Helper method for other objects to set current game state
        Only utilized when king has been captured as determined by ChessVar.check_king_status()
        """
        self._game_state = state

    def get_turn(self):
        """
        Parameters: none
        Returns: self._turn (string WHITE or BLACK flags only)

        Helper method to get current turn
        Utilized by ChessVar.make_move()
        """
        return self._turn

    def set_turn(self, player):
        """
        Parameters: player (string WHITE or BLACK flags only)
        Returns: None

        Helper method to set turn (i.e. when current turn is completed)
        Utilized by ChessVar.make_move()
        """
        self._turn = player

    def get_column_index(self, index_letter):
        """
        Parameter: index_letter(string or char), must be a thru h; automatically handles upper-case input
        using lower() method
        Returns: column_index (int)

        Helper method to translate algebraic notation of column to an index integer
        """
        return self._column_index[index_letter.lower()]

    def make_move(self, source, destination):
        """
        Parameters:
            -source: (string), current square of piece to be moved, must be 2 characters in length with
            a letter (a-h) followed by a number (1-8). Invalid input will be handled with other called methods
            inside make_move
            -destination: (string), same constraints as source
        Returns: Bool, dependent on valid or invalid move and game state

        This is the most complicated method of ChessVar and may benefit from use of further encapsulation/abstraction
        The following steps are performed:
            1. Check for game state and if finished return False
            2. Determine active player object based on turn state
            3. Parse row, column for source and destination squares
            4. Check that the source square is valid (i.e. not occupied by enemy, occupied by self)
            5. Determine possible moves for source piece and try to match to destination input
            6. If pawn is moved, update flag notating whether it is first move or not
            7. If a valid move, update piece location and board, and capture if necessary
            8. Check if either King has been captured, and if so update game state with relevant winner
            9. Update turn
        """
        # Check if game over; return False if so
        if self.get_game_state() != 'UNFINISHED':
            print(self.get_game_state())
            return False

        # Determine who is playing based on turn
        if self.get_turn() == 'WHITE':
            player = self._white
            opponent = self._black
        else:
            player = self._black
            opponent = self._white

        # Parse source and destination inputs, ensure on board
        source_row = int(source[1])
        destination_row = int(destination[1])

        try:
            source_column = self.get_column_index(source[0])
            destination_column = self.get_column_index(destination[0])
        except:
            return False

        source_piece = self.check_source_square(player, source_row, source_column)

        # If player does not have a piece on source square, return False
        if source_piece is None:
            return False

        # determine legal moves and check validity for source square piece
        # get_candidate_moves will return a tuple(row, column, enemy=None)
        # generator function yields False once all moves have been yielded
        candidate_move = False
        for candidate_move in source_piece.get_candidate_moves():
            if candidate_move and (candidate_move[0] == destination_row) and (candidate_move[1] == destination_column):
                break

        # if input move is not legal, return False
        if candidate_move is False:
            return False

        # update movement flag if pawn moved
        if type(source_piece) is Pawn:
            source_piece.set_pawn_move_flag()

        # update piece location and empty source square
        source_piece.set_location(candidate_move[0], candidate_move[1])

        # check if destination occupied, and if so make a capture
        if candidate_move[2] is not None:
            self.make_capture(candidate_move[2], opponent)

        # Check if a King has been captured
        self.check_king_status(player, opponent)

        # update board and print it
        self._gameboard.update_board(source_row, source_column, candidate_move[0],
                                     candidate_move[1], source_piece.get_symbol())
        self._gameboard.draw_board()

        # update turn and return True
        self.set_turn(opponent.get_color())

        return True

    def make_capture(self, captured_piece, opponent):
        """
        Parameter: captured_piece (must be object with inheritance from Piece class)
        Returns: None

        Takes a captured piece off the board by setting location to (None, None) and updating status
        Used by ChessVar.make_move()
        """
        captured_piece.set_location(None, None)
        captured_piece.set_status("CAPTURED")

        if type(captured_piece) is not Pawn:
            opponent.lost_a_piece()

    def check_source_square(self, player, source_row, source_column):
        """
        Parameters:
            -player: must be a Player object
            -source_row: (int), row of piece to be moved
            -source_column(int), column of piece to be moved

        This method is a helper method for ChessVar.make_move(). It iterates through all the
        Player's piece objects to see if any are located on the provided source square. If a match
        is found, the corresponding Piece object is returned, otherwise returns None
        """
        # Check if source square is unoccupied or enemy
        for piece in player.get_pieces():
            # if piece location matches source location, hold onto piece and return
            location = piece.get_location()
            if (location[0] == source_row) and (location[1] == source_column):
                return piece

        return None

    def check_king_status(self, player, opponent):
        """
        Parameters: player, opponent (both must be Player objects)
        Returns None

        This class is used by ChessVar.make_move() to determine whether or not king has been captured
        after current move is made. If the King is captured, the game state is updated appropriately.
        """
        for piece in opponent.get_pieces():
            if type(piece) is King and piece.get_status() == 'CAPTURED':
                if player.get_color() == 'WHITE':
                    self.set_game_state('WHITE_WON')
                else:
                    self.set_game_state('BLACK_WON')

    def enter_fairy_piece(self, fairy_piece, destination):
        """
        Parameters:
            -fairy_piece: (char), must be "F/f" or "H/h", upper or lower case depending on
            player color
            -destination: (string), must be on home rank, empty square
        Returns: Bool, dependent on valid or invalid move and game state

        The following steps are performed:
            1. Check for game state and if finished return False
            2. Determine active player object based on turn state, and valid home ranks
            3. Parse row, column for destination squares
            4. Check that the destination square is valid (i.e. not occupied, on home ranks)
            5. Check that piece meets criteria for deployment
            6. Place piece on board and update board
            7. Update turn
        """
        # Check if game over, return False if so
        if self.get_game_state() != 'UNFINISHED':
            print(self.get_game_state())
            return False

        # Determine who is playing based on turn and which ranks are home rank
        if self.get_turn() == 'WHITE':
            player = self._white
            opponent = self._black
            home_rank = (1, 2)
        else:
            player = self._black
            opponent = self._white
            home_rank = (7, 8)

        # parse input square
        destination_row = int(destination[1])

        try:
            destination_column = self.get_column_index(destination[0])
        except:
            return False

        # find player piece
        piece = None
        for item in player.get_pieces():
            if item.get_symbol() == fairy_piece:
                piece = item

        if piece is None:
            return False

        # validate input square (empty, on home ranks, on board)
        if piece.check_empty(destination_row, destination_column) is None:
            return False
        if destination_row not in home_rank:
            return False
        if destination_column < 0 or destination_column > 7:
            return False

        # validate piece (falcon/hunter)
        # validate piece is not on board or captured
        if piece.get_status() == "CAPTURED" or piece.get_status() == "ON_BOARD":
            return False

        # validate  that enough pieces are captured, return False if not
        if player.get_pieces_lost() < 1:
            return False

        # If valid, place piece on board and update board
        piece.set_status("ON_BOARD")
        piece.set_location(destination_row, destination_column)
        self._gameboard.update_board(None, None, destination_row, destination_column, piece.get_symbol())
        self._gameboard.draw_board()

        # Update turn state, return True
        # Decrement lost piece count
        player.dec_pieces_lost()
        self.set_turn(opponent.get_color())

        return True

    def test_loop(self):
        """
        Test loop for easier entry of moves via console for debugging
        Parameters, Returns: None
        """

        test_input1 = input("Enter C for chess move, or F for fairy move, or Q to quit: ")
        while test_input1.upper() != 'Q':
            if test_input1.upper() == "F":
                test_input1 = input("Input Fairy Piece: ")
                test_input2 = input("Input destination square: ")
                self.enter_fairy_piece(test_input1, test_input2)
            elif test_input1.upper() == "C":
                test_input1 = input("Input source square: ")
                test_input2 = input("Input destination square: ")
                self.make_move(test_input1, test_input2)

            test_input1 = input("Enter C for chess move, or F for fairy move, or Q to quit: ")






class Board:
    """
    Creates an object that will represent and track the game board. The board is represented by
    a dictionary, with row number acting as key and corresponding to a list of column values for that row.
    Each square contains a text representation for a piece, with upper case representing White and
    lowercase representing Black. An empty square is represented by "." Each square can be cross-referenced
    to the game's Piece objects by referencing the relevant row and column.

    The Board class provides methods for initial board setup, updating piece placement on the board, and
    printing the current board state to the console. It can also provide the contents of any given square on
    the board referenced by row and column coordinates. It interacts frequently with the Piece subclasses and
    Player classes to track the ongoing changes to the game.
    """

    def __init__(self):
        """
        Init method for Board object

        Creates a private self._board data member which contains the dictionary of lists representing
        the current state of the gameboard
        """
        self._board = {8: ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
                       7: ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
                       6: ['.', '.', '.', '.', '.', '.', '.', '.'],
                       5: ['.', '.', '.', '.', '.', '.', '.', '.'],
                       4: ['.', '.', '.', '.', '.', '.', '.', '.'],
                       3: ['.', '.', '.', '.', '.', '.', '.', '.'],
                       2: ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
                       1: ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
                       }

    def set_board(self, black_player, white_player):
        """
        Parameters: black_player, white_player (must be Player objects)
        Returns: None

        This method is called once by ChessVar when the game is initialized.
        It iterates through the initial board representation and creates individual Piece objects of type
        corresponding to filled square/player color.
        """
        for row in self._board.keys():
            for column, value in enumerate(self._board[row]):
                if value == '.':
                    continue
                elif value.isupper():
                    white_player.add_piece(self, row, column, value, black_player)
                else:
                    black_player.add_piece(self, row, column, value, white_player)

        # Add Falcon Pieces
        white_player.add_piece(self, None, None, "F", black_player)
        black_player.add_piece(self, None, None, "f", white_player)

        # Add Hunter pieces
        white_player.add_piece(self, None, None, "H", black_player)
        black_player.add_piece(self, None, None, "h", white_player)

    def update_board(self, source_row, source_column, destination_row, destination_column, piece_value):
        """
        Parameters:
            source_row, source_column, destination_row, destination_column: must be int
            piece_value: must be char/string, length of one character, must correspond to chess pieces

        Returns: none

        This method is called by ChessVar.make_move() after a valid move is input. It will place a "."
        at the source square and the moved piece to the destination square
        """
        if source_row is not None:
            self._board[source_row][source_column] = '.'
        self._board[destination_row][destination_column] = piece_value

    def draw_board(self):
        """
        Parameters: none
        Returns: None

        This method is called by ChessVar.init() and ChessVar.make_move(). It prints the current
        board representation to the console.
        """
        row_count = 8

        for key in self._board.keys():
            # print start of row
            print(str(row_count) + "| ", end='')
            row_count -= 1

            # print each value in row
            for value in self._board[key]:
                print(value + '  ', end='')
            print('')
        # formatting for output
        print("  -----------------------")
        print("   a  b  c  d  e  f  g  h")

        print()
        print()

    def get_square(self, row, column):
        """
        Parameters: row, column (must be int, must be on Board)
        Returns: char/string containing value at passed square coordinates, either "." or a chess piece

        Used by Piece objects when determining candidate moves
        """
        return self._board[row][column]


class Player:
    """
    Creates an object that will represent each player (Black and White).
    Tracks how many pieces have been lost, to aid in determining eligibility
    Maintains a list of all Piece objects belonging to the player. Utilized extensively by ChessVar
    to help track game state and eligibility to add fairy pieces to board in game.
    """

    def __init__(self, color):
        """
        Init method for Player object
        Receives: color (must be string, "BLACK" or "WHITE" flag only)
        """
        self._color = color
        self._pieces_lost = 0
        self._pieces = []

    def add_piece(self, board, row, column, value, opponent):
        """
        Parameters:
            -board: must be Board object
            -row, column: must be integers, must correspond to location on board
            -value: must be char/string, must be "." or piece value
            -opponent: must be opposing Player object

        Returns: none

        This method is called by Board.set_board() repeatedly as it iterates through the board
        representation, whenever a piece value is encountered. It also is called twice for each player
        in order to create their Falcon and Hunter pieces, which are initially off the board. A piece
        is created and appended to the player's piece list based on piece value.
        """

        # determine color
        if value.isupper():
            color = "WHITE"
        else:
            color = "BLACK"

        # add piece depending on board value at given square
        if value == 'p' or value == 'P':
            self._pieces.append(Pawn(row, column, color, board, opponent))
        elif value == 'n' or value == 'N':
            self._pieces.append(Knight(row, column, color, board, opponent))
        elif value == 'b' or value == 'B':
            self._pieces.append(Bishop(row, column, color, board, opponent))
        elif value == 'r' or value == 'R':
            self._pieces.append(Rook(row, column, color, board, opponent))
        elif value == 'q' or value == 'Q':
            self._pieces.append(Queen(row, column, color, board, opponent))
        elif value == 'k' or value == 'K':
            self._pieces.append(King(row, column, color, board, opponent))
        elif value == 'f' or value == 'F':
            self._pieces.append(Falcon(row, column, color, board, opponent))
        elif value == 'h' or value == 'H':
            self._pieces.append(Hunter(row, column, color, board, opponent))

    def get_pieces(self):
        """
        Parameters: none
        Returns: list of Piece objects held by Player

        This method is utilized by ChessVar.make_move(),Piece.check_enemy_piece() and by
        the get_candidate_move() method of individual piece types
        """
        return self._pieces

    def get_color(self):
        """

        Parameter: none
        Returns: string, "BLACK" or "WHITE" flag only

        Get method for returning Player color type. Used by ChessVar.make_move() and
        ChessVar.check_king_status()
        """
        return self._color

    def lost_a_piece(self):
        """
        Parameters: none
        Returns: None

        Called by make_move()/enter_fairy_piece() when a major piece is captured (but not a pawn) to track number lost and help
        determine eligibility for deploying a Falcon or Hunter piece.
        """
        self._pieces_lost += 1

    def get_pieces_lost(self):
        """
        Parameters: none
        Returns: number of pieces lost (int)

        Used to determine eligibility for entering a fairy piece.
        """
        return self._pieces_lost

    def dec_pieces_lost(self):
        """
        Parameter: none
        Returns: none

        Decrements piece lost count when enter_fairy_piece() is successfully called
        """
        self._pieces_lost -= 1


class Piece:
    """
    This class is used as a base class for each individual piece of the game. Because each piece has
    unique movements and capturing abilities, we utilize inheritance; i.e. there are separate classes for
    each piece type which inherit from Piece. This class and it's children are used extensively by Board,
    Player, and ChessVar classes.

    The Piece class itself creates a template with private data members for aspects such as location,
    color, status, etc. It also holds references to the piece's opponent (Player) and the board that it is
    located on (Board) which it will use to aid in determining candidate moves and "collision detection".
    Individual children objects will use polymorphism via the get_candidate_moves()
    generator to return all possible moves for the piece at its current position.

    There are many helper methods contained within this class to get/set these data members, while
    check_empty(), check_self(), check_enemy_piece(), and square_in_bounds() are utilized to help validate
    potential candidate moves as well as input moves.
    """

    def __init__(self, row, column, color, board, opponent):
        """
        Parameters:
            -row, column: must be integer, must be valid location on board
            -color: must be string, "WHITE" or "BLACK" flag oly
            -board: must be Board object
            -opponent: must be Player object

        Returns: None

        Init method for Piece object that sets initial values for all common private data members
        """
        self._color = color
        self._row = row
        self._column = column
        self._status = None
        self._symbol = None
        self._gameboard = board
        self._opponent = opponent

    def get_location(self):
        """
        Parameters: none
        Returns: tuple(int, int)

        Helper method that returns a tuple containing row and column of Piece.
        """
        return self._row, self._column

    def set_location(self, row, column):
        """
        Parameters:
            -row, column: must be int, must be valid location on board
        Returns: None

        Helper method that updates location of Piece
        """
        self._row = row
        self._column = column

    def get_status(self):
        """
        Parameters: none
        Return: self._status(string or None); may be None, "CAPTURED", "ON_BOARD"

        Helper method that returns current status of Piece
        """
        return self._status

    def set_status(self, status):
        """
        Parameters: status (string), may be None, "CAPTURED", "ON_BOARD"
        Return: self._status(string or None); may be None, "CAPTURED", "ON_BOARD"

        Helper method that sets current status of Piece
        """
        self._status = status

    def get_symbol(self):
        """
        Parameters: none
        Return: self._symbol (char/string)

        Helper method that returns symbol of Piece
        """
        return self._symbol

    def check_empty(self, row, column):
        """
        Parameters: row, column (integer); must be valid location on board
        Returns None OR (row, column, None)

        Helper method to check if a square is empty. If a square is empty, a tuple containing
        (row, column, None) is returned which will be used by other methods for piece movement,
        move validation etc.
        """
        if self._gameboard.get_square(row, column) == '.':
            return row, column, None

    def check_enemy_piece(self, row, column):
        """
        Parameters: row, column (integer), must be valid location on board
        Returns None OR (row(int), column(int), piece(Piece))

        Helper method to check if a square contains an enemy piece. Generally used by
        individual piece methods that generate candidate moves for determining collisions and captures.
        If an enemy piece is found to be on provided square, the location and reference to the enemy
        Piece are returned in a tuple. This information may be used for move validation or for making
        a capture.
        """
        for piece in self._opponent.get_pieces():
            if (piece.get_location()[0] == row) and (piece.get_location()[1] == column):
                return row, column, piece

    def check_self(self, row, column):
        """
        Parameters: row, column (int); must be valid location on board
        Returns: Bool

        Helper method to determine if Player has a piece at supplied location (rather than
        an enemy piece or empty). If the square isn't empty and isn't an enemy, Player has a piece there.
        Used for move validation and collision detection when generating candidate moves.
        """
        if self.check_empty(row, column) is None and self.check_enemy_piece(row, column) is None:
            return True
        else:
            return False

    def square_in_bounds(self, row, column):
        """
        Parameters: row, column (int);
        Returns: Bool

        Helper method to determine if supplied coordinates are a valid location on board, returning
        relevant Bool value.
        """
        # check if row is valid
        if row < 1 or row > 8:
            return False
        # check if column is valid
        elif column < 0 or column > 7:
            return False
        else:
            return True

class Pawn(Piece):
    """
    Inherits from Piece class, represents pawn movements and captures
    Contains additional data members that account for board
    orientation, and whether or not pawn has made a move (since on first
    turn pawn may advance two squares)
    """

    def __init__(self, row, column, color, board, opponent):
        super().__init__(row, column, color, board, opponent)
        """
        Parameters: 
            -row, column (int), must be valid square
            -color (string), must be "WHITE" or "BLACK" flag
            -board (Board object)
            -opponent (Player object)
        Returns: None
        
        Init method for pawn objects, updates symbol and initializes
        first move to True. Also creates a direction vector depending 
        on piece color.
        Uses all data members from Piece class
        """
        self.set_status("ON_BOARD")
        # Init with first move true/false for double jump
        self._first_move = True
        # Init with directional vector for row based on color
        if color == "WHITE":
            self._vector = 1
            self._symbol = 'P'
        else:
            self._vector = -1
            self._symbol = 'p'

    def get_candidate_moves(self):
        """
        Parameters: none
        Returns: yields all valid candidate moves as a tuple (row, column, captured piece/None)
        Yields false when all valid candidate moves have been returned

        Generator function specific to pawn movements and captures
        """
        # Generate forward movement(row +1; row+2)
        # check for out of bounds
        # check for occupation
        candidate_row = self._row + (1 * self._vector)
        if 0 <= candidate_row <= 7:
            yield self.check_empty(candidate_row, self._column)

            if self._first_move is True:
                candidate_row = self._row + (2 * self._vector)
                if 0 <= candidate_row <= 7:
                    yield self.check_empty(candidate_row, self._column)

            # Generate captures (row +1, column +/-1)
            candidate_row = self._row + (1 * self._vector)

            # capture left
            candidate_column = self._column - 1
            if candidate_column >= 0:
                square = self._gameboard.get_square(candidate_row, candidate_column)
                if square != '.':
                    for piece in self._opponent.get_pieces():
                        if (piece.get_location()[0] == candidate_row) and (piece.get_location()[1] == candidate_column):
                            yield candidate_row, candidate_column, piece

            # capture right
            candidate_column = self._column + 1
            if candidate_column <= 7:
                square = self._gameboard.get_square(candidate_row, candidate_column)
                if square != '.':
                    for piece in self._opponent.get_pieces():
                        if (piece.get_location()[0] == candidate_row) and (piece.get_location()[1] == candidate_column):
                            yield candidate_row, candidate_column, piece

        yield False

    def set_pawn_move_flag(self):
        """
        Parameters: None
        Returns: None

        Helper function that updates after pawn makes it's first move
        so that it can no longer jump 2 squares forward
        """
        self._first_move = False


class Rook(Piece):
    """
    Inherits from Piece class, represents rook movements and captures
    Has a get_candidate_move polymorphic function that generates Rook moves
    """

    def __init__(self, row, column, color, board, opponent):
        super().__init__(row, column, color, board, opponent)
        """
        Parameters: 
            -row, column (int), must be valid square
            -color (string), must be "WHITE" or "BLACK" flag
            -board (Board object)
            -opponent (Player object)
        Returns: None
        
        Init method for rook objects, updates symbol.
        Uses all data members from Piece class"""
        self.set_status("ON_BOARD")

        if color == "WHITE":
            self._symbol = 'R'
        else:
            self._symbol = 'r'

    def get_candidate_moves(self):
        """
        Parameters: none
        Returns: yields each valid candidate move as a tuple (row, column, captured piece/None)
        Yields false when all valid candidate moves have been returned

        Generator function specific to rook movements and captures
        """
        # Check upward movement
        candidate_row = self._row + 1
        while self.square_in_bounds(candidate_row, self._column):
            if self.check_self(candidate_row, self._column):
                break
            yield self.check_empty(candidate_row, self._column)
            yield self.check_enemy_piece(candidate_row, self._column)
            if self.check_enemy_piece(candidate_row, self._column):
                break
            candidate_row += 1

        # Check downward movement
        candidate_row = self._row - 1
        while self.square_in_bounds(candidate_row, self._column):
            if self.check_self(candidate_row, self._column):
                break
            yield self.check_empty(candidate_row, self._column)
            yield self.check_enemy_piece(candidate_row, self._column)
            if self.check_enemy_piece(candidate_row, self._column):
                break
            candidate_row -= 1

        # Check left  movement
        candidate_column = self._column - 1
        while self.square_in_bounds(self._row, candidate_column):
            if self.check_self(self._row, candidate_column):
                break
            yield self.check_empty(self._row, candidate_column)
            yield self.check_enemy_piece(self._row, candidate_column)
            if self.check_enemy_piece(self._row, candidate_column):
                break
            candidate_column -= 1

        # Check right movement
        candidate_column = self._column + 1
        while self.square_in_bounds(self._row, candidate_column):
            if self.check_self(self._row, candidate_column):
                break
            yield self.check_empty(self._row, candidate_column)
            yield self.check_enemy_piece(self._row, candidate_column)
            if self.check_enemy_piece(self._row, candidate_column):
                break
            candidate_column += 1

        yield False


class Knight(Piece):
    """
    Inherits from Piece class, represents knight movements and captures
    Has a get_candidate_move polymorphic function that generates knight moves
    """

    def __init__(self, row, column, color, board, opponent):
        super().__init__(row, column, color, board, opponent)
        """        
        Parameters: 
            -row, column (int), must be valid square
            -color (string), must be "WHITE" or "BLACK" flag
            -board (Board object)
            -opponent (Player object)
        Returns: None
        
        Init method for knight objects, updates symbol.
        Uses all data members from Piece class
        """
        self.set_status("ON_BOARD")

        if color == "WHITE":
            self._symbol = 'N'
        else:
            self._symbol = 'n'

    def get_candidate_moves(self):
        """
        Parameters: none
        Returns: yields each valid candidate move as a tuple (row, column, captured piece/None)
        Yields false when all valid candidate moves have been returned

        Generator function specific to knight movements and captures
        """
        # Check 8 possible jumps and captures
        # Each movement can be either a jump or a capture
        # No need to check intervening squares
        # Check long axis first, then knee to ensure in bounds, then check move or capture

        # Check up
        candidate_row = self._row + 2
        if candidate_row <= 8:
            # Check left knee
            candidate_column = self._column - 1
            if candidate_column >= 0:
                yield self.check_empty(candidate_row, candidate_column)
                yield self.check_enemy_piece(candidate_row, candidate_column)

            # Check right knee
            candidate_column = self._column + 1
            if candidate_column <= 7:
                yield self.check_empty(candidate_row, candidate_column)
                yield self.check_enemy_piece(candidate_row, candidate_column)

        # Check down
        candidate_row = self._row - 2
        if candidate_row >= 1:
            # Check left knee
            candidate_column = self._column - 1
            if candidate_column >= 0:
                yield self.check_empty(candidate_row, candidate_column)
                yield self.check_enemy_piece(candidate_row, candidate_column)

            # Check right knee
            candidate_column = self._column + 1
            if candidate_column <= 7:
                yield self.check_empty(candidate_row, candidate_column)
                yield self.check_enemy_piece(candidate_row, candidate_column)

        # Check right
        candidate_column = self._column + 2
        if candidate_column <= 7:
            # Check up knee
            candidate_row = self._row + 1
            if candidate_row <= 8:
                yield self.check_empty(candidate_row, candidate_column)
                yield self.check_enemy_piece(candidate_row, candidate_column)

            # Check down knee
            candidate_row = self._row - 1
            if candidate_row >= 1:
                yield self.check_empty(candidate_row, candidate_column)
                yield self.check_enemy_piece(candidate_row, candidate_column)

        # Check left
        candidate_column = self._column - 2
        if candidate_column >= 0:
            # Check up knee
            candidate_row = self._row + 1
            if candidate_row <= 8:
                yield self.check_empty(candidate_row, candidate_column)
                yield self.check_enemy_piece(candidate_row, candidate_column)

            # Check down knee
            candidate_row = self._row - 1
            if candidate_row >= 1:
                yield self.check_empty(candidate_row, candidate_column)
                yield self.check_enemy_piece(candidate_row, candidate_column)

        yield False


class Bishop(Piece):
    """
    Inherits from Piece class, represents knight movements and captures
    Has a get_candidate_move polymorphic function that generates bishop moves
    """

    def __init__(self, row, column, color, board, opponent):
        super().__init__(row, column, color, board, opponent)
        """
        Parameters: 
            -row, column (int), must be valid square
            -color (string), must be "WHITE" or "BLACK" flag
            -board (Board object)
            -opponent (Player object)
        Returns: None
        
        Init method for bishop objects, updates symbol..
        Uses all data members from Piece class
        """
        self.set_status("ON_BOARD")

        if color == "WHITE":
            self._symbol = 'B'
        else:
            self._symbol = 'b'

    def get_candidate_moves(self):
        """
        Parameters: none
        Returns: yields each valid candidate move as a tuple (row, column, captured piece/None)
        Yields false when all valid candidate moves have been returned

        Generator function specific to bishop movements and captures
        """
        # seed first candidate square in each vector
        # while row in bounds, column in bounds
        # if square is own piece
        # break
        # else
        # yield check empty
        # yield check enemy

        # increment or decrement row/column for next square depending on vector

        # Check right upper diagonal movement/captures
        candidate_row = self._row + 1
        candidate_column = self._column + 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row += 1
            candidate_column += 1

        # Check right lower diagonal movement/captures
        candidate_row = self._row - 1
        candidate_column = self._column + 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row -= 1
            candidate_column += 1

        # Check left  upper diagonal movement/captures
        candidate_row = self._row + 1
        candidate_column = self._column - 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row += 1
            candidate_column -= 1

        # Check left lower diagonal  movement/captures
        candidate_row = self._row - 1
        candidate_column = self._column - 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row -= 1
            candidate_column -= 1

        yield False


class Queen(Piece):
    """
    Inherits from Piece class, represents queen movements and captures
    Has a get_candidate_move polymorphic function that generates queen moves
    """

    def __init__(self, row, column, color, board, opponent):
        super().__init__(row, column, color, board, opponent)
        """        Parameters: 
            -row, column (int), must be valid square
            -color (string), must be "WHITE" or "BLACK" flag
            -board (Board object)
            -opponent (Player object)
        Returns: None
        
        Init method for queen objects, updates symbol.
        """
        self.set_status("ON_BOARD")

        if color == "WHITE":
            self._symbol = 'Q'
        else:
            self._symbol = 'q'

    def get_candidate_moves(self):
        """
        Parameters: none
        Returns: yields each valid candidate move as a tuple (row, column, captured piece/None)
        Yields false when all valid candidate moves have been returned

        Generator function specific to queen movements and captures
        """
        # Check right upper diagonal movement/captures
        candidate_row = self._row + 1
        candidate_column = self._column + 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row += 1
            candidate_column += 1

        # Check right lower diagonal movement/captures
        candidate_row = self._row - 1
        candidate_column = self._column + 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row -= 1
            candidate_column += 1

        # Check left  upper diagonal movement/captures
        candidate_row = self._row + 1
        candidate_column = self._column - 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row += 1
            candidate_column -= 1

        # Check left lower diagonal  movement/captures
        candidate_row = self._row - 1
        candidate_column = self._column - 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row -= 1
            candidate_column -= 1

        # Check upward movement
        candidate_row = self._row + 1
        while self.square_in_bounds(candidate_row, self._column):
            if self.check_self(candidate_row, self._column):
                break
            yield self.check_empty(candidate_row, self._column)
            yield self.check_enemy_piece(candidate_row, self._column)
            if self.check_enemy_piece(candidate_row, self._column):
                break
            candidate_row += 1

        # Check downward movement
        candidate_row = self._row - 1
        while self.square_in_bounds(candidate_row, self._column):
            if self.check_self(candidate_row, self._column):
                break
            yield self.check_empty(candidate_row, self._column)
            yield self.check_enemy_piece(candidate_row, self._column)
            if self.check_enemy_piece(candidate_row, self._column):
                break
            candidate_row -= 1

        # Check left  movement
        candidate_column = self._column - 1
        while self.square_in_bounds(self._row, candidate_column):
            if self.check_self(self._row, candidate_column):
                break
            yield self.check_empty(self._row, candidate_column)
            yield self.check_enemy_piece(self._row, candidate_column)
            if self.check_enemy_piece(self._row, candidate_column):
                break
            candidate_column -= 1

        # Check right movement
        candidate_column = self._column + 1
        while self.square_in_bounds(self._row, candidate_column):
            if self.check_self(self._row, candidate_column):
                break
            yield self.check_empty(self._row, candidate_column)
            yield self.check_enemy_piece(self._row, candidate_column)
            if self.check_enemy_piece(self._row, candidate_column):
                break
            candidate_column += 1

        yield False


class King(Piece):
    """
    Inherits from Piece class, represents knight movements and captures
    Has a get_candidate_move polymorphic function that generates king moves
    """

    def __init__(self, row, column, color, board, opponent):
        super().__init__(row, column, color, board, opponent)
        """
                Parameters: 
            -row, column (int), must be valid square
            -color (string), must be "WHITE" or "BLACK" flag
            -board (Board object)
            -opponent (Player object)
        Returns: None
        
        Init method for king objects, updates symbol.
        Uses all data members from Piece class
        """
        self.set_status("ON_BOARD")

        if color == "WHITE":
            self._symbol = 'K'
        else:
            self._symbol = 'k'

    def get_candidate_moves(self):
        """
        Parameters: none
        Returns: yields each valid candidate move as a tuple (row, column, captured piece/None)
        Yields false when all valid candidate moves have been returned

        Generator function specific to king movements and captures
        """
        for column in range(-1, 2):
            for row in range(-1, 2):
                if row == 0 and column == 0:
                    continue
                else:
                    if self.square_in_bounds(self._row + row, self._column + column):
                        if self.check_self(self._row + row, self._column + column):
                            continue
                        yield self.check_empty(self._row + row, self._column + column)
                        yield self.check_enemy_piece(self._row + row, self._column + column)

        yield False


class Hunter(Piece):
    """
    Inherits from Piece class, represents knight movements and captures
    Has a get_candidate_move polymorphic function that generates hunter moves
    """

    def __init__(self, row, column, color, board, opponent):
        super().__init__(row, column, color, board, opponent)
        """
        Parameters: 
            -row, column (int), must be valid square
            -color (string), must be "WHITE" or "BLACK" flag
            -board (Board object)
            -opponent (Player object)
        Returns: None
        
        Init method for Hunter objects, updates symbol and initializes
        forward/reverse vectors depending 
        on piece color.
        Uses all data members from Piece class
        """
        self.set_status("OFF_BOARD")
        if color == "WHITE":
            self._backward_vector = -1
            self._forward_vector = 1
            self._symbol = 'H'
        else:
            self._symbol = 'h'
            self._backward_vector = 1
            self._forward_vector = -1

    def get_candidate_moves(self):
        """
        Parameters: none
        Returns: yields each valid candidate move as a tuple (row, column, captured piece/None)
        Yields false when all valid candidate moves have been returned

        Generator function specific to hunter movements and captures
        """

        # Check forward straight vector, accounting for board orientation
        # White will go up, Black will go down
        candidate_row = self._row + self._forward_vector
        while self.square_in_bounds(candidate_row, self._column):
            if self.check_self(candidate_row, self._column):
                break
            yield self.check_empty(candidate_row, self._column)
            yield self.check_enemy_piece(candidate_row, self._column)
            if self.check_enemy_piece(candidate_row, self._column):
                break
            candidate_row += self._forward_vector

        # Check backward diagonal vector, accounting for board orientation
        # White will go down, Black will go up
        # Check left
        candidate_row = self._row + self._backward_vector
        candidate_column = self._column - 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row += self._backward_vector
            candidate_column -= 1

        # Check right
        candidate_row = self._row + self._backward_vector
        candidate_column = self._column + 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row += self._backward_vector
            candidate_column += 1

        yield False


class Falcon(Piece):
    """
    Inherits from Piece class, represents knight movements and captures
    Has a get_candidate_move polymorphic function that generates falcon moves
    """

    def __init__(self, row, column, color, board, opponent):
        super().__init__(row, column, color, board, opponent)
        """
        Parameters: 
            -row, column (int), must be valid square
            -color (string), must be "WHITE" or "BLACK" flag
            -board (Board object)
            -opponent (Player object)
        Returns: None
        
        Init method for Hunter objects, updates symbol and initializes
        forward/reverse vectors depending 
        on piece color.
        Uses all data members from Piece class"""
        self.set_status("OFF_BOARD")

        if color == "WHITE":
            self._symbol = 'F'
            self._backward_vector = -1
            self._forward_vector = 1
        else:
            self._symbol = 'f'
            self._backward_vector = 1
            self._forward_vector = -1

    def get_candidate_moves(self):
        """
        Parameters: none
        Returns: yields each valid candidate move as a tuple (row, column, captured piece/None)
        Yields false when all valid candidate moves have been returned

        Generator function specific to falcon movements and captures
        """

        # Check forward diagonal vectors, accounting for board orientation
        # White will go up, Black will go down
        # Check left
        candidate_row = self._row + self._forward_vector
        candidate_column = self._column - 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row += self._forward_vector
            candidate_column -= 1

        # Check right
        candidate_row = self._row + self._forward_vector
        candidate_column = self._column + 1
        while self.square_in_bounds(candidate_row, candidate_column):
            if self.check_self(candidate_row, candidate_column):
                break
            yield self.check_empty(candidate_row, candidate_column)
            yield self.check_enemy_piece(candidate_row, candidate_column)
            if self.check_enemy_piece(candidate_row, candidate_column):
                break
            candidate_row += self._forward_vector
            candidate_column += 1

        # Check backward straight vector, accounting for board orientation
        # White will go down, Black will go up
        candidate_row = self._row + self._backward_vector
        while self.square_in_bounds(candidate_row, self._column):
            if self.check_self(candidate_row, self._column):
                break
            yield self.check_empty(candidate_row, self._column)
            yield self.check_enemy_piece(candidate_row, self._column)
            if self.check_enemy_piece(candidate_row, self._column):
                break
            candidate_row += self._backward_vector

        yield False  

my_game = ChessVar()
my_game.test_loop()