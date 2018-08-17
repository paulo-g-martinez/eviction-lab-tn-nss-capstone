# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
#import dash_colorscales
import pandas as pd
import cufflinks as cf
import numpy as np
import re

import plotly.graph_objs as go
from scipy import stats

from plotly.offline import init_notebook_mode, iplot
from IPython.display import display, HTML
#init_notebook_mode(connected = True)

#app = dash.Dash(__name__)
app = dash.Dash()
#server = app.server

'''
####################################################
####---- READ AND PRE-PROCESS DATA ----------------#
####################################################
'''

counties_evicts_df = pd.read_csv('../data/counties.csv')
counties_evicts_df.rename(columns = {'low-flag': 'imputed',
                                    'imputed': 'subbed',
                                    'subbed': 'low-flag'}, inplace = True)
main_df = pd.read_csv('../data/all.csv', nrows = 17)
county_correlations_df = pd.read_csv('../data/county_correlations.csv')


'''###--- Add County Boxblot Time-Series Traces ----------------------'''
poverty_trace = go.Box(
    y = counties_evicts_df['poverty-rate'],
    x = counties_evicts_df.year,
    #hover = ('name'), # hover is not allowed in boxplot
    name = 'TN Poverty Rate Distributions',
    visible = 'legendonly',
    opacity = 0.5,
    marker = dict(color = '#434878', opacity = 0.5, symbol = 'square')
)
poverty_state_trace = go.Scatter(
    x = main_df[main_df.name == 'Tennessee'].year,
    y = main_df[main_df.name == 'Tennessee']['poverty-rate'],
    name = 'Tn Mean Poverty Rate  ',
	#visible = 'legendonly',
    line = dict(
    color = '#434878', dash = 'dash',
    width = 1)
)
eviction_trace = go.Box(
    y = counties_evicts_df['eviction-rate'],
    x = counties_evicts_df.year,
    name = 'TN Eviction Rate Distributions',
    opacity = 0.5,
    marker = dict(color = '#e24000', opacity = 0.75, symbol = 'square'),
	visible = 'legendonly',
)
eviction_state_trace = go.Scatter(
    x = main_df[main_df.name == 'Tennessee'].year,
    y = main_df[main_df.name == 'Tennessee']['eviction-rate'],
    name = 'Tn Mean Eviction Rate   ',
    line = dict(color = '#e24000', dash = 'dash', width = 1)
	#visible = 'legendonly',
)
'''filing_trace = go.Box(
    y = counties_evicts_df['eviction-filing-rate'],
    x = counties_evicts_df.year,
    name = 'County Filing Rates ',
    opacity = 0.5,
    marker = dict(color = 'orange', opacity = 0.5, symbol = 'square'),
	visible = 'legendonly',
) # the eviction-filing-rate traces (the % of renter occupied households that received an eviction filing in court but not necessarily an eviction) is currently not being used in the app.
filing_state_trace = go.Scatter(
    x = main_df[main_df.name == 'Tennessee'].year,
    y = main_df[main_df.name == 'Tennessee']['eviction-filing-rate'],
    name = 'Tn Mean Filing Rate  ',
    line = dict(
        color = 'orange', dash = 'dash',
        width = 1
    ),
	#visible = 'legendonly',
) # the eviction-filing-rate traces (the % of renter occupied households that received an eviction filing in court but not necessarily an eviction) is currently not being used in the app.
#---- Davidson Traces
davidsonPovertyTrace = go.Scatter(
    x = counties_evicts_df[counties_evicts_df.name == 'Davidson County'].year,
    y = counties_evicts_df[counties_evicts_df.name == 'Davidson County']['poverty-rate'],
    name = 'Davidson Pvty % ',
	visible = 'legendonly',
    line = dict(
    color = '#434878',
    width = 2)
)
davidsonEvicRateTrace = go.Scatter(
    x = counties_evicts_df[counties_evicts_df.name == 'Davidson County'].year,
    y = counties_evicts_df[counties_evicts_df.name == 'Davidson County']['eviction-rate'],
    name = 'Davidson Evic % ',
	visible = 'legendonly',
    line = dict(
    color = '#e24000',
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
)'''
timeSeriesData = [poverty_state_trace, eviction_state_trace, #filing_state_trace,
					poverty_trace,  eviction_trace, #filing_trace,
					#davidsonPovertyTrace, davidsonEvicRateTrace, davidsonEvicFilingRateTrace,
					]
'''###--- add each county poverty and eviction rates traces in a loop'''
for cnty in counties_evicts_df.name.unique():
    cnty_df = counties_evicts_df[counties_evicts_df.name == cnty]
    timeSeriesData.append(go.Scatter(
        x = cnty_df.year,
        y = cnty_df['poverty-rate'],
        name = cnty,
        visible = 'legendonly',
        line = {'color': '#434878', 'width' : '2'}
    ))
    timeSeriesData.append(go.Scatter(
        x = cnty_df.year,
        y = cnty_df['eviction-rate'],
        name = cnty,
        visible = 'legendonly',
        line = {'color': '#e24000', 'width' : 2}
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

'''###----- Add Scatter Plot with Linear Regression Traces -------'''
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

scatterData = [povertyEvictionTrace, povEvLineTrace#,
                #filingEvictionTrace, povFilingLineTrace
                ]
scatterLayout = dict(title = 'Linear Regression (OLS) Color-Coded by % White',
             			xaxis = dict(title = 'Eviction/Filing Rate'),
             			yaxis = dict(title = 'Poverty Rate'),
						#height = 700,
						legend = dict(x = -.1, y = 1.2,
                                        orientation = 'h'
									  )
						)

'''###--- Add Time-Series of the Correlation Coefficient ---###'''
x = counties_evicts_df.year.unique()
y = []
for yr in x:
    #print(x)
    y.append(np.corrcoef(
            x = counties_evicts_df[counties_evicts_df.year == yr].dropna()['eviction-rate'],
            y = counties_evicts_df[counties_evicts_df.year == yr].dropna()['poverty-rate']
    )[0][1])
    #print(y)
# add corrcoef timeseires trace
corrTimeSeriesTrace = go.Scatter(
    x = x,
    y = y,
    name = 'Pearson Corr. Coeff.',
	#visible = 'legendonly',
    line = dict(
        color = '#e24000',
        width = 2)
)
# add the r-squared trace
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
'''###--- Add a Histogram of County Correlation Coefficients'''
#######-------- corrHistogramData
corrHistPovEvicTrace = go.Histogram(
    x = county_correlations_df['pov-evic-corr'],
    marker = {'color':'#434878'},
    opacity = .5
)
corrHistogramData = [corrHistPovEvicTrace]
corrHistogramLayout = go.Layout(barmode = 'stack')
###### -------- bootstrapReplicates DATA
# for 1,000 simulated samples
bs_replicates = np.empty(1000)
for i in range(1000):
    # get indices of the empirical data
    inds = list(counties_evicts_df.dropna()['eviction-rate'].index)

    # get random selection of the indices (note: "double-dipping" is allowed)
    bs_inds = np.random.choice(list(counties_evicts_df.dropna()['eviction-rate'].index),
                              len(list(counties_evicts_df.dropna()['eviction-rate'].index)))

    # get the randomly sampled data pairs
    bs_ev_rate = counties_evicts_df.dropna()['eviction-rate'][bs_inds]
    bs_pv_rate = counties_evicts_df.dropna()['poverty-rate'][bs_inds]

    # get the
    bs_replicates[i] = np.corrcoef(x = bs_ev_rate, y = bs_pv_rate)[0][1]
bsRepsTrace = go.Histogram(
    x = bs_replicates,
    name = 'County-Wide BS Rep. Distribution',
    #text = str(np.median(filtered_df['pct-white'])),
    #hoverinfo = 'text',
    #marker = {'color' : filtered_df[filtered_df.name == cnty]['pct-white'].dropna().mean()},
    #marker = {'color': np.mean([p for p in filtered_df[filtered_df.name == cnty]['pct-white'] if not pd.isnull(p)])},
    #marker = {'color': x/1},
    #marker = {'colorscale': 'Viridis'},
    opacity = .2,
    #cumulative = True,
    #autobinx = False,
    #xbins = {'start': -1.0, 'end': 1.0, 'size' : .1}
)
bsReplicatesData = [bsRepsTrace]
bsReplicatesLayout = go.Layout(title = '95% Confidence Interval for Corr. Coeff: {}'.format(np.percentile(bs_replicates, [2.5, 97.5]).round(2)),
    xaxis = {'title': 'Coefficient'},
    yaxis = {'title': 'Count'},
    hovermode = 'closest',
    paper_bgcolor = '#F4F4F8',
    plot_bgcolor = '#F4F4F8',
    #legend = {'x': -.1, 'y': 1.3, 'orientation': 'h'},
    #cumulative = True,
    #colorbar = True,
    shapes = [
        # x,y reference to the plot, paper respectively
        {
            'type': 'line',
            'xref': 'x',
            'yref': 'paper',
            'x0': -0.21,
            'y0': 0,
            'x1': -0.21,
            'y1': 0.9,
            'line': {
                'color': '#e24000',
                'width': 2,
            },
        },
        # rectangle confidence Interval
        {
            'type': 'rect',
            'yref': 'paper',
            'x0': np.percentile(bs_replicates, 2.5),
            'y0': 0,
            'x1': np.percentile(bs_replicates, 97.5),
            'y1': 0.9,
            'line': {
                'color': '#e24000',
                'width': .5
            },
            'fillcolor': '#e24000',
            'opacity': '.1',
            }

        #},
    ]
)
# - initialize some utility variables -------

YEARS = [1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]
'''BINS = ['0-2', '2.1-4', '4.1-6', '6.1-8', '8.1-10', '10.1-12', '12.1-14', \
		'14.1-16', '16.1-18', '18.1-20', '20.1-22', '22.1-24',  '24.1-26', \
		'26.1-28', '28.1-30', '>30']
DEFAULT_COLORSCALE = ["#2a4858", "#265465", "#1e6172", "#106e7c", "#007b84", \
	"#00898a", "#00968e", "#19a390", "#31b08f", "#4abd8c", "#64c988", \
	"#80d482", "#9cdf7c", "#bae976", "#d9f271", "#fafa6e"]
DEFAULT_OPACITY = 0.4
DEFAULT_COLORSCALE = reversed(DEFAULT_COLORSCALE)
#mapbox_access_token = "pk.eyJ1IjoiamFja3AiLCJhIjoidGpzN0lXVSJ9.7YK6eRwUNFwd3ODZff6JvA"
'''
el_orange = '#e24000'
el_purple = '#434878'
el_green = '#2c897f'
cntyCensusYears = [y in [2000, 2005, 2010, 2011] for y in counties_evicts_df.year]
BonafideRows = [f == 0 for f in counties_evicts_df['low-flag']]
BonafideCensusRows = [census and bonafide for census, bonafide in zip(cntyCensusYears, BonafideRows)]
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~ APP LAYOUT ~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


app.layout = html.Div(children=[
    html.H1(children = 'Evictions & Poverty in Tennessee, 2000 - 2016',
        style = {'margin': 20, 'marginTop': 10, 'color': '#e24000'}
    ),
    html.H4("Here's the Story:", style = {'margin': 20, 'color': "#434878"}),#, className = 'three columns'),
    html.H5('* "Today, most poor renting families spend at least half of their income on housing costs"', style = {'margin': 20}),#, className = 'three columns'),
    html.H5('* "One in four of those families spending over 70 percent of their income just on rent and utilities"', style = {'margin': 20}),#, className = 'three columns'),
    html.H5('* "Incomes for Americans of modest means have flatlined while housing costs have soared"', style = {'margin': 20}),#, className = 'three columns'),
    html.H5('* "Only one in four families who qualifies for affordable housing programs gets any kind of help"', style = {'margin': 20}),#, className = 'three columns'),
    html.H5('* "Almost everywhere in the United States, evictions take place in civil court, where renters have no right to an attorney"', style = {'margin': 20}),
    html.H5('* "A growing number [of poor renting families] are living one misstep or emergency away from eviction"', style = {'margin': 20}),#, className = 'three columns'), #style = {'fontSize': 12, 'margin' : 5}),
    html.P('* This research uses data from The Eviction Lab at Princeton University, a project directed by Matthew Desmond and designed by Ashley Gromis, Lavar Edmonds, James Hendrickson, Katie Krywokulski, Lillian Leung, and Adam Porton. The Eviction Lab is funded by the JPB, Gates, and Ford Foundations as well as the Chan Zuckerberg Initiative. More information is found at evictionlab.org.', style = {'margin': 20, 'fontSize': 11}),#, style = {'fontSize': 11}, className = 'three columns'),
    #html.Br(),
    html.Div( #second row, as it were
        children = [
        html.Iframe(# inset of evictionlab.org map page
                    **{ #kwargs passed as a dictionary
                    'id':'eviction-lab-iframe',
                    'title':'Eviction Lab iframe',
                    'width': '97%',
                    'height': 700,
                    'src': 'https://evictionlab.org/map/#/2016?geography=counties&bounds=-90.752,31.558,-81.512,38.125&type=er&choropleth=pr&locations=47,-86.074,35.831%2B47037,-86.785,36.187%2B47157,-89.897,35.184'
                    },
                    style = {'margin': 20, 'marginRight': 0}),
        html.P("The Eviction Lab's Own Website and Interactive Map: (All content © 2018 Eviction Lab. All rights reserved)", style = {'margin': 5}),
        ], className = 'nine columns', style = {'marginLeft': 0, 'background-color': '#d7e3f4b3'}), #light purple #'background-color': '#e24000' #el orange
        # embeddable npr iframe with the desmond gross fresh air interview, #<iframe src="https://www.npr.org/player/embed/601783346/601892980" width="100%" height="290" frameborder="0" scrolling="no" title="NPR embedded audio player"></iframe>
        html.H2("What the Map Shows:", className = 'three columns', style = {'marginLeft': 20}),#, style = {'color': '#2c897f'}), #el green
        html.H5("Counties are colored in by poverty-rate (darker means poorer)", className = 'three columns', style = {'color': '#434878', 'marginLeft': 20}),
        html.P(html.I('Poverty-rate: percent of population living in poverty; recorded during census years only.', className = 'three columns', style = {'marginLeft': 35})),
        html.H5('Red bubbles are sized by eviction-rate (larger means higher eviction rate)', className = 'three columns', style = {'color': '#e24000', 'marginLeft': 20}),
        html.P(html.I('Eviction-rate: percent of the renting population that has received an eviction ruling in court; recorded annualy.', className = 'three columns', style = {'marginLeft': 35})),
        html.P("The Eviction Lab's map is highly interactive and allows you to explore multiple aspects of thier data. But since it combines eviction data, which is collected anually, with census data, which was only collected in 2000, 2005, 2010, & 2011, it can be hard to discern exactly what the relationship between evictions and poverty has been. (I.e. if you arrow through the year slider from 2000 to 2016 you'll notice that the poverty-rate data only updates during census years. This could lead to the misleading perception that when eviction-rates change poverty-rates do not.)", className = 'three columns', style = {'marginLeft': 20}),# For simplicity's sake the rest of this analysis will focus primarily on the relationship between eviction-rates and poverty-rates.", className = 'three columns'),
        #html.H5('* Only one in four families who qualifies for affordable housing programs gets any kind of help', className = 'three columns'),
        #html.H5('* A growing number [of poor renting families] are living one misstep or emergency away from eviction', className = 'three columns'), #style = {'fontSize': 12, 'margin' : 5}),
        #html.P('* This research uses data from The Eviction Lab at Princeton University, a project directed by Matthew Desmond and designed by Ashley Gromis, Lavar Edmonds, James Hendrickson, Katie Krywokulski, Lillian Leung, and Adam Porton. The Eviction Lab is funded by the JPB, Gates, and Ford Foundations as well as the Chan Zuckerberg Initiative. More information is found at evictionlab.org.', style = {'fontSize': 11}, className = 'three columns'),
    html.Div([ #-- LEFT COLUMN
		dcc.Graph(id = 'time-series',
			figure = go.Figure(data = timeSeriesData, layout = timeSeriesLayout)
		),
        html.H4("Explore the Correlation"),
        html.P('The scatter plot below initially seems to suggest that as the percentage of evicted renters goes up in a county, the percentage of people in poverty in that county goes down.'),
        html.Div([
        html.P(html.I("- Click through individual years to see how the correlation has changed over the years."), style = {'marginLeft': 20}),
        html.Div([ # year slider
            dcc.Slider(id = 'year-slider',
                        min=min(YEARS),
                        max= max(YEARS),
                        value= min(YEARS),
                        marks = {str(year): str(year) for year in YEARS},
                            ),
            ], style={'width':650, 'display':'inline-block', 'marginBottom':25, 'marginLeft': 20,
                }),
        html.P("In fact, the correlation seems to get weaker and weaker as we approach the peak of the housing crisis around 2009."),
        dcc.Graph(id = 'scatter-with-slider'),
            ], style = {'marginBottom': 0, 'marginTop': 0}),
        dcc.Checklist( id = 'checked-years',
            options = [{'label': str(yr), 'value': str(yr)} for yr in YEARS],
            values = [str(y) for y in YEARS],
            labelStyle = {'display': 'inline-block', 'fontSize': 10,
                            'margin': 1,
                            #'marginTop': 0, 'rotation':45
            }),
        #html.Br(),
        html.Div([
            html.H4('Cutting Through the Noise'),
            #html.P(html.I('Check the box to filter down to data from census years only.'), style = {'color': el_green}),
			dcc.Checklist(id='census-checkbox',
			    options=[{'label': 'Check the box to filter down to census-years only: (2000, 2005, 2010, 2011). Poverty Rates were only measured during census years.', 'value': 'census_filter'}
                ],
				values=[],
				labelStyle={'display': 'inline-block', 'color': el_green},
			),
            html.P(html.I("- Otherwise, during non-census years, it will seem like changes in eviction-rates are met with no change whatsoever in poverty-rates."), style = {'marginLeft': 20}),
            dcc.Checklist(id = 'low-checkbox',
                options = [{'label': 'Low-Flag Filter. Some eviction values were flagged as under-reported by The Eviction Lab.', 'value': 'low_flag_filter'}],
                values = [],
                labelStyle={'display': 'inline-block'},
            ),
		], style={'display':'inline-block'}),
        dcc.Graph(id = 'corr-timeseries',
            figure = go.Figure(data = corrTimeSeriesData, layout = corrTimeSeriesLayout)
        ),
	], className='seven columns', style={'margin':20}),
    html.Div([# -- RIGHT COLUMN
        html.Div([
            html.Br(),
            html.H4("How Eviction and Poverty Rates Have Changed Over Time")
        ], #style={'display': 'inline-block', 'marginTop': 20}
        ),
        html.P(html.I("- The dotted lines show Tennessee's average poverty rate and eviction rates over the years, but averages can be distorted by a even a few outliers."), style = {'marginLeft': 25}),
        html.H6(html.I("- For better a better idea of the overall distribution of poverty and eviction rates for TN counties click on the third and fourth items on the legend. They show the box-plot distributions for all of TN counties over the years."),style = {'marginLeft': 25, 'color': el_green}),
        html.P(html.I("- You can also scroll through the legend and click on the county you want to inspect individually."),style = {'marginLeft': 25}),
        html.P([
            "Notice that some counties have likely under-reported their eviction rates during some years. In fact, the entire state of TN has been flagged as under-reporting it's eviction rates because over 25% of TN counties under-report their own eviction rates.  ",
            html.A("See page 39 of the Eviction Lab's Methodology report pdf for the technical methods used for this determination.", href = 'https://evictionlab.org/docs/Eviction%20Lab%20Methodology%20Report.pdf', target = "_blank", style = {'fontSize': 11, 'display': 'inline-block'})
            ], style = {'color': el_orange}),
        html.Br(),
        html.Br(),
        html.H4('County Trends vs State Trends'),
        html.P('''TN's state-level overall correlation is weak, but there are counties with very strong "downwards" correlations (less than -.70) that, when taken as an average, are cancelling out those counties with very strong "updwards" correlation (greater than .70).'''),
        #html.P(html.I("The histogram below initally shows a 'bimodal distribution' where most counties seem to have a weak (strength less than .50) correlation between their eviction and poverty rates."), style = {'marginLeft': 20}),
        #html.P(""),
        dcc.Graph(id = 'corr-histogram',
            figure = go.Figure(data = corrHistogramData, layout = corrHistogramLayout)
        ),
        html.P(html.I("Hover over the Histogram to see a county's rates"), style = {'color': el_green, 'marginLeft': 20}),
        html.H5('When we filter down to census-year data we can see that, in fact, most counties have a significant correlation between eviction and poverty rates. But the effect is polarized; In some counties eviction and poverty rates seem to, like magnets, repel eachother, and in others they seem to attract eachother.', style = {'color': el_orange}),
        html.P("Select a county to analyze its individual correlation data", style={'display': 'inline-block', 'color': el_green}),
    	dcc.Dropdown(id = 'county-dropdown',
            options = [{'label':cnty, 'value':cnty} for cnty in counties_evicts_df.name.unique()],
            value = None,
    	),
        #html.Br(),
        dcc.Graph(id = 'bootstrap-replicates-distribution',
            figure = go.Figure(data = bsReplicatesData, layout = bsReplicatesLayout)
        ),
        html.P('* This research uses data from The Eviction Lab at Princeton University, a project directed by Matthew Desmond and designed by Ashley Gromis, Lavar Edmonds, James Hendrickson, Katie Krywokulski, Lillian Leung, and Adam Porton. The Eviction Lab is funded by the JPB, Gates, and Ford Foundations as well as the Chan Zuckerberg Initiative. More information is found at evictionlab.org., consulted, 07-24-2018, CST')
	], className='five columns', style={'margin':0}),
])
## Stlye Sheet
app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/EQZeaW.css'}),

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~ app interactivity/callbacks ~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
@app.callback(
    dash.dependencies.Output('scatter-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
                        Input('low-checkbox', 'values'),
                        Input('checked-years', 'values'),
                        Input('county-dropdown', 'value')
    ])
def update_scatter(selected_year, checklist_values, checked_year_values, selected_county):
    #print('selected_year', selected_year)
    #print('============>>>>>>>>sel cnty', selected_county)
    #------ handle filters
    fltr = [str(y) in checked_year_values for y in counties_evicts_df.year]
    if 'low_flag_filter' in checklist_values:
        fltr = [f and bnfd for f, bnfd in zip(fltr, BonafideRows)]
    filtered_df = counties_evicts_df[fltr]
    # filter by county
    if selected_county != None:
        filtered_df = filtered_df[[cnty in selected_county for cnty in filtered_df.name]]
    #------ add checked year(s) scatter and line
    traces=[]
    # add the checked scatter
    traces.append(go.Scatter(
        x = filtered_df['eviction-rate'],
        y = filtered_df['poverty-rate'],
        text = filtered_df['name']
        #zip(filtered_df['name'], filtered_df['year'])
        #filtered_df[['name', 'year']] # 'DataFrame' is not JSON serializable
        #str(filtered_df['name']) #+ str(filtered_df['year']) #returns enormous string of series
        ,
        mode = 'markers',
        opacity = '0.4',
        marker = {'symbol': 'circle',#'circle-open',
            'size' : 10,
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
                color = '#e24000', #dash = 'dot', #opacity = 0.3,
                width = 3),
                name = 'Selected Years Lin. Reg.',
                opacity = .5,
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
                'size' : 11,
                'line': {'width':1.5, 'color': 'black'},
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
                color = '#e24000',
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
    for cnty in sorted(set(filtered_df.name)):
        cc = round(
                np.corrcoef(
                        x = filtered_df[filtered_df.name == cnty].dropna()['eviction-rate'],
                        y = filtered_df[filtered_df.name == cnty].dropna()['poverty-rate']
                    )[0][1],
                3)
        if not pd.isnull(cc):
            traces.append(go.Histogram(
                                x = [cc],
                                name = cnty.split(' ')[0],
                                #name = str(filtered_df[filtered_df.name == cnty]['poverty-rate'].dropna().mean()),
                                text =  cnty.split(' ')[0] + ': ' +
                                        'corr. ' + str(cc) + ',\n' +
                                        ' mdn evic %: ' + str(round(filtered_df[filtered_df.name == cnty]['eviction-rate'].dropna().median(), 3)) + ',\n' +
                                        ' mdn pvty %: ' + str(round(filtered_df[filtered_df.name == cnty]['poverty-rate'].dropna().median(), 3)) + ',\n'
                                ,
                                hoverinfo = 'text',
                                hoverlabel = {'bgcolor': '#e24000'},
                                marker = {'color' : '#434878', 'line':{'width': .1, 'color': 'white'}},
                                #marker = {
                                #    'color': 'red',
                                #    'line': {
                                #        'color': filtered_df[filtered_df.name == cnty]['poverty-rate'].dropna().mean(),
                                #        'color': '#434878',
                                #        #'color': '#F4F4F8',
                                #        #'cmin': 0,
                                #        #'cmax': 30, #max poverty rate is 30%
                                #        #'colorscale': 'Purples',
                                #        #'colorscale': 'Viridis',
                                #        #'reversescale': True,
                                #        'width': 10 - filtered_df[filtered_df.name == cnty]['eviction-rate'].dropna().mean()
                                #    }
                                #},
                                #opacity = 1,
                                opacity = filtered_df[filtered_df.name == cnty]['poverty-rate'].dropna().mean()/30, #scaled over 30 since that is the max saturation value on eviction lab's own choropleth
                                #opacity = filtered_df[filtered_df.name == cnty]['pct-white'].dropna().mean()/100,
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
            barmode = 'stack',
            #bargap = 0.8,
            #bargroupgap = 0.5,

        )
    }

@app.callback(
    dash.dependencies.Output('bootstrap-replicates-distribution', 'figure'),
    [dash.dependencies.Input('low-checkbox', 'values'),
                        Input('checked-years', 'values'),
                        Input('county-dropdown', 'value')]
)
def update_confidence_interval(checklist_values, checked_year_values, selected_county):
    #------ handle filters
    #print('in update conf func')
    fltr = [str(y) in checked_year_values for y in counties_evicts_df.year]
    if 'low_flag_filter' in checklist_values:
        fltr = [f and bnfd for f, bnfd in zip(fltr, BonafideRows)]
    filtered_df = counties_evicts_df[fltr]
    if selected_county != None:
        filtered_df = filtered_df[[cnty in selected_county for cnty in filtered_df.name]]
    #------ add trace for each county
    traces = []
    bs_replicates = np.zeros(200)
    print('entering bs reps loop')
    for i in range(200):
        #print(i)
        # get indices of the empirical data
        inds = list(filtered_df.dropna()['eviction-rate'].index)
        # get random selection of the indices (note: "double-dipping" is allowed)
        bs_inds = np.random.choice(list(filtered_df.dropna()['eviction-rate'].index),
                                    len(list(filtered_df.dropna()['eviction-rate'].index)))
        # get the randomly sampled data pairs
        bs_ev_rate = filtered_df.dropna()['eviction-rate'][bs_inds]
        bs_pv_rate = filtered_df.dropna()['poverty-rate'][bs_inds]
        # get the bs replicates themselves
        if not pd.isnull(np.corrcoef(x = bs_ev_rate, y = bs_pv_rate)[0][1]):
            bs_replicates[i] = np.corrcoef(x = bs_ev_rate, y = bs_pv_rate)[0][1]
        xbn = [r for r in bs_replicates if not pd.isnull(r)]
    traces.append(go.Histogram(
        #x = bs_replicates.dropna(),
        x = xbn,
        name = 'County-Wide BS Rep. Distribution',
        #text = str(np.median(filtered_df['pct-white'])),
        #hoverinfo = 'text',
        #marker = {'color' : filtered_df[filtered_df.name == cnty]['pct-white'].dropna().mean()},
        #marker = {'color': np.mean([p for p in filtered_df[filtered_df.name == cnty]['pct-white'] if not pd.isnull(p)])},
        #marker = {'color': x/1},
        #marker = {'colorscale': 'Viridis'},
        opacity = .2,
        #cumulative = True,
        #autobinx = False,
        #xbins = {'start': -1.0, 'end': 1.0, 'size' : .1}
    ))

    return { # can only return first positional output
        'data': traces,
        'layout': go.Layout(title = '95% Confidence Interval for Corr. Coeff: {}'.format(np.percentile(xbn, [2.5, 97.5]).round(2)),

                        yaxis = {'title': 'Count'},
                        xaxis = {'title': 'Correlation Coeff.',
                            'range': [-1.1, 1.1]},
                        hovermode = 'closest',
                        paper_bgcolor = '#F4F4F8',
                        plot_bgcolor = '#F4F4F8',
                        #legend = {'x': -.1, 'y': 1.3, 'orientation': 'h'},
                        #cumulative = True,
                        #colorbar = True,
                        shapes = [
                        # x,y reference to the plot, paper respectively
                        {
                        'type': 'line',
                        'xref': 'x',
                        'yref': 'paper',
                        'x0': round(np.corrcoef(x = filtered_df.dropna()['eviction-rate'],
                                                y = filtered_df.dropna()['poverty-rate']
                                                )[0][1], 2),
                        'y0': 0,
                        'x1': round(np.corrcoef(x = filtered_df.dropna()['eviction-rate'],
                                                y = filtered_df.dropna()['poverty-rate']
                                                )[0][1], 2),
                        'y1': 0.9,
                        'line': {
                            'color': '#e24000',
                            'width': 2,
                            },
                        },
                        # rectangle confidence Interval
                        {
                        'type': 'rect',
                        'yref': 'paper',
                        'x0': np.percentile(xbn, 2.5),
                        'y0': 0,
                        'x1': np.percentile(xbn, 97.5),
                        'y1': 0.9,
                        'line': {
                            'color': '#e24000',
                            'width': .5
                            },
                            'fillcolor': '#e24000',
                            'opacity': '.1',
                            }]
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
