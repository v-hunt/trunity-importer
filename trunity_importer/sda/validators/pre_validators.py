"""
Validators that validate questions before parsing.
They validate "item" tags from Xml_Export_DDDD.xml file before moving them
to parsing process.
"""
from bs4 import Tag

from trunity_importer.sda.warnings import warnings


def _distractors_tag_exist(item_tag: Tag) -> bool:
    """
    Check if "distractors" exist. This tag is container for
    MultipleChoice answer options.
    """
    distractors_tag = item_tag.distractors

    if not distractors_tag:
        warnings.add(
            item_id=item_tag['id'],
            message="No distractors tag found!"
        )

    return bool(distractors_tag)


def _display_text_tag_exist(item_tag: Tag) -> bool:
    """
    "display_text" tag is a container for question text.
    """
    display_text_tag = item_tag.display_text

    if not display_text_tag:
        warnings.add(
            item_id=item_tag['id'],
            message="No display_text tag found!"
        )

    return bool(display_text_tag)


def _rubric_tag_exist(item_tag: Tag) -> bool:
    """
    "rubric" tag is a container for correct answer in Essay questions.
    """
    rubric_text_tag = item_tag.rubric_text

    if not rubric_text_tag:
        warnings.add(
            item_id=item_tag['id'],
            message="No rubric_text tag found!"
        )

    return bool(rubric_text_tag)


def validate(item_tag: Tag) -> bool:
    validators = [
        _display_text_tag_exist,
    ]

    if item_tag['type'] == 'MultipleChoice':
        validators.append(_distractors_tag_exist)

    elif item_tag['type'] == 'ConstructedResponse':
        validators.append(_rubric_tag_exist)

    validators_applied = [validator(item_tag) for validator in validators]

    if not all(validators_applied):
        return False

    # question types that are not validated here a valid by default:
    return True
