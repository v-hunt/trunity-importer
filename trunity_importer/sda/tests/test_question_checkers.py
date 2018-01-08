from unittest import TestCase

from trunity_importer.sda.question_containers import MultipleChoice, Answer
from trunity_importer.sda import question_checkers


class QuestionCheckersTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test__all_answers_has_one_true(self):
        true_anwer = Answer('some text', True, 5)
        false_answer = Answer('some text', False, 0)

        self.assertTrue(
            question_checkers._all_answers_has_one_true(
                MultipleChoice(
                    text='some text',
                    answers=[
                        false_answer,
                        true_anwer,  # !
                        false_answer,
                        false_answer,
                    ],
                    audio_file='audio.mp3',
                    test_id='123',
                    item_position=1,
                    item_id=12345,
                )
            ),
        )

        self.assertFalse(
            question_checkers._all_answers_has_one_true(
                MultipleChoice(
                    text='some text',
                    answers=[
                        false_answer,
                        true_anwer,  # !
                        false_answer,
                        true_anwer,
                    ],
                    audio_file='audio.mp3',
                    test_id='123',
                    item_position=1,
                    item_id=12345,
                )
            ),
        )

        self.assertFalse(
            question_checkers._all_answers_has_one_true(
                MultipleChoice(
                    text='some text',
                    answers=[
                        false_answer,
                        false_answer,  # !
                        false_answer,
                        false_answer,
                    ],
                    audio_file='audio.mp3',
                    test_id='123',
                    item_position=1,
                    item_id=12345,
                )
            ),
        )

