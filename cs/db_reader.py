import os
from xmemo import settings
from json import load

db_path = os.path.join(settings.STATIC_ROOT, 'db/by-date/')


class Question:
    def __init__(self, struct):
        self.struct = struct
        self.heading = self.struct["question"]
        self.child_list = self.get_child_list()
        self.child_html = self.get_child_html()
        self.html = self.get_html()

    def get_child_list(self):
        ans_list = self.struct["answers"]
        child_list = []
        for i in range(len(ans_list)):
            child_list.append(Answer(ans_list[i]))

        return child_list

    def get_html(self):
        html = f"""\
<div class="question">
    <p>{self.heading}</p>
    <div></div>
</div>
{self.child_html}
<div class="major-line-break"></div>"""
        return html

    def get_child_html(self):
        child_html = ""
        for i in range(len(self.child_list)):
            if i != len(self.child_list) - 1:
                child_html += self.child_list[i].html
            else:
                child_html += self.child_list[i].html.replace("""<div class="minor-line-break"></div>""", "")
        return child_html


class Answer:
    def __init__(self, struct):
        self.struct = struct
        self.html = self.get_html()

    def get_html(self):
        html = f"""\
<p class="main-text">
    By ~ <bold>{self.struct["author"]}</bold><br>
    Published on ~ <bold>{self.struct["publish_date"]}</bold><br><br>
    <bold>Answer:</bold><br><br><br><br>
</p>
<pre class="code-block"><code class="lang-python">{self.struct["answer"]}</code></pre>
<p class="main-text">Is this answer correct?</p>
<div class="validity-check">
    <span class="right inline-btn">Correct</span>
    <span class="wrong inline-btn">Incorrect</span>
</div>
<p class="main-text">{self.struct["correct_val"]} found this answer to be correct<br><br>
{self.struct["wrong_val"]} found this answer to be incorrect.
<div class="minor-line-break"></div>"""
        return html


def read_tree(json_file):
    html = ""
    for question in json_file:
        html += Question(question).html
    return html


def read_json(file_name, db=db_path):
    path = f"{db}{file_name}.json"
    with open(path) as json_file:
        json = load(json_file)
        html = read_tree(json)
    return html
