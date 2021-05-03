# Instructions for setting up periodic scraping of CoWin for vaccine appointments.

1. Fill in the following details in secrets.py file :
	1. email: Your gmail ID
	1. password: Your gmail password
	1. email_recipients: The list of email IDs to which you want to send emails to when there is an available slot.
	1. finkode_url: The URL containing list of areas with pincodes for the city you are interested in. Please look for your city in https://finkode.com/. For example, https://finkode.com/ka/bangalore.html for Bangalore. The script will loop through all the pincodes mentioned in this webpage, and check for available slots in them.

1. To run the script periodically, on linux / macOS run:
	```
	crontab -e
	```
	This will open an editor. Enter the following text and save the file :
	```
	*/30 * * * * cd ~/Development/covid && ./work.sh > ~/Development/covid/cron.log 2>&1 
	```
	This will run the script every 30 minutes. You can see the status of the latest run by running:
	```
	cat ~/Development/covid/cron.log
	```

1. To run the script just one time, run:
	```
	cd ~/Development/covid && ./work.sh
    ```