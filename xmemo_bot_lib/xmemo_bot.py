import os
import json
import requests
from datetime import date
from xmemo import settings
from dotenv import load_dotenv
from ..xmemo_bot_lib.match_funcs import *
from ..views import is_valid_date
from ..models import Question


db_path = os.path.join(settings.STATIC_ROOT, 'db')


def get_date():
    return date.today().strftime("%d %B %Y")


class XmemoBot:
    if 'on_heroku' not in os.environ:
        load_dotenv()
    token = os.environ.get("bot_api_token")  # bot token
    private_token = os.environ.get("private_token")
    base_url = f"https://api.telegram.org/bot{token}"

    def __init__(self):
        self.reported_error = False
        self.fixed_error = True

    def get_msg_list(self):
        url = f"{self.base_url}/getUpdates"
        r = requests.get(url)

        # server check
        if r.status_code == 200:
            message_list = json.loads(r.content)["result"]
        else:
            return self.get_msg_list()  # in case server didn't respond try again

        # update-object length check
        if len(message_list) > 0:  # best case scenario
            return message_list
        else:  # in case server responds with an empty list try again one time
            new_url = f"{self.base_url}/getUpdates"
            new_list = json.loads(requests.get(new_url).content)["result"]

            # in case still no new messages keep trying again
            if len(new_list) > 0:
                return new_list
            else:
                return self.get_msg_list()

    def get_last_msg(self, offset, timeout=100):
        url = f"{self.base_url}/getUpdates?timeout={timeout}&offset={offset+1}"
        r = requests.get(url)

        if r.status_code == 200:
            message_list = json.loads(r.content)["result"]
        else:
            return self.get_last_msg(offset, 200)

        if len(message_list) > 0:
            return message_list
        else:
            new_list = self.get_last_msg(offset, 200)
            if len(new_list) > 0:
                return new_list
            else:
                return self.get_last_msg(offset, 300)

    def send_msg(self, text, chat_id):
        url = f"{self.base_url}/sendMessage?text={text}&chat_id={chat_id}"
        r = requests.get(url)
        if r.status_code == 200:
            return json.loads(r.content)["result"]
        else:
            self.send_msg(text, chat_id)

    def add_question(self, chat_id):

        # QUERY 1
        self.send_msg("Please enter the question: ", chat_id)
        offset = self.get_msg_list()[-1]["update_id"]  # get the last offset value
        response: dict = self.get_last_msg(offset)[-1]["message"]  # get reply for the question
        question = response["text"]  # the reply
        author = f'{response["chat"]["first_name"]} {response["chat"]["last_name"]}'

        answer_struct = {
            "author": author,
            "publish_date": get_date(),
            "answer": "",
            "correct_val": 0,
            "wrong_val": 0
        }

        offset += 1  # increment offset to receive further replies

        # get a list of all similar questions from the database
        similar_questions = [
            model for model in Question.objects.all() if are_similar(question, model.question)
        ]

        if len(similar_questions) > 0:
            # QUERY 2 (CONDITIONAL)
            self.send_msg(
                "Check if any of these are the same as your question and are just written differently? "
                "If yes just type the number written before the number, or just say no.",
                chat_id
            )

            response: str = self.get_last_msg(offset)[-1]["message"]["text"]
            offset += 1

            # User responded with a number hence adding to an existing question
            if response.isnumeric():
                answer = self.get_last_msg(offset)[-1]["message"]["text"]
                offset += 1
                answer_struct["answer"] = answer

                # get the existing answer list from database and add new answer in it
                question_obj = similar_questions[int(response)]
                old_answer_list = json.loads(question_obj.answer)
                question_obj.answer = json.dumps(old_answer_list.append(answer_struct))

                # inform user after updating database
                self.send_msg(
                    "Database was updated successfully!",
                    chat_id
                )
                return  # break function as data base has been updated successfully

            # User responded no hence adding as to a new question
            elif response.lower() == "no":
                # Not breaking function because operation isn't complete yet
                self.send_msg(
                    "Ok, Adding this as a new question",
                    chat_id
                )
            else:
                # let the user know this wasn't a valid response
                self.send_msg(
                    "This was not a valid response, hence I have to cancel this operation. Please try again.",
                    chat_id
                )
                # since the user didn't respond with one of these responses [0,1,...,9, no] breaking function
                return

        # QUERY 2 CONDITIONAL
        self.send_msg(
            "Please tell me the date this question was assigned (Doesn't have to be accurate)? \n"
            "Use this format (DD month_name YYYY) eg: (25 march 2021)",
            chat_id
        )

        response = self.get_last_msg(offset)[-1]["message"]["text"]
        offset += 1
        if is_valid_date(response):
            answer = self.get_last_msg(offset)[-1]["message"]["text"]
            offset += 1
            answer_struct["answer"] = answer
            question_obj = Question(question=question, date=response, answer=answer_struct)
            question_obj.save()

            self.send_msg(
                "Database was updated successfully!",
                chat_id
            )

    def handle_response(self, text, chat_id):
        if match(text, "add question"):
            self.add_question(chat_id)

    def report_error(self, error_msg="Fixed Error"):
        if self.reported_error:
            self.send_msg(error_msg, self.private_token)
        elif self.reported_error and self.fixed_error:
            self.reported_error = False
            self.send_msg(error_msg, self.private_token)