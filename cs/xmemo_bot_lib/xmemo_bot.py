import os
import json
import requests
from datetime import date
from xmemo import settings
from dotenv import load_dotenv
from ..xmemo_bot_lib.match_funcs import *
from ..views import is_valid_date

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
        self.send_msg("Please enter the question: ", chat_id)
        offset = self.get_msg_list()[-1]["update_id"]  # get the last offset value
        message = self.get_last_msg(offset)[-1]  # get reply for the question
        question = message["message"]["text"]  # the reply
        author = f'{message["message"]["chat"]["first_name"]} {message["message"]["chat"]["last_name"]}'

        answer_struct = {
            "author": author,
            "publish_date": get_date(),
            "answer": "",
            "correct_val": 0,
            "wrong_val": 0
        }

        offset += 1  # increment offset to receive further replies

        # -------------------------------------------------------------
        # verify if any existing records collide with the given question
        self.send_msg(
            "Are any of these questions the same as your question? (Type the question number if yes or just say no): ",
            chat_id
        )
        # get the keyword database
        with open(f"{db_path}/by-keyword/keywords.json") as keywords:
            key_db = json.load(keywords)
        # initialize an empty list to store similar questions which are the keys in the dictionary stored in keyword db
        similar_questions = []
        question_number = 0  # keep track of the question number to later access keys from the similar_questions list
        # loop over the keyword db and check for similar questions
        for existing_question, question_location in key_db.items():
            if are_similar(question, existing_question):
                similar_questions.append(existing_question)
                self.send_msg(f"{question_number}:  {existing_question}", chat_id)
            question_number += 1

        if len(similar_questions) == 0:
            # If no similar questions found apologize and move on...
            self.send_msg("I couldn't find any similar questions adding as new question.", chat_id)
        else:
            # if similar records found verify if any any are actually similar
            resp = self.get_last_msg(offset)[-1]["message"]["text"]  # reply for which question is similar
            offset += 1

            # if the user thinks a question is similar...
            if resp.lower() != "no":
                question_key = similar_questions[int(resp)]
                file = key_db[question_key][:-2]
                list_pos = int(key_db[question_key][-2:])

                # Display gathered information till now
                self.send_msg(f"\"{question_key}\" is selected now.", chat_id)
                self.send_msg(f"{author} is the author.", chat_id)
                self.send_msg(f"Please enter your answer now: ", chat_id)

                # get the answer
                answer = self.get_last_msg(offset)[-1]["message"]["text"]
                offset += 1

                # update the answer struct
                answer_struct["answer"] = answer

                # open the database and update it
                with open(f"{db_path}/by-date/questions.json") as existing_db_file:
                    existing_db = json.load(existing_db_file)
                    existing_db[file][list_pos]["answers"].append(answer_struct)

                with open(f"{db_path}/by-date/questions.json", "w") as old_db:
                    json.dump(existing_db, old_db, indent=2, sort_keys=True)
                print(True)

                self.send_msg("Database updated successfully.", chat_id)

                return

        self.send_msg("On which date was this question assigned? Use this format (6 september 2020)", chat_id)
        question_date = self.get_last_msg(offset)[-1]["message"]["text"]
        offset += 1

        self.send_msg("Please enter your answer now: ", chat_id)
        answer = self.get_last_msg(offset)[-1]["message"]["text"]

        file_path = f"{db_path}/by-date/questions.json"
        key_db_path = f"{db_path}/by-keyword/keywords.json"

        answer_struct["answer"] = answer

        question_struct = {
            "question": question,
            "answers": [
                answer_struct
            ]
        }

        if is_valid_date(question_date):
            with open(file_path) as existing_db_file:
                existing_db = json.load(existing_db_file)
            # if question_date not in existing_db.keys():
            #     existing_db[question_date] = []
            if question not in existing_db.keys():
                existing_db[question_date] = []
            existing_db[question_date].append(question_struct)
            question_index = len(existing_db) - 1
            with open(file_path, "w") as old_db:
                json.dump(existing_db, old_db, indent=2, sort_keys=True)
            with open(key_db_path) as old_key_db_file:
                old_key_db = json.load(old_key_db_file)
            old_key_db[question] = f"{question_date} {question_index}"
            with open(key_db_path, "w+") as old_key_db_file:
                json.dump(old_key_db, old_key_db_file, indent=2, sort_keys=True)

            self.send_msg("Database updated successfully.", chat_id)
        else:
            self.send_msg("This is not a valid date... Please try again.", chat_id)

    def handle_response(self, text, chat_id):
        if match(text, "add question"):
            self.add_question(chat_id)

    def report_error(self, error_msg="Fixed Error"):
        if self.reported_error:
            self.send_msg(error_msg, self.private_token)
        elif self.reported_error and self.fixed_error:
            self.reported_error = False
            self.send_msg(error_msg, self.private_token)
