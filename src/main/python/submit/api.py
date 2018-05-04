from collections import defaultdict
from pony import orm

from . import convert
from .models import Student, Assignment, Submission, Image


class WordLimitError(Exception):
    pass


class ClosedAssignmentError(Exception):
    pass


@orm.db_session()
def register_assignment(description, due_date, word_limit=None, nimages=0):
    assignment = Assignment(description=description,
                            due_date=due_date,
                            nimages=nimages)
    if word_limit is not None:
        assignment.word_limit = word_limit
    orm.commit()
    return assignment.id


@orm.db_session()
def register_student_list(students):
    for student_info in students:
        Student(student_id=student_info['id'],
                name=student_info['name'],
                email=student_info['email'])


@orm.db_session()
def get_student_list():
    students = orm.select(s for s in Student)
    return [s.to_dict() for s in students]


@orm.db_session()
def register_submission(student_id, assignment_id, text, images):
    assignment = Assignment[assignment_id]

    if not assignment.isopen:
        raise ClosedAssignmentError('Assignment is closed')
    if assignment.word_limit:
        textlen = len([w for w in text.split() if w not in ['#', '##', '###']])
        if textlen > assignment.word_limit:
            raise WordLimitError(
                'Trying to submit {} words for assignment with word limit {}'
                .format(textlen, assignment.word_limit))

    student = Student[student_id]

    if student.has_submitted(assignment):
        raise ClosedAssignmentError(
            'Student has already submitted for this assignment')

    submission = Submission(text=text,
                            assignment=assignment,
                            student=student)
    if assignment.nimages > 0:
        for name, im in images.items():
            Image(submission=submission,
                  name=name,
                  image=im.stream.read())

    return student.name, student.student_id


@orm.db_session()
def merge_student_submissions(student_id, assignment_ids,
                              target='html', url='http://127.0.0.1:5000'):
    student = Student[student_id]
    text = defaultdict(lambda i: 'Not submitted')
    if assignment_ids == 'all':
        assignment_ids = [submission.assignment.id
                          for submission in student.submissions]
    for submission in student.submissions:
        if submission.assignment.id in assignment_ids:
            text[submission.assignment.id] = submission.with_images(
                url, not target == 'markdown')
    text = [text[assignment_id] for assignment_id in assignment_ids]
    text = '\n---\n'.join(text)
    if target == 'markdown':
        return text
    else:
        formatter = getattr(convert, 'to_{}'.format(target))
        return formatter(text)


@orm.db_session()
def merge_assignment_submissions(assignment_id, student_ids,
                                 target='html', url='http://127.0.0.1:5000'):
    assignment = Assignment[assignment_id]
    if student_ids == 'all':
        student_ids = [submission.student.student_id
                       for submission in assignment.submissions]
    text = defaultdict(lambda i: 'Student {}: Not submitted'.format(i))
    for submission in assignment.submissions:
        if submission.student.student_id in student_ids:
            text[submission.student.student_id] = submission.with_images(
                url, not target == 'markdown')
    text = [Student[student_id].pretty() + '\n' + text[student_id]
            for student_id in student_ids]
    newpage = '\n<div style="page-break-after: always;"></div>\n'
    text = newpage.join(text)
    if target == 'markdown':
        return text
    else:
        formatter = getattr(convert, 'to_{}'.format(target))
        return formatter(text)


@orm.db_session()
def get_assignment(assignment_id):
    assignment = Assignment[assignment_id]
    return assignment.as_dict()


@orm.db_session()
def get_figure_for_submission(submission_id, figure_name):
    submission = Submission[submission_id]
    figure = submission.images.get(name=figure_name)
    return figure.image
