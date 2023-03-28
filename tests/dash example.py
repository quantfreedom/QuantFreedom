from datetime import date
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
prices = pd.read_csv(
    'E:/Coding/backtesters/QuantFreedom/tests/data/30min.csv', index_col='time')
price_index = prices.index.to_list()
index_list = price_index[1:]
start_time = price_index[0].split(" ")[1]
index_time = [start_time]
for x in index_list:
    temp_time = x.split(" ")[1]
    if temp_time == start_time:
        break
    index_time.append(x.split(" ")[1])

price_start_date = price_index[0].split(" ")[0].split("-")
start_year=int(price_start_date[0])
start_month=int(price_start_date[1])
start_day=int(price_start_date[2])

price_end_date = price_index[-1].split(" ")[0].split("-")
end_year=int(price_end_date[0])
end_month=int(price_end_date[1])
end_day=int(price_end_date[2])

app = Dash(__name__)
app.layout = html.Div([
    dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=date(start_year, start_month, start_day),
            max_date_allowed=date(end_year, end_month, end_day),
            initial_visible_month=date(start_year, start_month, start_day),
            end_date=date(end_year, end_month, end_day),
        ),
    html.Div(id='output-container-date-picker-range')
])


@app.callback(
    Output('output-container-date-picker-range', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix


if __name__ == '__main__':
    app.run_server(debug=True, Port=3003)
