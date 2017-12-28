import os
from unittest import TestCase

from bs4 import BeautifulSoup
from trunity_3_client.builders import Answer

from trunity_importer.sda.parser import Parser, QuestionType, MultipleChoice


DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),  # current file dir
    'data'
)


class ParserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        assert os.path.isdir(DATA_DIR), "Data directory isn't exist!"

        with open(
                os.path.join(DATA_DIR, 'multiple_choice.xml')
        ) as fo:
            cls.multiple_choice_xml = fo.read()

    def test__get_multiple_choice(self):
        tag = BeautifulSoup(self.multiple_choice_xml, "xml")
        question = Parser._get_multiple_choice(tag)

        self.assertEqual(
            question.text,
            "<p>Text</p>",
            "Wrong text for MultipleChoice question!"
        )

        self.assertListEqual(
            question.answers,
            [
                Answer("<p>Answer 1</p>", False, 0, "<p>Feedback 1</p>"),
                Answer("<p>Answer 2</p>", True, 1, "<p>Feedback 2</p>"),
                Answer("<p>Answer 3</p>", False, 0, "<p>Feedback 3</p>"),
            ],
            "Wrong answer for MultipleChoice question!"
        )

        self.assertEqual(
            question.audio_file,
            "12345.mp3",
            "Wrong audio file for MultipleChoice question!"
        )

    def test_get_questions(self):
        parser = Parser(self.multiple_choice_xml)

        for question in parser.get_questions():
            self.assertEqual(
                question['type'],
                QuestionType.MULTIPLE_CHOICE,
            )
            self.assertTrue(
                isinstance(question['question'], MultipleChoice),
            )
