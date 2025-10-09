"""Implementation of the guessing game logic.

Public function: startguesssing(start, end)
 - start: inclusive lower bound (int)
 - end: inclusive upper bound (int)

The function runs an interactive loop asking the user to guess the secret number.
It returns the number of attempts when the user guesses correctly, or None when
the user quits via EOFError (Ctrl-D/Ctrl-Z depending on platform).
"""
import random

def startguesssing(start=1, end=100):
    """Start an interactive guessing game.

    Returns the number of attempts when guessed correctly, or None if the user
    quits with EOF (Ctrl-D on Unix, Ctrl-Z on Windows + Enter).
    """
    # allow start == end so tests can force a deterministic secret
    if start > end:
        raise ValueError("start must be less than or equal to end")

    secret = random.randint(start, end)
    attempts = 0

    while True:
        attempts += 1
        try:
            user_input = input(f"Attempt {attempts}: Enter your guess: ")
        except EOFError:
            print(f"Quitting the game. The number was {secret}")
            return None

        if not user_input:
            print("Empty input, try again!")
            attempts -= 1
            continue

        try:
            guess = int(user_input)
        except ValueError:
            print("Invalid input. Please enter a whole number.")
            attempts -= 1
            continue

        if guess < start or guess > end:
            print(f"Please guess a number between {start} and {end}.")
            attempts -= 1
            continue
        elif guess < secret:
            print(f"Too low! ({guess})")
        elif guess > secret:
            print(f"Too high! ({guess})")
        else:
            print(f"Correct! The number was {secret}. Attempts: {attempts}")
            return attempts

