from unittest import TestCase

from trunity_importer.sda.question_containers import MultipleChoice, Answer
from trunity_importer.sda import question_checkers


class QuestionCheckersTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.true_anwer = Answer('some text', True, 5)
        cls.false_answer = Answer('some text', False, 0)

    def test__all_answers_has_one_true(self):
        self.assertTrue(
            question_checkers._all_answers_has_one_true(
                MultipleChoice(
                    text='some text',
                    answers=[
                        self.false_answer,
                        self.true_anwer,  # !
                        self.false_answer,
                        self.false_answer,
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
                        self.false_answer,
                        self.true_anwer,
                        self.false_answer,
                        self.true_anwer,
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
                        self.false_answer,
                        self.false_answer,
                        self.false_answer,
                        self.false_answer,
                    ],
                    audio_file='audio.mp3',
                    test_id='123',
                    item_position=1,
                    item_id=12345,
                )
            ),
        )

