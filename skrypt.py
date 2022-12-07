from selenium.webdriver.firefox.service import Service
import sys
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
import base64
import codecs
import selenium
from twocaptcha import TwoCaptcha

#Initializing firefox browser and pointing It to 6obcy website
def init():
    new_driver_path='/bin/geckodriver'
    serv = Service(new_driver_path)
    browser=selenium.webdriver.Firefox(service=serv)
    browser.get('https://6obcy.org/')
    browser.find_element(By.ID,"intro-start").click()
    return browser

#Downloads capcha from 6obcy as an image, and sends It to 2capcha API to retrieve a response
def capcha(browser,solv):
    while browser.find_elements(By.CLASS_NAME,"caper-image-holder"): #while captcha is visible
        based64=browser.find_element(By.CLASS_NAME,'caper-image-holder').get_attribute('src')[22:] #Image is base64encoded and put in an image src parameter
        f=open("capcha.jpg","wb")
        f.write(base64.decodebytes(codecs.encode(based64)))
        f.close()
        print("WRITTEN")
        #Sometimes solv.normal returns "Capcha Unsolvable" error
        try:
            print("TRYY")
            result=solv.normal('capcha.jpg')
            print(result['code'])
            browser.find_elements(By.CLASS_NAME,"caper-solution-input")[0].send_keys(result['code'])
            browser.find_elements(By.CSS_SELECTOR,".sd-interface button")[1].click() #Zatwierdz button is clicked
        except Exception as e:
            print(e)
        if browser.find_elements(By.CLASS_NAME,"caper-wrong-field"):
            browser.find_elements(By.CSS_SELECTOR,".sd-interface button")[0].click()

#Sends all newly received messages to the other browser
def sending(bmain,baux,counter):
    wiadom=bmain.find_elements(By.CSS_SELECTOR,".log-stranger .log-msg-text")
    while len(wiadom)>counter and bmain.find_elements(By.CLASS_NAME,"log-dis-stranger")[0].is_displayed()==False:
        print("no i mamy ze tak powiem....")
        baux.find_element(By.ID,"box-interface-input").send_keys(wiadom[counter].text)
        baux.find_element(By.CLASS_NAME,"o-send").click()
        counter=counter+1
    return counter

#When either of 2 sides decides to disconnect, find a new chat patner for both of them
def rematch(bmain,baux):
    #It takes 1 escape button click for the disconnected side to find a new partner and 3 clicks for the still-connected side
    if bmain.find_elements(By.CLASS_NAME,"log-disconnected")[0].is_displayed():
        baux.find_element(By.CLASS_NAME,"o-esc").click()
        baux.find_element(By.CLASS_NAME,"o-esc").click()
        if baux.find_elements(By.CLASS_NAME,"sd-unit"):
            #There is an anti-bot mechanism present on the website that displays a warning (class sd-unit)
            #when you are trying to disconnect from newly initiated conversation. This if statement gets rid of this
            # pop-up and waits the time necessary to switch conversation (5s) , then initiates the "quitting sequence" again
            baux.find_element(By.CSS_SELECTOR,".sd-unit button").click()
            time.sleep(5)
            baux.find_element(By.CLASS_NAME,"o-esc").click()
            baux.find_element(By.CLASS_NAME,"o-esc").click()
        bmain.find_element(By.CLASS_NAME,"o-esc").click()
        baux.find_element(By.CLASS_NAME,"o-esc").click()
def main():
    if len(sys.argv)!=2:
        sys.exit("Usage: python skrypt.py <Your_2CAPCHA_API_KEY>")
    API=sys.argv[1]
    solver=TwoCaptcha(API)
    b1=init()
    b2=init()
    while 1:
        capcha(b1,solver)
        capcha(b2,solver)
        # Variable counter determines how many messages has each of the browser received. Faciliates the copying process in sending
        counter1=0
        counter2=0
        #Waiting until both of the browsers have found a partner
        while b1.find_element(By.ID,"log-searching-global").is_displayed() or b2.find_element(By.ID,"log-searching-global").is_displayed():
            pass
        #exchanging messages until on of the sides disconnects
        while b1.find_elements(By.CLASS_NAME,"log-dis-stranger")[0].is_displayed()==False and b2.find_elements(By.CLASS_NAME,"log-dis-stranger")[0].is_displayed()==False:
           counter1=sending(b1,b2,counter1)
           counter2=sending(b2,b1,counter2)
        rematch(b1,b2)
        rematch(b2,b1)
if __name__=="__main__":
    main()



