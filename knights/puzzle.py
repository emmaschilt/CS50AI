from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(

    Or(AKnight, AKnave), # Game rules

    Or( 
        And(AKnight, AKnave), # A truth
        And(AKnave, Not(AKnight)) # A lie
    )
    
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(

    # A says
    And(AKnave, BKnight),
    # Game rules
    Or(AKnight, AKnave),
    Or(BKnave, BKnight)
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # A says 
    Or(
        And(AKnight, BKnight),
        And(AKnave,BKnight)
    ),

    # B says 
    Or(
        And(AKnave, BKnight),
        And(AKnave, BKnave)
    ),

    # Game rules
    Or(AKnave, AKnight),
    Or(BKnight, BKnave)

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # A says 
    Not(AKnave), # Impossible to say "I am a knave" according to game rules

    # B says
    Or(
        And(BKnight, AKnave),
        And(BKnave, AKnight)
    ),

    Or(
        And(Not(BKnave), CKnave),
        And(BKnave, CKnight)
    ),

    # C says
    Or(
        And(CKnight, AKnight),
        And(CKnave, AKnave)
    ),

    # Game rules
    Or(CKnave, CKnight),
    Or(BKnight, BKnave)

)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
