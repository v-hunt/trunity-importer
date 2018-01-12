from typing import List

from trunity_3_client.builders import Answer


class QuestionType:
    MULTIPLE_CHOICE = 'multiple_choice'
    MULTIPLE_ANSWER = 'multiple_answer'
    ESSAY = 'essay'


class Question:

    def __init__(self, type_: str, text: str,  audio_file: str,
                 test_id: str, item_position: int, item_id: int):
        self.text = text
        self.audio_file = audio_file
        self.test_id = test_id
        self.item_position = item_position
        self.item_id = item_id  # question id in xml

        self.type = type_


class MultipleChoice(Question):
    """
    Container for parsed MultipleChoice question.
    """

    def __init__(self, text: str, answers: List[Answer],
                 audio_file: str, test_id: str, item_position: int, item_id: int):

        super(MultipleChoice, self).__init__(
            type_=QuestionType.MULTIPLE_CHOICE,
            text=text,
            audio_file=audio_file,
            test_id=test_id,
            item_position=item_position,
            item_id=item_id,
        )

        self.answers = answers


class MultipleAnswer(Question):
    """
    Container for parsed MultipleAnswer question.
    """

    def __init__(self, text: str, answers: List[Answer],
                 audio_file: str, test_id: str, item_position: int, item_id: int):

        super(MultipleAnswer, self).__init__(
            type_=QuestionType.MULTIPLE_ANSWER,
            text=text,
            audio_file=audio_file,
            test_id=test_id,
            item_position=item_position,
            item_id=item_id,
        )

        self.answers = answers


class Essay(Question):
    """
    Container for parsed MultipleChoice question.
    """

    def __init__(self, text: str, correct_answer: str,
                 audio_file: str, test_id: str, item_position: int,
                 item_id: int):

        super(Essay, self).__init__(
            type_=QuestionType.ESSAY,
            text=text,
            audio_file=audio_file,
            test_id=test_id,
            item_position=item_position,
            item_id=item_id,
        )

        self.correct_answer = correct_answer

