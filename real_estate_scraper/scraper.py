import httpx
from selectolax.parser import HTMLParser
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
import time
import re
import pathlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_price_data(p):
    """
    Cleans and converts the price data to integers.
    """
    p = [x for x in p if x.replace('$', '').replace(',', '').isdigit()]
    p = [int(x.replace('$', '').replace(',', '').replace('+', '')) for x in p]
    return p


def clean_sqft_data(s):
    """
    Cleans and converts the square footage data to integers.
    """
    s = [int(x.replace(' sqft', '').replace(',', '').strip()) for x in s if 'acre' not in x]
    return s


def get_page(u):
    """
    Send an HTTP request to the specified URL and return the HTTP response.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0'
    }

    page = httpx.get(url=u, headers=headers)
    status = {
        1: "Informational response",
        2: "Successful response",
        3: "Redirect",
        4: "Client error",
        5: "Server error",
    }.get(page.status_code // 100, "")

    if status != "Successful response":
        logging.error('Connection issue. Status: %s', status)
        exit()

    return page


def parse_data(html):
    """
    Extract relevant data from the HTML response and return it in a structured format.
    """
    df = html.css_first('#__NEXT_DATA__').text()
    data = {'Address': [], 'Price': [], 'Beds': [], 'Baths': [], 'Sqft': [], 'Price per Sqft': []}

    try:
        address = re.findall(r'"fullLocation":"([^"]+)"', df)
        data['Address'].extend(address)

        price = re.findall(r'"formattedPrice"\s*:\s*"([^"]+)"', df)
        cleaned_price = clean_price_data(price)
        data['Price'].extend(cleaned_price)

        bedrooms = re.findall(r'"bedrooms":{"formattedValue":"([^"]+)"', df)
        data['Beds'].extend(bedrooms)

        bathrooms = re.findall(r'"bathrooms":{"formattedValue":"([^"]+)"', df)
        data['Baths'].extend(bathrooms)

        sqft = re.findall(r'"formattedDimension":"([^"]+)"', df)
        cleaned_sqft = clean_sqft_data(sqft)
        data['Sqft'].extend(cleaned_sqft)

        for p, s in zip(cleaned_price, cleaned_sqft):
            price_per_sqft = p / s
            data['Price per Sqft'].append(round(price_per_sqft, 2))

    except AttributeError as ae:
        logging.error('Error parsing data: %s', ae)

    return data


def pagination(html):
    """
    Handle pagination to extract data from all available pages.
    """
    try:
        next_page_url = f"https://www.trulia.com{html.css_first('li[data-testid=pagination-next-page] a').attributes['href']}"
        while next_page_url:
            logging.info('Next page URL: %s', next_page_url)
            curr_resp = get_page(next_page_url)
            curr_html = HTMLParser(curr_resp.text)
            data = parse_data(curr_html)
            create_dataframe(data)
            next_page_url = f"https://www.trulia.com{curr_html.css_first('li[data-testid=pagination-next-page] a').attributes['href']}"
            time.sleep(5)
    except AttributeError:
        logging.info('No more pages.')


def create_dataframe(d):
    """
    Create a Pandas DataFrame from the extracted data and write it to a CSV file.
    """
    csvfile = pathlib.Path('neighborhoods_listings.csv')
    df = pd.DataFrame.from_dict(d, orient='index').transpose()
    df.to_csv('neighborhoods_listings.csv', mode='a', header=not csvfile.exists(), index=False)


def get_avg_price_data(t, data):
    """
    Calculate the average home price and average price per square foot for the specified town.
    """
    avg_data = {'Location': [t], 'Average Price': [], 'Average Price per SQFT': []}
    avg_price = round(sum(data['Price']) / len(data['Address']), 2)
    avg_price_per_sqft = round(sum(data['Price per Sqft']) / len(data['Address']), 2)
    avg_data['Average Price'].append(avg_price)
    avg_data['Average Price per SQFT'].append(avg_price_per_sqft)
    return avg_data


def avg_dataframe(avg):
    """
    Create a Pandas DataFrame from the average price data.
    """
    df = pd.DataFrame(avg, columns=['Location', 'Average Price', 'Average Price per SQFT'])
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    return df


def avg_data_to_csv(avg_data):
    """
    Write the average price data to a CSV file.
    """
    csvfile = pathlib.Path('AVG_DATA.csv')
    df = pd.DataFrame(avg_data, columns=['Location', 'Average Price', 'Average Price per SQFT'])
    df.to_csv('AVG_DATA.csv', mode='a', index=False, header=not csvfile.exists())


def avg_price_graph():
    """
    Create a bar graph of the average home prices using Matplotlib from CSV file.
    """
    data = pd.read_csv('AVG_DATA.csv')
    fig, ax = plt.subplots()
    plt.ticklabel_format(style='plain')
    ax.barh(data['Location'].values, data['Average Price'].values)
    ax.set_ylabel('Location', weight='bold')
    ax.set_xlabel('Price in USD', weight='bold')
    ax.set_title('Average Home Price', weight='bold')
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    fig.tight_layout()
    plt.show()


def avg_price_per_sqft_graph():
    """
    Create a bar graph of the average price per square foot using Matplotlib from CSV file.
    """
    data = pd.read_csv('AVG_DATA.csv')
    fig, ax = plt.subplots()
    plt.ticklabel_format(style='plain')
    ax.barh(data['Location'].values, data['Average Price per SQFT'].values)
    ax.set_ylabel('Location', weight='bold')
    ax.set_xlabel('Price in USD', weight='bold')
    ax.set_title('Average Price per Square Foot', weight='bold')
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    fig.tight_layout()
    plt.show()


def main():
    """
    Main function to orchestrate the scraping, data processing, and visualization.
    """
    cities = {
        'Greenville': 'SC',
        'Charlotte': 'NC',
        'Raleigh': 'NC',
        'Huntsville': 'AL',
        'Sarasota': 'FL',
        'Boise': 'ID',
        'Charleston': 'SC'
    }

    for city, state in cities.items():
        url = f"https://www.trulia.com/{state}/{city}/"
        resp = get_page(url)
        html = HTMLParser(resp.text)
        data = parse_data(html)
        data['Location'] = [f'{city}, {state}']
        create_dataframe(data)
        pagination(html)
        avg = get_avg_price_data(city, data)
        avg_dataframe(avg)
        avg_data_to_csv(avg)
        time.sleep(3)

    avg_price_graph()
    avg_price_per_sqft_graph()


if __name__ == '__main__':
    main()
