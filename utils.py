import requests, itertools, sklearn, aiohttp, asyncio, yaml
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup

class Portfolio():
    def __init__(self, config_path='./portfolio_list.yaml'):
        self.config_path = config_path

    def load(self): 
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def add(self, category, code):
        category = category.lower()
        with open(self.config_path, 'r') as f:
            loaded_portfolio_list = yaml.safe_load(f)
            if category not in loaded_portfolio_list:
                loaded_portfolio_list[category] = []
                res = f"[INFO] '{category}' category does not exist. Automatically created."
                print(res)
            if code not in loaded_portfolio_list[category]: 
                try:
                    yf.Ticker(code).info
                    loaded_portfolio_list[category].append(code)
                    res = f"[SUCCESS] Added stock '{code}' to category '{category}'."
                    print(res)
                except Exception as e:
                    res = f"[ERROR] Failed to add stock '{code}' to category '{category}': {e}"
                    print(res)
                    return loaded_portfolio_list
            else:
                res = f"[WARNING] Stock '{code}' already exists in category '{category}'."
                print(res)
        with open(self.config_path, 'w') as f:
            yaml.dump(loaded_portfolio_list, f, default_flow_style=False)
        return loaded_portfolio_list, res

    def remove(self, category, code):
        category = category.lower()
        with open(self.config_path, 'r') as f:
            loaded_portfolio_list = yaml.safe_load(f)
            if category in loaded_portfolio_list:
                if code in loaded_portfolio_list[category]:
                    loaded_portfolio_list[category].remove(code)
                    res = f"[SUCCESS] Removed stock '{code}' from category '{category}'."
                    print(res)
                    if not loaded_portfolio_list[category]:  # Remove industry if empty
                        del loaded_portfolio_list[category]
                        res = f"[INFO] category '{category}' is now empty and has been removed."
                        print(res)
                else:
                    res = f"[WARNING] Stock '{code}' not found in category '{category}'."
                    print(res)
            else:
                res = f"[ERROR] category '{category}' does not exist."
                print(res)
        with open(self.config_path, 'w') as f:
            yaml.dump(loaded_portfolio_list, f, default_flow_style=False)
        return loaded_portfolio_list, res

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
  def __init__(self, portfolio_list):
    self.market = '^IXIC'
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
