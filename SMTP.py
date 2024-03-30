import smtplib
from email.mime.text import MIMEText
from email.header import Header
from dotenv import load_dotenv
from os import getenv


class SmtpFeedback:
    """Класс для отправки отзывов через SMTP"""
    def __enter__(self):
        load_dotenv()
        self.smtp_server = getenv('SMTP_SERVER')
        self.smtp_port = int(getenv('SMTP_PORT'))
        self.smtp_username = getenv('SMTP_USER')
        self.smtp_password = getenv('SMTP_PASS')
        self.sender_email = getenv('SENDER')
        self.receiver_email = getenv('RECEIVER')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def send_feedback(self, message_to_send: str, user_id: int) -> None:

        """Отправка отзыва
        :param message_to_send: отзыв
        :param user_id: id пользователя

        :return: None"""

        msg = MIMEText(f'{message_to_send}, отправивший гений: {user_id}', 'plain', 'utf-8')
        msg['Subject'] = Header('Отзыв', 'utf-8')
        msg['From'] = self.smtp_username
        msg['To'] = self.receiver_email

        connection = smtplib.SMTP(self.smtp_server, 587, timeout=10)

        try:
            connection.starttls()
            connection.login(self.smtp_username, self.smtp_password)
            connection.sendmail(msg['From'], self.receiver_email, msg.as_string())
        except Exception as e:
            print(e)
        finally:
            connection.quit()
