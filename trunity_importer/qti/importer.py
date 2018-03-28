from zipfile import ZipFile

from trunity_3_client.clients.auth import initialize_session_from_creds
from trunity_3_client.clients.endpoints import (
    TopicsClient,
    FilesClient,
)
from trunity_3_client.builders import Questionnaire


from trunity_importer.qti.parsers import (
    QuestionType,
    Question,
    ManifestParser,
    QuestionnaireMetaInfoParser,
)
from bs4 import BeautifulSoup

from trunity_importer.utils import create_qst_pool
from trunity_importer.qti.handlers import AdobeFlashHandler


class Importer(object):
    """
    Import question pools from QTI XML file to Trunity.
    """

    def __init__(self, username: str, password: str, book_id: int,
                 path_to_zip: str):

        self._book_id = book_id
        self._zip_file = ZipFile(path_to_zip)
        self.t3_session = initialize_session_from_creds(username, password)

        # key: topic_title, value: topic_id
        self._topics = {}
        self._cur_topic_id = None

        self._topic_client = TopicsClient(self.t3_session)
        self._files_client = FilesClient(self.t3_session)

        # we need json content type for uploading questionnaires:
        self.t3_json_session = initialize_session_from_creds(
            username, password, content_type='application/json')

    def _upload_images(self, question_soup: BeautifulSoup):
        """
        Upload all images to Trunity and replace src attributes with new urls.
        """
        for img in question_soup.find_all("img"):
            file_obj = self._zip_file.open('testitems/' + img['src'])
            cdn_file_url = self._files_client.list.post(file_obj=file_obj)
            img['src'] = cdn_file_url

        return question_soup

    def _upload_mp3_file(self, name: str) -> str:
        print("Uploading mp3 for question...", end='')

        src = 'testitems/' + name
        file_obj = self._zip_file.open(src)
        cdn_file = self._files_client.list.post(file_obj=file_obj)

        print("\t\t Success!")
        return cdn_file

    def handle_flash_audio(self, soup):
        handler = AdobeFlashHandler(soup)

        player_template = """ 
        <p>
            <audio controls>
              <source src="{mp3_source}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        </p>
        """

        if handler.audio_file_name:
            cdn_mp3 = self._upload_mp3_file(handler.audio_file_name)
            player_template = player_template.format(mp3_source=cdn_mp3)
            handler.replace_flash_tag(markup=player_template)
            soup = handler.soup

        return soup

    def _import_question_pool(self, questionnaire_meta_xml: str, topic_id: int):
        questionnaire = Questionnaire(self.t3_json_session)

        meta_info = QuestionnaireMetaInfoParser.from_xml(questionnaire_meta_xml)
        topic = meta_info.get_section_title()  # TODO: implement creating topics

        if topic not in self._topics:
            print("Creating new topic: {}".format(topic), end='')
            self._cur_topic_id = self._topic_client.list.post(self._book_id, topic, topic_id)
            self._topics[topic] = self._cur_topic_id
            print('\t\t Done!')

        # xml files with questions for questionnaire:
        question_xml_files = meta_info.get_file_names()

        for xml_file in question_xml_files:  # TODO: extract it
            xml = self._zip_file.open('testitems/' + xml_file)
            question = Question.from_xml(xml)
            question._soup = self.handle_flash_audio(question._soup)
            question._soup = self._upload_images(question._soup)

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
                    correct_answer=question.parser.get_correct_answer(),
                    score=1,
                )

            xml.close()

        questionnaire_id = create_qst_pool(
            self.t3_session, self._book_id,
            content_title=meta_info.get_questionnaire_title(),
            topic_id=self._cur_topic_id,
        )
        questionnaire.upload(questionnaire_id)

    def perform_import(self, topic_id=None):

        questionnaire_files = ManifestParser.from_xml(
            self._zip_file.open('imsmanifest.xml')
        ).get_questionnaire_files()

        for questionnaire_file in questionnaire_files:
            questionnaire_meta_xml = self._zip_file.open(questionnaire_file)
            self._import_question_pool(questionnaire_meta_xml, topic_id)
            questionnaire_meta_xml.close()

