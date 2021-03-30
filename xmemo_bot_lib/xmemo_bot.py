import os
import json
import django
import requests
from datetime import date
from .match_funcs import *
from dotenv import load_dotenv
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmemo.settings')
django.setup()
from cs.models import Question
from cs.views import is_valid_date


def get_date():
    return date.today().strftime("%d %B %Y")


class XmemoBot:
    if 'on_heroku' not in os.environ:
        load_dotenv()
    token = os.environ.get("bot_api_token")  # bot token
    private_token = os.environ.get("private_token")
    base_url = f"https://api.telegram.org/bot{token}"

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
        similar_questions = []

        exact_match = False

        for model in Question.objects.all():
            if model.question.lower() == question:
                self.send_msg(
                    "This question already exists in, adding to existing question.",
                    chat_id
                )
                similar_questions = [model]
                exact_match = True
            elif are_similar(question, model.question):
                similar_questions.append(model)

        if len(similar_questions) > 0:
            # QUERY 2 (CONDITIONAL)
            if not exact_match:
                self.send_msg(
                    "Check if any of these are the same as your question and are just written differently? "
                    "If yes just type the number written before the number, or just say no.",
                    chat_id
                )

                i = 0
                for each_question in similar_questions:
                    self.send_msg(f"{i}: {each_question.question}", chat_id)
                    i += 1

                response: str = self.get_last_msg(offset)[-1]["message"]["text"]
                offset += 1
            else:
                response: str = "0"

            # User responded with a number hence adding to an existing question
            if response.isnumeric():

                self.send_msg(
                    "Please give your answer now: ",
                    chat_id
                )

                answer = self.get_last_msg(offset)[-1]["message"]["text"]
                offset += 1
                answer_struct["answer"] = answer

                # get the existing answer list from database and add new answer in it
                question_obj = similar_questions[int(response)]
                print(question_obj)
                old_answer_list = json.loads(question_obj.answer)
                old_answer_list.append(answer_struct)
                print(old_answer_list)
                question_obj.answer = json.dumps(old_answer_list)
                print(question_obj.answer)
                question_obj.save()

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

            self.send_msg(
                "Please give your answer now: ",
                chat_id
            )

            answer = self.get_last_msg(offset)[-1]["message"]["text"]
            offset += 1
            answer_struct["answer"] = answer
            question_obj = Question(question=question, date=response, answer=json.dumps([answer_struct]))
            question_obj.save()

            self.send_msg(
                "Database was updated successfully!",
                chat_id
            )

            return
        else:
            self.send_msg(
                "This is not a valid date, cancelling operation. Please try again!",
                chat_id
            )

    def handle_response(self, text, chat_id):
        if match(text, "add question"):
            self.add_question(chat_id)
