import sqlite3

from selenium import webdriver
import time
import os
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

db_path = "contacts.db"
conn = sqlite3.connect(db_path)
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



def clear_person():
    search_box = driver.find_element(By.XPATH, '//div[@aria-label="Search input textbox"]')
    search_box.click()  # Ensure the search box is focused
    search_box.clear()  # Attempt to clear the text
    search_box.send_keys(Keys.CONTROL + "a")  # Select all text
    search_box.send_keys(Keys.DELETE)  # Delete selected text
    time.sleep(0.5)  # Small delay to ensure the clearing action is processed

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

    pdf_paths = find_pdfs()
    for pdf_path in pdf_paths:
        try:
            attach_button = driver.find_element(By.XPATH, "//span[@data-icon='attach-menu-plus']")
            attach_button.click()
            time.sleep(1)
            # Re-locate the file input element for each upload attempt
            pdf_input = driver.find_element(By.XPATH, '//input[@accept="*"]')
            pdf_input.send_keys(pdf_path)
            time.sleep(3)


            # Click the send button
            send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']")
            send_button.click()
            time.sleep(3)  # Wait for the file to be sent


        except Exception as e:
            print(f"An error occurred while sending file {pdf_path}: {str(e)}")



def fetch_contacts():
    query = 'SELECT name FROM contacts'
    cursor.execute(query)
    contacts = [row[0] for row in cursor.fetchall()]
    return contacts


def delete_contact(contact):
    try:
        delete_sql = "DELETE FROM contacts WHERE name = ?"
        cursor.execute(delete_sql, (contact,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def isRightPerson(contact):
    try:
        # Locate the span inside the div with class "_amie"
        profile_text = driver.find_element(By.XPATH, '//div[@class="_amie"]//span').text
        # Compare the profile text with the contact
        if contact == profile_text:
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred while verifying the contact: {str(e)}")
        return False


def main():
    contacts = fetch_contacts()
    print(contacts)
    message = """
            Hello! We are excited to share our latest furniture catalogs and price lists with you. This month, we have some amazing discounts on our top-quality furniture:
            Vino Sofa: 27% off
            Rahat Furniture: 10% off
            Lucente: 30% off
            Please find the attached PDFs above for more details. We look forward to your orders and inquiries.
            Best regards, Halit Altun - VIA Dış Ticaret
            
    """

    start()
    input("ENTERA BAS QR GİRİNCE")

    for contact in contacts:
        try:
            clear_person()
            search_person(contact)
            if isRightPerson(contact):
                send_pdfs()
                time.sleep(2)
                send_message(message)
                delete_contact(contact)
        except Exception:
            print("Error for contact: ", contact)

main()


