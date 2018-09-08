# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
#import dash_colorscales
import pandas as pd
import cufflinks as cf
import numpy as np
#import re

import plotly.graph_objs as go
from scipy import stats

from plotly.offline import init_notebook_mode, iplot
from IPython.display import display, HTML
#init_notebook_mode(connected = True)
import colorlover as cl

app = dash.Dash(__name__)
#app = dash.Dash()

server = app.server

'''
####################################################
####---- READ AND PRE-PROCESS DATA ----------------#
####################################################
'''

counties_evicts_df = pd.read_csv('https://raw.githubusercontent.com/paulo-g-martinez/eviction-lab-tn-nss-capstone/master/data/counties.csv')
counties_evicts_df.rename(columns = {'low-flag': 'imputed',
                                    'imputed': 'subbed',
                                    'subbed': 'low-flag'}, inplace = True)
main_df = pd.read_csv('https://raw.githubusercontent.com/paulo-g-martinez/eviction-lab-tn-nss-capstone/master/data/all.csv', nrows = 17)
county_correlations_df = pd.read_csv('https://raw.githubusercontent.com/paulo-g-martinez/eviction-lab-tn-nss-capstone/master/data/county_correlations.csv')

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
#Purples = cl.scales['30']['seq']['Purples']
cntyCensusYears = [y in [2000, 2005, 2010, 2011] for y in counties_evicts_df.year]
BonafideRows = [f == 0 for f in counties_evicts_df['low-flag']]
BonafideCensusRows = [census and bonafide for census, bonafide in zip(cntyCensusYears, BonafideRows)]

'''###--- Add County Boxblot Time-Series Traces ----------------------'''
poverty_trace = go.Box(
    y = counties_evicts_df['poverty-rate'],
    x = counties_evicts_df.year,
    #hover = ('name'), # hover is not allowed in boxplot
    name = 'TN Poverty % Dist.',
    visible = 'legendonly',
    opacity = 0.5,
    marker = dict(color = '#434878', opacity = 0.5, symbol = 'square')
)
poverty_state_trace = go.Scatter(
    x = main_df[main_df.name == 'Tennessee'].year,
    y = main_df[main_df.name == 'Tennessee']['poverty-rate'],
    name = 'Tn Mean Poverty %',
	#visible = 'legendonly',
    line = dict(
    color = '#434878', dash = 'dash',
    width = 1)
)
eviction_trace = go.Box(
    y = counties_evicts_df['eviction-rate'],
    x = counties_evicts_df.year,
    name = 'TN Eviction % Dist.',
    opacity = 0.5,
    marker = dict(color = '#e24000', opacity = 0.75, symbol = 'square'),
	visible = 'legendonly',
)
eviction_state_trace = go.Scatter(
    x = main_df[main_df.name == 'Tennessee'].year,
    y = main_df[main_df.name == 'Tennessee']['eviction-rate'],
    name = 'Tn Mean Eviction %',
    line = dict(color = '#e24000', dash = 'dash', width = 1)
	#visible = 'legendonly',
)
eviction_under_reporters_trace = (go.Box(
    x = counties_evicts_df[counties_evicts_df['low-flag'] == 1].year,
    y = counties_evicts_df[counties_evicts_df['low-flag'] == 1]['eviction-rate'],
    name = 'Under-Report Dist.',
    visible = 'legendonly',
    marker = {'color': 'gold', 'opacity': .75, 'symbol' : 'square'}
))

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
					poverty_trace,  eviction_trace, eviction_under_reporters_trace, #filing_trace,
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
        line = {'color': '#434878', 'width' : 2}
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
        name = cnty.split()[0]+' low flag',
        visible = 'legendonly',
        mode = 'markers',
        marker = {'color': 'gold', 'opacity': .5,
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
                        #width = '90%',
                        margin = {'l': 0, 'r': 0},
                        #legend = dict(#x = 0, y = -20,
						#			  orientation = 'h',),
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
        colorscale = 'Viridis',
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
        'width': 2
    },
    visible = 'legendonly',
)
corrTimeSeriesData = [corrTimeSeriesTrace, determinationCoeffTimeSeriesTrace]
corrTimeSeriesLayout = dict(#title = 'Correlation on a Scale From -1.0 to 1.0',
                        titlefont = {'size': 15, 'color': '#e24000'},
             			xaxis = dict(title = 'Year'),
             			yaxis = dict(title = 'Pearson Corr. Coeff.'),
              			#boxmode = 'group',
						#height = 150,
                        #margin = {'t': 10, 'b': 10},
						#legend = dict(#x = -.1, #y = 1.1, orientation = 'v'),
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
bs_replicates = np.empty(200)
for i in range(200):
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
bsReplicatesLayout = go.Layout(
    #title = '95% Confidence Interval for Corr. Coeff: {}'.format(np.percentile(bs_replicates, [2.5, 97.5]).round(2)),
    title = '{}'.format(np.percentile(bs_replicates, [2.5, 97.5]).round(2)),
    titlefont = {'size': 15, 'color': el_orange},
    #height = 250,
    #margin = {'t': 40, 'b': 30},
    #xaxis = {'title': 'Coefficient'},
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
            'opacity': .1,
            }

        #},
    ]
)

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~ APP LAYOUT ~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <meta name="viewport" content="width=device-width,initial-scale=0.625">
        <title>Martinez Capstone</title>
        <link rel="icon" type="image/png" href="assets/corrTseriesIcon.png">
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
        </footer>
    </body>
</html>
'''


app.layout = html.Div(children=[
    html.Div(id = 'first-row', children= [#first row ----
        html.H1( #title
            children = 'Unpacking the Eviction-Poverty Correlation in Tennessee, 2000 - 2016',
            style = {'margin': 20, 'marginTop': 20, 'color': el_orange}
        ),
        # embeddable me with the NPR desmond gross fresh air interview, #<me src="https://www.npr.org/player/embed/601783346/601892980" width="100%" height="290" frameborder="0" scrolling="no" title="NPR embedded audio player"></me>
        html.Div( # subtitle and bullets
            children=[
            html.H2("Why Evictions? Here's the Story:", style = {'margin': 20}),
            html.H5(' - "Today, most poor renting families spend at least half of their income on housing costs*"', style = {'margin': 20}),
            html.H5(' - "One in four of those families spending over 70 percent of their income just on rent and utilities*"', style = {'margin': 20}),
            html.H5(' - "Incomes for Americans of modest means have flatlined while housing costs have soared*"', style = {'margin': 20}),
            html.H5(' - "Only one in four families who qualifies for affordable housing programs gets any kind of help*"', style = {'margin': 20}),
            html.H5(' - "Almost everywhere in the United States, evictions take place in civil court, where renters have no right to an attorney*"', style = {'margin': 20}),
            html.H5(' - "A growing number [of poor renting families] are living one misstep or emergency away from eviction*"', style = {'margin': 20}),
            html.P('* This research uses data from The Eviction Lab at Princeton University, a project directed by Matthew Desmond and designed by Ashley Gromis, Lavar Edmonds, James Hendrickson, Katie Krywokulski, Lillian Leung, and Adam Porton. The Eviction Lab is funded by the JPB, Gates, and Ford Foundations as well as the Chan Zuckerberg Initiative. More information is found at evictionlab.org.',
                style = {'margin': 20, 'fontSize': 11, 'fontFamily': 'Monaco, monospace', 'color':'grey'},
            ),
        ]),
    ]),#---------------------- end first row
    html.Div(id = 'second-row',# secod row ----
        children = [
            html.Div([ #row 2 header
                html.H2("25% of Tennessee counties under-report their eviction data.*"),
            ], style = {'textAlign': 'right', 'marginRight': 20, 'marginTop': 100}
            ),
        html.Div(children = [# row 2, left column
                html.Div(# .iframe-container biggerThanMobile
                    children = [
                        html.Iframe(
                            **{
                                'src': 'https://evictionlab.org/map/#/2016?geography=counties&bounds=-94.033,31.119,-80.472,39.343&type=er&choropleth=pr&locations=47,-87.187,35.804%2B47037,-86.785,36.187', #'https://evictionlab.org/map/#/2016?geography=counties&bounds=-91.23,30.388,-79.584,37.785&type=er&choropleth=pr&locations=47,-85.908,35.813%2B47037,-86.785,36.187',#'https://evictionlab.org/map/#/2016?geography=counties&bounds=-90.911,29.999,-79.903,38.14&type=er&choropleth=pr&locations=47,-85.908,35.813%2B47037,-86.785,36.187',
                            },
                            style = {
                                'position': 'absolute',
                                'top': 0,
                                'left': 0,
                                'width': '100%',
                                'height': '100%',
                            },
                        ),
                    ],
                    style = {
                        'position': 'relative',
                        'paddingBottom': '80%',
                        'height': 0,
                        'overflow': 'scroll',
                        #'display': 'none', #this should be handled in the css
                    },
                    className = 'biggerThanMobile',
                ),
                html.Div(children = [ #iframe-container mobile
                    html.Iframe(# iframe of evictionlab.org
                            **{ #kwargs passed as a dictionary
                            'id':'eviction-lab-iframe',
                            'title':'Eviction Lab iframe',
                            'width': '100%',
                            'height': '100%',
                            #'src': 'https://evictionlab.org/map/#/embed/2016?geography=counties&bounds=-93.571,28.167,-79.256,40.043&type=er&choropleth=pr&locations=47,-85.984,35.832%2B47037,-86.786,36.187', #this will give a weaker but less volatile inset of a map.
                            'src': "https://evictionlab.org/map/#/embed/2016?geography=counties&bounds=-93.421,28.893,-79.262,39.659&type=er&choropleth=pr&locations=47,-87.187,35.804%2B47037,-86.785,36.187"
                            },
                            style = {#iframe style
                                'marginLeft': 0, 'marginRight': 0,
                                'border': 0, 'height': '100%', 'left': 0,
                                'position': 'absolute', 'top': 0, #'width': '100%',
                            }
                    ),
                    html.Script(
                        **{
                        'type': 'text/javascript',
                        'src': "https://pym.nprapps.org/pym-loader.v1.min.js",
                        },
                    ),
                ], style = {
                'overflow': 'hidden',
                 'paddingBottom': '56.25%',
                 'position': 'relative'},
                 className = 'forMobile',
                ),
                ###############################################
                html.P("The Eviction Lab's Own Website and Interactive Map: (All content © 2018 Eviction Lab. All rights reserved)", style = {'marginLeft': 20}),
            ], className = 'nine columns', style = {'marginLeft': 0, 'height': '3em'}
        ),#-------------------------------------- end row 2, left col
        html.Div( # row 2 right col
            children = [
                html.I([html.A("* See page 39 of the Eviction Lab's Methodology report pdf for the technical methods used for this determination.",
                            href = 'https://evictionlab.org/docs/Eviction%20Lab%20Methodology%20Report.pdf',
                            target = "_blank",
                            style = {'fontSize': 11, 'textAlign': 'right'},
                        ),
                ], style = {'marginLeft': '0em', 'marginTop': '0em'}),
                html.H5(['🔍', html.I("The Eviction Lab's map is highly interactive. Click on a county to see more information about its eviction and poverty data.")],
                style = {'color': el_green, 'marginLeft': '0em', 'marginTop': '1em'}),
                html.Div([# tech specs
                    html.H6(html.B('Technical Specifications: ')),
                    html.P([html.B('- Poverty Rate: '), 'Percent of population living in poverty; recorded during census years only']),#'fontFamily': 'DecimaMono,Consolas,Monaco,monospace'}),
                    html.P([html.B('- Eviction Rate: '),'Percent of the renting population that has received an eviction ruling in court; recorded annualy']),
                    html.P([html.B('- Red bubbles: '),'Are sized by eviction rate (a larger bubble indicates a higher eviction rate)']),
                    html.P([html.B('- Shading: '), 'Counties are shaded in by poverty rate (a deeper shade indicates a higher poverty rate)']),
                    html.P([
                        html.B('Periodicity Problem: '),
                        "The map combines eviction data (which is collected anually) with census data (which was only collected in 2000, 2005, 2010, & 2011) making it more difficult to discern exactly what the relationship between evictions and poverty has been. (I.e. if you arrow through the year slider from 2000 to 2016 you'll notice that the poverty rate data only updates during census years. This could lead to the misleading perception that when eviction rates change poverty-rates do not.)",
                        html.P("   For simplicity the rest of this analysis will focus primarily on the relationship between eviction-rates and poverty-rates. It should be noted, however, that potentially significant differentiation across the racial composition and urbanization of a county has also been observed prima facie and requires further investigation.")
                        ]),
                    ], style = {'fontFamily': 'Times New Romann, Times, serif', 'marginTop': '1em', 'color': 'grey'}),
                ], className = 'three columns',
                style = {'height': 'auto', 'marginLeft': '.5em'},
        ),#------------------------ end row 2, right col
    ], style = {'height': 'auto', 'marginBottom': '0em'}), #---------------------- end second row
    html.Div(id = 'third-row',# third row ----
        children = [
            html.H2('One out of every four Tennessee counties has a poverty rate above 17%', style = {'marginLeft': 20, 'marginBottom': 0, 'marginTop': '0em', 'display': 'block'}),
            html.Div([# third row left column
                html.P(" TN's average poverty rate was 13% during the last census (in 2011). But that average has been skewed downwards by a few outlier counties with very low poverty rates.", style = {'marginTop': '3em', 'marginLeft': 25}),
                html.H5(['🔍 ', html.I("Scroll through the chart's legend and click on any county to see its eviction and poverty rates and for which years, if any, it under-reported its eviction data.")], style = {'color': el_green, 'marginLeft': 25}),
                html.P([
                    html.H6(html.B('Displaying & analyzing the annual distributions: ')),
                    html.P('- Click on the 3rd or 4th items in the chart legend to display a time series of box plots.'),
                    html.P('- Hover over a box plot to display the values of each quartile as well as the median value.'),
                    html.P('- Double click a legend item to toggle between isolating that trace and displaying all traces together.'),
                    html.P('- Click and drag over the plot area to zoom into the selected area. (Double click anywhere on the plot area to reset to the default zoom.)'),
                    html.P('- Click and drag over the tick marks of an axis to scroll through that axis.'),
                ] ,style = {'color': 'grey', 'fontFamily': 'Times New Roman, Times, serif', 'marginLeft': 20}),
            ], className = 'five columns', style = {'marginLeft': '0em', 'marginRight': '0em'}),
            html.Div([# third row right column
                dcc.Graph(id = 'time-series',
        			     figure = go.Figure(data = timeSeriesData, layout = timeSeriesLayout),
        		          style = {'margin':10}),
            ], className = 'seven columns', style = {'marginRight': '0em'}),
        ],style = {'marginTop': '90em'}
    ), #---------------------- end third row
    html.Br(),
    html.Div(id = 'fourth-row', children = [# fourth row ---
        html.H2('In Tennessee, eviction & poverty rates have been correlated negatively & weakly. This is changing quickly.',
            #className = 'twelve columns', style = {'textAlign': 'right', 'marginTop': 100}, #margin right nnot working
            style = {'textAlign': 'right', 'marginTop': '20em', 'marginRight': 20},
        ),
        html.Div([# fourth row left column
            html.Div([
                html.Div([# year slider
                    dcc.Slider(id = 'year-slider',
                            min=min(YEARS),
                            max= max(YEARS),
                            value= min(YEARS),
                            marks = {year: {'label': str(year), 'style': {'color': el_orange}} if year in [2000, 2005, 2010, 2011] else {'label': str(year), 'style': {'color': 'grey'}} for year in YEARS},
                            included = False,
                    ),
                ], style={'marginTop': 0,
                    #'width':650,
                    #'display':'inline-block',
                    'marginBottom':25,
                    #'marginLeft': 0, #not working
                    #'color': el_orange, #not working
                    }
                ),
                html.P(['🔍', html.I('Click through individual years to see how the correlation has changed.')],
                style = {'marginTop': 20, 'marginLeft': 0, 'color': el_green, 'marginBottom': 0}),
                dcc.Graph(id = 'scatter-with-slider'),
            ], style = {'marginBottom': 0, 'marginTop': 0, 'marginLeft': 0}),
            html.Div([dcc.Checklist( id = 'checked-years',
                    options = [{'label': str(yr), 'value': str(yr)} for yr in YEARS if yr >1999],
                    values = [str(y) for y in YEARS if y > 1999 ],
                    labelStyle = {'display': 'inline-block', 'fontSize': 9, 'margin': 1}),
    		], style={'display':'inline-block'}),
        ], className = 'seven columns'),
        html.Div([ # fourth row right column
            html.P([html.B('''The correlation appears to be disappearing. Either that or "the pendulum is beginning to swing the other way" and a strengthening positive correlation is taking root.'''), ' (Meaning every additional increase in eviction rates would correspond to a larger and larger increase in poverty rates.)'],
            style = {'marginLeft': '2em', 'marginTop': '0em', 'marginRight': 20}),
            html.P('''For TN, the linear model predicts a 3% decrease in poverty rates for every 4% increase in eviction rate.''',
            style = {'marginLeft': '2em', 'marginTop': 10, 'marginRight': 20, 'color': 'grey', 'fontFamily': 'Times New Roman, Times, serif'}),
            html.Div([
                html.P('Correlation Coefficient For Selected Years and Counties:', style = {'marginLeft': '2em', 'marginTop': 10, 'textAlign': 'left'}),
                dcc.Graph(id = 'corr-timeseries',
                    figure = go.Figure(data = corrTimeSeriesData, layout = corrTimeSeriesLayout), #style = {'display': 'inline-block',}, #'marginRight': 80}
                ),
            ]),
            html.P([html.B('To overcome the periodicity problem: '), ' we can filter out eviction data from years without a census measurement of the poverty rate.'],
            style = {'marginLeft': 20, 'marginTop': 10, 'color': 'grey', 'fontFamily': 'Times New Roman, Times, serif'}),
            html.Div([
                dcc.Checklist(id='census-checkbox',
                    options=[{'label': 'Census-years only: (2000, 2005, 2010, 2011).',# Poverty Rates were measured only during census years.',
                                'value': 'census_filter'}
                    ],
                    values=['census_filter'],
                    labelStyle={'display': 'inline-block', 'color': el_green},
                ),
                dcc.Checklist(id = 'low-checkbox',
                    options = [{'label': 'Low-Flag Filter.',#Some eviction values were flagged as under-reported by The Eviction Lab.',
                    'value': 'low_flag_filter'}],
                    values = [],
                    labelStyle={'display': 'inline-block'},
                ),
            ], style = {'marginLeft': '2em'}),
        ], className = 'five columns', style = {'marginRight': 0, 'marginLeft': 0}),
    ],), #-------------------- end fourth row
    html.Div(id = 'fifth-row', children = [# fifth row ----
        html.H3('''Counties' eviction & poverty rate correlations may be extreme and polarized.''',
            className = 'twelve columns', style = {'textAlign': 'left', 'marginTop': 10, 'marginBottom': 0, 'marginLeft': 20}
        ),
        html.Div([ #-- fifth row LEFT COLUMN
            html.P('''While TN as a state has a weak correlation, there is evidence to suggest that the majority of its counties actually have very strong correlations between their eviction and poverty rates.''',
            style = {'marginTop': 0, 'marginLeft': 20}),
            html.P('''In some counties an increase in eviction rates would seem to accompany a big decrease in the percent of that county's population that is living in poverty. But in other counties an increase in eviction rates might be accompanied by a big increase in the percent of its population that is living in poverty.''',
            style = {'marginTop': 0, 'marginLeft': 20}),
            html.Div([
                dcc.Dropdown(id = 'county-dropdown',
                    options = [{'label':cnty, 'value':cnty} for cnty in counties_evicts_df.name.unique()],
                    value = None,
                    multi = True,
                    placeholder = '🔍 Select a county to analyze its individual correlation data',
            	),
                html.P(html.I("🔍 Hover over the Histogram to see a county's rates"),
                style = {'color': el_green, 'marginTop': 20, 'margin': 20, 'textAlign': 'left'}),
            ], style = {'marginLeft': 20},),
            html.B('Additional data is required ', style = {'marginLeft': 20, 'marginTop': 100}),
            html.P("A single county only has four data points (the census years); not enough to find a good degree of confidence in the hypothesized correlation coefficient. One way to overcome this obstacle is the addition of reliable annual poverty data for each county.",
            style = {'marginLeft': 20}),
        ], className='five columns', style={'margin':20, 'marginTop': 20, 'marginLeft': 0, 'marginRight': 0}),
        html.Div([# fifth row RIGHT COLUMN
            html.P('Histogram of County Correlation Coefficients for Selected Years', style = {'textAlign': 'center', 'marginTop': 20, 'marginBottom': 0}),
            dcc.Graph(id = 'corr-histogram',
                figure = go.Figure(data = corrHistogramData, layout = corrHistogramLayout),
            ),
            html.P('95% Confidence Interval for Correlation Coefficient for Selected Years and Counties', style = {'marginTop': 15, 'textAlign': 'center'}),
            dcc.Graph(id = 'bootstrap-replicates-distribution',
                figure = go.Figure(data = bsReplicatesData, layout = bsReplicatesLayout)
            ),
            html.P("The confidence interval chart uses  200 bootstrap replicate correlation coefficients for the input data. (If the interval does not have a tight bell-curve behind it, then you can be 95% confident we don't know what the correlation coefficient actually is.)",
                style = {'marginLeft': 20, 'marginBottom': '7.5em', 'color': 'grey', 'fontFamily': 'Times New Roman, Times, serif'}
            ),
    	], className='seven columns', style={'marginLeft':0, 'marginRight': 0}),
    ]), #--------------------- end fifth row
])
## Stlye Sheet: currently serving locally from assets/moded.csv
#app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/EQZeaW.css'}),


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
    #if selected_county != None:
    if selected_county: #pythonically leverage some sort of inherent boolean attribute of empty objects
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
        opacity = 0.4,
        marker = {'symbol': 'circle',#'circle-open',
            'size' : 10,
            'line': {'width':.5, 'color': 'white'},
            'color': counties_evicts_df['pct-white'],
            'colorbar': {'x': -.3, 'title': 'pct-white','thickness': 15},
            'colorscale' : 'Viridis',
            'showscale' : True
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
                        legend = {'x' : 'center', 'y' : 1.15,
                        'orientation': 'h'},

                    )
    }

@app.callback(
    dash.dependencies.Output('corr-timeseries', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
                        Input('low-checkbox', 'values'),
                        Input('checked-years', 'values')])
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
            name = 'Pearson Correlation Coefficient',
        	#visible = 'legendonly',
            line = dict(
                color = el_orange,
                width = 3)
        )
    ),
    traces.append(
        go.Scatter(
            x = x,
            y = [r*r for r in y],
            name = 'Coefficient of Determination, r-squared',
            line = {
                'color' : 'magenta',
                'width': 2
            },
            visible = 'legendonly',
        )
    ),
    return { # can only return first positional output
        'data': traces,
        'layout': go.Layout(
            #title= 'County-Wide Correlation Coefficient for Selected Years: {}'.format(round(np.corrcoef(
            title = '{}'.format(round(np.corrcoef(
                                                    x = filtered_df.dropna()['eviction-rate'],
                                                    y = filtered_df.dropna()['poverty-rate']
                                    )[0][1], 2)
            ),
            #xaxis = {'title': 'Year'},
            yaxis = {'title': 'Coeff'},
            paper_bgcolor = '#F4F4F8',
            plot_bgcolor = '#F4F4F8',
            legend = {'x': -.1, 'y': 1.3,#'xanchor': 'left',
                #'xanchor': 'left',
                'orientation': 'h'},
            titlefont = {'size': 15, 'color': '#e24000'},
            height = 230,
            #width = 400,
            margin = {'t': 90, 'b': 0},
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
                1)
        if not pd.isnull(cc):
        #if 0 == 1: #used as an on/off switch during debugging
            traces.append(go.Histogram(
                                x = [cc],
                                name = cnty.split()[0],
                                #name = cnty.split(' ')[0],
                                #name = str(filtered_df[filtered_df.name == cnty]['poverty-rate'].dropna().mean()),
                                text =  cnty.split(' ')[0] + ': ' +
                                        'corr. ' + str(cc) + ',\n' +
                                        ' mdn evic %: ' + str(round(filtered_df[filtered_df.name == cnty]['eviction-rate'].dropna().median(), 1)) + ',\n' +
                                        ' mdn pvty %: ' + str(round(filtered_df[filtered_df.name == cnty]['poverty-rate'].dropna().median(), 1)) + ',\n'
                                ,
                                hoverinfo = 'text',
                                hoverlabel = {'bgcolor': '#e24000'},
                                marker = {#'color' : '#434878',
                                    'cmax': 30,
                                    'cmin': 0,
                                    'color': [round(filtered_df[filtered_df.name == cnty]['poverty-rate'].dropna().median(), 1)],
                                    'colorscale': [[0, 'rgba(215, 227, 244, 0.7)'], [1, 'rgba(37, 51, 132, 0.9)']],
                                    'line':{'width': .2, 'color': el_purple}},
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

                                #used as a proxy for colorscale of purples; before I figured out how to use the rgba array.
                                #opacity = filtered_df[filtered_df.name == cnty]['poverty-rate'].dropna().mean()/30, #scaled over 30 since that is the max saturation value on eviction lab's own choropleth

                                #opacity = filtered_df[filtered_df.name == cnty]['pct-white'].dropna().mean()/100,
                                #cumulative = True,
                                #autobinx = False,
                                xbins = {'start': -1, 'end': 1, 'size' : .1}

            ))
    colorBarStandInTrace = {
        'x': [2],
        'name': 'color bar',
        'marker': {
            'cmax': 30,
            'cmin': 0,
            'color': [0, 5, 10, 15, 20, 25, 30, 35],
            #'color': el_purple,
            'colorscale': [[0, 'rgba(215, 227, 244, 0.7)'], [1, 'rgba(37, 51, 132, 0.9)']],
            'showscale': True,
            'colorbar': {'tickside': 'left', 'title': 'Poverty', 'titleside': 'top', 'outlinecolor': 'white', 'outlinewidth': 0, 'ticksuffix': '%', 'x': -.3},
        },
        'type': 'histogram',
        'uid': '2b3561',
        'xbins': {'start': -1, 'end': 1, 'size' : .1}
    }
    traces.append(colorBarStandInTrace)
    return { # can only return first positional output
        'data': traces,
        'layout': go.Layout(#title = 'Checked Years {}'.format(checked_year_values),
            #title= 'Histogram of County Correlation Coefficients for Selected Years',
            xaxis = {'title': 'Coefficient', 'range': [-1, 1]},
            #yaxis = {'title': 'Count'},
            hovermode = 'closest',
            paper_bgcolor = '#F4F4F8',
            plot_bgcolor = '#F4F4F8',
            legend = {#'x': -.1, 'y': 1.3,
                'orientation': 'v', 'xanchor': 'left'},
            #cumulative = True,
            height = 175,
            #width = 600,
            margin = {'t': 18,
                #'r': 180, 'l': 180,
                'b': 28},
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
    #if selected_county != None:
    if selected_county:
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
        'layout': go.Layout(#title = '95% Confidence Interval for Corr. Coeff: {}'.format(np.percentile(xbn, [2.5, 97.5]).round(2)),
                        title = '{}'.format(np.percentile(bs_replicates, [2.5, 97.5]).round(2)),
                        titlefont = {'size': 15, 'color': el_orange},
                        height = 90,
                        #width = 710,
                        margin = {'t': 24, 'b': 18,
                        #'l': 140, 'r': 50
                        'r': 120, 'l': 130,
                        },
                        #yaxis = {'title': 'Count'},
                        xaxis = {#'title': 'Correlation Coeff.',
                            'range': [-1.1, 1.1]},
                        hovermode = 'closest',
                        paper_bgcolor = '#F4F4F8',
                        plot_bgcolor = '#F4F4F8',
                        legend = {'x': -.1, 'y': 1.3, 'orientation': 'h'},
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
                            'opacity': .1,
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
