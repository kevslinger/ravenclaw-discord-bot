from selenium import webdriver
import os


def get_chromedriver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument('--no-gpu')
    options.add_argument('--sandbox')
    options.add_argument("start-maximized")
    options.binary_location = '/app/.apt/usr/bin/google-chrome'
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })
    driver = webdriver.Chrome(options=options,
                              executable_path='/app/.chromedriver/bin/chromedriver')
    return driver
