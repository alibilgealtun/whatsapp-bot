import sqlite3
from tkinter import filedialog, messagebox, Listbox, Entry
import customtkinter as ctk
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
import vobject

# -*- coding: utf-8 -*-


class WhatsAppBot:
    """WhatsApp Bot class for sending messages and files via WhatsApp Web."""

    def __init__(self):
        self.pdf_file_paths = None
        self.driver = None
        self.image_file_path = None
        self.pdf_file_path = None

    def start(self):
        try:
            if driver_path is None:
                Files.select_driver_path()

            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service)

            self.driver.get("https://web.whatsapp.com")
            time.sleep(15)  # Wait for the QR Scanning
        except Exception as e:
            print(f"An error occurred: {str(e)}")

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
    """Class to control contact list"""

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
    global root, entry_new_contact, listbox_contacts

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

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("dark-blue")  # or green,red whatever u want

    root = ctk.CTk()
    root.title("WhatsApp Bot")
    root.geometry("700x1000")  # window size

    contactFrame = ctk.CTkFrame(root)
    contactFrame.pack(pady=40, padx=40, fill="both")

    # Add contacts to listbox
    listbox_contacts = Listbox(contactFrame, width=30, height=20, selectmode="multiple", background="gray",
                               font=("Arial", 20))
    for contact in contacts.contacts:
        listbox_contacts.insert('end', contact[0])

    listbox_contacts.grid(row=1, column=3)

    label_contacts = ctk.CTkLabel(contactFrame, text="Kişiler", font=('Arial', 20))
    label_contacts.grid(row=0, column=3)

    contactFrameTexts = ctk.CTkFrame(contactFrame)
    contactFrameTexts.grid(padx="10", pady="10", row=1, column=4)

    button_addVCF = ctk.CTkButton(contactFrameTexts, text="Rehber Ekle (VCF)", command=contacts.readVCF, width=15,
                                  height=2, font=('Arial', 20), fg_color="green")
    button_addVCF.grid(row=0, column=0, padx=10, pady=10)

    button_reset_contacts = ctk.CTkButton(contactFrameTexts, text="Sıfırla", command=contacts.reset_contacts, width=15,
                                          height=2, font=('Arial', 20), fg_color="red")
    button_reset_contacts.grid(row=0, column=1, padx=10, pady=10)

    button_remove_selected_contacts = ctk.CTkButton(contactFrameTexts, text="Seçilenleri Sil",
                                                    command=contacts.remove_selected_contacts, width=35, height=2,
                                                    font=('Roboto', 20))
    button_remove_selected_contacts.grid(row=1, column=0, columnspan=2)

    plusMinusbuttons = ctk.CTkFrame(contactFrame)
    plusMinusbuttons.grid(row=2, column=3, pady=15)
    label_new_contact = ctk.CTkLabel(plusMinusbuttons, text="Kişi Ekle:", width=10, height=2, font=('Arial', 20))
    label_new_contact.grid(row=0, column=0, padx=15, pady=10)
    entry_new_contact = Entry(plusMinusbuttons, width=15, font=('Arial', 20), bg="gray")
    entry_new_contact.grid(row=0, column=1, padx=15, pady=10)

    button_add_contact = ctk.CTkButton(plusMinusbuttons, text=" + ", font=('Arial', 20), command=contacts.add_contact,
                                       width=10, height=2)
    button_add_contact.grid(row=0, column=2, padx=15, pady=10)

    sending_frame = ctk.CTkFrame(root)
    sending_frame.pack(pady=40, padx=40, fill="both")

    label_message = ctk.CTkLabel(sending_frame, text="Mesaj:", font=("Arial", 24), )
    label_message.grid(row=0, column=0)

    entry_message = Entry(sending_frame, width=50, font=("Arial", 20), bg="gray")
    entry_message.grid(row=0, column=1,columnspan=2, padx=20)

    button_select_image = ctk.CTkButton(sending_frame, text="Resim Seç", command=Files.select_image, width=15, height=2,
                                        font=("Arial", 24), anchor="center")
    button_select_image.grid(row=1, column=1, padx=20, pady=20)

    button_select_pdf = ctk.CTkButton(sending_frame, text="PDF Seç", command=Files.select_pdf, width=15, height=2,
                                      font=("Arial", 24), )
    button_select_pdf.grid(row=1,column=2, padx=20,pady=20)

    button_select_driver = ctk.CTkButton(root, text="Sürücü Yolu Seç", command=Files.select_driver_path, width=15,
                                         font=("Arial", 24),
                                         height=2)
    button_select_driver.pack(side="left", padx=100)

    button_start = ctk.CTkButton(root, text="Başlat", command=start_bot, width=15, height=2, font=("Arial", 24), )
    button_start.pack(side="right", padx=100)


    root.mainloop()


driver_path = None
entry_new_contact = ""
listbox_contacts = None
bot = WhatsAppBot()
root = None

contacts = Contacts()

if __name__ == "__main__":
    main()
    contacts.close_contacts_db()
