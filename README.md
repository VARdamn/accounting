# Accounting Bot
Telegram bot for writing expenses and getting statistics about.

# Usage
1. Create your telegram bot and write it's token in .env file, located in root directory

2. Go to https://console.cloud.google.com/apis/dashboard, create new project and enable google drive API and google sheets API

3. Go to Credentials page, create new service account

4. Download credentials file (creds.json) and paste it to the root directory of project

5. Create google sheet and copy it's ID

![image](https://user-images.githubusercontent.com/74242594/210259390-c7e0d0ee-1ac1-48ae-9012-3852156f528e.png)

6. Give access as editor to created service account - write created by google email (it is very-very long) and give access

7. Add your spreadsheet in bot using command **/add_sheet** 

![image](https://user-images.githubusercontent.com/74242594/210259533-2d220266-1ceb-42cd-8332-5cd6d0b0929d.png)

8. See list of all commands using **/help**
 
Don't forget to download Python on your machine and install all libraries using command **pip install -r requirements.txt**
