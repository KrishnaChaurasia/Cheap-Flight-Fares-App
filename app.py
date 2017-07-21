# -*- coding: utf-8 -*-
"""
Created on Tues Jul 18 11:00:29 2017

@author: Krishna Chaurasia

"""

# The div class needs to be changed at aprropriate places before executing

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

import schedule
import time

def checkFlights():
    # Initialize the source URL
    url = "https://www.google.com/flights/explore/#explore;f=JFK,EWR,LGA;t=r-Europe-0x46ed8886cfadda85%253A0x72ef99e6b3fcf079;li=8;lx=12;d=2017-07-27"
    
    # Initialize the PhantomJS browser with appropriate parameters
    # such as User Agent and fetch the data using Selenium
    driver = webdriver.PhantomJS()
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36")
    driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true'])
    driver.implicitly_wait(20)
    driver.get(url)

	# Wait to allow AJAX request to return a reply
    wait = WebDriverWait(driver, 20)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.A1UDLMB-v-c")))

    # Use beautiful soup for data for parsing the DOM
    s = BeautifulSoup(driver.page_source, "lxml")

    # Problem due to changes in the website, so applied manually later
    # The div class no more has the price value now
    bestPriceTags = s.find_all('div', 'A1UDLMB-w-f')
    if(len(bestPriceTags) < 4):
        print('Failed to Load Page Data')
        sys.exit(0)
    else:
        print("Page Data Successfully Loaded!")

    for tag in bestPriceTags:
        try:
            bestPrices.append(int(tag.text.replace('$', '').replace(',', '')))
        except:
            print()
    # Fix it manually using the price displayed for the lowest bar in the URL
    bestPrice = 367

    # Find the best height, the div class needs to be changed before running
    bestHeightTags = s.find_all('div', 'A1UDLMB-w-f')
    bestHeights = []
    for tag in bestHeightTags:
        try:
            bestHeights.append(float(tag.attrs['style'].split('height:')[1].replace('px;', '')))
        except:
            print()

    bestHeight = bestHeights[0]

    # Price of each flights is deduced based on the height of the bar
    pricePerHeight = bestPrice / bestHeight

    # list of information for all the cities in the page
    cities = s.findAll('div', 'A1UDLMB-w-o')

    # Calculate the price for each city by extracting the height for each city
    hlist = []
    for bar in cities[0].findAll('div', 'A1UDLMB-w-x'):
        hlist.append(float(bar['style'].split('height: ')[1].replace('px;', '')) * pricePerHeight)

    # Create the dataframe for further analysis
    fares = pd.DataFrame(hlist, columns = ['price'])
    #fares.sort_values('price', inplace=True)
    fares.head()

    # Visualize the fares using the scatter plot
    fig, axes = plt.subplots(figsize=(15, 8))
    plt.scatter(np.arange(len(fares['price'])), fares['price'])
    plt.show()

    px = [x for x in fares['price']]
    ff = pd.DataFrame(px, columns=['fare']).reset_index()
    ff.head()

    # Normalize the data points as (x - mean) / std
    X = StandardScaler().fit_transform(ff)

    # Apply the DBSCAN algorithm with proper parameters on the normalized data
    db = DBSCAN(eps = 0.5, min_samples=1).fit(X)

    # Clusters' labels of the DBSCAN results
    labels = db.labels_
    clusters = len(set(labels))
    uniqueLabels = set(labels)

    # Set the color map for the plot
    colors = plt.cm.Spectral(np.linspace(0, 1, len(uniqueLabels)))

    # Apply unique color to each cluster
    plt.subplots(figsize=(15, 8))
    for k, c in zip(uniqueLabels, colors):
        classMemberMask = (labels == k)
        xy = X[classMemberMask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor = c, markeredgecolor = 'k', markersize = 14)

    plt.title('Total Clusters : {}'.format(clusters), fontsize = 14, y = 1.01)
    plt.show()

    # Merge the cluster id with each of the fares
    pf = pd.concat([ff, pd.DataFrame(db.labels_,columns=['cluster'])], axis=1)

    # Find the count of each of the clusters
    rf = pf.groupby('cluster')['fare'].agg(['min','count']).sort_values('min', ascending=True)

    # If number of clusters is more than 1 and
    # cluster min is equal to the lowest price fare and
    #  cluster size if less than 10th percentile and
    # min cluster price is atleast $100 less than the next lowest priced cluster
    # then generate the alert
    if clusters > 1 \
        and ff['fare'].min() == rf.iloc[0]['min'] \
        and rf.iloc[0]['count'] < rf['count'].quantile(.10) \
        and rf.iloc[0]['fare'] + 100 < rf.iloc[1]['fare']:
        city = s.find('span', 'A1UDLMB-v-c').text
        fare = s.find('div', 'A1UDLMB-w-e').text
        print('Opprtunity to book flights!', city, ' ', fare)
    else:
        print('no alert triggered')

    # run the script after every 10 minutes
    schedule.every(10).minutes.do(checkFlights)
    while(1):
        schedule.run_pending()
        time.sleep(1)

print("Successfully build!")
checkFlights()