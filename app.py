import dash
import dash_bootstrap_components as dbc
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd

## variables
coffee_flavours_1 = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/718417069ead87650b90472464c7565dc8c2cb1c/sunburst-coffee-flavors-complete.csv')
coffee_flavours_2= pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/718417069ead87650b90472464c7565dc8c2cb1c/coffee-flavors.csv')
coffee_exports = pd.read_csv('data_processing/coffee_exports.csv')


def get_coffee_flavours(model):
  dataset = None
  if model == 1:
    dataset = coffee_flavours_1
  elif model == 2:
    dataset = coffee_flavours_2
  else:
    print("whattt")
  
  fig = go.Figure()
  fig.add_trace(go.Sunburst(
      ids=dataset.ids,
      labels=dataset.labels,
      parents=dataset.parents,
      domain=dict(column=model)
  ))

  fig.update_layout(
    margin = dict(t=20, l=2, r=2, b=2)
  )
  fig.layout
  return fig;


def get_coffee_exports(selected_year, selected_variable):
  filtered_df = coffee_exports[coffee_exports.Anio == selected_year]
  trace1 = go.Bar(x=filtered_df['PaisDestino'], y=filtered_df[selected_variable], name="toneladas", )
  return {
  'data': [trace1],
  'layout': go.Layout(colorway=["#EF963B"], hovermode="closest",
                      xaxis={'title': "Países", 'titlefont': {'color': 'black', 'size': 14},
                             'tickfont': {'size': 9, 'color': 'black'}},
                      yaxis={'title': selected_variable, 'titlefont': {'color': 'black', 'size': 14, },
                             'tickfont': {'color': 'black'}})}

navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Menú de aplicaciones",
            children=[
                dbc.DropdownMenuItem("App 1"),
                dbc.DropdownMenuItem("App 2"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Entry 3"),
            ],
        ),
    ],
    brand="Arjé Coffee - Entendiendo el café",
    brand_href="https://arjecoffee.co",
    sticky="top",
)

body = dbc.Container(
    [
      dbc.Row([
        dbc.Col([
          html.H2("Ser un catador"),
          html.P(
              """Asímismo, cuando pruebes cosas, piensa de verdad en lo que estás
           percibiendo. Intenta comprender qué fue lo que causó aquella diferencia
            en el sabor. [Un catador con experiencia] suele usar un lenguaje más
             complejo y descriptivo y está más acostumbrado a separar las partes
              más allá de las sensaciones de sabor básicas. Esto te ayudará a tener
               mayor experiencia en percibir los alimentos y las bebidas,
                ser más consciente del sabor y desarrollar la forma
                 en la que te comunicas acerca del sabor"""
          ),
          html.A([
            dbc.Button([ "Aprender más"], color="primary",)
          ], href="https://www.perfectdailygrind.com/2018/10/notas-de-sabor-como-ayudar-a-los-consumidores-a-entenderlas/"),
          ],md=4,
        ),
        dbc.Col([
          html.H2("Las notas del café"),
          html.P("""El café tiene notas maravillosas. Descúbrelas!"""),
          dcc.Dropdown(
              id='coffee-flavours-dropdown',
              options=[
                  {'label': 'Por categoría', 'value': '1'},
                  {'label': 'Por sabor', 'value': '2'},
              ],
              value='1'
          ),
          dcc.Graph(
              id='coffee-flavours',
          ),
          ]
        ),]
      ),
      dbc.Row([
        dbc.Col([
          html.H2("Exportaciones anuales de café"),
          dcc.Dropdown(
              id='coffee-exports-dropdown',
              options=[
                  {'label': 'USD en miles', 'value': 'ValorMilesFOBDol'},
                  {'label': 'Pesos Colombianos en miles', 'value': 'ValorMilesPesos'},
                  {'label': 'Toneladas', 'value': 'VolumenToneladas'},
              ],
              value='ValorMilesFOBDol',
          ),
        ])
        
      ]),
      dbc.Row([
        dbc.Col([
          dcc.Graph(id='exportaciones-por-anho'),
          html.Div([
            dcc.Slider(
                id='exportaciones-year-slider',
                min=coffee_exports['Anio'].min(),
                max=coffee_exports['Anio'].max(),
                value=coffee_exports['Anio'].min(),
                marks={str(year): str(year) for year in coffee_exports['Anio'].unique()},
                step=None,
            ),
          ],style={'paddingBottom': 40, 'paddingTop': 40}),
          
        ], md=12),
        
      ]),
      dbc.Row([
        html.H2(["Tabla dinámica para otros insights"])
      ]),
      dbc.Row([
        dbc.Col([
          dash_table.DataTable(
              id='datatable-interactivity',
              columns=[
                  {"name": i, "id": i, "deletable": True, "selectable": True} for i in coffee_exports.columns
              ],
              data=coffee_exports.to_dict('records'),
              editable=True,
              filter_action="native",
              sort_action="native",
              sort_mode="multi",
              column_selectable="single",
              row_selectable="multi",
              row_deletable=True,
              selected_columns=[],
              selected_rows=[],
              page_action="native",
              page_current= 0,
              page_size= 10,
          ),
          html.Div(id='datatable-interactivity-container')
        ])
      ]),

    ],
    className="mt-4",
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([navbar, body])



@app.callback(
    dash.dependencies.Output('coffee-flavours', 'figure'),
    [dash.dependencies.Input('coffee-flavours-dropdown', 'value')])
def update_output(value):
    return get_coffee_flavours(int(value))


@app.callback(
    Output('exportaciones-por-anho', 'figure'),
    [Input('exportaciones-year-slider', 'value'),
    Input('coffee-exports-dropdown', 'value')])
def update_figure(selected_year, selected_variable):
    return get_coffee_exports(selected_year, selected_variable)


@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = coffee_exports if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff["PaisDestino"],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["ValorMilesFOBDol", "ValorMilesPesos", "VolumenToneladas"] if column in dff
    ]






if __name__ == "__main__":
    app.run_server(port=8051, debug=True)