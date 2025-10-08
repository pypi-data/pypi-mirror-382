#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 19 16:45:53 2025

@author: shylakupis
"""

from obspy.signal.detrend import polynomial
from obspy import read, Stream, UTCDateTime 
from obspy.signal.filter import lowpass, highpass, bandpass 
from obspy.signal.trigger import classic_sta_lta
                                   
from scipy.signal import find_peaks, correlate, find_peaks, correlation_lags

import pandas as pd
import os
import re
import glob
import numpy as np
import pickle

from pathlib import Path

from .inversion import inversion
from .spicey_plotter import spicey_plotter
# import pykonal_plotter
import matplotlib.pyplot as plt
import pyproj 
# import geopy
# import geopy.distance # uses Vincenty distance, for some reason need to call geopy.distance seperately to find geopy.distance 


class spice:
    """
    A comprehensive class for processing seismic data including shot extraction,
    filtering, rotation, peak detection, and various utility functions.
    """
    
    def __init__(self):
        """Initialize the SeismicDataProcessor class."""
        pass
    

    def append_to_multiindex(self, index, new_tuple):
        """
        Function to append a new tuple to the MultiIndex. Do not use lists
        
        Parameters:
        -----------
        index : pandas MultiIndex 
            MultiIndex for pandas DataFrame
        new_tuple : tuple
            Tuple to create multi-indexed column for pandas DataFrame
            
        Returns:
        -----------
        pandas MultiIndex 
            New MultiIndex as tuple using the updated list
        """  
        
        # List to tuples and then you can append to list 
        tuples_list = list(index)
        tuples_list.append(new_tuple)
        
        # Recreating a new MultiIndex as tuple using the updated list
        return pd.MultiIndex.from_tuples(sorted(tuples_list))                 

    def find_nearest_station(self, lat, lon, target_lat, target_lon):
        """
        Find which station is closest to the target lat/lon coordinate pair using 
        the Euclidean distance. This simple approximation works well for small
        regions. For more accuracy across the globe, you should use the great 
        circle distance.
        """
        
        # Find the index of the minimum distance
        distances = np.sqrt((lat - target_lat)**2 + (lon - target_lon)**2)
        min_idx = np.unravel_index(distances.argmin(), distances.shape)
        
        return min_idx
        
    def RotateStream(self, stream, tilted_angle=None):  
        """
        Pre-process seismic data. Correct for sensor tilt. Option to apply 
        high- or low- pass frequency filters. Combine 3C channels into new 
        seismic waveform. 
        
        Parameters:
        -----------
        stream : ObsPy stream 
            Collection of seismic trace(s)
        tilted_angle : float, optional
            Correct seismic waveform for sensor tilt if angle is provided
        
        Returns:
        -----------
        stream : ObsPy stream 
            Updated collection of processed seismic trace(s) with new channel
        """
    
        # Extract data from each channel and apply bandpass filter 
        freqmin = 1
        freqmax = 300

        for tr in stream:
            # Bandpass filter 
            sampling_rate = tr.stats.sampling_rate
            min(sampling_rate / 2, freqmax)
            tr.data = bandpass(tr, freqmin, freqmax, tr.stats.sampling_rate)

        # # Need to change if N, E are not inline and crossline, respectively
        # ztr = stream.select(channel='GPZ')[0].data
        # inlinetr = stream.select(channel='GPN')[0].data
        # crosslinetr = stream.select(channel='GPE')[0].data
        
        # if tilted_angle is not None:
        #     # Rotate channels to correct for sensor tilt (clockwise rotation)
        #     tilted_angle = np.deg2rad(tilted_angle)
        #     L = (np.cos(tilted_angle)*ztr) + (np.sin(tilted_angle)*inlinetr)
        #     T = -(np.sin(tilted_angle)*ztr) + (np.cos(tilted_angle)*inlinetr)
              
        #     # Update each channel
        #     stream.select(channel='GPZ')[0].data = L
        #     stream.select(channel='GPN')[0].data = T
                       
        # # Rotate traces
        # tr = stream[0].copy()

        # M3d = np.array([[np.cos(inc), -np.sin(inc) * np.sin(ba), -np.sin(inc) * np.cos(ba)], 
        #                 [np.sin(inc), np.cos(inc) * np.sin(ba), np.cos(inc) * np.cos(ba)],
        #                 [0, -np.cos(ba), np.sin(ba)]])
        # L = M3d[0, :] * np.array([[ztr], [inlinetr], [crosslinetr]]) 
        # Q = M3d[1, :] * np.array([[ztr], [inlinetr], [crosslinetr]]) 
        # T = M3d[2, :] * np.array([[ztr], [inlinetr], [crosslinetr]]) 
            
        # # Align in p-wave propagation
        # tr.stats.channel = 'GPL'
        # tr.data = L
        # stream.append(tr)

        # # Align in SV-phase propagation        
        # tr.stats.channel = 'GPQ'
        # tr.data = Q
        # stream.append(tr)
        
        # # Align in SH-phase propagation        
        # tr.stats.channel = 'GPT'
        # tr.data = T
        # stream.append(tr)
    
        # Copy metadata from one of the channels
        new_stream = stream.copy()
        new_trace = stream[0].copy()  
        
        # Create new channel as combination of other channels
        if len(self.channels) > 1:
            channel = "GP"+"".join([c[2].upper() for c in self.channels])
            new_trace.stats.channel = channel
    
            result = 0 
            for tr in new_stream:
                if tr.stats.channel in self.channels:
                    # Normalise each component by its RMS before adding, i.e., average power of signal
                    result += tr.data / np.sqrt(np.mean(tr.data**2)) 
                        
            # Perform the calculation
            new_trace.data = result 
            
            # Append new channel to stream
            stream.append(new_trace)
            
        # Updated stream with new channel
        return stream 

    def create_ricker_wavelet(self, wavelet_length, fm=60):
        """
        Generate amplitude of Ricker wavelet with peak frequency parameter, fm
        
        Parameters:
        -----------
        wavelet_length : int
            Length of wavelet in samples
        fm : float
            Dominant frequency of hammer strike in Hz
        """
        # Time axis centered at zero
        t = (np.arange(wavelet_length) - wavelet_length // 2) / self.sampling_rate
        
        # Ricker wavelet formula
        wavelet = (1 - 2 * (np.pi * fm * t) ** 2) * np.exp(-(np.pi * fm * t) ** 2)
        
        return wavelet
    
    def DetectPeaks(self, signal, fm, numstrikes=None, hammer_duration=1000.0):
        """
        Detect first refracted P-wave arrivals from hammer strikes
        
        Parameters:
        -----------
        signal : NumPy array
            Seismic waveform data from source ObsPy stream
        fm : float
            Dominant frequency of hammer strike in Hz            
        numstrikes : NumPy array
            Number of hammer strikes to detect
        dt : float, default
            Sampling rate 
        hammer_duration : float, default
            Number of milliseconds hammer strike lasts
        
        Returns:
        -----------
        hammer_strikes : NumPy array
            Updated collection of processed seismic trace(s) with new channel
        """       

        # Normalize the signal
        signal_normalized = signal / np.max(np.abs(signal)) if np.max(np.abs(signal)) > 0 else signal
        
        # Find peaks with minimum distance between them
        min_distance = int(self.sampling_rate * hammer_duration / 1000)  # Convert hammer_duration to samples

        if self.template_wavelet is None:
            # Calculate wavelet length based on frequency and sampling rate
            wavelet_length = int(4 * (self.sampling_rate / fm[1]))  # 4 cycles for good resolution
            if wavelet_length % 2 == 0:  # Ensure odd length for symmetry
                wavelet_length += 1
            
            # Create Ricker wavelet template
            ricker_wavelet = self.create_ricker_wavelet(wavelet_length, fm=fm[1])
            
            # Normalize the wavelet
            self.template_wavelet = ricker_wavelet / np.max(np.abs(ricker_wavelet))

        # correlation_df = pd.DataFrame(columns=['coeff', 'lag'])
        # length = int(len(self.template_wavelet))
        # for i in range(0, len(signal_normalized) - length, int(min_distance / 2)):
        #     data = signal_normalized[i: i + min_distance]
        #     c = correlate(data, self.template_wavelet, mode="same")
        #     lags = correlation_lags(data.size, length, mode="same")
        #     correlation_df.loc[i, 'coeff'] = np.max(c)
        #     correlation_df.loc[i, 'lag'] = lags[np.argmax(c)]    
            
            
        # # First, remove any high energy events unrelated to hammer strikes
        # template_energy = np.sum(self.template_wavelet **2) / len(self.template_wavelet)
        
        # # Iterate through segments of min_distance length
        # for i in range(0, len(signal_normalized), int(self.sampling_rate * 20)):
        #     # Define segment boundaries
        #     segment_start = i
        #     segment_end = min(i + min_distance, len(signal_normalized))  # Don't exceed signal length
            
        #     # Extract segment 
        #     segment_data = signal_normalized[segment_start: segment_end]
        #     segment_energy = np.sum(segment_data ** 2) / len(segment_data)
            
        #     if segment_energy > 3 * template_energy:
        #         signal_normalized[segment_start: segment_end] = 0
                    
        # Perform cross-correlation
        correlation = correlate(signal_normalized, self.template_wavelet, mode='same')
        
        # Take absolute value for peak detection
        correlation_abs = np.abs(correlation)
                
        # Find correlation peaks
        hammer_strikes, properties = find_peaks(
            correlation_abs,
            height=0.4,
            distance=min_distance
        )  

        # hammer_strikes = []
        # length = len(self.template_wavelet)
        # for candidate in candidates:
        #     hammer_strikes.append(np.argmax(signal[candidate - int(length /2) : candidate + int(length /2)]))
            
        # If the number of hammer strikes has been recorded, then...
        if numstrikes is not None:
                        
            if len(hammer_strikes) > numstrikes:
                
                hammer_strikes = np.sort(hammer_strikes)[:numstrikes]
                # ind_diff = hammer_strikes[1:] - hammer_strikes[:-1]
                # # Only keep highest peaks in the list 
                # pd.DataFrame([hammer_strikes, properties['peak_heights']])                
                # ind = np.argsort(properties['peak_heights'])[::-1][:numstrikes]
                # hammer_strikes = hammer_strikes[ind]
                                
        return hammer_strikes


    def ExtractData(self):
        """
        Process and stack seismic traces from hammer refraction survey
        
        Parameters:
        -----------

        Returns:
        -----------
        self.seisdict : dict
            Dictionary containing ObsPy streams of raw seismic waveform data
            at every seismic station over duration of hammer refraction survey
        """    
                    
        # Survey start
        start_year = self.starttime.year
        start_month = self.starttime.month
        start_day = self.starttime.day
        start_period = UTCDateTime(start_year, start_month, start_day)

        # Survey end        
        end_year = self.endtime.year
        end_month = self.endtime.month
        end_day = self.endtime.day
        end_period = UTCDateTime(end_year, end_month, end_day)
        
        numdays = int((end_period - start_period) / 86400)
        
        # Date string        
        tstart = self.starttime.strftime('%Y-%m-%d_%H-%M')
        tend = self.endtime.strftime('%Y-%m-%d_%H-%M')

        # Create Regex string to find miniseed files corresponding to survey 
        if numdays > 0: # Multi-day survey
            dates = [start_period + 86400 * j for j in range(numdays+1)]
            pattern_list = [f'{date.year}.{date.month}.{date.day}' for date in dates]
        
        else: # Single-day survey
            pattern_list = [f'{start_year}.{start_month:02d}.{start_day:02d}']
        
        for receiver in self.snlist:
            # Initialise
            station_stream = Stream()    

            files = glob.glob(str(self.datapath / f"{receiver}/{receiver}*.miniseed"))
            subfiles = []
            
            # Create a regex pattern to pull files only from date of interest
            for file in files:
                match = [file for pattern in pattern_list if re.search(pattern, file)]
                if len(match) > 0:
                    subfiles.append(file)
           
            # Add raw seismic data to stream
            for f in subfiles:    
                st = read(f)
                
                # Trim traces around survey start and end time
                for tr in st:
                    station_stream.append(tr.trim(self.starttime, self.endtime))
                                           
            # Saving dictionary of traces for seisimc shots
            filename = str(self.outpath / f"{receiver}-raw-{tstart}-{tend}.pkl")
            with open(filename, 'wb') as f:
                pickle.dump(station_stream, f)  
                

    def Initialise(self, json_config):          
        """ 
        Load configuration json file and make sure you have necessary
        inputs to run SPIce
                       
        Parameters:
        -----------
        json_config : str
            Path to SPIce json configuration file. 
            Please refer to create-spice-json.py for an example run. 
            
        Returns:
        -----------
        
        """ 
        
        # Setup                
        self.geod = pyproj.Geod(ellps="WGS84")
        self.idx = pd.IndexSlice
                      
        # Check that necessary paths and inputs exist
        try:
            self.datapath = Path(json_config['DataPath'])
            self.datapath.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            print(f"Error with raw seismic data directory: {str(e)}")    
            
        try:
            self.outpath = Path(json_config['OutPath'])
            self.outpath.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            print(f"Error with output directory: {str(e)}")                  

        try:
            self.sitename = json_config['Sitename']
            
        except Exception as e:
            print(f"Error with site name: {str(e)}")    
            
        try:
            self.starttime = UTCDateTime(json_config['UTCStartTime'])
            self.endtime = UTCDateTime(json_config['UTCEndTime'])
            
        except Exception as e:
            print(f"Error with survey start and end times: {str(e)}")    

        if 'SourceNode' in json_config:
            self.source_node = json_config['SourceNode']            
        
        else: # Will default to extract raw seismic data from miniseed files 
            self.source_node = None 

        if 'ExtractData' in json_config:
            self.extract_data = json_config['ExtractData']            
        
        else: # Will default to extract raw seismic data from miniseed files 
            self.extract_data = True 
            
        if 'TiltFile' in json_config:            
            # Load tilted angles of seismic nodes
            TiltFile = json_config['TiltFile']
            
            if os.path.isfile(TiltFile):
                self.tiltdf = pd.read_csv(TiltFile, header=[0, 1], index_col=0)

            else:
                print("File containing tilted angles does not exist")
            
        else:
            print("No file specified with tilted angles. Will skip tilted angle correction.")   
            
        
        if 'TemplateWavelet' in json_config:
            TemplateWavelet = json_config['TemplateWavelet']
            df = pd.read_csv(TemplateWavelet, header=0)
            self.template_wavelet = df.values.flatten()
            
            # Normalize the wavelet
            self.template_wavelet /= np.max(np.abs(self.template_wavelet))
        
        else:
            self.template_wavelet = None
            
        
        if 'NoiseWavelet' in json_config:
            NoiseWavelet = json_config['NoiseWavelet']
            df = pd.read_csv(NoiseWavelet, header=0)
            self.noise_wavelet = df.values.flatten()
            
            # Normalize the wavelet
            self.noise_wavelet /= np.max(np.abs(self.noise_wavelet))
        
        else:
            self.noise_wavelet = None
            
        try:
            # Load metadata of hammer shot start and end times with source location 
            ShotsFile = json_config["ShotsFile"]
            self.shots_metadata = pd.read_csv(ShotsFile, header=0)
        
            # Load receiver metadata with locations at each source location
            ReceiverFile = json_config['ReceiverFile']
            df = pd.read_csv(ReceiverFile, header=0)
            
            self.snlist = np.unique(df['station_id'])
            cols = pd.MultiIndex.from_product([self.snlist, 
                                               ['latitude', 'longitude']])
            self.receivers = pd.DataFrame(index=self.shots_metadata.index,
                                          columns=cols, dtype=float)
            
            try:
                # Create receivers metadata dataframe using "closest" recorded time of waypoint
                for shot, shottime in zip(self.shots_metadata.index, self.shots_metadata['shot_starttime']):
                    
                    if self.source_node is not None:
                        # Update roamer geophone with source locations
                        lat, lon = self.shots_metadata.loc[shot, ['latitude', 'longitude']]
                        self.receivers.loc[shot, self.idx[int(self.source_node), 'latitude']] = lat
                        self.receivers.loc[shot, self.idx[int(self.source_node), 'longitude']] = lon        

                    for receiver in self.snlist:
                        receiver_metadata = df.where(df['station_id'] == receiver).dropna()
                        times = pd.to_datetime(receiver_metadata['time'])                    
                        shottime_dt = pd.to_datetime(shottime)
                        ix = shottime_dt >= times
                    
                        t = times[ix]
                        timediff = shottime_dt - t  
                        
                        if len(timediff) >= 1:
                            if len(timediff) > 1:
                                index = timediff.dt.total_seconds().idxmin()
                                
                            else:
                                index = timediff.index[0]
                                
                            lat, lon = df.loc[index, ['latitude', 'longitude']]
                            self.receivers.loc[shot, self.idx[int(receiver), 'latitude']] = lat
                            self.receivers.loc[shot, self.idx[int(receiver), 'longitude']] = lon
            
                # Save dataframe with receiver locations during each hammer shot location
                filename = self.outpath / f'{self.sitename}-receiver-locations.csv'       
                self.receivers.to_csv(filename, index=False)
        
            except Exception as e:
                print(f"Error creating dataframe of receiver locations: {str(e)}")
            
                            
        except Exception as e:
            print(f"Error with loading metadata: {str(e)}")

        if 'RayTracing' in json_config:
            self.ray_tracing = json_config['RayTracing']  
            
        else: # do not perform ray tracing unless specified
            self.ray_tracing = False    
            
            
    def SeismicDataProcess(self, json_config):
        """
        Process and stack seismic traces from hammer refraction survey
        
        Parameters:
        -----------
        json_config : str
            Path to SPIce json configuration file. 
            Please refer to create-spice-json.py for an example run. 
                    
        signal : NumPy array
            Seismic waveform data from source ObsPy stream
        numstrikes : NumPy array
            Number of hammer strikes to detect
        dt : float, default
            Sampling rate 
        hammer_duration : float, default
            Number of milliseconds hammer strike lasts
        
        Returns:
        -----------
        self.processed_seisdict : dict
            Dictionary containing ObsPy stream of processed and stacked seismic 
            trace(s) from each refraction test
        """      
        
        # Initialise
        self.Initialise(json_config)
        
        self.processed_seisdict = {} # for storage of processed streams 
        g = pyproj.Geod(ellps='WGS84') # define ellipsoid              
        cols = pd.MultiIndex.from_product([self.snlist, ['offset']])
        self.offsets = pd.DataFrame(index=self.shots_metadata.index, columns=cols, dtype=int)

        # Date string        
        tstart = self.starttime.strftime('%Y-%m-%d_%H-%M')
        tend = self.endtime.strftime('%Y-%m-%d_%H-%M')
                        
        if self.extract_data:
            self.ExtractData()    

        for i in self.shots_metadata.index[:29]:            
            # Source and receiver locations        
            ys, xs = self.shots_metadata.loc[i, ['latitude', 'longitude']]
            yr = self.receivers.loc[i, self.idx[:, 'latitude']].values
            xr = self.receivers.loc[i, self.idx[:, 'longitude']].values

            # Set station id as closest node 
            ind = self.find_nearest_station(yr, xr, ys, xs)[0]
            self.source_node = self.snlist[ind]       
            # self.shots_metadata.loc[i, 'station_id'] = self.source_node 

            self.source_node =  self.shots_metadata.loc[i, 'station_id']                        
                                        
            for receiver in self.snlist:
                
                # Calculate geodesic distance using EPSG 4326 between source and receiver(s)
                yr = self.receivers.loc[i, self.idx[receiver, 'latitude']]
                xr = self.receivers.loc[i, self.idx[receiver, 'longitude']]
                az_forward, az_backward, dist = g.inv(xs, ys, xr, yr) # forward azimuth, backward azimuth, geodesic distance             
                
                # For Shyla, include receivers with either positive or negative offsets 
                self.offsets.loc[i, self.idx[receiver, 'offset']] = int(dist)
                   
            # Number of hammer strikes for each test
            hammer_duration = 1000 # in ms 
            if 'hammer_strikes' in self.shots_metadata.columns:
                numstrikes = int(self.shots_metadata.loc[i, 'hammer_strikes'])
                maxtime = 2 * (numstrikes - 1) * numstrikes * (hammer_duration / 1000)
                
            else:
                numstrikes = np.nan
                maxtime = 180 
                
            stime = UTCDateTime(self.shots_metadata.loc[i, 'shot_starttime'])
            try:
                etime = min(UTCDateTime(self.shots_metadata.loc[i+1, 'shot_starttime']), 
                            stime + maxtime)
                
            except:
                etime = stime + maxtime
                               
            try:
                tilted_angle = self.tiltdf.loc[i, self.idx['tilted_angle', str(self.source_node)]]
                
            except:
                tilted_angle = None
            
            # Load stream closest to source location
            filename = str(self.outpath / f"{self.source_node}-raw-{tstart}-{tend}.pkl")
            with open(filename, 'rb') as f:
                station_stream = pickle.load(f)  
    
            # Pull the vertical channel
            self.sampling_rate = station_stream[0].stats.sampling_rate
            self.channels = np.unique([tr.stats.channel for tr in station_stream])            
            channel = [channel for channel in self.channels if re.search('Z', channel)][0]      
            
            stream = station_stream.merge(method=0, fill_value=0)
            stream = self.RotateStream(stream, tilted_angle=tilted_angle)
            zstream = stream.select(channel=channel)

            # Find peaks with minimum distance between them
            hammer_duration = 1000
            min_distance = int(self.sampling_rate * hammer_duration / 1000)  # Convert hammer_duration to samples
                                
            if self.noise_wavelet is None:
            
                # Normalize the signal
                data = zstream[0].data
                signal_normalized = data / np.max(np.abs(data)) if np.max(np.abs(data)) > 0 else data

                # Perform cross-correlation
                correlation = correlate(signal_normalized, self.noise_wavelet, mode='same')
                
                # Take absolute value for peak detection
                correlation_abs = np.abs(correlation)
                        
                # Find correlation peaks
                candidates, properties = find_peaks(
                    correlation_abs,
                    height=1,
                    distance=min_distance
                )     
            
                for candidate in candidates:
                    left_ind = candidate + int(len(self.noise_wavelet) / 2) - 2 * hammer_duration
                    right_ind = candidate + int(len(self.noise_wavelet) / 2) + 2 * hammer_duration
                
                    data[left_ind : right_ind] = 0
                
                # Update Z-channel with "noise-like" events removed
                zstream[0].data = data
                        
            # Trim traces closely to first arrival of hammer strikes within a minute
            zst = zstream.slice(stime, etime).merge(method=0, fill_value=0)
            # Using fill_mask value in case of 1e20 so USE this option            
            zst[0].data = np.ma.filled(zst[0].data, 0) 
       
            delta = zst[0].stats.delta    
            signal = zst[0].data
            
            # Detect hammer strikes from largest signal amplitude, signifying hammer strike
            hammer_duration = 1000 # duration of hammer strike in ms 
            fm = np.array([60, 120, 200]) # hammer strike dominant frequency range in Hz
            hammer_strikes = self.DetectPeaks(signal, 
                                              fm=fm,
                                              numstrikes=numstrikes,
                                              hammer_duration=hammer_duration)
            
            times2 = np.array([stime + j * delta for j in hammer_strikes])
        
            fig, ax = plt.subplots(constrained_layout=True, figsize=(12,8))  
            plt.scatter(hammer_strikes, signal[hammer_strikes], color='blue', marker='*')
            plt.plot(signal,color='black')
            outfile = self.outpath / f"source{i}-new-way-detected-hammer-strikes{numstrikes}-channel{channel}.png"
            plt.savefig(outfile, dpi=300, bbox_inches='tight')
            plt.close('all')
            # plt.show()
        
            # Process and stack traces at each receiver
            times2 = np.sort(times2)
                   
            for receiver in self.snlist:

                filename = str(self.outpath / f"{receiver}-raw-{tstart}-{tend}.pkl")
                with open(filename, 'rb') as f:
                    station_stream = pickle.load(f)  
                
                try:
                    # Correct for sensor tilt
                    tilted_angle = self.tiltdf.loc[i, self.idx[receiver, 'tilted_angle']]
                
                except:
                    tilted_angle = None
                                
                self.processed_seisdict[i, receiver] = Stream()
                stream = Stream()
                
                for j,t in enumerate(times2): 
                           
                    # Trim traces closely to first arrival of shot
                    st = station_stream.slice(t - 0.1, t + 0.5)
                    st = self.RotateStream(st, tilted_angle=tilted_angle)
                    st.merge(method=0, fill_value=0)
                    
                    # Using fill_mask value in case of 1e20 so USE this option
                    for tr in st:
                        tr.data = np.ma.filled(tr.data, 0)   
                                
                        # Add to stream 
                        stream.append(tr)
                        
                    # Stack traces 
                    for channel in self.channels:
                        tr = stream.select(channel=channel)
                        
                        if len(tr) > 1:
                            tr.stack(stack_type='linear')    
                        
                        # Append stacked trace to stream 
                        tr[0].stats.channel = channel
                        self.processed_seisdict[i, receiver].append(tr[0])

        return self.processed_seisdict

    def StackTraces(self):
        """
        Create a dictionary to store stacked traces with same offset
        
        Parameters:
        -----------
        
        Returns:
        -----------
        self.stacked_traces : dict
            Dictionary of ObsPy stream storing stacked traces
        """  
                
        self.stacked_stream = Stream()  
        self.unique_offsets = np.unique(self.offsets.loc[:, self.idx[:, 'offset']].dropna().values)
        
        for station, offset in enumerate(self.unique_offsets):
            
            stream = Stream()  
            for receiver in self.snlist:
                
                indices = self.offsets.loc[:, self.idx[receiver, 'offset']]==offset
                for r, ind in zip(indices, indices.index):
                    if r == True:
                        # Station with designated offset and shot 
                        st = self.processed_seisdict[ind, receiver].copy()
                        
                        for tr in st:
                            stream.append(tr)

            # Stack traces 
            for channel in self.channels:
                tr = stream.select(channel=channel)
                
                if len(tr) > 1:
                    tr.stack(stack_type='linear')    
                                
                # Append stacked trace to stream with same offset
                tr[0].stats.channel = channel
                tr[0].stats.offset = offset
                self.stacked_stream.append(tr[0])
                       

    def FirstBreakPicker(self, json_config):  
        
        """ 
        Run the seismic diving wave refraction worfklow
                       
        Parameters:
        -----------
        json_config : str
            Path to SPIce json configuration file. 
            Please refer to create-spice-json.py for an example run. 
            
        Returns:
        -----------
        self.offsets : pandas DataFrame
            pandas DataFrame of source-receiver offsets 
        outputs : pandas DataFrame
            Herglotz-Wiechert outputs, including fitted traveltime and velocity
            depth profile
        points_df : pandas DataFrame
            If exists, clicked arrival times from spicey_plotter class
        """  
        
        # Load pickle file storing seismic traces
        filename = self.inpath + f"{self.sitename}-traces.pkl"
        if os.path.isfile(filename):
            # Loading dictionary of traces for seisimc shots
            with open(filename,'rb') as f:
                self.seisdict = pickle.load(f)

        # Process and stack seismic traces from hammer refraction survey 
        self.SeismicDataProcess()
        
        # Stack traces with same source-receiver offset spacing 
        self.StackTraces()
                
        self.start_triggers = pd.DataFrame()
        
        # Use the vertical channel
        channel = [channel for channel in self.channels if re.search('Z', channel)][0]      
        zst = self.stacked_stream.select(channel=channel).copy()
        starttime = min([tr.stats.starttime for tr in zst])
        
        offsets = []
        for station, tr in enumerate(zst):
            # Run STA/LTA trigger plot
            offset = tr.stats.offset
            offsets.append(offset)
            
            # Detrend seismic waveform 
            tr.data = polynomial(tr.data, order=3, plot=False)
            
            if station == 0:
                tstart = starttime
                tend = tr.stats.endtime
                
            tr.trim(tstart, tend)
            times = np.array([tr.stats.starttime + j * tr.stats.delta for j in np.arange(0, tr.stats.npts)])
            
            # Simple method works better than STA/LTA for p-wave arrival picker
            ampdiff = np.abs(np.diff(tr.data, 10))
            indx = np.argwhere(ampdiff > 0.15 * np.max(np.abs(tr.data)))
            start_trigger = indx[0][0]
            
            # Pick arrival time and then trim waveform at next station as arrival can only be later 
            arrival_time = times[start_trigger]
            tstart = arrival_time
        
            plt.figure()
            plt.title(f'Station {station} at Offset {offset} m')
            plt.plot(times, tr.data, color='black')
            plt.plot(arrival_time, tr.data[start_trigger], '*r')
            plt.show()
                
            # Order of columns should be distance_km, offset_m, travel_time_s, station
            travel_time = arrival_time - starttime
            point_list = [offset/1000, offset, travel_time, station]   
            self.start_triggers.loc[station+1, ['Distance (km)','Offset (m)','Travel time (s)','Station']] = point_list

        # Reshape into a proper DataFrame with columns
        ttdf = self.start_triggers.loc[:, ['Offset (m)','Travel time (s)']].copy()
        ttdf = pd.DataFrame({
            'x': ttdf['Offset (m)'].values,
            't': ttdf['Travel time (s)'].values
        })
        ttdf = ttdf.sort_values(by='x').reset_index(drop=True)
        df = ttdf.loc[1:,['x','t']].copy()
        df['t'] -= ttdf.loc[0,'t'] # subtracting arrival time to source
        df = df.dropna()
        df['t'] *= 1000 # convert to ms
        df = df.sort_values("x").reset_index(drop=True)
        fpath = self.outpath / f"{self.sitename}-hwi-refraction"
        
        # Execute Herglotz-Wiechert inversion for seismic velocity-depth model         
        outputs = inversion.DivingWaveAnalysis(df, Vice=3800/1000, 
                                               plot_results=True, fpath=fpath) 
        
        outputs['ttmodel (ms)'] += ttdf.loc[0,'t']*1000
        
        outfile = self.outpath / f"{self.sitename}-tracelineup-{self.channel}"
        plotter = spicey_plotter()
        points_df = plotter.SeismicWigglePlotter(
                    self.stacked_stream, 
                    outfile=outfile, 
                    stackedchannel=self.channel,  # Use actual channel name as string
                    channel=None,      
                    scale_factor=0.75, 
                    input_points=self.points_list, 
                    input_csv=None, 
                    traveltime_df=outputs
        ) 
   
        """ 
        Calculate shortest ray paths in the travel-time field using PyKonal
        """
        
        # Source/receiver geometry 
        rxs = self.unique_offsets # Receiver offsets
        sxs = np.array([0.]) # Source location
        
        # Minimum and maximum P-wave velocity (m/s) limits for ice 
        vmin = 300 
        vmax = 4000
        
        # Number of x,y grid points in Cartesian coordinate system
        nx = int(outputs['Offset (m)'].max())
        ny = int(outputs['z (m)'].max())
        
        outfile = self.outpath / f"{self.sitename}-velocity-depth"
        
        # Plot true velocity-depth on geometry
        vtrue = pd.DataFrame(columns=['z', 'v'],dtype=float)
        vtrue['v'] = outputs['v (m/ms)'].dropna() * 1000
        vtrue['z'] = outputs['z (m)'].dropna()
        
        # # Instantiate PyKonal plotter class
        # pyplotter = pykonal_plotter()
        # _ = pyplotter.ShortestRayPath(
        #     vs=vtrue,
        #     rxs=rxs, 
        #     sxs=sxs,
        #     nx=nx,
        #     ny=ny,
        #     vmin=vmin, 
        #     vmax=vmax, 
        #     fpath=outfile
        # )   
                    
        return self.offsets, outputs, points_df                

# This block only runs when you execute the file directly
if __name__ == "__main__":
    import matplotlib
    import json
    matplotlib.use('Qt5Agg')

    sitename = "loken-moraine"
    outpath = Path(f"/Volumes/ExternalStorage/DTC_ALL/{sitename}-seismic/")

    # Save config to file
    filename = outpath / f"{sitename}-spice-config.json"  

    # Load config and run a demo
    with open(filename, 'r') as f:
        config = json.load(f)
    
    processor = spice()
    processor.FirstBreakPicker(config)