import os
from pathlib import Path, PurePath
import logging
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask.helpers import get_root_path
from .dash_app.account import Account
from .dash_app.layout import TAB_STYLE, TAB_SELECTED_STYLE
from .dash_app.content import (main_header, tab_balance, tab_category_breakdown,
                               tab_sub_category_breakdown, tab_transaction)

logger = logging.getLogger('finances.dash_app')

ASSETS_PATH = os.path.join(get_root_path('__main__'), r'finances\dash_app\assets')


def run_app(project_folder: str, database_name: str):
    """
    Run the app
    :param project_folder: folder of the project
    :param database_name: name of the database
    """
    database = Path(PurePath(project_folder, database_name))
    account_name = 'HSBC UK'  # Whren more accounts are supported, this will be selected via callback in the dash_app
    account = Account(database=database, account_name=account_name)
    app = dash.Dash(__name__, assets_folder=ASSETS_PATH)
    app.title = 'Transactions Analysis'
    app.layout = html.Div(
        children=[
            main_header(account),
            dcc.Tabs(
                children=[
                    dcc.Tab(label='Balance', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                            children=[tab_balance(account)]),
                    dcc.Tab(label='Category breakdown', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                            children=[tab_category_breakdown(account)]),
                    dcc.Tab(label='Sub-category breakdown', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                            children=[tab_sub_category_breakdown(account)]),
                    dcc.Tab(label='Transaction', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                            children=[tab_transaction(account)]),
                ]
            ),
        ]
    )

    @app.callback(
        Output('sub_category_figure_bar', 'figure'),
        [Input('category_radio_item', 'value')])
    def update_figure(category):
        return account.get_sub_category_figure_bar(category)

    logger.info(f'App is running in http://127.0.0.1:8050/')
    app.run_server(debug=False)
