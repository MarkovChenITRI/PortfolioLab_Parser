import requests, itertools, sklearn, aiohttp, asyncio, yaml
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup

def fetch_ticker_info(code, columns):
    df = yf.Ticker(code)
    row_data = {}
    for key in columns:
        row_data[key] = df.info.get(key, None)
    row_data['Sharpo'] = get_sharpo(code)
    return code, row_data

def get_sharpo(code):
    response = requests.get(f'https://portfolioslab.com/symbol/{code}')
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    header_element = soup.find(id='sharpe-ratio')
    res = str(header_element.find_all('b')[1]).replace('<b>', '').replace('</b>', '')
    return float(res)

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
    def __init__(self, config_path='./portfolio_list.yaml'):
        self.market = '^IXIC'
        self.info_table = None
        self.config_path = config_path

    async def update_async(self):
        self.columns = ['Sharpo', 'beta', 'trailingPE', 'forwardPE', 'shortRatio', 'marketCap', 'profitMargins', 'priceToBook', 'currentPrice', 'targetHighPrice', 'targetLowPrice', 'recommendationMean']
        self.info_table = pd.DataFrame(columns=self.columns)

        async with aiohttp.ClientSession() as session:
            tasks = [
                fetch_ticker_info_async(session, code, self.columns)
                for code in set(tuple(itertools.chain(*self.load().values())))
            ]
            results = await asyncio.gather(*tasks)

        for code, row_data in results:
            self.info_table.loc[code] = row_data
        return self.info_table

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
                    if isinstance(self.info_table, pd.DataFrame):
                        if code not in self.info_table.index:
                            code, row_data = fetch_ticker_info(code, self.columns)
                            self.info_table.loc[code] = row_data
                            self.fit()
                    
                except Exception as e:
                    res = f"[ERROR] Failed to add stock '{code}' to category '{category}': {e}"
                    print(res)
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
                    if isinstance(self.info_table, pd.DataFrame):
                        if code in self.info_table.index:
                            self.info_table = self.info_table.drop(index=code)
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

    def fit(self, features = ['forwardPE', 'trailingPE', 'beta', 'shortRatio', 'profitMargins']):
        X, y = self.info_table[features], self.info_table['Sharpo']
        self.model = sklearn.ensemble.RandomForestRegressor(random_state=42)
        self.model.fit(X, y)
        y_pred = self.model.predict(X)
        self.r2 = sklearn.metrics.r2_score(y, y_pred)
        print(f"R-squared score: {self.r2}")
        self.info_table['Premium'] = y_pred * self.r2 + self.info_table['Sharpo'] * (1 - self.r2)
        return self.info_table.sort_values(by=['Premium'], ascending=False)

