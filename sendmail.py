from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def enviarcorreo():
    # create message object instance
    msg = MIMEMultipart()
    message = str('Orden montada, verificar en Binance')
    # setup the parameters of the message
    password = "v12959363"
    msg['From'] = "info@dvconsultores.com"
    msg['To'] = str('adominguez@dvconsultores.com')
    msg['Subject'] = str('Mensaje de autobot')

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()

    # print ("successfully sent email to %s:" % (msg['To']))

def initops():
    # create message object instance
    msg = MIMEMultipart()
    message = str('Iniciando análisis')
    # setup the parameters of the message
    password = "v12959363"
    msg['From'] = "info@dvconsultores.com"
    msg['To'] = str('adominguez@dvconsultores.com')
    msg['Subject'] = str('Mensaje de autobot')

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()

    print ('Enviado')


