import asyncio
from utils import IXIC_Parsor
#from IPython.display import display_markdown

portfolio_list = {'silicon': ['NVDA','ARM', 'INTC', 'IBM', 'META', 'AMD', 'TXN', 'QCOM', 'AVGO', 'MU'],
          'robotics': ['BSX', 'TELA'],
          'fab': ['TSM', 'ASML', 'AMAT', 'INTC', 'AMKR'],
          'ai': ['XOVR', 'MSFT', 'META', 'GOOG'],
          'it/ot': ['MSFT', 'AMZN', 'GOOG'],
          'pda': ['AAPL', 'DELL', 'HPQ', 'META']
}

parser = IXIC_Parsor(portfolio_list = portfolio_list)
asyncio.run(parser.update_async())
df = parser.fit()
df.to_csv('output.csv', index=True)
#display_markdown(f"### Goodness of Fit: {parser.r2}\n" + df.to_markdown(), raw=True)
