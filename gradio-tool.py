import gradio as gr
from PIL import Image
from utils import IXIC_Parsor, asyncio
import requests
import pandas as pd

class Functions():
    def __init__(self):
        self.df = None
        self.detail_col = ['Name', 'beta', 'Premium', 'forwardPE', 'shortRatio', 'currentPrice', 'targetLowPrice', 'targetHighPrice']

    def is_internet_connected(self):
        try:
            response = requests.get("https://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def update_dataframe(self, positive_reward, negative_reward, neutral_reward):
        if not self.is_internet_connected():
            gr.Info("Internet not are not connected.", duration=5)
            return None
        else:
            df = self.df.copy()
            if positive_reward:
                df = df[df['Premium'] > 1]
                positive_reward, negative_reward, neutral_reward = True, False, False
            if negative_reward:
                df = df[df['Premium'] < -1]
                positive_reward, negative_reward, neutral_reward = False, True, False
            if neutral_reward:
                df = df[(df['Premium'] >= -1) & (df['Premium'] <= 1)]
                positive_reward, negative_reward, neutral_reward = False, False, True


            return df.loc[:, self.detail_col], positive_reward, negative_reward, neutral_reward

    def analysis_portfolio(self):
        if not self.is_internet_connected():
            gr.Info("Internet not are not connected.", duration=5)
            return None, None, None
        else:
            portfolio_list = parser.load()
            asyncio.run(parser.update_async())
            self.df = parser.fit()
            categories = []
            for code in self.df.index:
                for category in portfolio_list:
                    if code in portfolio_list[category]:
                        categories.append(category); break
            self.df['categories'] = categories
            self.df['Name'] = self.df.index
            self.df['Premium'] = self.df['Premium'].round(2)
            return self.df, self.df.loc[:, self.detail_col], gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True)

    def add_stock(self, category, stock):
        portfolio_list, res = parser.add(category, stock)
        gr.Info(res, duration=5)
        if isinstance(self.df, pd.DataFrame):
            df = parser.info_table.copy()
            categories = []
            for code in df.index:
                for category in portfolio_list:
                    if code in portfolio_list[category]:
                        categories.append(category); break
            df['categories'] = categories
            df['Name'] = df.index
            df['Premium'] = df['Premium'].round(2)
            self.df = df.loc[:, self.detail_col]
        return self.df, transform_portfolio(portfolio_list), gr.update(value=""), gr.update(value="")

    def remove_stock(self, category, stock):
        portfolio_list, res = parser.remove(category, stock)
        gr.Info(res, duration=5)
        if isinstance(self.df, pd.DataFrame):
            df = parser.info_table.copy()
            categories = []
            for code in df.index:
                for category in portfolio_list:
                    if code in portfolio_list[category]:
                        categories.append(category); break
            df['categories'] = categories
            df['Name'] = df.index
            df['Premium'] = df['Premium'].round(2)
            self.df = df.loc[:, self.detail_col]
        return self.df, transform_portfolio(portfolio_list), gr.update(value=""), gr.update(value="")

def transform_portfolio(portfolio_dict):
    transformed = {}
    for category, stocks in portfolio_dict.items():
        transformed[category.upper()] = {
            "default": " | ".join(stocks) + "\n",
            "type": '\n'
        }
    return transformed

func = Functions()
parser = IXIC_Parsor('./portfolio_list.yaml')
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown(
                """
                # 股票觀察清單管理工具
                """
            )
            industry_input = gr.Textbox(label="Industry")
            stock_input = gr.Textbox(label="Stock")
            add_button = gr.Button("Add Stock")
            remove_button = gr.Button("Remove Stock")
    
            paramviewer = gr.ParamViewer(transform_portfolio(parser.load()),
                header='Portfolio List',
            )
            start_button = gr.Button("Update/Test")

        with gr.Column(scale=12):
            with gr.Tab("Overview"):
                scatter_plot = gr.ScatterPlot(x='Premium', y='beta', color='categories', height=420)

            with gr.Tab("Financial Wellness"):
                with gr.Row():
                    positive_reward = gr.Checkbox(label="Positive Reward", value=False, interactive=False)
                    negative_reward = gr.Checkbox(label="Negative Reward", value=False, interactive=False)
                    neutral_reward = gr.Checkbox(label="Neutral", value=False, interactive=False)
                dataframe = gr.DataFrame()

    positive_reward.change(func.update_dataframe, 
                        inputs= [positive_reward, negative_reward, neutral_reward],
                        outputs=[dataframe, positive_reward, negative_reward, neutral_reward])
    negative_reward.change(func.update_dataframe, 
                        inputs= [positive_reward, negative_reward, neutral_reward],
                        outputs=[dataframe, positive_reward, negative_reward, neutral_reward])
    neutral_reward.change(func.update_dataframe, 
                        inputs= [positive_reward, negative_reward, neutral_reward],
                        outputs=[dataframe, positive_reward, negative_reward, neutral_reward])
    start_button.click(func.analysis_portfolio, 
                        inputs= None, 
                        outputs=[scatter_plot, dataframe, 
                                 positive_reward, negative_reward, neutral_reward])
    add_button.click(func.add_stock, 
                     inputs=[industry_input, stock_input], 
                     outputs=[dataframe, paramviewer, industry_input, stock_input])
    remove_button.click(func.remove_stock, 
                        inputs=[industry_input, stock_input], 
                        outputs=[dataframe, paramviewer, industry_input, stock_input])
demo.launch()