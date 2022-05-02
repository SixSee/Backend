from .models import Quiz, Question
import random


def get_random_questions_for_quiz(quiz_obj: Quiz):
    subject_ids = quiz_obj.subjects.values_list('id').all()
    question_set = []
    dirty_question = (Question.objects.
                      filter(is_approved=True,
                             subjects__in=subject_ids)
                      .distinct()
                      .all())
    Flag = 0
    # import ipdb; ipdb.set_trace()
    for question in dirty_question:
        subjects = question.subjects.values_list('id').all()
        for sub in subjects:
            if sub[0] not in subject_ids:
                Flag = True
            Flag = False
        if Flag:
            continue
        question_set.append(question.id)

    random.shuffle(question_set)
    if quiz_obj.no_of_questions < 10:
        raise Exception("At least 10 question are required for a quiz")
    return question_set[:quiz_obj.no_of_questions]
