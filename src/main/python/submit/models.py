import os
from io import BytesIO
import base64
from PIL import Image as pImage
from pony import orm
from datetime import date

db = orm.Database()


def bind():
    if os.getenv('USER') == 'zubmit':
        db.bind('sqlite', filename='current_db.sqlite')
        db.generate_mapping(create_tables=True)
    else:
        bind_test()


def bind_test():
    db.bind('sqlite', filename=':memory:')
    db.generate_mapping(create_tables=True)


class Student(db.Entity):
    student_id = orm.PrimaryKey(int)
    name = orm.Required(str)
    email = orm.Required(str)
    submissions = orm.Set('Submission')

    def has_submitted(self, assignment):
        for submission in self.submissions:
            if submission.assignment == assignment:
                return True
        else:
            return False

    def to_dict(self):
        return {'student_id': self.student_id,
                'name': self.name,
                'email': self.email,
                'nsubmissions': len(self.submissions)}

    def pretty(self):
        return ('- Student name: {}\n- Student id: {}\n- Student email: {}\n'
                .format(self.name, self.student_id, self.email))


class Assignment(db.Entity):
    due_date = orm.Required(date)
    word_limit = orm.Optional(int)
    submissions = orm.Set('Submission')
    description = orm.Required(str)
    isopen = orm.Required(bool, default=True)
    nimages = orm.Required(int, default=0)

    def as_dict(self):
        return {'id': self.id,
                'isopen': self.isopen,
                'word_limit': self.word_limit,
                'due_date': self.due_date,
                'description': self.description,
                'nimages': self.nimages}


class Submission(db.Entity):
    text = orm.Required(str)
    assignment = orm.Required(Assignment)
    student = orm.Required(Student)
    grade = orm.Optional(int)
    images = orm.Set('Image')

    def with_images(self, url, inline=False):
        elements = [self.text]
        for img in self.images:
            if inline:
                buff = BytesIO(img.image)
                image = pImage.open(buff)
                buff = BytesIO()
                image.save(buff, format='PNG')
                img_str = base64.b64encode(buff.getvalue()).decode('utf-8')
                image_url = 'data:image/png;base64,{}'.format(img_str)
            else:
                image_url = ('{}/api/submissions/{}/figures/{}/'
                             .format(url, self.id, img.id))
            elements.append('<p><h3>{}</h3><br><img src="{}" /></>'
                            .format(img.name
                                    .title()
                                    .replace('_', ' '),
                                    image_url))
        return '\n\n'.join(elements)


class Image(db.Entity):
    submission = orm.Required(Submission)
    name = orm.Required(str)
    image = orm.Required(bytes)
