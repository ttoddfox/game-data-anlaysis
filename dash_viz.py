
import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server
origin_df=pd.read_csv('./game_data.csv')
df = pd.read_csv('./cleaned_game_data.csv')
cat=pd.read_csv('./cat.csv')
plot_cat=cat.sum()[cat.sum()>200].sort_values()
variable_list=['min_players','max_players','avg_time', 'min_time', 'max_time',
               'avg_rating','geek_rating', 'num_votes']
total_list=list(df.columns[~pd.Series(df.columns).isin(origin_df.columns)])
variable_options=[
    {"label": variable, "value": variable}
    for variable in variable_list
]
app.layout = html.Div(
    [

                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Game data analysis",
                                    style={'text-align':'center',
                                           'font-size':'45px'},

                                ),
                                html.H5(
                                    "demo presentation",
                                    style={'text-align':'center',
                                           'font-size':'15px'}
                                ),
                            ]
                        )
                    ],
                                        id="title",
                ),

        html.Div(
            [
                html.Div(
                    [

                        html.P("Geek rating or average rating for box plot:", className="control_label"),
                        dcc.RadioItems(
                            id="rating",
                            options=[
                                {"label": "Geek rating", "value": "geek_rating"},
                                {"label": "Average rating ", "value": "avg_rating"}

                            ],
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        html.P("variable distribution selector", className="control_label"),
                        dcc.Dropdown(
                            id="distr_var",
                            options=variable_options,
                            multi=False,
                            value=list(variable_list),
                            className="dcc_control",
                            style={'width':'240px'},
                        )
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                )]),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="distribution_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="boxplot_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        )
    ])

@app.callback(
    Output("distribution_graph", "figure"),
    [
        Input("distr_var", "value"),
    ],
)
def distribution_variable(variable):
    plot_values=df[variable][df[variable]<=df[variable].quantile(0.95)]
    distribution_figure=px.histogram(x=plot_values, title='distribution plot of '+variable)

    return distribution_figure

@app.callback(
    Output("boxplot_graph", "figure"),
    [
         Input("rating", "value"),
    ],
)
def boxplot_variable(rating):
    boxplot_df = pd.merge(df[[rating]], cat, left_index=True, right_index=True)
    melted_boxplot = pd.melt(boxplot_df, id_vars=[rating], value_vars=np.unique(total_list), var_name='category',
                             value_name='belong')
    melted_boxplot = melted_boxplot.loc[
                     (melted_boxplot['belong'] == 1) & (melted_boxplot['category'].isin(plot_cat.index)), :]
    melted_boxplot = pd.merge(melted_boxplot, pd.DataFrame(melted_boxplot.groupby('category')[rating].mean()),
                              left_on='category', right_index=True, how='left')
    melted_boxplot.columns = [rating, 'category', 'belong', 'mean_rating']
    melted_boxplot = melted_boxplot.sort_values('mean_rating', ascending=False)
    boxplot_figure=px.box(melted_boxplot, y=rating, x='category',color='category', title='box plot of '+rating)

    return boxplot_figure

if __name__ == "__main__":
    app.run_server()