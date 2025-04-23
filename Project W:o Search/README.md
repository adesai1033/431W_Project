# Progress Review

## README

**Authors:** Team Doja Cats (Deep, Om, Jack, Abhi)  
**Date:** March 24, 2025

## Overview
This code directory is the foundation of the NittanyBusiness platform's log-in and database functionalities. It consists of two web pages, which will serve as the log-in and register homepage for users of NittanyBusiness. Additionally, twelve different tables have been created in "database.db" and were populated with the dataset given by the professor. However, we hashed the passwords in the "Users" table for additional security purposes. For this progress review checkpoint, we only utilize the "Users" table. 

## Features
This code directory provides the functionality of logging into the NittanyBusiness platform with valid credentials. With a simple user interface, the webpage asks for a valid email and password associated with an existing NittanyBusiness account. For the sake of this progress review, there is a given dataset of emails/passwords that are already registered. So, the webpage is simply linked to the "Users" table in "database.db", and uses it to determine whether given credentials are valid or not for log-in. Additionally, a successful log-in would result in a success message to be displayed and an error message otherwise.

### Password Security
Passwords are securely stored as hashed values which are obtained through the bcrypt Python library. We used the hashpw function on all passwords in the database with salt added (extra padding) to ensure more security within the hashed values and prevents outside attacks. During the login process, we utilize the checkpw function within the bcrypt library to check if the inputted password hashes to the the matching hashed password when using the same salt.

[Hashing Passwords in Python with BCrypt - GeeksforGeeks]

## Organization
The files are organized such that the log-in and register web pages have their own .html file and are placed in the templates folder, and there is an app.py file which incorporates Flask and sqlite3 to conduct the backend actions with the database. Once you run the app.py file, a database will be created if it does not already exist. As mentioned earlier, only the "Users" table is used, so the database will be created with one table for now (also triggered when log-in and register buttons are pressed). The rest will be automatically created as we progress with the project.

### File Breakdown:
- `app.py` = The file consisting Flask and sqlite3 functionalities for database interactions
- **Templates Folder:**
  - `index.html` = log-in page to access the NittanyBusiness platform
  - `register.html` = page that allows a new user to register and account

## Instructions
To run this code:
1. Download the zip file and unzip it to access the files
2. Go to the directory that the file is located in, in the terminal
3. Within that directory, run `python3 app.py`
4. Once running, visit the host: 'http://127.0.0.1:5000/'
5. Now you will find yourself at the log-in page
6. Navigate accordingly

> **NOTE:** If at first the host url does not load, please give it a few seconds to properly connect and try refreshing

Thank you!




