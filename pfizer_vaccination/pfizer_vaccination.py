import os
import sys
import platform
if platform.system == "Windows":
    import winsound
import configparser

import telethon.sync
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
PeerChannel
)

from urlextract import URLExtract
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

import gtts
from playsound import playsound

# Reading Configs
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)
client.start()
print("Client Created")
# Ensure you're authorized
if not client.is_user_authorized():
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))

user_input_channel = "https://t.me/corona_impftermine_muc"
# user_input_channel = "https://t.me/test1234678910"

if user_input_channel.isdigit():
    entity = PeerChannel(int(user_input_channel))
else:
    entity = user_input_channel

my_channel = client.get_entity(entity)

def handle_pfizer_call(link):
    driver = webdriver.Chrome()
    driver.get(link)
    while True:
        try:
            driver.find_element_by_xpath('/html/body/div[6]/div/div[2]/div/div/div/div[2]/div/div[2]/div[1]/div/div[3]/div[2]/select/option[3]').click()
            break
        except NoSuchElementException as e:
            pass
    while True:
        try:
            # driver.find_element_by_id('booking_motive').click()
            if config['Pfizer']['private_insurance']:
                select = Select(driver.find_element_by_id('booking_insurance_sector'))
                select.select_by_visible_text('Privat versichert')
                # driver.find_element_by_id('booking_insurance_sector').click()
            break
        except NoSuchElementException as e:
            print(e.with_traceback)
        
    while True:
        try:
            select = Select(driver.find_element_by_id('booking_motive'))
            select.select_by_visible_text('Erstimpfung Covid-19 (BioNTech-Pfizer)')
            # driver.find_element_by_id('booking_motive').click()
            break
        except NoSuchElementException as e:
            print(e.with_traceback)
    
    duration = 0.2  # seconds
    freq = 300  # Hz     
    try:
        if platform.system == "Windows":
            winsound.Beep(freq, duration)
            winsound.Beep(freq, duration)
            # winsound.Beep(freq, duration)
            # winsound.Beep(freq, duration)
        else:
            os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
            os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
            # os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
            # os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
    except:
        pass
    driver.switch_to.window(driver.current_window_handle)
    tts = gtts.gTTS("Please choose date for your Pfizer vaccine, master")
    tts.save("p.mp3")
    playsound("p.mp3")
    os.remove("p.mp3")
    client.disconnect()
    input()

@client.on(events.NewMessage(my_channel))
def handler(event):
    if 'BioNTech' in event.message.message:
        urls = URLExtract().find_urls(event.message.message)
        for url in urls:
            if "doctolib" in url:
                handle_pfizer_call(url)
client.run_until_disconnected()

