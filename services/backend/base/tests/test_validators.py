import pytest
from base.validators import MaximumLengthValidator


@pytest.mark.parametrize(
    'max_length,expected_text',
    [
        (1, 'Your password must contain at most 1 character.'),
        (64, 'Your password must contain at most 64 characters.'),
        (128, 'Your password must contain at most 128 characters.'),
    ],
)
def test_max_length_validator_help_text(max_length, expected_text):
    """
    Verify help text formatting for various max_length values.
    """

    validator = MaximumLengthValidator(max_length=max_length)
    help_text = validator.get_help_text()

    assert expected_text in help_text
