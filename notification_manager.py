from data_manager import DataManager, STEINHQ_ENDPOINT_U, STEINHQ_HEADER
from flight_search import FlightSearch
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import smtplib
import imaplib
import email

import requests

sheet_data = DataManager().get_destination_data()
sheet_data_users = DataManager().get_email_list()
search = FlightSearch()


class NotificationManager:
    """Configures and sends the email"""

    def __init__(self):
        """Configures the email's credentials"""

        self.sender_address = "my.personal.address@gmail.com"
        self.sender_pass = "my.personal.pass"
        self.mail_content = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <style type="text/css">
          table {
            background: white;
            border-radius:3px;
            border-collapse: collapse;
            height: auto;
            max-width: 900px;
            padding:5px;
            width: 100%;
            animation: float 5s infinite;
          }
          th {
            color:#D5DDE5;;
            background:#1b1e24;
            border-bottom: 4px solid #9ea7af;
            font-size:14px;
            font-weight: 300;
            padding:10px;
            text-align:center;
            vertical-align:middle;
          }
          tr {
            border-top: 1px solid #C1C3D1;
            border-bottom: 1px solid #C1C3D1;
            border-left: 1px solid #C1C3D1;
            color:#666B85;
            font-size:16px;
            font-weight:normal;
          }
          tr:hover td {
            background:#4E5066;
            color:#FFFFFF;
            border-top: 1px solid #22262e;
          }
          td {
            background:#FFFFFF;
            padding:10px;
            text-align:left;
            vertical-align:middle;
            font-weight:300;
            font-size:13px;
            border-right: 1px solid #C1C3D1;
          }
        </style>
      </head>
      <body>
        <h2>Today's best flight deals:</h2>
      <table>
      <thead>
            <tr style="border: 1px solid #1b1e24;">
                <tr>
                  <th>Destination Country:</th>
                  <th>Fly from:</th>
                  <th>Fly to:</th>
                  <th>Stop overs:</th>
                  <th>Dates:</th>
                  <th>Ticket:</th>
                  <th>Fare:</th>
                </tr> """

    def update_email_list(self):
        """Reads the emails with new user's credentials and updates the google sheet"""

        gmail_host = 'imap.gmail.com'

        # set connection
        mail = imaplib.IMAP4_SSL(gmail_host)

        # login
        mail.login(self.sender_address, self.sender_pass)

        # select inbox
        mail.select("INBOX")

        # select specific mails
        _, selected_mails = mail.search(None, '(FROM "webwave@webwavecms.com")')

        # total number of mails from specific user
        selected_mails_list = selected_mails[0].split()
        # print("Total Messages from webwave@webwavecms.com:", len(selected_mails_list))
        query_list = []
        for num in selected_mails_list:
            _, data = mail.fetch(num, '(RFC822)')
            _, bytes_data = data[0]

            # convert the byte data to message
            email_message = email.message_from_bytes(bytes_data)

            for part in email_message.walk():
                # print(part.__getitem__("div"))
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    message = part.get_payload(decode=True)

                    message_object = email.message_from_string(message.decode())
                    soup = BeautifulSoup(message_object.get_payload(), "html.parser")
                    mail_content = soup.find_all(name="div", class_="content")

                    content_str = ""
                    for content in mail_content:
                        content_str += content.getText().strip() + " "
                    data_list = (content_str.split())
                    first_name = data_list[1]
                    last_name = data_list[2]
                    email_data = data_list[0].lower()
                    credentials_dict = {
                        "First Name": first_name,
                        "Last Name": last_name,
                        "Email": email_data
                    }
                    query_list.append(credentials_dict)
        return query_list

    def create_email(self):
        """Append the flight details for each found flight deal to the mail_content and send the email"""

        for row in sheet_data:
            try:
                flight = search.check_flights(origin_destination="OTP", city_destination_code=row["IATA Code"])
                if flight.flight_price < int(row["Lowest Price"]):
                    if flight.stop_overs > 0:
                        self.mail_content += f"<tr><td>✈️{flight.destination_country}</td>" \
                                        f"<td>{flight.origin_city}-{flight.origin_airport}</td>" \
                                        f"<td>{flight.destination_city}-{flight.destination_airport}</td>" \
                                        f"<td>{flight.stop_overs} stop over, via {flight.via_city}</td>" \
                                        f"<td>{flight.out_date} to {flight.return_date}</td>" \
                                        f"<td><a href={flight.flight_ticket}>Buy ticket!</a></td>" \
                                        f"<td>€{flight.flight_price}</td></tr>"
                    else:
                        self.mail_content += f"<tr><td>✈️{flight.destination_country}</td>" \
                                        f"<td>{flight.origin_city}-{flight.origin_airport}</td>" \
                                        f"<td>{flight.destination_city}-{flight.destination_airport}</td>" \
                                        f"<td>No stop overs</td>" \
                                        f"<td>{flight.out_date} to {flight.return_date}</td>" \
                                        f"<td><a href={flight.flight_ticket}>Buy ticket!</a></td>" \
                                        f"<td>€{flight.flight_price}</td></tr>"
            except IndexError:
                continue

        # Get the email list
        self.mail_content += "</thead></table></body></html><br><br><h3>Regards,<br>Adrian Mihăilă</h2>"

        email_list = [row["Email"].strip() for row in sheet_data_users]  # call the old list
        new_email_list = self.update_email_list()  # call the new email list of dictionaries

        # Update the sheet with new users
        if len(new_email_list) != 0:
            for credentials_dict in new_email_list:
                if credentials_dict["Email"] in email_list:
                    continue
                else:
                    print("New user found")
                    email_list.append(credentials_dict["Email"])
                    query = [credentials_dict]
                    add_new_user = requests.post(url=STEINHQ_ENDPOINT_U, json=query, headers=STEINHQ_HEADER)
                    add_new_user.raise_for_status()

        for _ in email_list:
            self.send_email(mail_content=self.mail_content, receiver_address_list=_.split())  # Send email

    def send_email(self, mail_content, receiver_address_list):
        """Sends the email"""

        receiver_address = receiver_address_list

        # Setup the MIME
        message = MIMEMultipart()
        message["From"] = self.sender_address
        message["To"] = ", ".join(receiver_address)
        message["Subject"] = "Low price alert"  # The subject line

        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, "html"))

        # Create SMTP session for sending the mail
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()  # enable security
            connection.login(self.sender_address, self.sender_pass)
            text = message.as_string()
            connection.sendmail(self.sender_address, receiver_address, text)