###############################################################################
# art_pals.py Test Suite
###############################################################################
import pytest
import re
import random
from unittest.mock import patch
from artpack import art_pals
from artpack.palettes import pals


# Input validations
## n
@pytest.mark.parametrize("n_invalid", ["five", -3, 5.5])
def test_n_error_message(n_invalid):
    expected_n_error_message = (
        f"n must be a positive integer. You've supplied: {n_invalid}"
    )
    with pytest.raises(ValueError, match=expected_n_error_message):
        art_pals(n=n_invalid)


## pal
def test_pal_type_error_message():
    invalid_type_pal = ("hi", "bye")
    expected_type_error_message = (
        f"pal must be a single character string. You've supplied: {invalid_type_pal}"
    )
    with pytest.raises(TypeError, match=re.escape(expected_type_error_message)):
        art_pals(pal=invalid_type_pal)


def test_wrong_pal_error_message():
    invalid_pal = "DtMF"
    valid_pals = ", ".join(pals.keys())
    expected_pal_error_message = f"'{invalid_pal.lower()}' is not a valid palette. Please choose one of the following: {valid_pals}"
    with pytest.raises(ValueError, match=expected_pal_error_message):
        art_pals(pal=invalid_pal)


@pytest.mark.parametrize(
    "pal_valid, expected_output",
    [
        ("OCEAN", ["#12012E", "#144267", "#15698C", "#0695AA", "#156275"]),
        ("NaTuRe", ["#686C20", "#1D3A1D", "#C77F42", "#532F00", "#5B0000"]),
        ("rainBOW", ["#AF3918", "#822B75", "#154BAF", "#277E9D", "#f26e0a"]),
    ],
)
def test_pal_variations_work(pal_valid, expected_output):
    assert art_pals(pal_valid) == expected_output


## direction
@pytest.mark.parametrize(
    "direction_valid, expected_output",
    [
        ("regUlAr", ["#12012E", "#144267", "#15698C", "#0695AA", "#156275"]),
        ("REv", ["#156275", "#0695AA", "#15698C", "#144267", "#12012E"]),
    ],
)
def test_direction_work(direction_valid, expected_output):
    assert art_pals(direction=direction_valid) == expected_output


def test_direction_error_message():
    invalid_directions = ("Up", "DOWN", "left", "Riiiight")
    invalid_direction = random.choice(invalid_directions).lower()
    expected_direction_error_message = f"'{invalid_direction}' is not a valid direction. `direction` must be one of: regular, reg, reverse, rev"
    with pytest.raises(ValueError, match=expected_direction_error_message):
        art_pals(direction=invalid_direction)


## randomize
def test_randomize_error_message():
    expected_randomize_error_message = "`randomize` must be True or False"
    with pytest.raises(TypeError, match=re.escape(expected_randomize_error_message)):
        art_pals(randomize="TRUE")


def test_randomize_works():
    with patch("artpack.palettes.random.shuffle") as mock_shuffle:
        art_pals(randomize=True)
        mock_shuffle.assert_called_once()


## art_pals() works by default
def test_default_art_pals_work():
    expected_output = ["#12012E", "#144267", "#15698C", "#0695AA", "#156275"]
    assert art_pals() == expected_output


## art_pals() works with a chonk n
def test_big_n_art_pals_work():
    expected_output = [
        "#af3918",
        "#a71f3d",
        "#99185c",
        "#842972",
        "#6f297e",
        "#512f8d",
        "#2046a9",
        "#1066b4",
        "#0f81b5",
        "#217fa3",
        "#358570",
        "#539035",
        "#b7a134",
        "#e89425",
        "#f26e0a",
    ]
    assert art_pals("rainbow", 15) == expected_output
