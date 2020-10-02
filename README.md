# c19_plotting

Module for plotting various covid19 data using data from IHME, to be run from command line.

Commands:
-d: Plots C19 daily death statistics along with mobility data.
-hosp: Plots C19 cases and hospitalization data along with deaths as proportion of population.
-t: Plots C19 cummulative death statistics along with mobility data.
-l <jurisdiction>: Choose specific juristiction to plot (default is global).
-p: Includes future projections in plots.
-log: Changes y-axis to log scale.

Data source: 
https://ihmecovid19storage.blob.core.windows.net/latest/ihme-covid19.zip

File name:
Reference_hospitalization_all_locs.csv
