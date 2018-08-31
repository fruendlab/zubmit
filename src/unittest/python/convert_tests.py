from unittest import TestCase, mock

from zubmit import convert


class TestToHtml(TestCase):

    def test_should_format_basic_html(self):
        self.assertEqual(
            convert.to_html('# Head\nText'),
            '<h1>Head</h1>\n<p>Text</p>')


class TestToPdf(TestCase):

    def setUp(self):
        self.patches = mock.patch.multiple('zubmit.convert',
                                           HTML=mock.DEFAULT,
                                           CSS=mock.DEFAULT,
                                           to_html=mock.DEFAULT)

    def test_should_return_stream_from_write_pdf(self):
        with self.patches as mocks:
            self.assertEqual(convert.to_pdf('test'),
                             mocks['HTML']().write_pdf.return_value)

    def test_should_create_html_from_text(self):
        with self.patches as mocks:
            mocks['to_html'].return_value = 'ANY_HTML'
            convert.to_pdf('test')
            mocks['HTML'].assert_called_once_with(string='ANY_HTML')

    def test_should_write_pdf_with_stylesheet(self):
        with self.patches as mocks:
            convert.to_pdf('test')
            mocks['HTML']().write_pdf.assert_called_once_with(
                stylesheets=[mocks['CSS'].return_value])
