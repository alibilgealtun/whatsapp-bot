import sqlite3
from tkinter import Tk, Label, Entry, Button, filedialog, Listbox, messagebox, Frame, BOTTOM, LEFT
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
import vobject


class WhatsAppBot:
    def __init__(self):
        self.pdf_file_paths = None
        self.driver = None
        self.image_file_path = None
        self.pdf_file_path = None

    def start(self):
        if driver_path is None:
            Files.select_driver_path()

        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service)

        self.driver.get("https://web.whatsapp.com")
        time.sleep(15)  # Wait for the QR Scanning

    def stop(self):
        if self.driver:
            self.driver.quit()

    def send_message(self, message):
        contacts.update_db()
        for contact in contacts.contacts:
            # Search for the name
            search_box = self.driver.find_element("xpath", "//div[@contenteditable='true']")
            search_box.send_keys(contact)
            time.sleep(2)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)

            # Send message
            message_box = self.driver.find_element("xpath", "//div[@title='Type a message']")
            message_box.send_keys(message)
            message_box.send_keys(Keys.ENTER)
            time.sleep(2)

    def send_file(self, file_path):
        contacts.update_db()
        for contact in contacts.contacts:
            search_box = self.driver.find_element("xpath", "//div[@content editable='true']")
            search_box.send_keys(contact)
            time.sleep(2)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)

            attachment_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@title='Attach']"))
            )
            attachment_button.click()
            time.sleep(2)

            file_input = self.driver.find_element("xpath", "//input[@accept='*']")
            file_input.send_keys(file_path)
            time.sleep(2)

            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']"))
            )
            send_button.click()
            time.sleep(5)


class Contacts:
    def __init__(self):
        self.cursor = None
        self.conn = None
        self.contacts = None
        self.update_db()

    def add_contact(self):
        name = entry_new_contact.get()
        if name:
            self.cursor.execute("INSERT INTO contacts (name) VALUES (?)", (name,))
            self.conn.commit()
            listbox_contacts.insert('end', name)
            entry_new_contact.delete(0, 'end')

    def remove_contact(self):
        self.conn = sqlite3.connect("contacts.db")
        selected_index = listbox_contacts.curselection()
        if selected_index:
            name = listbox_contacts.get(selected_index)
            self.cursor.execute("DELETE FROM contacts WHERE name=?", (name,))
            self.conn.commit()
            listbox_contacts.delete(selected_index)

    def readVCF(self):
        self.vcf_path = Files.select_vcf()

        with open(self.vcf_path, 'r', encoding='utf-8') as file:
            vcf_data = file.read()

        vcf_parts = vobject.readComponents(vcf_data)

        for vcf_part in vcf_parts:
            try:
                name = vcf_part.fn.value
            except AttributeError:
                name = ''
            self.contacts.append(name)
            self.cursor.execute("INSERT INTO contacts (name) VALUES (?)", (name,))
            self.conn.commit()
            listbox_contacts.insert('end', name)
            entry_new_contact.delete(0, 'end')

    def reset_contacts(self):
        # Confirm resetting contacts
        confirmed = messagebox.askyesno("Onay", "Tüm rehberi sıfırlamak istediğinizden emin misiniz?")
        if confirmed:
            # Delete contacts
            self.cursor.execute("DELETE FROM contacts")
            self.conn.commit()

            # Clear listbox
            listbox_contacts.delete(0, 'end')

    def remove_selected_contacts(self):
        selected_indices = listbox_contacts.curselection()
        for index in selected_indices[::-1]:
            # Remove contacts starting from the last one
            name = listbox_contacts.get(index)
            self.cursor.execute("DELETE FROM contacts WHERE name=?", (name,))
            listbox_contacts.delete(index)
        self.conn.commit()

    def close_contacts_db(self):
        self.conn.close()

    def update_db(self):
        # Connect to DataBase
        self.conn = sqlite3.connect("contacts.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT
                    )
                """)

        # Fetch data from database
        self.cursor.execute("SELECT name FROM contacts")
        self.contacts = self.cursor.fetchall()


class Files:

    @staticmethod
    def select_image():
        bot.image_file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])

    @staticmethod
    def select_pdf():
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if file_paths:
            bot.pdf_file_paths = list(file_paths)

    @staticmethod
    def select_driver_path():
        global driver_path
        driver_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
        if driver_path:
            print(f"Driver path: {driver_path}")

    @staticmethod
    def select_vcf():
        vcf_path = filedialog.askopenfilename(filetypes=[("VCF Files", "*.vcf")])
        if vcf_path:
            print(f"File path: {vcf_path}")
        return vcf_path


def main():
    global window, entry_new_contact, listbox_contacts

    def start_bot():
        def run_bot():
            bot.start()
            message = entry_message.get()
            if message:
                bot.send_message(message)
            if bot.image_file_path:
                bot.send_file(bot.image_file_path)
            if bot.pdf_file_path:
                bot.send_file(bot.pdf_file_path)
            bot.stop()

        # Start a new thread to process in the background
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.start()

    window = Tk()
    window.title("WhatsApp Bot")
    window.geometry("500x1000")  # window size

    button_select_driver = Button(window, text="Sürücü Yolu Seç", command=Files.select_driver_path)
    button_select_driver.pack()

    contactFrame = Frame(window)
    contactFrame.pack(pady="50")

    # Add contacts to listbox
    listbox_contacts = Listbox(contactFrame, selectmode="extended", width=30, height=20)
    for contact in contacts.contacts:
        listbox_contacts.insert('end', contact[0])

    listbox_contacts.grid(row=1, column=0)

    label_contacts = Label(contactFrame, text="Kişiler")
    label_contacts.grid(row=0, column=0)

    contactFrameTexts = Frame(contactFrame)
    contactFrameTexts.grid(padx="10", row=1, column=1)

    button_addVCF = Button(contactFrameTexts, text="Rehber Ekle (VCF)", command=contacts.readVCF, fg="green", width=15, height=2)
    button_addVCF.grid(row=0,column=0)

    button_reset_contacts = Button(contactFrameTexts, text="Sıfırla", command=contacts.reset_contacts, width=15, height=2, fg="red")
    button_reset_contacts.grid(row=0,column=1)

    button_remove_selected_contacts = Button(contactFrameTexts, text="Seçilenleri Sil",
                                             command=contacts.remove_selected_contacts,width=35, height=2)
    button_remove_selected_contacts.grid(row=1, column=0, columnspan=2)



    plusMinusbuttons = Frame(contactFrame)
    plusMinusbuttons.grid()
    label_new_contact = Label(plusMinusbuttons, text="Kişi Ekle:", width=10,height=2)
    label_new_contact.grid(row=0, column=0)
    entry_new_contact = Entry(plusMinusbuttons, width=11)
    entry_new_contact.grid(row=0, column=1)

    button_add_contact = Button(plusMinusbuttons, text="+", command=contacts.add_contact, width=3, height=1)
    button_add_contact.grid(row=0, column=2)




    label_message = Label(window, text="Mesaj:")
    label_message.pack()

    entry_message = Entry(window)
    entry_message.pack()

    button_start = Button(window, text="Başlat", command=start_bot, width=15, height=2)
    button_start.pack()

    button_select_image = Button(window, text="Resim Seç", command=Files.select_image,width=15, height=2)
    button_select_image.pack()

    button_select_pdf = Button(window, text="PDF Seç", command=Files.select_pdf,width=15, height=2)
    button_select_pdf.pack()

    # listbox_contacts.bind("<<ListboxSelect>>")
    window.mainloop()


driver_path = None
entry_new_contact = ""
listbox_contacts = None
bot = WhatsAppBot()
window = None

contacts = Contacts()

if __name__ == "__main__":
    main()
    contacts.close_contacts_db()
