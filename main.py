
import requests, itertools, sklearn, yaml
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup

code = 'AAPL'  # Example ticker code, replace with actual code as needed
response = requests.get(f'https://portfolioslab.com/symbol/{code}')
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")
header_element = soup.find(id='sharpe-ratio')
#print(header_element)
res = str(header_element.find_all('b')[2]).replace('<b>', '').replace('</b>', '')
print(res)