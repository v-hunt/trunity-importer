from zipfile import ZipFile

from trunity_3_client.clients.auth import initialize_session_from_creds
from trunity_3_client.clients.endpoints import (
    ContentsClient,
    ContentType,
    ResourceType
)
from trunity_3_client.builders import Questionnaire


from trunity_importer.qti.parser import (
    QuestionType,
    Question,
    ManifestParser,
    QuestionnaireMetaInfoParser,
)


def create_qst_pool(session, site_id, content_title):
    cnt_client = ContentsClient(session)
    return cnt_client.list.post(
        site_id=site_id,
        content_title=content_title,
        content_type=ContentType.QUESTIONNAIRE,
        resource_type=ResourceType.QUESTION_POOL,
    )


class Importer(object):
    """
    Import question pools from QTI XML file to Trunity.
    """

    def __init__(self, username: str, password: str, book_id: int,
                 path_to_zip: str):

        self._book_id = book_id
        self._zip_file = ZipFile(path_to_zip)
        self.t3_session = initialize_session_from_creds(username, password)

        # we need json content type for uploading questionnaires:
        self.t3_json_session = initialize_session_from_creds(
            username, password, content_type='application/json')

    def _import_question_pool(self, questionnaire_meta_xml: str):
        questionnaire = Questionnaire(self.t3_json_session)

        meta_info = QuestionnaireMetaInfoParser.from_xml(questionnaire_meta_xml)
        topic = meta_info.get_section_title()  # TODO: implement creating topics

        # xml files with questions for questionnaire:
        question_xml_files = meta_info.get_file_names()

        for xml_file in question_xml_files:  # TODO: extract it
            xml = self._zip_file.open('testitems/' + xml_file)
            question = Question.from_xml(xml)

            if question.type == QuestionType.MULTIPLE_CHOICE:

                questionnaire.add_multiple_choice(
                    text=question.parser.get_text(),
                    answers=question.parser.get_answers(),
                )

            elif question.type == QuestionType.MULTIPLE_ANSWER:

                questionnaire.add_multiple_answer(
                    text=question.parser.get_text(),
                    answers=question.parser.get_answers(),
                )

            elif question.type == QuestionType.ESSAY:

                questionnaire.add_essay(
                    text=question.parser.get_text(),
                    correct_answer="",  # we have no answer for essays in xml
                    score=1,
                )

            xml.close()

        questionnaire_id = create_qst_pool(
            self.t3_session, self._book_id,
            content_title=meta_info.get_questionnaire_title()
        )
        questionnaire.upload(questionnaire_id)

    def perform_import(self):

        questionnaire_files = ManifestParser.from_xml(
            self._zip_file.open('imsmanifest.xml')
        ).get_questionnaire_files()

        for questionnaire_file in questionnaire_files:
            questionnaire_meta_xml = self._zip_file.open(questionnaire_file)
            self._import_question_pool(questionnaire_meta_xml)
            questionnaire_meta_xml.close()

