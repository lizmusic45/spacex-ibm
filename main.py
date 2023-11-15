# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_site_list = spacex_df['Launch Site'].unique()
launch_site_name_dict = {'KSC LC-39A':'Kennedy Space Center - Launch Site 39A',
                         'CCAFS LC-40':'Cape Canaveral Air Force Station - Launch Site 40',
                         'CCAFS SLC-40':'Cape Canaveral Air Force Station - Space Launch Site 40',
                         'VAFB SLC-4E':'Vandenberg Air Force Base - Space Launch Site 4E'}
print(spacex_df.info())
print(spacex_df.groupby(['Launch Site']).agg({'class':'sum'})[['class']].apply(lambda x:100*x/x.sum()))
print(spacex_df[spacex_df['class']==0].groupby(['Launch Site'])['class'].count())
print(spacex_df[spacex_df['class']==1].groupby(['Launch Site'])['class'].count())
print(spacex_df[spacex_df['Payload Mass (kg)']<=8000]['Payload Mass (kg)'])

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    options=[{'label':'All Sites','value':'ALL'},
                                             {'label':launch_site_name_dict[launch_site_list[0]],'value':launch_site_list[0]},
                                             {'label':launch_site_name_dict[launch_site_list[1]],'value':launch_site_list[1]},
                                             {'label':launch_site_name_dict[launch_site_list[2]],'value':launch_site_list[2]},
                                             {'label':launch_site_name_dict[launch_site_list[3]],'value':launch_site_list[3]},
                                             ],
                                    id='site-dropdown',
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site

                                html.Div([], id='success-pie-chart'),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                #dcc.RangeSlider(id='payload-slider',)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                value=[min_payload, max_payload],
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div([],id='success-payload-scatter-chart'),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(Output(component_id='success-pie-chart',
                     component_property='children'),
              Input(component_id='site-dropdown',
                    component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class',
                     names='Launch Site',
                     title='Total Success Launches by Site')
        return dcc.Graph(figure=fig)
    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        filtered_df = filtered_df.assign(count_records=1)
        filtered_df = filtered_df.assign(class_bool=np.where(filtered_df['class']==1, 'Success', 'Failure'))
        #print(filtered_df['class'])
        fig = px.pie(filtered_df,
                     values='count_records',
                     names='class_bool',
                     title='Total Success Launches by Site' + ' ' + entered_site)
        return dcc.Graph(figure=fig)


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart',
                     component_property='children'),
              [Input(component_id='site-dropdown',
                    component_property='value'),
              Input(component_id='payload-slider',
                     component_property='value')])

def get_scatter_chart(entered_site, entered_payload):
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)']>=entered_payload[0]) & \
                                (spacex_df['Payload Mass (kg)']<=entered_payload[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category')
        return dcc.Graph(figure=fig)
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) & \
                                (spacex_df['Payload Mass (kg)']>=entered_payload[0]) & \
                                (spacex_df['Payload Mass (kg)']<=entered_payload[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category')
        return dcc.Graph(figure=fig)


# Run the app
if __name__ == '__main__':
    app.run_server()
