import urllib.request
import ssl
import json
import re
from bs4 import BeautifulSoup
import warnings
from datetime import timedelta, date, datetime
import smtplib
import secrets


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def html_table(all_centers):
	html_contents = []
	html_contents.append('<table align="center"">')
	html_contents.append('<tr><th>')
	html_contents.append('</th><th>'.join(["Name", "Area", "Pincode", "Date", "Available Capacity", "Vaccine"]))
	html_contents.append('</th></tr>')
	for center in all_centers:
		html_contents.append('<tr><td>')
		html_contents.append('</td><td>'.join(center))
		html_contents.append('</td></tr>')
	html_contents.append('</table><br><br>')
	return '\n'.join(html_contents)

def sendmail(contents):
	# creates SMTP session
	s = smtplib.SMTP('smtp.gmail.com', 587)
	  
	# start TLS for security
	s.starttls()
	  
	# Authentication
	s.login(secrets.email, secrets.password)

	message = """From: Anirudh GP<anirudh.gp@gmail.com>
MIME-Version: 1.0
Content-type: text/html
Subject: Covid Vaccine Availability Found!
<head>
<style>
  table,
  th,
  td {{
    padding: 10px;
    border: 1px solid black;
    border-collapse: collapse;
    font-size:20px;
  }}
  table {{
    width: 900px;
  }}

  td {{
    width: 100px;
    font-weight: bold;
    text-align: center;
  }}
</style>
</head>
<body>
{}
</body>
""".format(contents)
	  
	# sending the mail
	s.sendmail(secrets.email, secrets.email_recipients, message)
	  
	# terminating the session
	s.quit()

warnings.catch_warnings()
warnings.simplefilter("ignore")
gcontext = ssl.SSLContext()

fp = urllib.request.urlopen(secrets.finkode_url, context=gcontext)
pincode_bytes = fp.read()
fp.close()
pincode_str = pincode_bytes.decode("utf8")
pincode_data = [[cell.text for cell in row("td")] for row in BeautifulSoup(pincode_str)("tr")]
pincode_data = [data for data in pincode_data if len(data) > 0]
pincodes = set()
pincode_map = dict()
for data in pincode_data:
	pincodes.add(data[2])
	pincode_map[int(data[2])] = data[0]

available_centers = dict()

today = date.today()
for pincode in pincodes:
	fp = urllib.request.urlopen(
		"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}".format(pincode, today.strftime("%d-%m-%Y")),
		context=gcontext)
	mybytes = fp.read()
	fp.close()

	mystr = mybytes.decode("utf8")
	schedule = json.loads(mystr)

	for center in schedule["centers"]:
		for session in center["sessions"]:
			if session["min_age_limit"] == 18:
				if session["available_capacity"] > 0:
					vaccine_name = session["vaccine"]
					fee = 0
					if "vaccine_fees" in session:
						for vaccine_fee in session["vaccine_fees"]:
							if vaccine_fee["vaccine"] == vaccine_name:
								fee = vaccine_fee
								break
					available_centers[center["center_id"]] = [center["name"], pincode_map[center["pincode"]], str(center["pincode"]), str(session["date"]), str(session["available_capacity"]), vaccine_name]

now = datetime.now()
if len(available_centers.values()) > 0:
	print("{} : Available centers found! Sending mail".format(now.strftime("%d/%m/%Y %H:%M:%S")))
	sendmail(html_table(list(available_centers.values())))
else:
	print("{} : No available centers found".format(now.strftime("%d/%m/%Y %H:%M:%S")))