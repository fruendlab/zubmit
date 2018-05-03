from splinter import Browser
import time
import os
import subprocess

from submit import cli

URL = 'http://127.0.0.1:5000'

print('Registering students')
cli.register({'register': True, '<STUDENT_LIST>': 'students.csv'}, URL)

print('Students registered')
cli.list_students({'list-students': True}, URL)

print('Uploading assignment')
cli.assign({'assign': True,
            '<DESCRIPTION>': 'description.md',
            '<DUE_DATE>': '2018-05-20',
            '--word-limit': '20',
            '--number-of-images': 2}, URL)

time.sleep(0.3)


executable = '/home/ingo/bin/chromedriver'
with Browser('chrome', executable_path=executable) as browser:
    browser.visit(URL + '/enter/1/')
    browser.fill('student_id', '1234')
    browser.fill('submission_text',
                 '# This is a test\n'
                 'Test if I can enter something')
    browser.fill('figure_1', os.path.abspath('./test.png'))
    submit_button = browser.find_by_id('submit-button')
    submit_button.click()


for fmt, viewer in [('markdown', 'less'),
                    ('html', 'google-chrome'),
                    ('pdf', 'zathura')]:
    cli.download({'--output-format': fmt,
                  '<ASSIGNMENT_ID>': '1',
                  '--output': 'test.{}'}, URL)
    ext = 'md' if fmt == 'markdown' else fmt
    subprocess.run('{} test.{}'.format(viewer, ext), shell=True)
