# -*- coding: utf-8 -*-

import datetime as dt
import pandas as pd
from pandas.tseries.offsets import Day
import sqlite3
import plotly.offline as py
import cufflinks as cf
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_table as dte
import copy
import os
from flask import send_from_directory
import sys

# Dash: http://127.0.0.1:8050/

DIR = ('C:/Users/hugo/OneDrive/Documents/SynologyDrive/Administrative/'
       'Finances/HSBC/Financial Analysis')
TEMP = 'C:\\Temp'
COLORS = dict(
    background='#000000',
    text='#CCCCCC',
    plot='#191A1A',
    grid='#404040'
    )


def to_month(date_str):
    date = pd.to_datetime(date_str, format='%Y-%m-%d')
    return (date - Day(6)).strftime('%Y-%m')


def month_format(date_str):
    date = pd.to_datetime(date_str, format='%Y-%m-%d')
    return (date - Day(6)).strftime('%b %Y')


def date_format(date_str):
    date = pd.to_datetime(date_str, format='%Y-%m-%d')
    return date.strftime(' %d %b %Y')


def replace_none(sub_category):
    if sub_category is None:
        return 'None'
    else:
        return sub_category


def generate_layout(title):
    return dict(
        title=title,
        autosize=True,
        height=500,
        font=dict(color=COLORS['text']),
        titlefont=dict(color=COLORS['text'], size='14'),
        margin=dict(l=45, r=35, b=35, t=45),
        legend=dict(bgcolor=COLORS['background'],
                    font=dict(color=COLORS['text']),
                    orientation='h'),
        paper_bgcolor=COLORS['background'],
        plot_bgcolor=COLORS['plot'],
        yaxis1=dict(tickfont=dict(color=COLORS['text']),
                    gridcolor=COLORS['grid'],
                    titlefont=dict(color=COLORS['text']),
                    zerolinecolor=COLORS['grid'],
                    showgrid=True,
                    title=''),
        xaxis1=dict(tickfont=dict(color=COLORS['text']),
                    gridcolor=COLORS['grid'],
                    titlefont=dict(color=COLORS['text']),
                    zerolinecolor=COLORS['grid'],
                    showgrid=True,
                    title=''),
        barmode='group'
        )


database = DIR + '/finance.db'
con = sqlite3.connect(database)
con.execute('pragma foreign_keys=ON')
c = con.cursor()
c.execute('''SELECT S.date, S.detail, E.name, S.amount, M.name, T.name,
          C.name, SC.name
          FROM Statement S
          OUTER LEFT JOIN Entity E
              on E.entity_id = S.entity_id
          OUTER LEFT JOIN Method M
              on M.method_id = S.method_id
          INNER JOIN Type T
              on T.type_id = S.type_id
          OUTER LEFT JOIN Category C
              on C.category_id = S.category_id
          OUTER LEFT JOIN Sub_category SC
              on SC.sub_category_id = S.sub_category_id; ''')
res = c.fetchall()
con.close()
cf.go_offline()
cols = [
    'date', 'detail', 'entity', 'amount', 'method', 'type',
    'category', 'sub_category'
    ]
df = pd.DataFrame(res, columns=cols)
df_month = df.copy()
df_month.loc[:, ('date')] = df_month['date'].apply(to_month)

app = dash.Dash()

@app.server.route('/static/<path:path>')
def static_file(path):
    static_folder = os.path.join(DIR, 'static')
    return send_from_directory(static_folder, path)


app.css.append_css(
    dict(external_url=('https://cdn.rawgit.com/plotly/dash-app-stylesheets/'
                       '2d266c578d2a6e8850ebce48fdb52759b2aef506/'
                       'stylesheet-oil-and-gas.css'))
    )

# Bar Total
fig_bar = (
    df_month.groupby(['date', 'category'], as_index=False)['amount']
    .sum()
    .pivot(index='date', columns='category', values='amount')
    .iplot(kind='bar', barmode='group', asFigure=True)
    )
df_total = (
    df_month.groupby(['date'], as_index=False)['amount']
    .sum()
    .set_index('date')
    )
fig_bar['layout'] = generate_layout(title='All Transactions')
fig_bar['data'].append(dict(
    type='scatter',
    x=list(df_total.index),
    y=df_total['amount'],
    mode='lines+markers',
    marker=dict(
        size=3,
        color='rgba(255, 0, 0, 0.7)'
        ),
    line=dict(
        color='rgba(255, 0, 0, 0.7)',
        width=2
        ),
    name='Total'
    ))

# Cum total
fig_total = (
    df_total.cumsum()
    .iplot(asFigure=True)
    )
fig_total['layout'] = generate_layout(title='Total Balance')
balance = df['amount'].sum()
month_pnl = (df_month[df_month['date'] == df_month['date'].max()]['amount']
             .sum())
avg_pnl = balance / len(set(df_month['date']))

def class_name_number(number):
    if number >=0 :
        return 'green_text'
    else:
        return 'red_text'

app.layout = html.Div(
    style=dict(backgroundColor=COLORS['background']),
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Link(rel='stylesheet',
                                  href='/static/stylesheet_colors.css'),
                        html.H2(
                            children=date_format(df['date'].max()),
                            style=dict(
                                color=COLORS['text'],
                                fontSize='100%',
                                textAlign='center'
                                )
                            ),
                        html.Br(),
                        html.Ul(
                            children=[
                                html.Li(
                                    children=[
                                        html.Span(children='Balance: '),
                                        html.Span(
                                         children='£{:,.2f}'.format(balance),
                                         className=class_name_number(balance)
                                         )
                                    ]),
                                html.Li(
                                    children=[
                                        html.Span(
                                            children=month_format(
                                                df['date'].max()
                                                ) + ': '
                                            ),
                                        html.Span(
                                         children='£{:,.2f}'.format(month_pnl),
                                         className=class_name_number(month_pnl)
                                         )
                                    ]),
                                html.Li(
                                    children=[
                                        html.Span(
                                            children='Monthly avg: '
                                            ),
                                        html.Span(
                                         children='£{:,.2f}'.format(avg_pnl),
                                         className=class_name_number(avg_pnl)
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
                    className='two columns'
                    ),
                html.Div(
                    children=[
                        html.H1(
                            children='Transactions Analysis',
                            style=dict(
                                color=COLORS['text'],
                                # fontFamily='Bebas',
                                fontSize='300%',
                                textAlign='center'
                                )
                            )
                        ],
                    className='eight columns'
                    ),
                html.Img(
                    src='/static/profile picture.png',
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
                            figure=fig_bar
                            ),
                        ],
                    className='eight columns',
                    style=dict(marginTop=20)
                    ),
                html.Div(
                    children=[
                        dcc.Graph(
                            id='total',
                            figure=fig_total
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
                        dcc.Graph(id='bar_sub'),
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
                            options=[
                                    dict(label=k, value=k) for k in
                                    set(df['category'])
                                    ],
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
                    rows=df.to_dict('records'),
                    editable=False,
                    filterable=True,
                    sortable=True,
                    resizable=True,
                    column_widths=[100, 80, 150, 120, 120, 120, 300, 180],
                    columns=[
                        'date', 'amount', 'entity', 'type', 'category',
                        'sub_category', 'detail', 'method'
                        ],
                    row_selectable=True,
                    selected_row_indices=[],
                    enable_drag_and_drop=True,
                    id='datatable'
                    )
                ]
            )
        ]
    )


@app.callback(
    dash.dependencies.Output('bar_sub', 'figure'),
    [dash.dependencies.Input('category_radio_item', 'value')])
def update_figure(category):
    df_sub = df_month[df_month['category'] == category].copy()
    df_sub.loc[:, ('sub_category')] = (
        df_sub['sub_category']
        .apply(replace_none)
        )
    fig_bar_sub = (
        df_sub.groupby(['date', 'sub_category'], as_index=False)['amount']
        .sum()
        .pivot(index='date', columns='sub_category', values='amount')
        .iplot(kind='bar', barmode='group', asFigure=True)
        )
    df_total_sub = (
        df_sub.groupby(['date'], as_index=False)['amount']
        .sum()
        .set_index('date')
        )
    fig_bar_sub['layout'] = generate_layout(title=category)
    fig_bar_sub['data'].append(
        dict(
            type='scatter',
            x=list(df_total_sub.index),
            y=df_total_sub['amount'],
            mode='lines+markers',
            marker=dict(
                size=3,
                color='rgba(255, 0, 0, 0.7)'
                ),
            line=dict(
                color='rgba(255, 0, 0, 0.7)',
                width=2
                ),
            name='Total'
            )
        )
    return fig_bar_sub


if __name__ == '__main__':
    app.run_server(debug=False)
