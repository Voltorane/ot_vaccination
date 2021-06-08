import os
import platform
import time
import datetime
import json
import re
if platform.system == "Windows":
    import winsound
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

user_data = None
with open('data.json', 'r') as f:
    user_data = json.load(f)

TIME_FROM = datetime.datetime.strptime(user_data["From"], "%H:%M")
TIME_TO = datetime.datetime.strptime(user_data["To"], "%H:%M")
BLACKLIST_PLACES = user_data["Blacklisted_places"]
MANUAL_INPUT = user_data["Manual Input"]

driver = webdriver.Chrome()
driver.get("https://onlinetermine.zollsoft.de/patientenTermine.php?uniqueident=6087dd08bd763")

def find_accordeon():
    '''
    When page is loading, accordeon is not showing up right away
    Function waits till accordeon shows up
    '''
    accordeon = None
    while True:
        try:
            accordeon = driver.find_element_by_xpath('/html/body/zollsoftapptermine/div/div/div[1]/div[3]/div/div[1]/div/div[2]/div')
            return accordeon
        except NoSuchElementException as e:
            pass


def fill_form():
    '''
    Fills all forms provided by user
    '''
    try:
        form = driver.find_element_by_id('patientendaten-div-form-e2')
        while True:
            try:
                form.click()
                break
            except:
                pass
        form.find_element_by_name('vn').send_keys(user_data["Vorname"])
        form.find_element_by_id('nn').send_keys(user_data["Nachname"])
        form.find_element_by_id('geb').send_keys(user_data["Geburtstag"])
        form.find_element_by_id('tel').send_keys(user_data["Tel"])
        form.find_element_by_id('email').send_keys(user_data["Mail"])
        driver.find_element_by_xpath('/html/body/zollsoftapptermine/div/div/div[1]/div[3]/div/div[3]/div/form/div[3]/div/table/tbody/tr/td[1]/span[1]/input').click()
        return True
    except:
        print("Something went wrong while filling the forms")
        return False

    
def vaccine_pass(text):
    for vaccine in user_data["avoided_vaccines"]:
        if text in vaccine:
            return False
    return True


def get_schedule_list():
    while True:
        driver.refresh()
        accordeon = find_accordeon()
        while len(accordeon.find_elements_by_class_name('accordion__item')) <= 0:
            driver.refresh()
            accordeon = find_accordeon()
            
        vaccines = accordeon.find_elements_by_class_name('accordion__item')
        text = ""
        schedule_list = ""
        for vaccine in vaccines:
            try:
                text = vaccine.find_element_by_tag_name('h3').text
                if vaccine_pass(text):
                    vaccine.click()
                    return vaccine.find_elements_by_class_name('besuchsgrund-tr')
            except NoSuchElementException as _:
                pass


def place_termin():
    if MANUAL_INPUT:
        duration = 0.2  # seconds
        freq = 440  # Hz
        try:
            if platform.system == "Linux":
                os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
            elif platform.system == "Windows":
                winsound.Beep(freq, duration)
        except:
            pass
        driver.switch_to.window(driver.current_window_handle)
    else:
        duration = 0.1  # seconds
        freq = 300  # Hz
        # Fill all forms from info provided and places window on top
        # IT DOES NOT PLACE THE VACCINATION TERMIN - USER MUST CLICK THE BUTTON AFTER CHECKING ALL THE PROVIDED INFO
        try:
            if platform.system == "Windows":
                winsound.Beep(freq, duration)
                fill_form()
                winsound.Beep(freq, duration)
                winsound.Beep(freq, duration)
                winsound.Beep(freq, duration)
            else:
                os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
                fill_form()
                os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
                os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
                os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
        except:
            pass
        driver.switch_to.window(driver.current_window_handle)
        input()

def choose_place(schedule_list):
    schedule_list = schedule_list
    while True:
        for schedule in schedule_list:
            blacklisted = False
            if schedule.text.split(' ')[0] in BLACKLIST_PLACES:
                blacklisted = True
            if not blacklisted:
                schedule.find_element_by_tag_name('input').click()
                blacklisted = False
                break
        if not blacklisted:
            print(schedule.text.split(' ')[0])
            break
        else:
            schedule_list = get_schedule_list()
            
def choose_time():  
    driver.find_element_by_xpath('/html/body/zollsoftapptermine/div/div/div[1]/div[2]/div/button[2]').click()
    date = ''
    while date == '':
        try:
            date = driver.find_element_by_id('termine-span-e2').text
        except NoSuchElementException as _:
            pass
    date_time_obj = datetime.datetime.strptime(date, '%d.%m.%Y')
    termine = driver.find_elements_by_class_name('termine-tr')
    for termin in termine:
        termin_text = termin.find_element_by_class_name('termine-span-e3')
        date_time_obj = datetime.datetime.strptime(re.findall(r"^[0-9]+:[0-9]+", termin_text.text)[0], "%H:%M")
        if date_time_obj >= TIME_FROM and date_time_obj <= TIME_TO:
            termin.find_element_by_class_name('termine-td-radio').click()
            break

    while driver.find_element_by_xpath('/html/body/zollsoftapptermine/div/div/div[1]/div[2]/div/button[2]').get_attribute('disabled') == 'true':
        pass
    driver.find_element_by_xpath('/html/body/zollsoftapptermine/div/div/div[1]/div[2]/div/button[2]').click()

def main():
    choose_place(get_schedule_list())
    choose_time()
    place_termin()

if __name__ == "__main__":
    main()