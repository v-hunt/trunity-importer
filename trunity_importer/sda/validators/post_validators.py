"""
Some items in XMl are "dirty". So we need to check questions for correctness.
Thise validators check questions after parsing xml and before uploading
them to Trunity.
"""
from warnings import warn
from trunity_importer.sda.question_containers import (
    Question,
    MultipleChoice,
    MultipleAnswer,
    QuestionType,
)
from trunity_importer.sda.warnings import warnings


def _all_answers_has_one_true(question: MultipleChoice) -> bool:
    """
    Return True if there are only one answer with True. False otherwise.
    """
    count_true = 0

    for answer in question.answers:
        if answer.correct is True:
            count_true += 1

    if count_true == 1:
        return True
    else:
        warnings.add(
            item_id=question.item_id,
            message="Question has not exactly one True answer!",
        )

        return False


def _all_answers_are_not_false(question: MultipleAnswer) -> bool:
    """
    Return False if there all answers with True. False otherwise.
    """
    count_true = 0

    for answer in question.answers:
        if answer.correct is True:
            count_true += 1

    if count_true >= 1:
        return True
    else:
        warnings.add(
            item_id=question.item_id,
            message="Question has all False answers!"
        )

        return False


def validate(question: Question) -> bool:
    """
    Check question is correct or not.
    """
    if question.type == QuestionType.MULTIPLE_CHOICE:
        return _all_answers_has_one_true(question)

    elif question.type == QuestionType.MULTIPLE_ANSWER:
        return _all_answers_are_not_false(question)

    else:
        # for all other questions we assume they are correct:
        return True
