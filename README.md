# Cheap-Flight-Fares-App
An application developed using Python that detect cheap flight fares using DBSCAN algorithm <br/>

The app performs the following functionalities:<br/>
1. Data acquisition using advanced web scraping techniques: Involves the use of important Python libraries: <br/>
    a.	Selenium - to automate web browsers    
    b.	PhantomJS – a headless browser ideal for data scraping
      
2. Parsing the DOM to extract the Pricing Data: <br/>
    a.	Use of the beautifulsoup library to extract the best heights based on the div class <br/>
    b.	Deduce the price of each flight using the height of the bar and the minimum price(obtained manually due to changes in the website)
    
3. Using Machine Learning to identify the cheap fares <br/>
    a.	Using the DBSCAN(Density-based Spatial Clustering of Applications with Noise) clustering algorithm - 
    https://practice2code.blogspot.in/2017/07/dbscan-clustering-algorithm.html

4.	Putting everything together to make an app
