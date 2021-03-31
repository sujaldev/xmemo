import os
import json
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmemo.settings')
django.setup()
from random import randrange
from cs.models import Question
from xmemo_bot_lib.match_funcs import *


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
        return f'<p class="main-text" style="margin-bottom: 85vh;"><bold>{date}</bold>' \
               ' no record for given date exists.Please try again. </p>'

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
<p class="main-text" style="margin-bottom: 85vh;"><bold>"{given_keywords}"</bold> ' \
               'could not find any questions similar to this. Please try again.</p>'
