import requests, itertools, sklearn
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from tqdm.notebook import trange, tqdm

class IXIC_Parsor():
  def __init__(self, portfolio_list):
    self.market = '^IXIC'
    self.company_list = portfolio_list
    self.update()

  def update(self):
    columns = ['Sharpo', 'beta', 'trailingPE', 'forwardPE', 'shortRatio', 'marketCap', 'profitMargins', 'priceToBook', 'currentPrice', 'targetHighPrice', 'targetLowPrice', 'recommendationMean']
    self.info_table = pd.DataFrame(columns=columns)
    for code in tqdm(set(tuple(itertools.chain(*portfolio_lists.values())))):
      row_data = {'Update': False}
      df = yf.Ticker(code)
      for key in columns:
        if key not in df.info:
          row_data[key] = None
        else:
          row_data[key] = df.info[key]
      row_data['Sharpo'] = self.get_sharpo(code)
      self.info_table.loc[code] = row_data
    return self.info_table

  def get_sharpo(self, code):
    web = requests.get(f'https://portfolioslab.com/symbol/{code}')
    soup = BeautifulSoup(web.text, "html.parser")
    header_element = soup.find(id='sharpe-ratio')
    res = str(header_element.find_all('b')[1]).replace('<b>', '').replace('</b>', '')
    return float(res)

  def fit(self, features = ['forwardPE', 'trailingPE', 'beta', 'shortRatio', 'profitMargins']):
    X, y = self.info_table[features], self.info_table['Sharpo']
    model = sklearn.ensemble.RandomForestRegressor(random_state=42)
    model.fit(X, y)
    y_pred = model.predict(X)
    self.r2 = sklearn.metrics.r2_score(y, y_pred)
    print(f"R-squared score: {self.r2}")
    self.info_table['RiskProfit'] = y_pred * self.r2 + self.info_table['Sharpo'] * (1 - self.r2)
    return self.info_table.sort_values(by=['RiskProfit'], ascending=False)
