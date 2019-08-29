import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dte
from flask.helpers import get_root_path
from finances.utils.database import ATTRIBUTES
from finances.app.layout import COLORS, get_color_class_name
from finances.app.account import Account

# Dash: http://127.0.0.1:8050/
ASSETS_PATH = os.path.join(get_root_path('__main__'), r'finances\app\assets')

DIR = ('C:/Users/hugo/OneDrive/Documents/SynologyDrive/Administrative/'
       'Finances/HSBC/Financial Analysis')
database = DIR + '/finance.db'



account = Account(database=database, account='HSBC UK')

app = dash.Dash(__name__, assets_folder=ASSETS_PATH)

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H2(
                            children=f'Last transaction date: {account.last_transaction_date:%d %b %Y}',
                            className='header'
                        ),
                        html.Br(),
                        html.Ul(
                            children=[
                                html.Li(
                                    children=[
                                        html.Span(children='Balance: '),
                                        html.Span(
                                            children=f'{account.balance:,.2f}',
                                            className=get_color_class_name(account.balance)
                                        )
                                    ]),
                                html.Li(
                                    children=[
                                        html.Span(
                                            children=f'Since beginning of {account.actual_month_end:%B %Y}: '
                                            f'{account.currency} '
                                        ),
                                        html.Span(
                                            children=f'{account.actual_month_pnl:,.2f}',
                                            className=get_color_class_name(account.actual_month_pnl)
                                        )
                                    ]),
                                html.Li(
                                    children=[
                                        html.Span(
                                            children=f'During {account.previous_month_end:%B %Y}: '
                                            f'{account.currency} '
                                        ),
                                        html.Span(
                                            children=f'{account.previous_month_pnl:,.2f}',
                                            className=get_color_class_name(account.previous_month_pnl)
                                        )
                                    ]),
                                html.Li(
                                    children=[
                                        html.Span(
                                            children=f'Monthly average: {account.currency} '
                                        ),
                                        html.Span(
                                            children=f'{account.avg_monthly_pnl:,.2f}',
                                            className=get_color_class_name(account.avg_monthly_pnl)
                                        )
                                    ])
                            ],
                            style=dict(
                                color=COLORS['text'],
                                fontSize='100%',
                                textAlign='left',
                                marginLeft=10
                            )
                        )
                    ],
                    className='three columns'
                ),
                html.Div(
                    children=[
                        html.H1(
                            children='Transactions Analysis',
                            style=dict(
                                color=COLORS['text'],
                                fontSize='300%',
                                textAlign='center'
                            )
                        )
                    ],
                    className='eight columns'
                ),
                html.Img(
                    src='/app/piggy_bank.png',
                    className='two columns',
                    style=dict(
                        height='10%',
                        width='10%',
                        float='right',
                        position='relative',
                        marginTop='10',
                        marginBottom='-10'
                    )
                )
            ],
            className='row'
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Graph(
                            id='bar',
                            figure=account.category_figure_bar
                        ),
                    ],
                    className='eight columns',
                    style=dict(marginTop=20)
                ),
                html.Div(
                    children=[
                        dcc.Graph(
                            id='total',
                            figure=account.total_figure_cumsum
                        ),
                    ],
                    className='four columns',
                    style=dict(marginTop=20)
                )
            ],
            className='row'
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Graph(id='sub_category_figure_bar'),
                    ],
                    className='eight columns',
                    style=dict(marginTop=20)
                ),
                html.Div(
                    children=[
                        html.H2(
                            children='Select category',
                            style=dict(
                                color=COLORS['text'],
                                fontSize='130%',
                                textAlign='left',
                                marginLeft=10
                            )
                        ),
                        dcc.RadioItems(
                            id='category_radio_item',
                            options=[dict(label=k, value=k) for k in account.categories],
                            style=dict(color=COLORS['text']),
                            value='Food & Drink'
                        )
                    ],
                    className='two columns',
                    style=dict(marginTop=20)
                ),
                html.Div(
                    children=[
                        html.H3(
                            children='Test',
                            style=dict(
                                color=COLORS['text'],
                                fontSize='100%',
                                textAlign='left'
                            )
                        )
                    ],
                    className='two columns'
                )
            ],
            className='row'
        ),
        html.Div(
            children=[
                dte.DataTable(
                    style_data={
                        'whiteSpace': 'normal',
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': COLORS['text'],
                        'border': '0px'
                    },
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }
                    ],
                    data=account.transaction_df.to_dict('records'),
                    editable=False,
                    filter_action='native',
                    sort_action='native',
                    sort_mode='multi',
                    selected_rows=[],
                    page_action='native',
                    page_current=0,
                    page_size=50,
                    columns=[
                        {'name': value,
                         'id': key,
                         'hideable': True} for key, value in ATTRIBUTES.items()
                    ],
                    style_cell={
                        'textAlign': 'left',
                        'color': COLORS['text'],
                        'boxShadow': '0 0'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(50, 50, 50)'
                        },
                        {
                            'if': {'column_id': 'amount'},
                            'textAlign': 'right',
                        }
                    ],
                    style_filter={
                        'backgroundColor': COLORS['text'],
                        'border': '0px'
                    },

                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'fontWeight': 'bold',
                        'border': '0px'
                    },
                    hidden_columns=['detail', 'method'],
                    locale_format={
                        'decimal': '.',
                        'group': ',',
                        'grouping': 3
                    },
                    style_table={
                        'width': '90%',
                        'marginLeft': '5%',
                        'marginRight': '5%'

                    },

                    id='datatable'
                )
            ],
            className='row'
        )
    ]
)


@app.callback(
    dash.dependencies.Output('sub_category_figure_bar', 'figure'),
    [dash.dependencies.Input('category_radio_item', 'value')])
def update_figure(category):
    return account.get_sub_category_figure_bar(category)


if __name__ == '__main__':
    app.run_server(debug=False)
