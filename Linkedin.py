#!/usr/bin/env python
# coding: utf-8

# ### Web scrabed using the coded present on the link below
# https://maoviola.medium.com/a-complete-guide-to-web-scraping-linkedin-job-postings-ad290fcaa97f
# 
# ### Used the link below to write/append existing dataframe to an existing google sheet
# https://medium.com/@jb.ranchana/write-and-append-dataframes-to-google-sheets-in-python-f62479460cf0
# 
# ### link to the google sheet where we will be tracking job postings.
# https://docs.google.com/spreadsheets/d/1RnwjV0Qd_OdMWSRLoVsUOs_mKn5DEgMDOwD0Hhsc0Kg/edit#gid=0
# 
# ### Read and Write data in GS 
# https://aryanirani123.medium.com/read-and-write-data-in-google-sheets-using-python-and-the-google-sheets-api-6e206a242f20
# 
# ### Instructions on how to create a CRON
# https://www.jcchouinard.com/python-automation-with-cron-on-mac/#What_You_Will_Need

# In[169]:


from selenium import webdriver
import time
import pandas as pd
import os


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# In[170]:


url="https://www.linkedin.com/jobs/search/?currentJobId=3170092398&geoId=105149290&keywords=coop%20data%20analyst&location=Ontario%2C%20Canada&refresh=true"


# In[171]:



os.chdir('/Users/tony/Desktop/')


# In[172]:


#headless mode
options = webdriver.ChromeOptions()
options.add_argument("headless")
wd = webdriver.Chrome(options=options)
wd.get(url)

# # window popup
# wd = webdriver.Chrome()
# wd.get(url)


# In[173]:


# lists no. of job posting
import re
no_of_jobs = int(wd.find_element("css selector", "h1 > span").get_attribute("innerText"))

#no_of_jobs=int(re.sub('[^A-Za-z0-9]+', '', no_of_jobs))


# In[174]:


# scrolling for you
i = 2
while i <= int(no_of_jobs/25)+1: 
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    i = i + 1
    try:
        wd.find_element_by_xpath("/html/body/main/div/section/button").click()
        time.sleep(5)
    except:
        pass
        time.sleep(5)


# In[175]:


job_lists = wd.find_element('class name','jobs-search__results-list')
jobs = job_lists.find_elements('tag name','li') # return a list


# In[176]:


job_id= []
job_title = []
company_name = []
location = []
date = []
job_link = []
for job in jobs:
    job_id0 = job.get_attribute("data-id")
    job_id.append(job_id0)

    job_title0 = job.find_element('css selector','h3').get_attribute('innerText')
    job_title.append(job_title0)

    company_name0 = job.find_element('css selector','h4').get_attribute('innerText')
    company_name.append(company_name0)

    location0 = job.find_element('css selector',"[class='job-search-card__location']").get_attribute('innerText')
    location.append(location0)
   

    date0 = job.find_element('css selector','div>div>time').get_attribute('datetime')
    date.append(date0)

    job_link0 = job.find_element('css selector','a').get_attribute('href')
    job_link.append(job_link0)


# In[177]:


df=pd.DataFrame([])
df=pd.DataFrame({'Title':job_title,'Company_name':company_name,'Location':location,'Date':date,'Job Link':job_link})


# In[178]:


df


# In[179]:



import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

scopes = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]


# In[180]:


credentials = Credentials.from_service_account_file(filename='lucid-destiny-344212-cbbebad672a7.json',scopes=scopes)


# In[181]:


gc = gspread.authorize(credentials)

gauth = GoogleAuth()
drive = GoogleDrive(gauth)


# In[182]:


# # open a google sheet
# gs = gc.open_by_url('https://docs.google.com/spreadsheets/d/1RnwjV0Qd_OdMWSRLoVsUOs_mKn5DEgMDOwD0Hhsc0Kg/edit#gid=0')
# # select a work sheet from its name
# worksheet1 = gs.worksheet('Sheet1')

# # write to dataframe (first load)
# worksheet1.clear()
# set_with_dataframe(worksheet=worksheet1, dataframe=df, include_index=False,
# include_column_header=True)


# In[183]:


open_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1RnwjV0Qd_OdMWSRLoVsUOs_mKn5DEgMDOwD0Hhsc0Kg/edit#gid=0').sheet1   
data = open_sheet.get_all_records() 
df2=pd.DataFrame([])
df3=pd.DataFrame([])
df2=pd.DataFrame(data)


# In[184]:


df2


# In[185]:


df3=pd.concat([df2,df])
#print(len(df3))
#print(len(df3)-len(df3.drop_duplicates(subset=['Title','Company_name','Location','Date'])))
#df3.reset_index().drop_duplicates(subset=['Title','Company_name','Location','Date'])
df3.drop_duplicates(keep='first',inplace=True, subset=['Title','Company_name','Location','Date'])


# In[186]:


# # San
# df.sort_values(by='Title').head()


# # In[187]:


# # San
# df2[['Title','Company_name','Location','Date']].sort_values(by='Title').head()


# In[188]:


df.drop(['Job Link'],axis = 1).isin(df2[['Title','Company_name','Location','Date']])#.all(axis=1)


# In[189]:


df3_no_dups = df3.drop_duplicates(keep='first', subset=['Title','Company_name','Location','Date'])


# In[190]:


length=df3_no_dups[~df3_no_dups[['Title','Company_name','Location','Date']].isin(df2[['Title','Company_name','Location','Date']]).all(axis=1)]


# In[191]:


#df3_no_dups


# In[192]:




if len(length)!=0:
#     New_df=df3.drop_duplicates(subset=['Title','Company_name','Location','Date'],keep=False)
#     New_df['Title_and_name']=New_df['Title']+"="+New_df['Company_name']
#     New_df['Title_and_name'].to_string()
    
    mail_content = length.Title.to_string(index=False)
    sender_address = 'kaizenware.studios@gmail.com'
    sender_pass = 'efimdkbgzzhdckwd'
    receiver_address = ['sanford.6458@gmail.com','jessicadsouza97@gmail.com']

    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = ", ".join(receiver_address)
    message['Subject'] = 'Job Alerts'   

    
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    
    #print('Mail Sent')
    


# In[193]:


# worksheet1=sheet.worksheet('Sheet1')
# worksheet1.clear()
#worksheet1 = open_sheet.worksheet('Sheet1')
open_sheet.clear()
set_with_dataframe(worksheet=open_sheet, dataframe=df3_no_dups, include_index=False,include_column_header=True)

