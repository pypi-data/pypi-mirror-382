
<em>SPIce</em> is a modular-based Python package for performing shallow diving-wave analysis of node-type data from hammer seismics. <em>SPIce</em> was developed to study the firn and shallow ice structures in ice sheets and permafrost. Every step in the seismic refraction workflow is included, beginning with
data handling and processing, first break picking of diving waves, travel-time curve fitting and seismic velocity analysis, and various plot operations. Data visualisation provides an interactive graphical platform for users if they wish to manually pick and export first breaks while viewing the detailed shape of waveforms.

<em>SPIce</em> Class Modules:
<ul>
    <li><em>spice</em> is the main class for performing data extraction, handling and processing whilst calling upon the other embedded classes. </li>
    <li><em>inversion</em> is the class that employs the analytic Herglotz-Wiechert inversion (HWI) algorithm to calculate the 1-D depth-velocity and depth-density profiles from the diving waves </li>
    <li><em>spicey_plotter</em> is the class that contains our interactive platform for data visualisation.</li>    
    <li><em>pykonal_plotter</em> is an optional class for users who would like to visualise the travel-time field using seismic
    ray tracing algorithms from <em>PyKonal</em> (White et al., 2022).</li>
</ul>

Include text file with list of files needed to run SPIce.
<ul>
    <li>Path to seismic waveform data</li>
    <li>Path to seismic node metadata with locations</li>
    <li>Path to hammer shot metadata containing any information about hammer shot times and number of strikes</li>
    <li>Option to include path to tilt angles of seismic nodes</li>
</ul>

The following section provides information on how to call the main method, trace_lineup_plot.

    trace_lineup_plot(stream, outfile=None, stackedchannel=None, newchannel=None,
                            scale_factor=1.0, input_points=None, input_csv=None, traveltime_df=None):

        stream - Obspy stream of traces
        outfile - filename to save CSV clicked points and seismic wiggle figure
        stackedchannel - name of channel of stacked traces (e.g. 'GPZS')
        channel - name of channel to display in black (e.g. 'GPZ')
        scale_factor - scaling factor for traces to fit in trace lineup plot
        input_points - tuples list of (distance_km, travel_time_s) or (distance_km, offset_m, travel_time_s, station)
        input_csv - path to load CSV file with seismic-derived traveltime points with column format, (distance_km, travel_time_s) or (distance_km, offset_m, travel_time_s, station)
        traveltime_df - pandas dataframe of seismic-derived traveltimes to input_points or input_csv

Example run:

```
from seismic_wiggle_plotter import SeismicWigglePlotter

plotter = SeismicWigglePlotter()
outfile = '/figures/stacked-tracelineup-plot-channelGPZ.png'

""" Tuples column format (distance_km, offset_m, travel_time_s, station)
where each row represents a station or trace in ObsPy stream, stacked_traces """
points_list = [[0.0, 0.0, 0.081, 0],
 [0.009, 9.0, 0.091, 1],
 [0.02, 20.0, 0.099, 2],
 [0.025, 25.0, 0.101, 3],
 [0.04, 40.0, 0.106, 4],
 [0.05, 50.0, 0.11, 5]]

""" Initialise traveltime dataframe with required columns """
traveltime_df = pd.DataFrame(columns=['xmodel (m)', 'ttmodel (ms)'])

points_df = plotter.trace_lineup_plot(
    stacked_traces,
    outfile=outfile,
    stackedchannel='GPZ',
    channel=None,
    scale_factor=1.0,
    input_points=points_list,
    input_csv=None,
    traveltime_df=traveltime_df
)
```
