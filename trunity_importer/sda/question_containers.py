from typing import List

from trunity_3_client.builders import Answer


class QuestionType:
    MULTIPLE_CHOICE = 'multiple_choice'


class MultipleChoice:
    """
    Container for parsed MultipleChoice question.
    """

    def __init__(self, text: str, answers: List[Answer],
                 audio_file: str, test_id: str, item_position: int, item_id: int):
        self.text = text
        self.answers = answers
        self.audio_file = audio_file
        self.test_id = test_id
        self.item_position = item_position
        self.item_id = item_id  # question id in xml
