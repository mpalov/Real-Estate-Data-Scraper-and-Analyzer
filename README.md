# Real Estate Data Scraper and Analyzer

This repository contains a Python project designed to scrape real estate listings from Trulia, extract relevant data, and generate visualizations of average home prices and average prices per square foot for specified cities. The data is saved to CSV files for further analysis and use.

## Features

- Scrapes real estate listings from Trulia for specified cities.
- Extracts data such as address, price, number of bedrooms and bathrooms, square footage, and price per square foot.
- Handles pagination to scrape data from multiple pages.
- Cleans and processes the scraped data.
- Saves the data to CSV files.
- Calculates average home prices and average prices per square foot for each city.
- Generates bar graphs visualizing the average home prices and average prices per square foot.

## Prerequisites
- selectolax
- httpx
- pandas
- matplotlib
  
## Usage

Real estate market analysis: The project provides valuable insights into the real estate market in various cities,
allowing users to compare prices, identify trends, and make informed decisions when buying or selling properties.

## Data collection: 
The project automates the process of collecting real estate data, saving time and effort for researchers, analysts, and investors who need access to this data.

![image](https://github.com/mpalov/Real-Estate-Data-Scraper-and-Analyzer/blob/main/real_estate_scraper/images/441383854_776569600956864_2564870580226518665_n.png)

![image](https://github.com/mpalov/Real-Estate-Data-Scraper-and-Analyzer/blob/main/real_estate_scraper/images/441544814_446133771723642_327457743471925701_n.png)

## Data Output
The scraped data and average price data are saved to the following CSV files:

- neighborhoods_listings.csv: Contains the detailed listings data.
- AVG_DATA.csv: Contains the average home prices and average prices per square foot for each city.

Graphs

The script generates two types of bar graphs:
- Average Home Price Graph: Shows the average home price for each city.
- Average Price per Square Foot Graph: Shows the average price per square foot for each city.
- These graphs are displayed using Matplotlib.

## License
This project is licensed under the MIT License. See the [LICENSE](Real-Estate-Data-Scraper-and-Analyzer/LICENSE) file for details.

## Note
Additionally, this project is for educational purposes only and should not be used for commercial purposes without permission from Trulia.com.
