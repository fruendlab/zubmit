from markdown import markdown
from weasyprint import HTML, CSS


def to_html(text):
    return markdown(text)


def to_pdf(text):
    html = HTML(string=to_html(text))
    css = CSS(string='')
    return html.write_pdf(stylesheets=[css])
