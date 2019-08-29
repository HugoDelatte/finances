import pandas as pd

COLORS = dict(
    background='#000000',
    text='#CCCCCC',
    plot='#191A1A',
    grid='#404040',
    border='#404040'
)


def generate_layout(title):
    return dict(
        title=title,
        autosize=True,
        height=500,
        font=dict(color=COLORS['text']),
        titlefont=dict(color=COLORS['text'], size=14),
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


def get_trace(df: pd.DataFrame):
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


def get_color_class_name(number):
    if number >= 0:
        return 'green'
    else:
        return 'red'
