import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# To avoid backend opening of file explorer
root = tk.Tk()
root.withdraw()


# Read GSTIN in given csv file

file_path = filedialog.askopenfilename(title="CSV File shall contain GSTIN as header",filetypes=[("CSV", "*.csv"), ("Text files","*.txt")])
df = pd.read_csv(file_path)
df_unique = df.drop_duplicates(subset=["GSTIN"], keep= "first").copy()


df_unique['Trade Name'] = ""
df_unique['GSTIN Status'] = ""
df_unique['Taxpayer Type'] = ""

# To launch chrome browser
s_browser = webdriver.ChromeOptions()
s_browser.add_experimental_option("detach", True)
browser = webdriver.Chrome(options=s_browser)


# To navigate the Search GSTN page
gst_url = "https://services.gst.gov.in/services/searchtp"
browser.get(gst_url)
browser.maximize_window()
time.sleep(1)

def wait_for_captcha():
    WebDriverWait(browser, 30).until(expected_conditions.visibility_of_element_located((By.ID,"imgCaptcha")))
    captcha_box = WebDriverWait(browser, 30).until(
                expected_conditions.presence_of_element_located((By.ID, "fo-captcha")))
    # while len(captcha_box.get_attribute("value")) < 6:
    #     time.sleep(10)
    # correct_captcha = WebDriverWait(browser,30).until(
    #         lambda browser: len(browser.find_element(By.ID, "fo-captcha").get_attribute("value")) >= 6)
    # captcha_box.clear()
    captcha_box.send_keys()
    start_time = time.time()
    while True:
        if len(captcha_box.get_attribute("value")) >= 6:
            return
        if time.time() - start_time > 29:
            captcha_box.clear()
            captcha_box.send_keys("123456")
            return
        time.sleep(0.5)       
    


def submit_all():    
       
    wait_for_captcha()
    submit_button = WebDriverWait(browser, 30).until(
        expected_conditions.element_to_be_clickable((By.ID, "lotsearch")))
    submit_button.click()

def collect_data(i):
    try:
        Trade_element =  WebDriverWait(browser, 5).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "div[data-ng-if='tradeFlag'] p:nth-of-type(2)"))
            )
        GSTIN_Status = WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH,"//*[@id='lottable']/div[2]/div[2]/div/div[2]/p[2]"))
            )
        TaxPayer_Type = WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH,"//*[@id='lottable']/div[2]/div[2]/div/div[3]/p[2]"))
            )

        Trade_name = Trade_element.text
        GSTIN_Status_name = GSTIN_Status.text
        TaxPayer_Typename = TaxPayer_Type.text

    except:
        Trade_name = "Not found"
        GSTIN_Status_name = "Not found"
        TaxPayer_Typename = "Not found"


    df_unique.loc[df_unique['GSTIN'] == i , 'Trade Name' ] = Trade_name
    df_unique.loc[df_unique['GSTIN'] == i , 'GSTIN Status' ] = GSTIN_Status_name
    df_unique.loc[df_unique['GSTIN'] == i , 'Taxpayer Type' ] = TaxPayer_Typename


def check_captcha_err():
    try:
        #captcha_error_locator = browser.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[1]/form/div[2]/div/div/span" )
        captcha_err_msg = WebDriverWait(browser, 1).until(
        expected_conditions.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[1]/form/div[2]/div/div/span" )))
        return True
    except:
        return False


# Main Engine
for i in df_unique['GSTIN']:
    gst_input = browser.find_element(By.ID, "for_gstin")
    gst_input.clear()
    gst_input.send_keys(i)
    
    while True:
        submit_all()
        if not check_captcha_err():
            break  
        
    collect_data(i)

browser.quit()

# To get CSV File
data_set = pd.DataFrame(df_unique, columns=["GSTIN","Trade Name","GSTIN Status","TaxPayer Type"])
#file_path = filedialog.asksaveasfilename(title="Save File", defaultextension=".csv", filetypes=[("CSV", "*.csv")])

validated_file = f"{os.path.dirname(file_path)}{"/Validated_file.csv"}"
data_set.to_csv(validated_file, index = False)
