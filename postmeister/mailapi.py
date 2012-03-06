#encoding=utf8
"""

Mail API

"""

__all__ = ['DummyServer', 'MailAPI']


import urlparse
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.charset import Charset, QP
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from jinja2 import Environment, PackageLoader, TemplateNotFound

class DummyServer(object):
    """a dummy mailer which does not send but stores mail. Can be used for testing"""

    def __init__(self, printout=False, *args, **kwargs):
        """initialize the dummy mail server"""
        self.mails = []
        self.printout = printout

    def connect(self, *args, **kwargs):
        pass

    def quit(self, *args, **kwargs):
        pass

    def sendmail(self, from_addr, to, msg):
        """send the mail means storing it in the list of mails"""
        m = {
            'from': from_addr,
            'to' : to,
            'msg' : msg
        }
        self.mails.append(m) # msg actually contains everything
        if self.printout:
            print "--------"
            print to
            print msg
            print "--------"

class MailAPI(object):
    """a mail API"""

    def __init__(self, server, encoding="utf-8", templates=None, from_addr = None):
        """initialize the mail API.

        :param server: an smtplib.SMTP server or a component implementing ``connect()``, ``sendmail()`` and ``quit()``
        :param encoding: the encoding to use for emails
        :param templates: The jinja2 template environment to use
        :param from_addr: the full name of the sender
        """
        self.server = server
        self.templates = templates
        self.from_addr = None

        self.charset = Charset("utf-8")
        self.charset.header_encoding = QP
        self.charset.body_encoding = QP

    def mail(self, to, subject, tmplname, from_addr=None, **kw):
        """send a plain text email

        :param to: a simple string in RFC 822 format
        :param subject: The subject of the email
        :param tmplname: template name to be used
        :param **kw: parameters to be used in the template
        """

        # render template
        tmpl = self.templates.get_template(tmplname)
        payload = tmpl.render(kw)

        # now create the message
        msg = Message()
        msg.set_payload(payload.encode("utf8"))
        msg.set_charset(self.charset)
        msg['Subject'] = Header(subject, "utf8")
        if from_addr is None:
            msg['From'] = self.from_addr
        else:
            msg['From'] = from_addr
        msg['To'] = to

        self.server.connect()
        self.server.sendmail(self.from_addr, [to], msg.as_string())
        self.server.quit()


    def mail_html(self, to, subject, tmplname_txt, tmplname_html, from_addr=None, **kw):
        """send a HTML and plain text email

        :param to: a simple string in RFC 822 format
        :param subject: The subject of the email
        :param tmplname_txt: template name to be used for the plain text version (not used if None)
        :param tmplname_html: template name to be used for the HTML version (not used if None)
        :param **kw: parameters to be used in the templates
        """

        # render template
        tmpl_txt = self.templates.get_template(tmplname_txt)
        tmpl_html = self.templates.get_template(tmplname_html)
        payload_txt = tmpl_txt.render(kw)
        payload_html = tmpl_html.render(kw)


        # now create the message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, "utf8")
        if from_addr is None:
            msg['From'] = self.from_addr
        else:
            msg['From'] = from_addr
        msg['To'] = to

        part1 = MIMEText(payload_txt.encode('utf-8'), 'plain', 'utf-8')
        part2 = MIMEText(payload_html.encode('utf-8'), 'html', 'utf-8')

        msg.attach(part1)
        msg.attach(part2)

        self.server.connect()
        self.server.sendmail(self.from_addr, [to], msg.as_string())
        self.server.quit()


