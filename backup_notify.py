#!/usr/bin/env python3
import requests
import datetime
import smtplib
import email.message
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_html(url):
    """Requests url of web-site."""
    response = requests.get(url)
    return response.text


def get_web_status_auth(url, login, password):
    """Requests response code of web-site."""
    response = requests.get(url, auth=HTTPBasicAuth(login, password))
    return response.status_code


def get_html_secured(url, login, password):
    """Requests url of secured web-site, using HTTPBasicAuth.
    
    Keyword arguments:
    url -- Web site URL
    login -- login or username for authorization
    password -- password for authorization

    """
    response = requests.get(url, auth=HTTPBasicAuth(login, password))
    return response.text


def get_all_links(html):
    """Get soup of web page."""
    soup = BeautifulSoup(html, 'lxml')
    return soup


def find_obj_id(soup, ob, ob_name):
    """Find simple object with id.
    
    Keyword arguments:
    soup -- beatifulsoup4 object
    ob -- Type of object to search (Table, id, div)
    ob_name -- Name of object to search
    
    """
    tds = soup.find(ob, id=ob_name)
    return tds


def format_table_email(html_part):
    content = str(html_part)
    pattern = """
    <html>
     <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <title>Backup status</title>
     </head>
     <body>
      <h1> Backup status: {}
      </h1>
      <table border cellpadding="3" cellspacing="2"  bordercolor="#000000">
       {}
      </table>
     </body>
    </html>
    """.format(str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M")), content[1:len(content) - 457])
    return pattern


def format_table_xferr_errors(cells):
    host_name = cells[12:len(cells) - 12:12]
    full_count = cells[14:len(cells) - 12:12]
    full_age = cells[15:len(cells) - 12:12]
    full_size = cells[16:len(cells) - 12:12]
    speed = cells[17:len(cells) - 12:12]
    incr_count = cells[18:len(cells) - 12:12]
    incr_age = cells[19:len(cells) - 12:12]
    last_backup = cells[20:len(cells) - 12:12]
    state = cells[21:len(cells) - 12:12]
    xfer_err = cells[22:len(cells) - 12:12]
    last_att = cells[23:len(cells) - 12:12]
    str_for_html = ''
    for x in range(len(host_name)):
        if str(xfer_err[x]) != '<td align="center" class="border">0</td>':
            str_for_html += '<tr bgcolor="#EC7063">\n' + str(host_name[x]) + '\n' + str(full_count[x]) + '\n' + \
                            str(full_age[x]) + '\n' + str(full_size[x]) + str(speed[x]) + '\n' + str(
                incr_count[x]) + '\n' + \
                            str(incr_age[x]) + '\n' + str(last_backup[x]) + '\n' + str(state[x]) + '\n' + \
                            str(xfer_err[x]) + '\n' + str(last_att[x]) + '\n</tr>\n'
        else:
            str_for_html += '<tr bgcolor="#ABEBC6">\n' + str(host_name[x]) + '\n' + str(full_count[x]) + '\n' + \
                            str(full_age[x]) + '\n' + str(full_size[x]) + str(speed[x]) + '\n' + str(
                incr_count[x]) + '\n' + \
                            str(incr_age[x]) + '\n' + str(last_backup[x]) + '\n' + str(state[x]) + '\n' + \
                            str(xfer_err[x]) + '\n' + str(last_att[x]) + '\n</tr>\n'
    pattern = """
    <html>
     <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <title>Backup status</title>
     </head>
     <body>
      <h1> Backup status: {}
      </h1>
      <table border cellpadding="3" cellspacing="2"  bordercolor="#000000">
       <tr class="tableheader" bgcolor="#AEB6BF">
	    <td class="border"> Host</td>
        <td class="border"> #Full</td>
        <td class="border"> Full age (days)</td>
        <td class="border"> Full age size (GB)</td>
        <td class="border"> Speed (MB/s)</td>
        <td class="border"> #Incr</td>
        <td class="border"> Incr age (days)</td>
        <td class="border"> Last backup (days)</td>
        <td class="border"> State</td>
	    <td class="border"> #Xfer errors</td>
        <td class="border"> Last attempt</td>
       </tr>
	    {}
      </table>
     </body>
    </html>
    """.format(str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M")), str_for_html)
    return pattern


def send_email(email_content):
    msg = email.message.Message()
    msg['Subject'] = 'Weekly backup'
    msg['From'] = 'backup@example.com'
    recipients = ['backup@example.com']
    msg['To'] = ", ".join(recipients)
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(email_content, 'utf-8')
    s = smtplib.SMTP('example.com')
    s.sendmail(msg['From'], recipients, msg.as_string())


def check_xfer_errors(cells):
    xfer_err = cells[22:len(cells) - 12:12]
    for x in range(len(xfer_err)):
        if str(xfer_err[x]) != '<td align="center" class="border">0</td>':
            return True
    return False


def main():
    login = 'login'
    password = 'password'
    response_code = get_web_status_auth('http://backuplg/backuppc/index.cgi?action=summary', login, password)
    if response_code == 200:
        url = get_html_secured('http://backuplg/backuppc/index.cgi?action=summary', login, password)
        soup = get_all_links(url)
        cells = find_obj_id(soup, 'div', 'Content').find_all_next('td')
        send_email(format_table_xferr_errors(cells))
    else:
        send_email('Response code: ' + str(response_code))


if __name__ == '__main__':
    main()
