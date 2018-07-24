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

from plotly.offline import init_notebook_mode, iplot
from IPython.display import display, HTML
init_notebook_mode(connected = True)

#app = dash.Dash(__name__)
app = dash.Dash()
#server = app.server

'''####### READ AND PRE-PROCESS DATA ###################'''

counties_evicts_df = pd.read_csv('../data/counties.csv')
counties_evicts_df.rename(columns = {'low-flag': 'imputed',
                                    'imputed': 'subbed',
                                    'subbed': 'low-flag'}, inplace = True)
main_df = pd.read_csv('../data/all.csv', nrows = 17)
county_correlations_df = pd.read_csv('../data/county_correlations.csv')
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

timeSeriesLayout = dict(title = 'Evictions & Poverty Time Series',
             			xaxis = dict(title = 'Year'),
             			yaxis = dict(title = 'Percent %'),
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
    color = 'darkred', dash = 'dot', #opacity = 0.3,
    width = 2),
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

############--- corrTimeSeriesData
x = counties_evicts_df.year.unique()
y = []
for yr in x:
    #print(x)
    y.append(np.corrcoef(
            x = counties_evicts_df[counties_evicts_df.year == yr].dropna()['eviction-rate'],
            y = counties_evicts_df[counties_evicts_df.year == yr].dropna()['poverty-rate']
    )[0][1])
    #print(y)

corrTimeSeriesTrace = go.Scatter(
    x = x,
    y = y,
    name = 'Pearson Corr. Coeff.',
	#visible = 'legendonly',
    line = dict(
        color = 'red',
        width = 2)
)
determinationCoeffTimeSeriesTrace = go.Scatter(
    x = x,
    y = [r*r for r in y],
    name = 'Coeff. of Determination, r-squared',
    line = {
        'color' : 'magenta',
        'width': '2'
    },
    visible = 'legendonly',
)
corrTimeSeriesData = [corrTimeSeriesTrace, determinationCoeffTimeSeriesTrace]
corrTimeSeriesLayout = dict(title = 'Correlation on a Scale From -1.0 to 1.0',
             			xaxis = dict(title = 'Year'),
             			yaxis = dict(title = 'Pearson Corr. Coeff.'),
              			#boxmode = 'group',
						height = 300,
						legend = dict(#x = -.1,
                                    #y = 1.1,
									  orientation = 'v'
									  ),
                        paper_bgcolor = '#F4F4F8',
                        plot_bgcolor = '#F4F4F8',
						)
#######-------- corrHistogramData
corrHistPovEvicTrace = go.Histogram(
    x = county_correlations_df['pov-evic-corr']
)
corrHistogramData = [corrHistPovEvicTrace]
corrHistogramLayout = go.Layout(barmode = 'stack')
#------------

YEARS = [1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]
BINS = ['0-2', '2.1-4', '4.1-6', '6.1-8', '8.1-10', '10.1-12', '12.1-14', \
		'14.1-16', '16.1-18', '18.1-20', '20.1-22', '22.1-24',  '24.1-26', \
		'26.1-28', '28.1-30', '>30']
DEFAULT_COLORSCALE = ["#2a4858", "#265465", "#1e6172", "#106e7c", "#007b84", \
	"#00898a", "#00968e", "#19a390", "#31b08f", "#4abd8c", "#64c988", \
	"#80d482", "#9cdf7c", "#bae976", "#d9f271", "#fafa6e"]
#DEFAULT_OPACITY = 0.4
cntyCensusYears = [y in [2000, 2005, 2010, 2011] for y in counties_evicts_df.year]
BonafideRows = [f == 0 for f in counties_evicts_df['low-flag']]
BonafideCensusRows = [census and bonafide for census, bonafide in zip(cntyCensusYears, BonafideRows)]
DEFAULT_COLORSCALE = reversed(DEFAULT_COLORSCALE)
#mapbox_access_token = "pk.eyJ1IjoiamFja3AiLCJhIjoidGpzN0lXVSJ9.7YK6eRwUNFwd3ODZff6JvA"

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
						style = {'fontWeight': 999, 'fontSize': 40}
				), # title
			]),
		html.Div([
			html.P('Data: Matthew Desmond, Ashley Gromis, Lavar Edmonds, \
			James Hendrickson, Katie Krywokulski, Lillian Leung, and Adam \
			Porton. Eviction Lab National Database: Version 1.0. Princeton: \
			Princeton University, 2018, www.evictionlab.org.',
			style = {'fontSize': 12}
			) # citation
		], style={'margin':0}),
		], style={'margin':0} ),
		dcc.Graph(id = 'time-series',
			figure = go.Figure(data = timeSeriesData, layout = timeSeriesLayout)
		),
		#html.P('Select County:(currently unused)', style={'display': 'inline-block'}),
		#dcc.Dropdown(id = 'county-dropdown',
        #    options = [{'label':cnty, 'value':cnty} for cnty in counties_evicts_df.name.unique()]
		#),
        #html.Br(),
        html.Div([
        html.P("Pick an Individual Year To Highlight and Analyze Below."),
        html.Div([
            dcc.Slider(id = 'year-slider',
                        min=min(YEARS),
                        max= max(YEARS),
                        value= min(YEARS),
                        marks = {str(year): str(year) for year in YEARS},
                            ),
            ], style={'width':700, 'display':'inline-block', 'marginBottom':12
                }),
        dcc.Graph(id = 'scatter-with-slider'),
            ], style = {'marginBottom': 0}),
        dcc.Checklist( id = 'checked-years',
            options = [{'label': str(yr), 'value': str(yr)} for yr in YEARS],
            values = [str(y) for y in YEARS],
            labelStyle = {'display': 'inline-block', 'fontSize': 10,
                            'margin': 1,
                            #'marginTop': 0, 'rotation':45
            }),
        html.Br(),
        html.Div([
			dcc.Checklist(id='census-checkbox',
			    options=[{'label': 'Census Years Filter: (2000, 2005, 2010, 2011). Poverty Rates were only measured during census years.', 'value': 'census_filter'}
                ],
				values=[],
				labelStyle={'display': 'inline-block'},
			),
            dcc.Checklist(id = 'low-checkbox',
                options = [{'label': 'Low-Flag Filter. Some eviction values were flagged as under-reported by The Eviction Lab.', 'value': 'low_flag_filter'}],
                values = [],
                labelStyle={'display': 'inline-block'},
            ),
			], style={'display':'inline-block'}),
        #html.H6('County-Wide Correlation Coefficient Time Series'),
        dcc.Graph(id = 'corr-timeseries',
            figure = go.Figure(data = corrTimeSeriesData, layout = corrTimeSeriesLayout)
        ),
	], className='seven columns', style={'margin':20}),

	html.Div([ #--- RIGHT COLUMN
    html.H2('What is the Story?'),
    html.H3('Time Series Insights'),
    html.H3('Scatter Plot Insights'),
    html.H2('What is the Story?'),
    html.H3('Time Series Insights'),
    html.H3('Scatter Plot Insights'),
    html.H2('What is the Story?'),
    html.H3('Time Series Insights'),
    html.H3('Scatter Plot Insights'),
    html.H2('What is the Story?'),
    html.H3('Time Series Insights'),
    html.H3('Scatter Plot Insights'),
    html.Br(),
    dcc.Graph(id = 'corr-histogram',
        figure = go.Figure(data = corrHistogramData, layout = corrHistogramLayout)
    )
	], className='five columns', style={'margin':0}),
])
app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/EQZeaW.css'}),

@app.callback(
    dash.dependencies.Output('scatter-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
                        Input('low-checkbox', 'values'),
                        Input('checked-years', 'values')
    ])
def update_scatter(selected_year, checklist_values, checked_year_values):
    #print('selected_year', selected_year)
    #------ handle filters
    fltr = [str(y) in checked_year_values for y in counties_evicts_df.year]
    if 'low_flag_filter' in checklist_values:
        fltr = [f and bnfd for f, bnfd in zip(fltr, BonafideRows)]
    filtered_df = counties_evicts_df[fltr]
    #------ add checked year scatter and line
    traces=[]
    # add the checked scatter
    traces.append(go.Scatter(
        x = filtered_df['eviction-rate'],
        y = filtered_df['poverty-rate'],
        text = filtered_df['name'],
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
            name = 'Selected Years'

            ))
    # Generate linear fit
    xi = filtered_df['eviction-rate']
    y = filtered_df['poverty-rate']
    # mask nans in the data to be fit
    mask = ~np.isnan(xi) & ~np.isnan(y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi[mask],y[mask])
    line = slope*xi+intercept
    # add the checked linear fit
    traces.append(go.Scatter(
            x = xi,
            y = line,
            #mode = 'lines',
            line = dict(
                color = 'red', #dash = 'dot', #opacity = 0.3,
                width = 3),
                name = 'Selected Years Lin. Reg.'
                #name = 'Lin. Reg. for: {}'.format(checked_year_values)
            ))
    #------ add slider year scatter and line
    # adjust filter for slider year
    if selected_year != 1999:
        filtered_df = counties_evicts_df[counties_evicts_df.year == selected_year]
        if 'low_flag_filter' in checklist_values:
            filtered_df = filtered_df[filtered_df['low-flag'] == 0]
        # add slider scatter
        traces.append(go.Scatter(
            x = filtered_df['eviction-rate'],
            y = filtered_df['poverty-rate'],
            text = filtered_df['name'],
            mode = 'markers',
            opacity = '0.6',
            marker = {'symbol': 'circle-open',
                'size' : 9,
                'line': {'width':2, 'color': 'black'},
                'color': 'black',
                },
            name = '{} Counties'.format(selected_year),
            #visible = 'legendonly'

                ))
        # Generate linear fit
        xi = filtered_df['eviction-rate']
        y = filtered_df['poverty-rate']
        # mask nans in the data
        mask = ~np.isnan(xi) & ~np.isnan(y)
        slope, intercept, r_value, p_value, std_err = stats.linregress(xi[mask],y[mask])
        line = slope*xi+intercept
        # add slider line
        traces.append(go.Scatter(
                x = xi,
                y = line,
                #mode = 'lines',
                line = dict(
                    color = 'black', dash = 'dot', #opacity = 0.3,
                    width = 1.5),
                name = '{} Lin. Reg.'.format(selected_year)
                ))
    #------ return output
    return { # can only return first positional output
        'data': traces,
        'layout': go.Layout(#title = 'Checked Years {}'.format(checked_year_values),
                        title = 'Scatter Plot; Linear Regression Analysis, (OLS)',
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
                        #legend = {'x': -.1, 'y': 1.3, 'orientation': 'h'},

                    )
    }
@app.callback(
    dash.dependencies.Output('corr-timeseries', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
                        Input('low-checkbox', 'values'),
                        Input('checked-years', 'values')
    ])
def update_corrTimeSeries(selected_year, checklist_values, checked_year_values):
    #------ handle filters
    fltr = [str(y) in checked_year_values for y in counties_evicts_df.year]
    if 'low_flag_filter' in checklist_values:
        fltr = [f and bnfd for f, bnfd in zip(fltr, BonafideRows)]
    filtered_df = counties_evicts_df[fltr]
    #------ generate coefficients
    #x = sorted([int(y) for y in checked_year_values])
    x = filtered_df.year.unique()
    #print(x)
    y = []
    for yr in x:
        #print(yr)
        #filtered_df = filtered_df[filtered_df.year == yr]
        y.append(np.corrcoef(
                x = filtered_df[filtered_df.year == yr].dropna()['eviction-rate'],
                y = filtered_df[filtered_df.year == yr].dropna()['poverty-rate']
        )[0][1])
        #print(y)
    #------ add checked year scatter and line
    traces=[]
    # add the checked scatter
    traces.append(
        go.Scatter(
            x = x,
            y = y,
            name = 'Pearson Corr. Coeff.',
        	#visible = 'legendonly',
            line = dict(
                color = 'red',
                width = 2)
        )
    ),
    traces.append(
        go.Scatter(
            x = x,
            y = [r*r for r in y],
            name = 'Coeff. of Determination, r-squared',
            line = {
                'color' : 'magenta',
                'width': '2'
            },
            visible = 'legendonly',
        )
    ),
    return { # can only return first positional output
        'data': traces,
        'layout': go.Layout(#title = 'Checked Years {}'.format(checked_year_values),
            title= 'County-Wide Correlation Coefficient for Selected Years: {}'.format(round(np.corrcoef(
                                                                    x = filtered_df.dropna()['eviction-rate'],
                                                                    y = filtered_df.dropna()['poverty-rate']
                                                                    )[0][1], 2)
                                                        ),
            xaxis = {'title': 'Year'},
            yaxis = {'title': 'Coeff'},
            #hovermode = 'spike',
            paper_bgcolor = '#F4F4F8',
            plot_bgcolor = '#F4F4F8',
            #legend = {'x': -.1, 'y': 1.3, 'orientation': 'h'},

        )
    }

@app.callback(
    dash.dependencies.Output('corr-histogram', 'figure'),
    [dash.dependencies.Input('low-checkbox', 'values'),
                        Input('checked-years', 'values')]
)
def update_histogram(checklist_values, checked_year_values):
    #------ handle filters
    fltr = [str(y) in checked_year_values for y in counties_evicts_df.year]
    if 'low_flag_filter' in checklist_values:
        fltr = [f and bnfd for f, bnfd in zip(fltr, BonafideRows)]
    filtered_df = counties_evicts_df[fltr]
    #------ add trace for each county
    traces = []
    for cnty in filtered_df.name.unique():
        if not pd.isnull(np.corrcoef(
                x = filtered_df[filtered_df.name == cnty].dropna()['eviction-rate'],
                y = filtered_df[filtered_df.name == cnty].dropna()['poverty-rate']
            )[0][1]):
            traces.append(go.Histogram(
                                x = [round(
                                        np.corrcoef(
                                                x = filtered_df[filtered_df.name == cnty].dropna()['eviction-rate'],
                                                y = filtered_df[filtered_df.name == cnty].dropna()['poverty-rate']
                                            )[0][1],
                                        3)
                                    ],
                                name = cnty,
                                #text = str(np.median(filtered_df['pct-white'])),
                                #hoverinfo = 'text',
                                #marker = {'color' : filtered_df[filtered_df.name == cnty]['pct-white'].dropna().mean()},
                                marker = {'color': np.mean([p for p in filtered_df[filtered_df.name == cnty]['pct-white'] if not pd.isnull(p)])},
                                #marker = {'color': x/1},
                                #marker = {'colorscale': 'Viridis'},
                                opacity = .7,
                                #cumulative = True,
                                #autobinx = False,
                                xbins = {'start': -1, 'end': 1, 'size' : .1}

            ))
    return { # can only return first positional output
        'data': traces,
        'layout': go.Layout(#title = 'Checked Years {}'.format(checked_year_values),
            title= 'Histogram of County Correlation Coefficients for Selected Years',
            xaxis = {'title': 'Coefficient'},
            yaxis = {'title': 'Count'},
            hovermode = 'closest',
            paper_bgcolor = '#F4F4F8',
            plot_bgcolor = '#F4F4F8',
            #legend = {'x': -.1, 'y': 1.3, 'orientation': 'h'},
            #cumulative = True,
            #colorbar = True
            barmode = 'stack'

        )
    }


@app.callback(
    dash.dependencies.Output('checked-years', 'values'),
    [dash.dependencies.Input('census-checkbox', 'values')#,
    #dash.dependencies.Input('checked-years', 'values')
                        ]
)
def update_checked_years(checklist_values):
    if 'census_filter' in checklist_values:
        return ['2000', '2005', '2010', '2011']
    else:
        return [str(y) for y in YEARS]

if __name__ == '__main__':
	app.run_server(debug=True)
