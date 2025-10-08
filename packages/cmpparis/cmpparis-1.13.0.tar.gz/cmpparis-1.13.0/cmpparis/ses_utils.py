import botocore
import boto3
import os
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from cmpparis.parameters_utils import *

def send_email_to_support(subject, content):
    """Envoie un email de support via AWS SES.

    Args:
        subject (str): Sujet du message.
        content (str): Corps (HTML/texte) du message.
    """
    from_email = get_parameter('generic', 'technical_report_email')
    to_email = get_parameter('generic', 'to_support_email')

    send_email(from_email, to_email, subject, content, [])

def send_email(from_email, to_email, subject, data, attachments=None):
    """Envoie un email via AWS SES avec options de pièces jointes.

    Args:
        from_email (str): Adresse expéditeur.
        to_email (str): Adresse(s) destinataire(s), séparées par virgules.
        subject (str): Sujet.
        data (str): Contenu HTML inséré dans un template simple.
        attachments (list[str] | None): Liste de chemins de fichiers à joindre.

    Returns:
        dict: Réponse de ``send_raw_email`` si succès.

    Raises:
        SystemExit: En cas d'erreur client SES (journalisée sur stdout).
    """
    try:
        aws_region_name = get_region_name()
        client = boto3.client('ses', region_name=aws_region_name)

        html = """\
            <html>
                <head><style>th {{ text-align: center; }} td:nth-child(2) {{ font-weight: bold; }}</style></head>
                <body>
                    {}
                </body>
            </html>
        """.format(data)

        msg = MIMEMultipart()

        html_content = MIMEText(html, "html")
        msg.attach(html_content)

        if attachments is not None:
            for file in attachments:
                att = MIMEApplication(open(file, "rb").read())

                att.add_header('Content-Disposition', 'attachment',
                            filename=os.path.basename(file))

                msg.attach(att)

        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        response = client.send_raw_email(
            Source=from_email,
            Destinations=to_email.split(','),
            RawMessage={'Data': msg.as_string()}
        )

        return response
    except botocore.exceptions.ClientError as e:
        print(f"Error while sending email : {e}")
        sys.exit(1)