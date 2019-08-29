import numpy as np
from pandas.tseries.offsets import MonthEnd
from typing import Union
from pathlib import Path
from finances.utils.database import load_all_transactions
from finances.utils.tools import replace_none
from finances.app.layout import generate_layout, get_trace
import cufflinks as cf

cf.go_offline()


class Account:

    def __init__(self, database: Union[Path, str], account: str):
        self.database = database
        self.account = account
        self._process_data()

    def _process_data(self):
        transaction_df = load_all_transactions(self.database, self.account)
        transaction_df['month_end'] = transaction_df['date'] + MonthEnd(1)
        transaction_df['sub_category'] = transaction_df['sub_category'].apply(replace_none)
        self.total_df = transaction_df.groupby('month_end').agg({'amount': np.sum}).sort_index()
        self.transaction_df = transaction_df
        self._summarize()
        self._get_figures()

    def _summarize(self):
        self.currency = self.transaction_df.iloc[0]['currency']
        self.categories = set(self.transaction_df['category'])
        self.last_transaction_date = self.transaction_df['date'].max()
        self.balance = self.transaction_df['amount'].sum()
        self.actual_month_end = self.total_df.index[-1]
        self.actual_month_pnl = self.total_df.loc[self.actual_month_end, 'amount']
        self.previous_month_end = self.total_df.index[-2]
        self.previous_month_pnl = self.total_df.loc[self.previous_month_end, 'amount']
        self.avg_monthly_pnl = self.total_df[:-1]['amount'].sum() / len(self.total_df[:-1])

    def _get_figures(self):
        total_figure_cumsum = self.total_df.cumsum().iplot(asFigure=True)
        total_figure_cumsum['layout'] = generate_layout(title='Total Balance')
        self.total_figure_cumsum = total_figure_cumsum
        category_figure_bar = (self.transaction_df
                               .pivot_table(index='month_end', columns='category', values='amount', aggfunc=np.sum,
                                            fill_value=0)
                               .iplot(kind='bar', barmode='group', asFigure=True))
        category_figure_bar['layout'] = generate_layout(title='All Transactions')
        category_figure_bar.add_trace(get_trace(self.total_df))
        self.category_figure_bar = category_figure_bar

    def get_sub_category_figure_bar(self, category: str):
        sub_category_df = self.transaction_df[self.transaction_df['category'] == category]
        sub_category_figure_bar = (sub_category_df
                                   .pivot_table(index='month_end', columns='sub_category', values='amount',
                                                aggfunc=np.sum, fill_value=0)
                                   .iplot(kind='bar', barmode='group', asFigure=True))
        sub_category_total_df = sub_category_df.groupby('month_end').agg({'amount': np.sum})
        sub_category_figure_bar['layout'] = generate_layout(title=category)
        sub_category_figure_bar.add_trace(get_trace(sub_category_total_df))
        return sub_category_figure_bar
