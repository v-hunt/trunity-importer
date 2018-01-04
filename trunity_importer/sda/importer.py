from zipfile import ZipFile

from trunity_3_client.clients.auth import initialize_session_from_creds
from trunity_3_client.clients.endpoints import (
    TopicsClient,
    FilesClient,
)
from trunity_3_client.builders import Questionnaire


from trunity_importer.sda.parser import Parser, QuestionType
from trunity_importer.sda.question_handler import QuestionHandler
from trunity_importer.utils import create_qst_pool


class Importer(object):
    """
    Import Science Dimensions Assessments to Trunity.
    """

    def __init__(self, username: str, password: str, book_id: int,
                 path_to_zip: str):

        self._book_id = book_id
        self._zip_file = ZipFile(path_to_zip)
        self.t3_session = initialize_session_from_creds(username, password)

        self._topic_client = TopicsClient(self.t3_session)

        # we need json content type for uploading questionnaires:
        self.t3_json_session = initialize_session_from_creds(
            username, password, content_type='application/json')

        self._question_handler = QuestionHandler(
            files_client=FilesClient(self.t3_session),
            zip_file=self._zip_file
        )

    def _get_xml_file_name(self):
        """
        Pattern is XML_Export_DDDD.xml
        """
        for file_name in self._zip_file.namelist():
            if file_name.startswith('XML_Export') and file_name.endswith('.xml'):
                return file_name

    def questionnaire_name(self) -> str:
        """
        Construct questionnaire name from zip file full path.

        Example:
            if full_path is '/home/username/bla-bla.zip',
            the result will be 'bla-bla'
        """
        file_name = self._zip_file.filename
        return file_name.split("/")[-1].replace('.zip', '')

    def perform_import(self):

        xml_file_name = self._get_xml_file_name()
        with self._zip_file.open(xml_file_name) as file_obj:
            xml = file_obj.read()

        parser = Parser(xml)

        questionnaires = {}  # key: test_id, value: Questionnaire inst

        def get_or_create_questionnaire(test_id: str) -> Questionnaire:
            if test_id in questionnaires:
                return questionnaires[test_id]

            else:
                questionnaire = Questionnaire(self.t3_json_session)
                questionnaires[test_id] = questionnaire
                return questionnaire

        for question in parser.get_questions():
            # handle question (upload media files etc..):
            question['question'] = self._question_handler.handle(
                question['question']
            )

            test_id = question['question'].test_id

            questionnaire = get_or_create_questionnaire(test_id)

            if question['type'] == QuestionType.MULTIPLE_CHOICE:
                questionnaire.add_multiple_choice(
                    question['question'].text,
                    question['question'].answers,
                )

        # uploading questionnaires:
        for test_id, questionnaire in questionnaires.items():

            title = parser.get_questionnaire_title(test_id)

            if title == "":
                title = "NO TITLE!"

            topic_id = input(
                "\nEnter the topic id you want the QP be attached to. "
                "Leave blank for the root topic\n"
                "The title of QP: {}\n".format(title)
            ).strip()
            topic_id = topic_id if topic_id != "" else None

            questionnaire_id = create_qst_pool(
                session=self.t3_session,
                site_id=self._book_id,
                content_title=title,
                topic_id=topic_id,
            )

            questionnaire.upload(questionnaire_id)
