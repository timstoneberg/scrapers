#!/usr/bin/python3
#/opt/rh/rh-python36/root/usr/bin/python
from selenium import webdriver
from urllib import urlopen
from shutil import copyfileobj
from contextlib import closing
import time

if __name__ == '__main__':

    chromeOptions = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images":2}
    chromeOptions.add_experimental_option("prefs", prefs)
    chromeOptions.add_argument('headless');
    chromeOptions.add_argument('window-size=1920x1080');
    driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chromeOptions)

    request = "https://finviz.com/map.ashx?t=sec"
    driver.get(request)

    time.sleep(5)

    share_map = driver.find_element_by_class_name("zoom")
    share_map = share_map.find_elements_by_tag_name("span")[-1]
    share_map.click()
    modal_body = driver.find_element_by_id("modal-body")
    time.sleep(5)
    link = modal_body.find_element_by_tag_name("img").get_property("src")
    path_out = "/home/analyticslab/rise-display/map_sp500.png"
    with closing(urlopen(link)) as in_stream:
        with open(path_out, 'wb') as out_file:
            copyfileobj(in_stream, out_file)

    driver.close()
    driver.quit()

