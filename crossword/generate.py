import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.crossword.variables:
            # Filter valid words
            valid_words = {word for word in self.crossword.words if len(word)==variable.length}
            self.domains[variable] = valid_words # Update variable domain

    

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        madeRevision = False

        # Check for overlaps
        if self.crossword.overlaps[x,y]: 
            x_index = self.crossword.overlaps[x,y][0]
            y_index = self.crossword.overlaps[x,y][1]
            
            for xword in self.domains[x].copy():
                match = False
                for yword in self.domains[y]:
                    if xword[x_index] == yword[y_index]:
                        match = True 
                        break
                if not match: # Remove words that had no match with words in the y-domain.
                    self.domains[x].remove(xword)
                    madeRevision = True

        return madeRevision


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        queue = []
        if arcs is None:
            # Create arcs from all possible overlaps
            arcs = self.crossword.overlaps
        queue.extend(arcs)

        while queue:
            result = queue.pop()
            #print(result)  # Print the tuple returned by queue.pop()
            #print(type(result))  # Print the type to confirm it's a tuple
            x, y = result
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False # Unsolvable 
                # Add related arcs (neighbors) to queues 
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z,x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var in assignment:
            val = assignment[var]

            if var.length!=len(val): # Check for correct length
                return False 
            for y in self.crossword.neighbors(var): # Check for overlaps
                if y in assignment:
                    val_y = assignment[y]
                    x_index = self.crossword.overlaps[var,y][0]
                    y_index = self.crossword.overlaps[var,y][1]
                    if val[x_index] != val_y[y_index]:
                        return False 
                
        # Check for duplicates
        values_set = set(assignment.values())
        if len(values_set)<len(assignment.values()):
            return False
        
        # Otherwise the assignment is consistent
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        constraint_cost = {} #n

        for value in self.domains[var]:
            constraint_cost[value] = 0 # Give every value a constraint cost
            for y in self.crossword.neighbors(var): # Check neighbors
                x_index = self.crossword.overlaps[var,y][0]
                y_index = self.crossword.overlaps[var,y][1]
                for option in self.domains[y]:
                    if value[x_index] != option[y_index]: # If a neighboring choic is eliminated
                        constraint_cost[value] += 1 # Increase the constraint cost


        # Create ordered list
        ordered_list = sorted(constraint_cost, key=lambda item: item[1]) 

        return ordered_list
    
    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        min_remaining = 1000
        for var in self.crossword.variables:
            if var not in assignment:
                if len(self.domains[var])<min_remaining:
                    min_remaining = len(self.domains[var])
                    current_min = var
                elif len(self.domains[var])==min_remaining: # Tied minimum
                    current_min = var if len(self.crossword.neighbors(var))>=len(self.crossword.neighbors(current_min)) else current_min

        
        return current_min
                            
                

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        

        # Check if the assignment is already complete
        if self.assignment_complete(assignment):
            return assignment 
        
        # Variable selection
        next_var = self.select_unassigned_variable(assignment)

        # Order domain values according to least constraining heuristic
        ordered_list = self.order_domain_values(next_var, assignment)
        if not ordered_list:
            return None

        # Create copy of assignment and trial least constraining domain value
        new_assignment = assignment.copy()
        new_assignment[next_var] = ordered_list[0]

        # Recursively call backtrack 
        if self.consistent(new_assignment):
            return self.backtrack(new_assignment)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
