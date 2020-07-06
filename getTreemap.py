#!/usr/bin/python3
#/opt/rh/rh-python36/root/usr/bin/python
from selenium import webdriver
from urllib import urlopen
from shutil import copyfileobj
from contextlib import closing
import time
import urllib2

if __name__ == '__main__':

    chromeOptions = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images":2}
    chromeOptions.add_experimental_option("prefs", prefs)
    chromeOptions.add_argument('headless');
    chromeOptions.add_argument('window-size=1920x1080');
    chromeOptions.add_argument('user-agent="Mozilla/5.0"')
    driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chromeOptions)

    finviz_request = "https://finviz.com/map.ashx?t=sec"
    driver.get(finviz_request)

    time.sleep(5)
    
    share_map = driver.find_element_by_class_name("zoom")
    share_map = share_map.find_elements_by_tag_name("span")[-1]
    
    # New anti-anti click measure
    # driver.execute_script("arguments[0].click();", share_map)
    webdriver.ActionChains(driver).move_to_element(share_map).click(share_map).perform()

    #share_map.click()
    modal_body = driver.find_element_by_id("modal-form")
    time.sleep(5)
    link = modal_body.find_element_by_tag_name("img").get_property("src")
    
    # New direct path
    path_out = "/home/vhost/www/CMELabDisplay/wwwroot/images/map_sp500.png"
    #path_out = "/home/analyticslab/CMELabDisplayScripts/images/map_sp500.png"

    req = urllib2.Request(link)
    req.add_header('User-Agent', 'Mozilla/5.0')

    with closing(urllib2.urlopen(req)) as in_stream:
        with open(path_out, 'wb') as out_file:
            copyfileobj(in_stream, out_file)

    time.sleep(5)
    
    request = "https://finviz.com/map.ashx?t=sec&st=w52"
    driver.get(request)
    time.sleep(5)

    share_map = driver.find_element_by_class_name("zoom")
    share_map = share_map.find_elements_by_tag_name("span")[-1]
    
    # New anti-anti click measure
    # driver.execute_script("arguments[0].click();", share_map)
    webdriver.ActionChains(driver).move_to_element(share_map).click(share_map).perform()

    #share_map.click()
    modal_body = driver.find_element_by_id("modal-body")
    time.sleep(5)
    link = modal_body.find_element_by_tag_name("img").get_property("src")
    
    # New direct path
    path_out = "/home/vhost/www/CMELabDisplay/wwwroot/images/map_sp500_1y.png"
    #path_out = "/home/analyticslab/CMELabDisplayScripts/images/map_sp500_1y.png"
    
    req = urllib2.Request(link)
    req.add_header('User-Agent', 'Mozilla/5.0')

    with closing(urllib2.urlopen(req)) as in_stream:
        with open(path_out, 'wb') as out_file:
            copyfileobj(in_stream, out_file)

    time.sleep(5)

    request = "https://finviz.com/map.ashx?t=sec&st=w26"
    driver.get(request)
    time.sleep(5)

    share_map = driver.find_element_by_class_name("zoom")
    share_map = share_map.find_elements_by_tag_name("span")[-1]
    
    # New anti-anti click measure
    # driver.execute_script("arguments[0].click();", share_map)
    webdriver.ActionChains(driver).move_to_element(share_map).click(share_map).perform()

    #share_map.click()
    modal_body = driver.find_element_by_id("modal-body")
    time.sleep(5)
    link = modal_body.find_element_by_tag_name("img").get_property("src")
    
    # New direct path
    path_out = "/home/vhost/www/CMELabDisplay/wwwroot/images/map_sp500_6m.png"
    #path_out = "/home/analyticslab/CMELabDisplayScripts/images/map_sp500_6m.png"
    
    req = urllib2.Request(link)
    req.add_header('User-Agent', 'Mozilla/5.0')

    with closing(urllib2.urlopen(req)) as in_stream:
        with open(path_out, 'wb') as out_file:
            copyfileobj(in_stream, out_file)

    driver.close()

