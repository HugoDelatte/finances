import dash_core_components as dcc
import dash_html_components as html
import dash_table as dte
from ..database.database import ATTRIBUTES
from ..dash_app.account import Account


def get_color_class_name(number):
    """
    Find the color css class to color a number
    :param number: number
    :return: red or green css class
    """
    if number >= 0:
        return 'green'
    else:
        return 'red'


def main_header(account: Account):
    """
    Create the main dash_app header
    :param account: Account Class
    :return: header content
    """
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Span(
                        children=f'Last transaction date: {account.last_transaction_date:%d %b %Y}',
                        className='header'
                    ),
                ],
                className='two columns'
            ),
            html.Div(
                children=[
                    html.H3(
                        children='Transactions Analysis',
                        style=dict(
                            textAlign='center'
                        )
                    )
                ],
                className='eight columns'
            ),
            html.Img(
                src='/assets/img/analysis.png',
                className='two columns',
                style=dict(
                    height='5%',
                    width='5%',
                    float='right',
                    position='relative',
                    marginTop='10',
                    marginRight='10',
                    marginBottom='0'
                )
            )
        ],
        className='row'
    )


def tab_balance(account: Account):
    """
    Create the tab Blance of the dash_app
    :param account: Account Class
    :return: Balance Tab content
    """
    return html.Div(
        children=[
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
                                children=f'Since {account.actual_month_begin:%d %b %Y}: '
                            ),
                            html.Span(
                                children=f'{account.currency} {account.actual_month_pnl:,.2f}',
                                className=get_color_class_name(account.actual_month_pnl)
                            )
                        ]),
                    html.Li(
                        children=[
                            html.Span(
                                children=f'During {account.previous_month_end:%B %Y}: '
                            ),
                            html.Span(
                                children=f'{account.currency} {account.previous_month_pnl:,.2f}',
                                className=get_color_class_name(account.previous_month_pnl)
                            )
                        ]),
                    html.Li(
                        children=[
                            html.Span(
                                children=f'Monthly average: '
                            ),
                            html.Span(
                                children=f'{account.currency} {account.avg_monthly_pnl:,.2f}',
                                className=get_color_class_name(account.avg_monthly_pnl)
                            )
                        ])
                ],
                style=dict(
                    marginTop=70
                ),
                className='three columns',
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        id='total_figure_cumsum',
                        figure=account.total_figure_cumsum
                    ),
                ],
                style=dict(
                    marginTop=20
                ),
                className='nine columns',

            )
        ],
        className='row'
    )


def tab_category_breakdown(account: Account):
    """
    Create the tab Category breakdown of the dash_app
    :param account: Account Class
    :return: Category breakdown Tab content
    """
    return html.Div(
        children=[
            html.Div(
                children=[
                    dcc.Graph(
                        id='bar',
                        figure=account.category_figure_bar
                    ),
                ],
                className='twelve columns',
                style=dict(marginTop=20)
            ),
        ],
        className='row'
    )


def tab_sub_category_breakdown(account: Account):
    """
    Create the tab Sub-category breakdown of the dash_app
    :param account: Account Class
    :return: Sub-category breakdown Tab content
    """
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.H6(
                        children='Category',
                    ),
                    dcc.RadioItems(
                        id='category_radio_item',
                        options=[dict(label=k, value=k) for k in account.categories],
                        style=dict(color='rgb(170, 170, 170)'),
                        value='Food & Drink'
                    )
                ],
                className='two columns',
                style=dict(
                    marginTop=10,
                    marginLeft=20
                )
            ),
            html.Div(
                children=[
                    dcc.Graph(id='sub_category_figure_bar'),
                ],
                className='nine columns',
                style=dict(marginTop=20)
            )

        ],
        className='row'
    )


def tab_transaction(account: Account):
    """
    Create the tab Transaction of the dash_app
    :param account: Account Class
    :return: Transaction Tab content
    """
    return html.Div(
        children=[
            html.Div(
                children=[
                    dte.DataTable(
                        style_data={
                            'whiteSpace': 'normal',
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'color': 'rgb(170, 170, 170)',
                            'border': '0px'
                        },
                        data=account.transaction_df.to_dict('records'),
                        editable=False,
                        filter_action='native',
                        sort_action='native',
                        sort_mode='multi',
                        selected_rows=[],
                        virtualization=True,
                        page_action='none',
                        columns=[
                            {'name': value,
                             'id': key,
                             'hideable': True} for key, value in ATTRIBUTES.items()
                        ],
                        fixed_rows={'headers': True, 'data': 0},
                        style_cell={
                            'textAlign': 'left',
                            'color': 'rgb(170, 170, 170)',
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
                            'backgroundColor': 'rgb(170, 170, 170)',
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
                            'width': '98%',
                            'maxHeight': '400px',
                            'marginTop': '0.3%',
                            'marginLeft': '1.5%',
                            'marginRight': '0px',
                            'marginBottom': '0.3%',

                        },

                        id='datatable'
                    )
                ],
                className='twelve columns',
                style=dict(marginTop=20)
            ),
        ],
        className='row'
    )
