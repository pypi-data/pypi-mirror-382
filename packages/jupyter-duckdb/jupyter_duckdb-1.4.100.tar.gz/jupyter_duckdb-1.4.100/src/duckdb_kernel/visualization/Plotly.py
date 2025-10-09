import json
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import uuid4

from .lib import init_plotly


def __div_id() -> str:
    return f'div-{str(uuid4())}'


def __layout(title: Optional[str]):
    layout = {
        'dragmode': False,
        'xaxis': {
            'rangeselector': {
                'visible': False
            }
        }
    }

    if title is not None:
        layout['title'] = {
            'text': title,
            'font': {
                'family': 'sans-serif',
                'size': 32,
                'color': 'rgb(0, 0, 0)'
            },
            'xanchor': 'center'
        }

    return layout


def __config():
    return {
        'displayModeBar': False,
        'scrollZoom': False
    }


def __fix_decimal(x: List):
    return [float(x) if isinstance(x, Decimal) else x
            for x in x]


def draw_chart(title: Optional[str], traces: List[Dict] | Dict) -> str:
    init = init_plotly()
    div_id = __div_id()
    layout = __layout(title)
    config = __config()

    if not isinstance(traces, str):
        traces = json.dumps(traces)

    return f'''
        <script type="text/javascript">
            {init}
        </script>

        <div id="{div_id}"></div>
        <script type="text/javascript">
            Plotly.newPlot('{div_id}', {traces}, {json.dumps(layout)}, {json.dumps(config)});
        </script>
    '''


def draw_scatter_chart(title: Optional[str], x, **ys) -> str:
    return draw_chart(title, [
        {
            'x': __fix_decimal(x),
            'y': __fix_decimal(y),
            'mode': 'markers',
            'type': 'scatter',
            'name': name
        }
        for name, y in ys.items()
    ])


def draw_line_chart(title: Optional[str], x, **ys) -> str:
    return draw_chart(title, [
        {
            'x': __fix_decimal(x),
            'y': __fix_decimal(y),
            'mode': 'lines+markers',
            'name': name
        }
        for name, y in ys.items()
    ])


def draw_bar_chart(title: Optional[str], x, **ys) -> str:
    return draw_chart(title, [
        {
            'x': __fix_decimal(x),
            'y': __fix_decimal(y),
            'type': 'bar',
            'name': name
        }
        for name, y in ys.items()
    ])


def draw_pie_chart(title: Optional[str], x, y) -> str:
    return draw_chart(title, [{
        'values': __fix_decimal(y),
        'labels': __fix_decimal(x),
        'type': 'pie'
    }])


def draw_bubble_chart(title: Optional[str], x, y, s, c) -> str:
    return draw_chart(title, [{
        'x': __fix_decimal(x),
        'y': __fix_decimal(y),
        'mode': 'markers',
        'marker': {
            'size': __fix_decimal(s),
            'color': __fix_decimal(c)
        }
    }])


def draw_heatmap_chart(title: Optional[str], x, y, z) -> str:
    return draw_chart(title, [{
        'x': __fix_decimal(x[0]),
        'y': __fix_decimal(y[0]),
        'z': [__fix_decimal(v) for v in z[0]],
        'type': 'heatmap'
    }])


__all__ = [
    'draw_chart',
    'draw_scatter_chart',
    'draw_line_chart',
    'draw_bar_chart',
    'draw_pie_chart',
    'draw_bubble_chart',
    'draw_heatmap_chart',
]
