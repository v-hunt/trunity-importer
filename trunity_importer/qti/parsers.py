import warnings
from typing import List
from abc import ABC

from bs4 import BeautifulSoup

from trunity_3_client.builders import Answer


class QuestionType:
    MULTIPLE_ANSWER = 'multiple_answer'
    MULTIPLE_CHOICE = 'multiple_choice'
    ESSAY = 'essay'
    SHORT_ANSWER = 'short_answer'


class AbstractQuestionnaireParser(ABC):

    def __init__(self, soup: BeautifulSoup):
        self._soup = soup

    @classmethod
    def from_xml(cls, xml: str):
        soup = BeautifulSoup(xml, "xml")
        return cls(soup)


class ManifestParser(AbstractQuestionnaireParser):
    """
    Parser for imsmanifest.xml file.
    """

    def get_questionnaire_files(self) -> List[str]:
        """
        Get list of files with questionnaire meta information for further
        parsing within QuestionnaireMetaInfoParser class.
        """
        resource_tags = self._soup.find_all("resource")
        questionnaire_resourse_tags = [tag for tag in resource_tags if tag.find("dependency")]
        return [tag['href'] for tag in questionnaire_resourse_tags]




class QuestionnaireMetaInfoParser(AbstractQuestionnaireParser):
    """
    Parser for xml file with questionnaire meta information.
    ('-CGM_CA15E_CAR_G04EYT_006.xml', '-JY_NS17E_OA_G05U01L01D05S00_000.xml' etc.)

    You can get list of such files from ManifestParser.
    """

    def get_questionnaire_title(self) -> str:
        return self._soup.find('assessmentTest')['title']

    def get_section_title(self) -> str:
        """
        Section title. Should be chapter title the current questionnaire
        belongs to.
        """
        return self._soup.testPart.assessmentSection['title']

    def get_file_names(self) -> List[str]:
        """
        Return list of xml files with questions
        ('-CGM_CA15E_CAR_G04EYT_006.xml' for instance)
        """
        return [
            tag['href'] for tag in
            self._soup.testPart.find_all("assessmentItemRef")
        ]


class MultipleChoiceParser(AbstractQuestionnaireParser):

    def get_text(self) -> str:
        return self._soup.itemBody.div.decode_contents().strip()

    def get_answers(self) -> List[Answer]:

        answers = []
        correct_identifier = self._soup.correctResponse.value.text

        for tag in self._soup.itemBody.find_all('simpleChoice'):
            text = tag.decode_contents().strip()
            correct = True if tag['identifier'] == correct_identifier else False
            score = 1 if tag['identifier'] == correct_identifier else 0

            answers.append(
                Answer(text, correct, score)
            )

        return answers


class MultipleAnswerParser(AbstractQuestionnaireParser):

    def get_text(self) -> str:
        return self._soup.choiceInteraction.prompt.decode_contents().strip()

    def get_answers(self) -> List[Answer]:
        answers = []
        correct_identifiers = [
            tag.text for tag in self._soup.correctResponse.find_all("value")
        ]

        for tag in self._soup.itemBody.find_all('simpleChoice'):
            text = tag.decode_contents().strip()
            correct = True if tag['identifier'] in correct_identifiers else False
            score = 1 if tag['identifier'] in correct_identifiers else 0

            answers.append(
                Answer(text, correct, score)
            )

        return answers


class ShortAnswerParser(AbstractQuestionnaireParser):

    def get_text(self) -> str:
        return self._soup.itemBody.div.decode_contents().strip()

    def get_answer(self) -> Answer:

        return Answer(
            text=self._soup.correctResponse.value.text.strip(),
            correct=True,
            score=1,
        )


class EssayParser(AbstractQuestionnaireParser):

    def get_text(self) -> str:
        return self._soup.itemBody.prompt.decode_contents().strip()

    def get_correct_answer(self):
        correct_answer = ''

        rubrick_block_tag = self._soup.itemBody.rubricBlock
        if rubrick_block_tag:
            correct_answer = rubrick_block_tag.decode_contents().strip()

        return correct_answer


class Question(object):
    """
    Main parser class for xml questions.
    """

    def __init__(self, soup: BeautifulSoup):
        self._soup = soup
        self._question_type = self._get_question_type()

        self._parser = None

    @classmethod
    def from_xml(cls, xml: str):
        soup = BeautifulSoup(xml, "xml")
        return cls(soup)

    @property
    def type(self):
        return self._question_type

    @property
    def parser(self):
        if not self._parser:
            return self._get_question_parser_instance()

        else:
            return self._parser

    def __check_essay_type(self) -> bool:
        is_essay = False

        if self._soup.find("extendedTextInteraction"):
            is_essay = True

        return is_essay

    def __check_multiple_choice_type(self) -> bool:
        is_multiple_choice = False

        if self._soup.find("simpleChoice") and \
                self._soup.responseDeclaration['cardinality'] == 'single':
            is_multiple_choice = True

        return is_multiple_choice

    def __check_multiple_answer_type(self) -> bool:
        is_multiple_answer = False

        if self._soup.find("simpleChoice") and \
                self._soup.responseDeclaration['cardinality'] == 'multiple':
            is_multiple_answer = True

        return is_multiple_answer

    def __check_short_answer(self) -> bool:
        is_short_answer = False

        if self._soup.find("textEntryInteraction"):
            is_short_answer = True
        return is_short_answer

    def _get_question_type(self) -> str:

        if self.__check_essay_type():
            return QuestionType.ESSAY

        elif self.__check_multiple_choice_type():
            return QuestionType.MULTIPLE_CHOICE

        elif self.__check_multiple_answer_type():
            return QuestionType.MULTIPLE_ANSWER

        elif self.__check_short_answer():
            return  QuestionType.SHORT_ANSWER

        else:
            warnings.warn(
                "Question type is unknown or parser is not yet implemented!"
            )
            print('\tUnknown question type. XML:')
            print(str(self._soup), end='\n\n')

    def _get_question_parser_instance(self):

        parsers = {
            QuestionType.MULTIPLE_CHOICE: MultipleChoiceParser,
            QuestionType.MULTIPLE_ANSWER: MultipleAnswerParser,
            QuestionType.ESSAY: EssayParser,
            QuestionType.SHORT_ANSWER: ShortAnswerParser,
        }

        try:
            return parsers[self.type](self._soup)

        except KeyError:
            warnings.warn(
                "No parser for this question type!"
            )
