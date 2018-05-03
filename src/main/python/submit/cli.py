from dateutil import parser
import requests


def assign(args, url):
    with open(args['<DESCRIPTION>']) as f:
        description = f.read()
    due_date = parser.parse(args['<DUE_DATE>'])
    payload = {'description': description,
               'due_date': due_date.strftime('%Y %m %d')}
    if args['<WORD_LIMIT>']:
        payload['word_limit'] = int(args['<WORD_LIMIT>'])

    r = requests.post(url+'/api/assignments/', data=payload)

    r.raise_for_status()
    print(r.json())


def register(args, url):
    with open(args['<STUDENT_LIST>']) as f:
        student_list = []
        for line in f:
            student_info = {key: value.strip()
                            for key, value in zip(
                                ['id', 'last name', 'first name', 'email'],
                                line.split(','))}
            student_info['name'] = '{} {}'.format(
                student_info.pop('first name'),
                student_info.pop('last name'))
            student_list.append(student_info)

    r = requests.post(url+'/api/students/',
                      json={'student_list': student_list})
    r.raise_for_status()
    print(r.text)


def list_students(args, url):
    r = requests.get(url+'/api/students/')
    r.raise_for_status()
    print(r.json())


def download(args, url):
    payload = {'format': args['--output-format']}
    formats2extensions = {
        'markdown': 'md',
        'pdf': 'pdf',
        'html': 'html',
    }
    r = requests.get(
        url+'/api/assignments/{}/'.format(args['<ASSIGNMENT_ID>']),
        params=payload)
    r.raise_for_status()
    outfilename = args['--output'].format(
        formats2extensions[args['--output-format']])
    with open(outfilename, 'wb') as f:
        f.write(r.content)
