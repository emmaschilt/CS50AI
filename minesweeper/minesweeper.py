import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        # We can be certain if we know all cells in sentence are mines
        return {cell for cell in self.cells if self.count == len(self.cells) and self.count!=0}

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # We can be certain that all cells are safe if there are no mines in sentence
        return {cell for cell in self.cells if self.count == 0}

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell) 
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        if cell[0]<self.height and cell[1]<self.width:
            self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)


    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # Mark the cell as a move that has been made, and mark as safe:
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Create set to store undecided cells for KB:
        new_sentence_cells = set()

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # If cells are already safe, ignore them:
                if (i, j) in self.safes:
                    continue

                # If cells are known to be mines, reduce count by 1 and ignore them:
                if (i, j) in self.mines:
                    count = count - 1
                    continue

                # Otherwise add them to sentence if they are in the game board:
                if 0 <= i < self.height and 0 <= j < self.width:
                    new_sentence_cells.add((i, j))

        # Add the new sentence to the AI's Knowledge Base:
        print(f'Move on cell: {cell} has added sentence to knowledge {new_sentence_cells} = {count}' )
        self.knowledge.append(Sentence(new_sentence_cells, count))

        # Iteratively mark guaranteed mines and safes, and infer new knowledge:
        knowledge_changed = True

        while knowledge_changed:
            knowledge_changed = False

            safes = set()
            mines = set()

            # Get set of safe spaces and mines from KB
            for sentence in self.knowledge:
                safes = safes.union(sentence.known_safes())
                mines = mines.union(sentence.known_mines())

            # Mark any safe spaces or mines:
            if safes:
                knowledge_changed = True
                for safe in safes:
                    self.mark_safe(safe)
            if mines:
                knowledge_changed = True
                for mine in mines:
                    self.mark_mine(mine)

            # Remove any empty sentences from knowledge base:
            empty = Sentence(set(), 0)

            self.knowledge[:] = [x for x in self.knowledge if x != empty]

            # Try to infer new sentences from the current ones:
            for sentence_1 in self.knowledge:
                for sentence_2 in self.knowledge:

                    # Ignore when sentences are identical
                    if sentence_1.cells == sentence_2.cells:
                        continue

                    if sentence_1.cells == set() and sentence_1.count > 0:
                        print('Error - sentence with no cells and count created')
                        raise ValueError

                    # Create a new sentence if 1 is subset of 2, and not in KB:
                    if sentence_1.cells.issubset(sentence_2.cells):
                        new_sentence_cells = sentence_2.cells - sentence_1.cells
                        new_sentence_count = sentence_2.count - sentence_1.count

                        new_sentence = Sentence(new_sentence_cells, new_sentence_count)

                        # Add to knowledge if not already in KB:
                        if new_sentence not in self.knowledge:
                            knowledge_changed = True
                            print('New Inferred Knowledge: ', new_sentence, 'from', sentence_1, ' and ', sentence_2)
                            self.knowledge.append(new_sentence)

        # Print out AI current knowledge to terminal:
        print('Current AI KB length: ', len(self.knowledge))
        print('Known Mines: ', self.mines)
        print('Safe Moves Remaining: ', self.safes - self.moves_made)
        print('====================================================')

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        safe_moves = self.safes - self.moves_made
        if safe_moves: # Make a random safe move that has not been made yet
            print('Making a Safe Move! Safe moves available: ', len(safe_moves))
            return random.choice(list(safe_moves))
 
        # Otherwise there are no certain safe moves
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possibleMoves = []
        for i in range(self.height):
            for j in range(self.width):
                if (i,j) not in self.moves_made and (i,j) not in self.mines:
                    possibleMoves.append((i,j))
            
        if len(possibleMoves)!=0:
            return random.choice(possibleMoves)