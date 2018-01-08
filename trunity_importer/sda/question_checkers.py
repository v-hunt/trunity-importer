"""
Some items in XMl are "dirty". So we need to check questions for correctness.
"""
from warnings import warn
from trunity_importer.sda.question_containers import MultipleChoice, QuestionType


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
        warn(
            "Question with id={} has not exactly one True answer!".format(
                question.item_id)
        )
        return False


def correct_question(question: MultipleChoice) -> bool:
    """
    Check question is correct or not.
    """
    if question.type == QuestionType.MULTIPLE_CHOICE:
        return _all_answers_has_one_true(question)

    else:
        # for all other questions we assume they are correct:
        return True
