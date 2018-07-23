# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_colorscales
import pandas as pd
import cufflinks as cf
import numpy as np
import re

import plotly.graph_objs as go
from scipy import stats


#app = dash.Dash(__name__)
app = dash.Dash()
#server = app.server

####### READ AND PRE-PROCESS DATA

counties_evicts_df = pd.read_csv('../data/counties.csv')
counties_evicts_df.rename(columns = {'low-flag': 'imputed',
                                    'imputed': 'subbed',
                                    'subbed': 'low-flag'}, inplace = True)
main_df = pd.read_csv('../data/all.csv', nrows = 17)

#YEARS = [sorted(set(counties_evicts_df.year))]
#######

#--- County Boxblot Traces
poverty_trace = go.Box(
    y = counties_evicts_df['poverty-rate'],
    x = counties_evicts_df.year,
    #hover = ('name'), # hover is not allowed in boxplot
    name = 'TN Poverty Rates',
    visible = 'legendonly',
    opacity = 0.5,
    marker = dict(color = 'black', opacity = 0.5, symbol = 'square')
)
poverty_state_trace = go.Scatter(
    x = main_df[main_df.name == 'Tennessee'].year,
    y = main_df[main_df.name == 'Tennessee']['poverty-rate'],
    name = 'Tn Mean Poverty Rate  ',
	#visible = 'legendonly',
    line = dict(
    color = 'black', dash = 'dash',
    width = 1)
)
eviction_trace = go.Box(
    y = counties_evicts_df['eviction-rate'],
    x = counties_evicts_df.year,
    name = 'TN Eviction Rates',
    opacity = 0.5,
    marker = dict(color = 'red', opacity = 0.5, symbol = 'square'),
	visible = 'legendonly',
)
eviction_state_trace = go.Scatter(
    x = main_df[main_df.name == 'Tennessee'].year,
    y = main_df[main_df.name == 'Tennessee']['eviction-rate'],
    name = 'Tn Mean Eviction Rate   ',
    line = dict(color = 'red', dash = 'dash', width = 1)
	#visible = 'legendonly',
)
filing_trace = go.Box(
    y = counties_evicts_df['eviction-filing-rate'],
    x = counties_evicts_df.year,
    name = 'County Filing Rates ',
    opacity = 0.5,
    marker = dict(color = 'orange', opacity = 0.5, symbol = 'square'),
	visible = 'legendonly',
)
filing_state_trace = go.Scatter(
    x = main_df[main_df.name == 'Tennessee'].year,
    y = main_df[main_df.name == 'Tennessee']['eviction-filing-rate'],
    name = 'Tn Mean Filing Rate  ',
    line = dict(
        color = 'orange', dash = 'dash',
        width = 1
    ),
	#visible = 'legendonly',
)
#---- Davidson Traces
davidsonPovertyTrace = go.Scatter(
    x = counties_evicts_df[counties_evicts_df.name == 'Davidson County'].year,
    y = counties_evicts_df[counties_evicts_df.name == 'Davidson County']['poverty-rate'],
    name = 'Davidson Pvty % ',
	visible = 'legendonly',
    line = dict(
    color = 'black',
    width = 2)
)
davidsonEvicRateTrace = go.Scatter(
    x = counties_evicts_df[counties_evicts_df.name == 'Davidson County'].year,
    y = counties_evicts_df[counties_evicts_df.name == 'Davidson County']['eviction-rate'],
    name = 'Davidson Evic % ',
	visible = 'legendonly',
    line = dict(
    color = 'red',
    width = 2)
)
davidsonEvicFilingRateTrace = go.Scatter(
    x = counties_evicts_df[counties_evicts_df.name == 'Davidson County'].year,
    y = counties_evicts_df[counties_evicts_df.name == 'Davidson County']['eviction-filing-rate'],
    name = 'Davidson Filing %  ',
	visible = 'legendonly',
    line = dict(
    color = 'orange',
    width = 2)
)
timeSeriesData = [poverty_state_trace, eviction_state_trace, #filing_state_trace,
					poverty_trace,  eviction_trace, #filing_trace,
					#davidsonPovertyTrace, davidsonEvicRateTrace, davidsonEvicFilingRateTrace,
					]
for cnty in counties_evicts_df.name.unique():
    cnty_df = counties_evicts_df[counties_evicts_df.name == cnty]
    timeSeriesData.append(go.Scatter(
        x = cnty_df.year,
        y = cnty_df['poverty-rate'],
        name = cnty,
        visible = 'legendonly',
        line = {'color': 'black', 'width' : '2'}
    ))
    timeSeriesData.append(go.Scatter(
        x = cnty_df.year,
        y = cnty_df['eviction-rate'],
        name = cnty,
        visible = 'legendonly',
        line = {'color': 'red', 'width' : 2}
    ))
    cntyLow_df = cnty_df[cnty_df['low-flag'] == 1]
    timeSeriesData.append(go.Scatter(
        x = cntyLow_df.year,
        y = cntyLow_df['eviction-rate'],
        name = cnty+' flagged low',
        visible = 'legendonly',
        mode = 'markers',
        marker = {'color': 'yellow', 'opacity': .5,
            'line': {'width':1, 'color': 'grey'},
            'size': 13
        }
        #line = {'color': 'red', 'width' : '2'}
    ))

timeSeriesLayout = dict(title = 'County Variables',
             			xaxis = dict(title = 'Year'),
             			yaxis = dict(title = 'Percentage'),
              			boxmode = 'group',
						height = 500,
						#legend = dict(x = -.1, y = 1.1,
									  #orientation = 'h'
						#			  )
                        paper_bgcolor = '#F4F4F8',
                        plot_bgcolor = '#F4F4F8',
						)

######----- Linear Regression Scatter Plot Traces -------
#----- Poverty v Evictions
povertyEvictionTrace = go.Scatter(
    x = counties_evicts_df['eviction-rate'],
    y = counties_evicts_df['poverty-rate'],
    mode = 'markers',
    marker = dict(
        size = 10,
        opacity = 0.33,
        color = counties_evicts_df['pct-white'],
        colorscale = 'seismic',
        showscale = True
    ),
    name = 'Eviction Rate v Poverty Rate'
)
# Generate linear fit
xi = counties_evicts_df['eviction-rate']
y = counties_evicts_df['poverty-rate']
# mask nans in the data
mask = ~np.isnan(xi) & ~np.isnan(y)
slope, intercept, r_value, p_value, std_err = stats.linregress(xi[mask],y[mask])
line = slope*xi+intercept
povEvLineTrace = go.Scatter(
    x = xi,
    y = line,
    #mode = 'lines',
    line = dict(
    color = 'red', dash = 'dot', #opacity = 0.3,
    width = 1),
    name = 'Eviction v Poverty Lin. Reg.'
)

#---- Filing v Poverty scatter plot
filingEvictionTrace = go.Scatter(
    y = counties_evicts_df['poverty-rate'],
    x = counties_evicts_df['eviction-filing-rate'],
    name = 'Ev. Filing Rate v Poverty Rate',
    visible = 'legendonly',
    mode = 'markers',
    marker = dict(
        size = 10,
        opacity = 0.33,
        color = counties_evicts_df['pct-white'],
        colorscale = 'Viridis',
        showscale = True
    )
)
# Generate linear fit
xi = counties_evicts_df['eviction-filing-rate']
y = counties_evicts_df['poverty-rate']
# mask nans in the data
mask = ~np.isnan(xi) & ~np.isnan(y)
slope, intercept, r_value, p_value, std_err = stats.linregress(xi[mask],y[mask])
line = slope*xi+intercept
# trace linear regression
povFilingLineTrace = go.Scatter(
    x = xi,
    y = line,
    mode = 'lines',
    marker = go.Marker(color = 'purple', opacity = 0.66),
    name = 'Filing v Poverty Lin. Reg.',
    visible = 'legendonly'
)

scatterData = [povertyEvictionTrace, povEvLineTrace, filingEvictionTrace, povFilingLineTrace]
scatterLayout = dict(title = 'Linear Regression (OLS) Color-Coded by % White',
             			xaxis = dict(title = 'Eviction/Filing Rate'),
             			yaxis = dict(title = 'Poverty Rate'),
						#height = 700,
						legend = dict(x = -.1, y = 1.2,
                                        orientation = 'h'
									  )
						)

#------------

YEARS = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, \
		2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]

BINS = ['0-2', '2.1-4', '4.1-6', '6.1-8', '8.1-10', '10.1-12', '12.1-14', \
		'14.1-16', '16.1-18', '18.1-20', '20.1-22', '22.1-24',  '24.1-26', \
		'26.1-28', '28.1-30', '>30']

DEFAULT_COLORSCALE = ["#2a4858", "#265465", "#1e6172", "#106e7c", "#007b84", \
	"#00898a", "#00968e", "#19a390", "#31b08f", "#4abd8c", "#64c988", \
	"#80d482", "#9cdf7c", "#bae976", "#d9f271", "#fafa6e"]

DEFAULT_OPACITY = 0.4

cntyCensusYears = [y in [2000, 2005, 2010, 2011] for y in counties_evicts_df.year]

#DEFAULT_COLORSCALE = reversed(DEFAULT_COLORSCALE)

mapbox_access_token = "pk.eyJ1IjoiamFja3AiLCJhIjoidGpzN0lXVSJ9.7YK6eRwUNFwd3ODZff6JvA"

'''
~~~~~~~~~~~~~~~~
~~ APP LAYOUT ~~
~~~~~~~~~~~~~~~~
'''

app.layout = html.Div(children=[

	html.Div([ #-- LEFT COLUMN
		html.Div([
			html.Div([
				html.H1(children='Evictions & Poveryt in Tennessee, 2000 - 2016',
						style = {'fontWeight': 999, 'fontSize': 30}
				),
			]),
		html.Div([
			html.P('Data: Matthew Desmond, Ashley Gromis, Lavar Edmonds, \
			James Hendrickson, Katie Krywokulski, Lillian Leung, and Adam \
			Porton. Eviction Lab National Database: Version 1.0. Princeton: \
			Princeton University, 2018, www.evictionlab.org.',
			style = {'fontSize': 12}
			)
		], style={'margin':0}),
		html.H2('Evictions and Poveryt Across Time',
			id = 'time-series-title',
			style = {'fontWeight':300, 'fontSize': 25}
		),
		#html.Div([
		#	dcc.Checklist(
		#	    options=[{'label': 'Hide legend', 'value': 'hide_legend'},
        #                {'label': 'Flag "too low" values', 'value': 'highlight_lows'},
        #                {'label': 'Filter by Census Years', 'value': 'filter_census'}
        #        ],
		#		values=[],
		#		labelStyle={'display': 'inline-block'},
		#		id='time-series-checkboxes',
		#	)
		#], style={'display':'inline-block'}),
        html.Br(),
		], style={'margin':0} ),
		dcc.Graph(id = 'time-series',
			figure = go.Figure(data = timeSeriesData, layout = timeSeriesLayout)
		),
		#html.P('Select County:(currently unused)', style={'display': 'inline-block'}),
		#dcc.Dropdown(id = 'county-dropdown',
        #    options = [{'label':cnty, 'value':cnty} for cnty in counties_evicts_df.name.unique()]
		#),
        html.Br(),
		html.Div([
			dcc.Checklist(
			    options=[#{'label': 'Hide legend', 'value': 'hide_scatter_legend'},
                        #{'label': 'Filter out "too low" values', 'value': 'highlight_lows_scatter'},
                        {'label': 'Filter by Census Years', 'value': 'filter_census_scatter'}
                ],
				values=[],
				labelStyle={'display': 'inline-block'},
				id='scatter-checkboxes',
			)
			], style={'display':'inline-block'}),

		html.H3('Linear Regression Analysis',
				id = 'lin-reg-title',
				style = {'fontWeight': 300, 'fontSize' : 25}
		),

		#dcc.Graph(
		#	id = 'scatter-plot',
		#	figure = go.Figure(data = scatterData, layout = scatterLayout
        #    )
		#),
        dcc.Graph(id = 'scatter-with-slider'),
        html.P('----------> Select Year:'),
        dcc.Slider(
                id = 'year-slider',
                min=min(YEARS),
                max= max(YEARS),
                value= min(YEARS), #although it would be cool to find a way to set it to a default that would show all the data at the same time
                marks = {str(year): str(year) for year in YEARS},
        )

	], className='seven columns', style={'margin':20}),

	html.Div([ #--- RIGHT COLUMN
		dcc.Graph(
			id = 'animated-data',
			figure = dict(
				data = [dict(x=0, y=0)],
				layout = dict(
					paper_bgcolor = '#F4F4F8',
					plot_bgcolor = '#F4F4F8',
					height = 700
				)
			),
			# animate = True
		)
	], className='three columns', style={'margin':0}),
])

app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/EQZeaW.css'}),

@app.callback(
    dash.dependencies.Output('scatter-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
                        Input('scatter-checkboxes', 'values')
    ])
def update_scatter(selected_year, census_filter = False):
    if census_filter:
        census_filtered_df = counties_evicts_df[cntyCensusYears]
        traces = [povEvLineTrace]
        traces.append(go.Scatter(
            x = census_filtered_df['eviction-rate'],
            y = census_filtered_df['poverty-rate'],
            text = census_filtered_df['name'],
            mode = 'markers',
            opacity = '0.4',
            marker = {'symbol': 'circle',#'circle-open',
                'size' : 8,
                'line': {'width':.5, 'color': 'white'},
                'color': census_filtered_df['pct-white'],
                'colorbar': {'x': -.3, 'title': 'pct-white','thickness': 15},
                'colorscale' : 'Viridis',
                'showscale' : 'True'
            },
            name = 'All Census Years'

        ))
        # filter by year
        filtered_df = census_filtered_df[census_filtered_df.year == selected_year]
        # Generate linear fit
        xi = filtered_df['eviction-rate']
        y = filtered_df['poverty-rate']
        # mask nans in the data
        mask = ~np.isnan(xi) & ~np.isnan(y)
        slope, intercept, r_value, p_value, std_err = stats.linregress(xi[mask],y[mask])
        line = slope*xi+intercept
        traces.append(go.Scatter(
            x = xi,
            y = line,
            #mode = 'lines',
            line = dict(
            color = 'red', dash = 'dot', #opacity = 0.3,
            width = 3),
            name = '{} Lin. Reg.'.format(selected_year)
        ))

        for cnty in census_filtered_df.name.unique():
            df_by_cnty = filtered_df[filtered_df['name'] == cnty]
            df_by_cnty = filtered_df[filtered_df['name'] == cnty]
            traces.append(go.Scatter(
                x = df_by_cnty['eviction-rate'],
                y = df_by_cnty['poverty-rate'],
                text = df_by_cnty['pct-white'],
                mode = 'markers',
                #opacity = 0.2,
                marker = {'symbol': 'circle-open',
                    'size': 8,
                    'line': {'width':1, 'color': 'black'},
                    'color': 'black',
                    #'color': df_by_cnty['pct-white'],
                    #'colorbar': {'x': -.2, 'title': 'pct-white','thickness': 15},
                    #'colorscale' : 'Viridis',
                    #'showscale' : 'True'
                },
                name = cnty,
                #visible = 'legendonly'
            ))
    if not census_filter:
        # add the linear regression to the data
        traces=[povEvLineTrace]
        # add the global scatter
        traces.append(go.Scatter(
            x = counties_evicts_df['eviction-rate'],
            y = counties_evicts_df['poverty-rate'],
            text = counties_evicts_df['name'],
            mode = 'markers',
            opacity = '0.4',
            marker = {'symbol': 'circle',#'circle-open',
                'size' : 8,
                'line': {'width':.5, 'color': 'white'},
                'color': counties_evicts_df['pct-white'],
                'colorbar': {'x': -.3, 'title': 'pct-white','thickness': 15},
                'colorscale' : 'Viridis',
                'showscale' : 'True'
                },
                name = 'All Years'

                ))
                # filter by year
        filtered_df = counties_evicts_df[counties_evicts_df.year == selected_year]
        # Generate linear fit
        xi = filtered_df['eviction-rate']
        y = filtered_df['poverty-rate']
        # mask nans in the data
        mask = ~np.isnan(xi) & ~np.isnan(y)
        slope, intercept, r_value, p_value, std_err = stats.linregress(xi[mask],y[mask])
        line = slope*xi+intercept
        traces.append(go.Scatter(
                x = xi,
                y = line,
                #mode = 'lines',
                line = dict(
                color = 'red', dash = 'dot', #opacity = 0.3,
                width = 3),
                name = '{} Lin. Reg.'.format(selected_year)
                ))

        for cnty in filtered_df.name.unique():
            df_by_cnty = filtered_df[filtered_df['name'] == cnty]
            traces.append(go.Scatter(
                x = df_by_cnty['eviction-rate'],
                y = df_by_cnty['poverty-rate'],
                text = df_by_cnty['pct-white'],
                mode = 'markers',
                    #opacity = 0.2,
                marker = {'symbol': 'circle-open',
                        'size': 8,
                        'line': {'width':1, 'color': 'black'},
                        'color': 'black',
                #'color': df_by_cnty['pct-white'],
                #'colorbar': {'x': -.2, 'title': 'pct-white','thickness': 15},
                #'colorscale' : 'Viridis',
                #'showscale' : 'True'
                        },
                name = cnty,
            #visible = 'legendonly'
            ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis = {'title': 'Eviction Rate',
                'range': [min(counties_evicts_df['eviction-rate']-1),
                            max(counties_evicts_df['eviction-rate']+1)]
            },
            yaxis = {'title': 'Poverty Rate',
                'range': [min(counties_evicts_df['poverty-rate']-1),
                            max(counties_evicts_df['poverty-rate']+1)
                ]
            },
            hovermode = 'closest',
            paper_bgcolor = '#F4F4F8',
            plot_bgcolor = '#F4F4F8',
            #legend = {'x': -.1, 'y': -.2, 'orientation': 'v'},
            updatemenus = [{'type':'buttons',
                            'buttons': [{'label': 'Play',
                                        'method': 'animate',
                                        'args': [None]
                            }]
            }]
        ),
        'frames': [dict(data=[dict(x=[counties_evicts_df['eviction-rate'][counties_evicts_df.year == yr]],
                                    y=[counties_evicts_df['poverty-rate'][counties_evicts_df.year == yr]],
                        mode='markers',
                        marker=dict(color='magenta', size=10)
                        )
                  ]) for yr in YEARS]
    }
#)

if __name__ == '__main__':
	app.run_server(debug=True)
