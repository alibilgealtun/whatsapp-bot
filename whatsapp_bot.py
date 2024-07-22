import sqlite3

from selenium import webdriver
import time
import os
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


conn = sqlite3.connect("contacts2.db")
cursor = conn.cursor()
# con.commit() need to be done to change in database

driver = None


def start():
    global driver
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")

        driver = webdriver.Chrome(options=chrome_options)

        driver.get("https://web.whatsapp.com")
    except Exception as e:
        print(f"An error occurred: {str(e)}")





def search_person(contact):
    search_box = driver.find_element(By.XPATH, '//div[@aria-label="Search input textbox"]')
    search_box.send_keys(contact)
    time.sleep(2)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)
def send_message(msg):
    message_box = driver.find_element(By.XPATH, '//div[@class="x1hx0egp x6ikm8r x1odjw0f x1k6rcq7 x6prxxf"]')
    message_box.send_keys(msg)
    message_box.send_keys(Keys.ENTER)
    time.sleep(2)


def find_pdfs():
    directory = 'files/'
    pdf_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                path = os.path.abspath(os.path.join(root, file))
                pdf_paths.append(path)
    return pdf_paths

def send_pdfs():
    # Click the attachment button


    pdf_paths = find_pdfs()
    for pdf_path in pdf_paths:
        try:
            attach_button = driver.find_element(By.XPATH, "//span[@data-icon='attach-menu-plus']")
            attach_button.click()
            time.sleep(1)
            # Re-locate the file input element for each upload attempt
            pdf_input = driver.find_element(By.XPATH, '//input[@accept="*"]')
            pdf_input.send_keys(pdf_path)
            time.sleep(1)  # Wait for the file to be selected

            # Click the send button
            send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']")
            send_button.click()
            time.sleep(3)  # Wait for the file to be sent


        except Exception as e:
            print(f"An error occurred while sending file {pdf_path}: {str(e)}")



def fetch_contacts(path):
    query = 'SELECT name FROM contacts'
    cursor.execute(query)
    contacts = [row[0] for row in cursor.fetchall()]
    return contacts

def main():
    db_path = "contacts2.db"
    contacts = fetch_contacts(db_path)
    message = """
        Bu bir deneme mesajıdır. Bot yazıyorum.
    """

    start()
    input("ENTERA BAS QR GİRİNCE")

    for contact in contacts:
        search_person(contact)
        send_message(message)
        send_pdfs()


main()


