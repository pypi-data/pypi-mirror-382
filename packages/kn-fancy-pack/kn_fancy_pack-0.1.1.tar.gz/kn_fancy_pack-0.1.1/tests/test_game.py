import builtins
import io
import sys
import random

from kn_fancy_pack import startguesssing


def test_guess_correct_immediately(monkeypatch, capsys):
    # Force secret to 5
    random.seed(0)
    # monkeypatch input to return the secret immediately
    monkeypatch.setattr('builtins.input', lambda prompt='': '50')
    # We don't know seed mapping; instead, call with start=end=50 to force secret
    attempts = startguesssing(50, 50) if False else startguesssing(50, 50)
    assert attempts == 1


def test_invalid_inputs_then_correct(monkeypatch, capsys):
    # Create a sequence of inputs: '', 'abc', '0', '101', '42'
    inputs = iter(['', 'abc', '0', '101', '42'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))

    # Force secret to 42 by setting range 42..42
    attempts = startguesssing(42, 42)
    # implementation decrements attempts for the invalid inputs, so final attempts is 1
    assert attempts == 1
