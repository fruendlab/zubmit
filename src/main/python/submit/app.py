from dateutil import parser
from flask import Flask, request, jsonify
from jinja2 import Environment, PackageLoader, select_autoescape

from submit import api, models


app = Flask(__name__)
env = Environment(
    loader=PackageLoader('submit', 'templates'),
    autoescape=select_autoescape(['html']),
)

models.bind_test()


@app.route('/enter/<assignment_id>/')
def submission_page(assignment_id):
    assignment = api.get_assignment(assignment_id)
    print(assignment)
    template = env.get_template('submission.html')
    return template.render(**assignment)


@app.route('/submit/<assignment_id>/', methods=['POST'])
def submission_finished(assignment_id):
    images = {img: request.files[img]
              for img in request.files
              if img.startswith('figure_')}

    student_name, student_id = api.register_submission(
        request.form['student_id'],
        assignment_id,
        request.form['submission_text'],
        images)
    template = env.get_template('finished.html')
    return template.render(student_name=student_name, student_id=student_id)


@app.route('/api/assignments/', methods=['POST'])
def upload_assignment():
    description = request.form['description']
    due_date = parser.parse(request.form['due_date'])
    word_limit = (int(request.form['word_limit'])
                  if 'word_limit' in request.form else None)
    nimages = request.form['nimages']
    assignment_id = api.register_assignment(description,
                                            due_date,
                                            word_limit,
                                            nimages)
    return jsonify({'id': assignment_id})


@app.route('/api/students/', methods=['POST'])
def register_students():
    api.register_student_list(request.json['student_list'])
    return 'OK'


@app.route('/api/students/', methods=['GET'])
def get_student_list():
    return jsonify(api.get_student_list())


@app.route('/api/assignments/<assignment_id>/', methods=['GET'])
def download_submissions_by_assignment(assignment_id):
    output_format = request.args.get('format', 'markdown')
    student_ids = request.args.get('students', 'all')
    return api.merge_assignment_submissions(assignment_id,
                                            student_ids,
                                            target=output_format)


@app.route('/api/students/<student_id>/', methods=['GET'])
def download_submissions_by_student(student_id):
    output_format = request.args.get('format', 'markdown')
    assignment_ids = request.args.get('assignment', 'all')
    return api.merge_student_submissions(student_id,
                                         assignment_ids,
                                         target=output_format)
