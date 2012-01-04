from postmeister import MailAPI, DummyServer
from jinja2 import PackageLoader

def test_mail():
    server = DummyServer()
    loader = PackageLoader("postmeister", "tests/templates")
    mailer = MailAPI(server, from_addr="Name <mail@example.org>", loader=loader)

    mailer.mail("to@example.org", "subject", "test.txt", user="a user")

    assert len(server.mails) == 1



