# -*- coding: utf-8 -*-

#download chromedriver (http://chromedriver.chromium.org/downloads)
chromedriver_path=u'C:\ProgramData\Anaconda3\conda-meta\chromedriver.exe'

#import requests 
from bs4 import BeautifulSoup
import pandas as pd
import re

#https://morvanzhou.github.io/tutorials/data-manipulation/scraping/5-01-selenium/
from selenium import webdriver
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.by import By
#from time import sleep
import time
import pickle

# 剔除list中的重複項
def remove_dup(x):
  return list(dict.fromkeys(x))

'''
log in facebook
'''
your_email=str(input('email: '))
your_password=str(input('password: '))

driver = webdriver.Chrome(chromedriver_path)   
driver.get("https://www.facebook.com/")
driver.find_element_by_css_selector("input#email").send_keys(your_email) # your email
driver.find_element_by_css_selector("input#pass").send_keys(your_password) # your password
driver.find_element_by_css_selector("#u_0_2").click() # log in

#手動允許開放權限，基本上只要按過一次之後就不會出現了
                                    
def links(fanpage):                                    
    driver.get(fanpage) # enter fan page (take ATCC as example)
    #sleep(5)

    '''
    scroll down to get more posts
    '''
    SCROLL_PAUSE_TIME = 2
    post_height=10000 # 想擷取多少篇貼文，越大越多篇
    
    while True:
        driver.execute_script("window.scrollTo(0, window.scrollY + 2000)") # Scroll down to bottom
        time.sleep(SCROLL_PAUSE_TIME) # Wait to load page
    
        new_height = driver.execute_script("return document.body.scrollHeight")
        print(new_height)
        if new_height >= post_height: 
            break

    '''
    抓粉專各貼文的按讚粉絲連結頁
    '''
    pageSource = driver.page_source  
    soup=BeautifulSoup(pageSource)
    
    links=[]
    regex = re.compile(r'href=*ft_ent_identifier=*；av=\d+') # link format
    first=soup.select("._66lg") # 第一層
    for f in first:    
        second=f.select('a[href^="/ufi/reaction/profile/browser/"]') #第二層
        for s in second:
            ans=('https://www.facebook.com/%s' % s.get('href'))
            links.append(ans)
            #print(ans)
        
    links_final=remove_dup(links) #因每個link會被抓到2次，剔除重複項
    
    return links_final

'''
抓貼文按讚粉絲的id
'''   
def article(links_final):
    try:
        links_final=links_final[:10]
    except:
        links_final= links_final

    ids_all=[] 
    for link in links_final:
        driver.get(link)
    
        LOAD_MORE_BUTTON_XPATH = "//div[@id='reaction_profile_pager1']//div//a[@class='pam uiBoxLightblue uiMorePagerPrimary'][contains(text(),'更多')]"
    
        while True:
            try:
                loadMoreButton = driver.find_element_by_xpath(LOAD_MORE_BUTTON_XPATH)
                time.sleep(2)
                loadMoreButton.click()
                time.sleep(5)                                        
            except:                
                #print(e)
                break
        print("Complete")
        time.sleep(10)
    
        pageSource1 = driver.page_source  
        soup1=BeautifulSoup(pageSource1)
        
        #找出貼文按讚粉絲的id
        ids=[]
        regex = re.compile(r'id=(\d+)') # id format
        first=soup1.select("._5i_q") # 第一層
        
        for f in first:
            second=f.select('a[href^="https://www.facebook.com/"]') #第二層
            for s in second:
                match = regex.search(str(s)) # match id format
                ids.append(match.group(1)) # group(0)=>'id'；group(1)=>一串id數字
                #print(match.group(1))
        
        ids_final=remove_dup(ids) #因每個id會被抓到2次，剔除重複項
        ids_all.append(ids_final)
    
    return ids_all

'''
save file
'''
def save(links_final, ids_all, num):
    # save all result(list)
    
    with open('ids_%d'%num, 'wb') as fp:
        pickle.dump(ids_all, fp)
    
    #with open ('tsaiingwen', 'rb') as fp:
        #ids_all = pickle.load(fp)
    
    # save id
    # 將不同貼文的id整理到同一個list
    ids_all_final=[]
    for i in ids_all:
        for j in i:
            ids_all_final.append(j)
    
    ids_all_final_1=remove_dup(ids_all_final)
    
    print(ids_all_final_1)
    ids_all_final_df=pd.DataFrame(ids_all_final_1)
    
    ids_all_final_df.to_csv('all_ids_%d.csv' % num) #10675；24165；
        
    #save links
    with open('links_%d'%num, 'wb') as fp:
        pickle.dump(links_final, fp)

    print(num)

'''
主程式
'''
fanpages=pd.read_csv('fanpages_50.csv')
for num in range(len(fanpages)):
    fanpage=fanpages[num]

    links_final=links(fanpage)
    ids_all=article(links_final)
    save(links_final, ids_all, num)
