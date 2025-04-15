# PortfolioLab-Parser
```python
portfolio_lists = {'silicon': ['NVDA','ARM', 'INTC', 'IBM', 'META', 'AMD', 'TXN', 'QCOM', 'AVGO', 'MU'],
          'robotics': ['BSX', 'TELA'],
          'fab': ['TSM', 'ASML', 'AMAT', 'INTC', 'AMKR'],
          'ai': ['XOVR', 'MSFT', 'META', 'GOOG'],
          'it/ot': ['MSFT', 'AMZN', 'GOOG'],
          'pda': ['AAPL', 'DELL', 'HPQ']
}
```
```python
from IPython.display import display_markdown

parsor = IXIC_Parsor(portfolio_list = portfolio_list)
df = parsor.fit()
display_markdown(f"### Goodness of Fit: {parsor.r2}\n" + df.to_markdown(), raw=True)
```
