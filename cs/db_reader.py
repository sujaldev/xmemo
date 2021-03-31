import os
import json
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmemo.settings')
django.setup()
from random import randrange
from cs.models import Question
from xmemo_bot_lib.match_funcs import *


# class Question_json:
#     def __init__(self, struct):
#         self.struct = struct
#         self.heading = self.struct["question"]
#         self.child_list = self.get_child_list()
#         self.child_html = self.get_child_html()
#         self.html = self.get_html()
#
#     def get_child_list(self):
#         ans_list = self.struct["answers"]
#         child_list = []
#         for i in range(len(ans_list)):
#             child_list.append(Answer(ans_list[i]))
#
#         return child_list
#
#     def get_html(self):
#         html = f"""\
# <div class="question">
#     <p>{self.heading}</p>
#     <div></div>
# </div>
# {self.child_html}
# <div class="major-line-break"></div>"""
#         return html
#
#     def get_child_html(self):
#         child_html = ""
#         for i in range(len(self.child_list)):
#             if i != len(self.child_list) - 1:
#                 child_html += self.child_list[i].html
#             else:
#                 child_html += self.child_list[i].html.replace("""<div class="minor-line-break"></div>""", "")
#         return child_html
#
#
# class Answer:
#     def __init__(self, struct):
#         self.struct = struct
#         self.html = self.get_html()
#
#     def get_html(self):
#         html = f"""\
# <p class="main-text">
#     By ~ <bold>{self.struct["author"]}</bold><br>
#     Published on ~ <bold>{self.struct["publish_date"]}</bold><br><br>
#     <bold>Answer:</bold><br><br><br><br>
# </p>
# <pre class="code-block"><code class="lang-python">{self.struct["answer"]}</code></pre>
# <p class="main-text">Is this answer correct?</p>
# <div class="validity-check">
#     <span class="right inline-btn">Correct</span>
#     <span class="wrong inline-btn">Incorrect</span>
# </div>
# <p class="main-text" style="color: green;">{self.struct["correct_val"]} found this answer to be correct</p>
# <p class="main-text" style="color: red;">{self.struct["wrong_val"]} found this answer to be incorrect.</p>
# <div class="minor-line-break"></div>"""
#         return html
#
#
# def read_tree(json_file):
#     html = ""
#     for question in json_file:
#         html += Question(question).html
#     return html
#
#
# def read_json(date, db=db_path):
#     path = f"{db}/by-date/questions.json"
#     with open(path) as json_file:
#         json = load(json_file)[date]
#         html = read_tree(json)
#     return html
#
#
# def contains(keyword, question):
#     key = keyword.lower()
#     ques = question.lower()
#     if key in ques:
#         return True
#     else:
#         return False
#
#
# def read_by_keyword(keyword, db=db_path):
#     key_path = f"{db}/by-keyword/keywords.json"
#     date_path = f"{db}/by-date/"
#     question_list = []
#     with open(key_path) as json_file:
#         key_db = load(json_file)
#
#     for key, value in key_db.items():
#         if contains(keyword, key):
#             with open(f"{date_path}{value[:-2]}.json") as json_file:
#                 question_list.append(load(json_file)[int(value[-1])])
#
#     if not question_list:
#         raise ValueError
#
#     return read_tree(question_list)

class QuestionJson:
    def __init__(self, model_obj):
        self.model_obj = model_obj
        self.heading = self.model_obj.question
        self.child_list = json.loads(model_obj.answer)
        self.child_html = self.get_child_html()

    def get_child_html(self):
        html = ""
        for each_child in self.child_list:
            html += AnswerJson(each_child).get_html()

        return html

    def get_html(self):
        html = f"""\
<span class="question_group">
    <div class="question">
        <p>{self.heading}</p>
        <div></div>
    </div>
    {self.child_html}
    <div class="major-line-break"></div>
</span>"""

        return html


class AnswerJson:
    def __init__(self, struct):
        self.struct = struct

    def get_html(self):
        html = f"""\
<p class="main-text">
    By ~ <bold>{self.struct["author"]}</bold><br>
    Published on ~ <bold>{self.struct["publish_date"]}</bold><br><br>
    <bold>Answer:</bold><br><br><br><br>
</p>
<pre class="code-block"><code class="lang-python">{self.struct["answer"]}</code></pre>
<p class="main-text">Is this answer correct?</p>
<div id="{self.struct["unique_id"]}" class="validity-check">
    <span class="right inline-btn" onclick="update_correct_val(this)">Correct</span>
    <span class="wrong inline-btn" onclick="update_incorrect_val(this)">Incorrect</span>
</div>
<p id="{self.struct["unique_id"]}correct_indicator" class="main-text" style="color: green;">
    {self.struct["correct_val"]} found this answer to be correct.
</p>
<p id="{self.struct["unique_id"]}wrong_indicator" class="main-text" style="color: red;">
    {self.struct["wrong_val"]} found this answer to be incorrect.
</p>
<div class="minor-line-break"></div>"""
        return html


def get_html_by_date(given_date):
    date = given_date.lower()
    html = ""
    question_list = Question.objects.filter(date=date)
    if len(question_list) > 0:
        for each_question in Question.objects.filter(date=date):
            html += QuestionJson(each_question).get_html()
    else:
        return f'<p class="main-text"><bold>{date}</bold> no record for given date exists. Please try again. </p>'

    return html


def get_html_by_key(given_keywords):
    keywords = given_keywords.lower()
    html = ""
    similar_questions = [model for model in Question.objects.all() if are_similar(keywords, model.question)]
    if len(similar_questions) > 0:
        for each_question in similar_questions:
            html += QuestionJson(each_question).get_html()
        return html
    else:
        return f'\
<p class="main-text"><bold>"{given_keywords}"</bold> ' \
               'could not find any questions similar to this. Please try again.</p>'
