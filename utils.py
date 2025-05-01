import requests, itertools, sklearn, aiohttp, asyncio
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from tqdm import tqdm

async def fetch_ticker_info_async(session, code, columns):
    df = yf.Ticker(code)
    row_data = {}
    for key in columns:
        row_data[key] = df.info.get(key, None)
    row_data['Sharpo'] = await get_sharpo_async(session, code)
    return code, row_data

async def get_sharpo_async(session, code):
    async with session.get(f'https://portfolioslab.com/symbol/{code}') as response:
        text = await response.text()
        soup = BeautifulSoup(text, "html.parser")
        header_element = soup.find(id='sharpe-ratio')
        res = str(header_element.find_all('b')[1]).replace('<b>', '').replace('</b>', '')
        return float(res)

class IXIC_Parsor():
  def __init__(self, portfolio_list, tqdm_provider=tqdm):
    self.market = '^IXIC'
    self.tqdm_provider = tqdm_provider
    self.company_list = portfolio_list

  async def update_async(self):
      columns = ['Sharpo', 'beta', 'trailingPE', 'forwardPE', 'shortRatio', 'marketCap', 'profitMargins', 'priceToBook', 'currentPrice', 'targetHighPrice', 'targetLowPrice', 'recommendationMean']
      self.info_table = pd.DataFrame(columns=columns)

      async with aiohttp.ClientSession() as session:
          tasks = [
              fetch_ticker_info_async(session, code, columns)
              for code in set(tuple(itertools.chain(*self.company_list.values())))
          ]
          results = await asyncio.gather(*tasks)

      for code, row_data in results:
          self.info_table.loc[code] = row_data
      return self.info_table


  def fit(self, features = ['forwardPE', 'trailingPE', 'beta', 'shortRatio', 'profitMargins']):
    X, y = self.info_table[features], self.info_table['Sharpo']
    model = sklearn.ensemble.RandomForestRegressor(random_state=42)
    model.fit(X, y)
    y_pred = model.predict(X)
    self.r2 = sklearn.metrics.r2_score(y, y_pred)
    print(f"R-squared score: {self.r2}")
    self.info_table['Premium'] = y_pred * self.r2 + self.info_table['Sharpo'] * (1 - self.r2)
    return self.info_table.sort_values(by=['Premium'], ascending=False)
