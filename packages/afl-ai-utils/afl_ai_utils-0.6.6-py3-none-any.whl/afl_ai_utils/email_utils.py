import pdb

import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os


class Email():
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def sendmail(self, subject: str, msg_body: str, data_frame: pd.DataFrame, from_email: str, to: str, cc: str,
                 bcc: str, attachment_file: str):
        # emaillist = recipients+cc_recipients
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to
        msg['Cc'] = cc
        rcpt = cc.split(",") + bcc.split(",") + [to]
        html = ""
        if msg_body and data_frame and len(msg_body) > 1 and len(data_frame) > 0:
            html = """\
            <html>
                {0}
              <head></head>
              <body>
                {1}
              </body>
            </html>
            """.format(msg_body, data_frame.to_html())
        else:

            html = """\
            <html>
              <head></head>
              <body>
                {0}
              </body>
            </html>
            """.format(msg_body)

        if html and len(html) > 1:
            part1 = MIMEText(html, 'html')
            msg.attach(part1)

        if attachment_file and len(attachment_file) > 1:
            attachment = attachment_file
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(attachment, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=attachment)
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.email, self.password)
        server.sendmail(msg['From'], rcpt, msg.as_string())

    def send_outlook_email(self, subject: str, msg_body: str, data_frame: pd.DataFrame, from_email: str, to: str,
                           cc: str,
                           bcc: str, attachment_file):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        html = ""
        if msg_body and data_frame is not None and len(msg_body) > 1 and len(data_frame) > 0:
            html = """\
            <html>
                {0}
              <head></head>
              <body>
                {1}
              </body>
            </html>
            """.format(msg_body, data_frame.to_html())
        else:

            html = """\
            <html>
              <head></head>
              <body>
                {0}
              </body>
            </html>
            """.format(msg_body)

        if html and len(html) > 1:
            part1 = MIMEText(html, 'html')
            msg.attach(part1)

        if attachment_file and len(attachment_file) > 1:
            if isinstance(attachment_file, list):
                for file in attachment_file:
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload(open(file, "rb").read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file)}')
                    msg.attach(part)
            else:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(attachment_file, "rb").read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=attachment_file)
                msg.attach(part)

        msg['Body'] = msg_body
        msg['From'] = from_email
        msg['To'] = to
        msg['Cc'] = cc

        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.email, self.password)
            server.send_message(msg)

    # def send_outlook_email(self, subject: str, msg_body: str, from_email: str, to: list, cc: list, attachment_file: str):
    #
    #     ## FILE TO SEND AND ITS PATH
    #     filename = 'test.csv'
    #     SourcePathName = os.getcwd() + "/" + filename
    #
    #     msg = MIMEMultipart()
    #     msg['From'] = os.getenv("FROM")
    #     msg['To'] = os.getenv("TO")
    #     msg['Subject'] = "Test file subject"
    #     body = 'Hi, \n, PFA \n regards, Abhay\n'
    #     msg.attach(MIMEText(body, 'plain'))
    #
    #     ## ATTACHMENT PART OF THE CODE IS HERE
    #     attachment = open(SourcePathName, 'rb')
    #     part = MIMEBase('application', "octet-stream")
    #     part.set_payload((attachment).read())
    #     encoders.encode_base64(part)
    #     part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    #     msg.attach(part)
    #
    #     server = smtplib.SMTP('smtp.office365.com', 587)  ### put your relevant SMTP here
    #     server.ehlo()
    #     server.starttls()
    #     server.ehlo()
    #     print(os.getenv("FROM"), os.getenv("PASSWORD"))
    #     server.login(os.getenv("FROM"), os.getenv("PASSWORD"))  ### if applicable
    #     server.send_message(msg)
    #     server.quit()
    #     print("Send email ", msg)

# e = Email()
# e.sendmail(subject=subject, data_frame=df, from_email=from_email, to=to, cc=cc, bcc=bcc, attachment_file=attachment_file, msg_body=body)
