import pandas as pd

COLORS = dict(
    background='rgb(15, 15, 15)',
    text='rgb(170, 170, 170)',
    plot='rgb(25, 25, 25)',
    grid='rgb(65, 65, 65)',
)

TAB_STYLE = {
    'color': 'rgb(170,170,170)',
    'backgroundColor': 'rgb(30,30,30)',
    'borderTop': '0px',
    'borderLeft': '0px',
    'borderRight': '0px',
    'borderBottom': '0.8px solid rgb(90,90,90)',
    'padding': '0.5%'
}

TAB_SELECTED_STYLE = {
    'color': 'rgb(200,200,200)',
    'backgroundColor': 'rgb(50,50,50)',
    'borderTop': '1px solid rgb(600,180,50)',
    'borderLeft': '0.8px solid rgb(100,100,100)',
    'borderRight': '0.8px solid rgb(100,100,100)',
    'borderBottom': '0px',
    'padding': '0.5%'
}


def generate_layout(title):
    """
    Generate the layout of a figure
    :param title: Title of the figure
    :return: figure layout
    """
    return dict(
        title=title,
        autosize=True,
        height=460,
        font=dict(color=COLORS['text']),
        titlefont=dict(color=COLORS['text'], size=14),
        margin=dict(l=30, r=20, b=30, t=30),
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


def get_trace(df: pd.DataFrame):
    """
    Return the figure trace of the DataFrame's amount column
    :param df: DataFrame containing the amount column
    :return: the figure trace
    """
    return dict(
        type='scatter',
        x=list(df.index),
        y=df['amount'],
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
