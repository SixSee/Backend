import django
import json

from apps.quiz.models import Question, QuestionChoice, Subjects
from multiprocessing import get_context
from tqdm import tqdm

django.setup()

with open("backup.json", "rb") as f:
    data = json.load(f)
collections: dict = data['__collections__']

submissions = collections['Submissions']
users = collections['Users']
admins = collections['admins']
blogs = collections['blogs']
bulletins = collections['bulletin']
competitions = collections['competition']
courses = collections['courses']
keys = collections['keys']
subjects = collections['subjects']
tests = collections['tests']
transactions = collections['transactions']

subject_map = {}


def create_subjects():
    for sub_id, subject in subjects.items():
        name = subject['name']['en_IN']
        subj = Subjects(name=name)
        subj.save()
        subject_map[sub_id] = subj


def parse_test(test_data):
    sub_map = test_data['map']
    test_data = test_data['data']

    sub_list = []
    if 'subjects' in test_data and list(test_data['subjects']):
        for sub_id in list(test_data['subjects']):
            sub_list.append(sub_map[sub_id])

    questions = test_data['questions']

    for question in questions:
        q_text = question['question']['en_IN']
        question_obj = Question(name=q_text)

        question_obj.save()
        for s in sub_list:
            question_obj.subjects.add(s)

        options = question['options']
        correct_choice = question['solution']

        for i, opt in enumerate(options):
            choice = QuestionChoice(
                question=question_obj,
                choice=opt['en_IN'],
                is_correct=(i == correct_choice)
            )
            choice.save()


def run():
    Subjects.objects.all().delete()
    Question.objects.all().delete()
    QuestionChoice.objects.all().delete()

    create_subjects()

    prepped_list = list(tests.values())
    prepped_list = [{'map': subject_map, 'data': x} for x in prepped_list]

    with get_context("spawn").Pool(processes=12) as p:
        with tqdm(total=len(tests)) as pbar:
            for _ in p.imap_unordered(parse_test, prepped_list):
                pbar.update()
