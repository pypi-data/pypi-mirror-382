#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import obspy
from obspy import Stream
idx = pd.IndexSlice
from matplotlib.transforms import blended_transform_factory
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import csv
import os
from pathlib import Path
from numpy.polynomial import Polynomial

class spicey_plotter:
    """
    This class provides interactive data visualisation and manual first arrival  
    picking of refracted arrivals 
    
    Interactive Workflow:
    ---------------------
    1. Allow user to manually pick first break of refracted arrivals
    2. Support point selection, deletion, and modification
    3. Enable polynomial or seismic-derived curve fitting of refracted arrivals
    4. Display seismic traces in vertical or horizontal section format
    5. Overlay seismic-derived travel time curves
    6. Automatically save travel time outputs and figures for further analysis

    Data Visualisation Features:
    -----------------------
    1. Dual-channel display (individual and/or stacked traces)
    2. Source/receiver identification
    3. Interactive point picking
    4. Real-time polynomial fitting
    5. Seismic-derived curve overlay
    """    
    
    def __init__(self):
        
        """
        Initialize the spicey_plotter class 
        """     
        self.clicked_points = []
        self.scatter_plot = None
        self.fig = None
        self.selected_point = None
        self.poly_line = None
        self.fitted_line = None
        self.zero_time_line = None
        self.has_poly_fit = False       # Flag to track if polynomial has been fitted
        self.has_hwi_fit = False        # Flag to track if polynomial has been fitted
        self.figure_closed = False      # Flag to ensure figure will close properly 

        # Add a DataFrame to store the points
        self.points_df = pd.DataFrame(columns=['Distance (km)', 'Offset (m)', 'Travel time (s)', 'Station'])


    def on_click(self, event):
        """
        Register click events on matplotlib figure for various plot operations
        and updates plot as needed
        
        Parameters:
        -----------
        event : matplotlib.backend_bases.MouseEvent
            Mouse event containing information about click
    
            Key attributes used:
            - event.inaxes : Axes object where the click occurred (None if outside axes)
            - event.xdata : X-coordinate of the click in data coordinates
            - event.ydata : Y-coordinate of the click in data coordinates  
            - event.button : Mouse button clicked (1=left, 2=middle, 3=right)
            - event.dblclick : Boolean indicating if this was a double-click
            - event.x : X-coordinate in pixel coordinates
            - event.y : Y-coordinate in pixel coordinates
        
        Mouse Actions:
        --------------
        - Left double-click: Add new point at clicked location
        - Left single-click: Select nearest existing point
        - Right-click: Remove nearest existing point            
            
        Returns:
        --------
                
        """        
        
        # Check if the event is in the axes
        if event.inaxes:
            
            x, y = event.xdata, event.ydata
            
            if event.button == 1 and event.dblclick:  # Left double-click -> add point to list
            
                if self.orientation == 'vertical':

                    # Iterate through specific stations and offsets to find the closest ones
                    find_closest_offset = lambda x: min(
                        [tr for j,tr in enumerate(self.stream)],
                    key=lambda tr: abs(tr.stats.distance / 1e3 - x)
                    ).stats.distance 
                    
                    find_closest_station = lambda x: min(
                        [tr for j,tr in enumerate(self.stream)],
                    key=lambda tr: abs(tr.stats.distance / 1e3 - x)
                    ).stats.station
                    
                    closest_offset = int(find_closest_offset(x)) # in m 
                    closest_station = find_closest_station(x)
                    
                    print(f"Added point at: Distance (km)={x}, Offset (m)={closest_offset}, Travel time (s)={y}, Station={closest_station}")
                    self.clicked_points.append((x, closest_offset, y, closest_station)) # will update later but for plotting purposes use x

                    # Add point to DataFrame
                    new_row = pd.DataFrame({
                        'Distance (km)': [x],
                        'Offset (m)': [closest_offset],
                        'Travel time (s)': [y],
                        'Station': [closest_station]
                    })
                
                if self.orientation == 'horizontal':

                    # Iterate through specific stations and offsets to find the closest ones
                    find_closest_offset = lambda x: min(
                        [tr for j,tr in enumerate(self.stream)],
                    key=lambda tr: abs(tr.stats.distance / 1e3 - x)
                    ).stats.distance 
                    
                    find_closest_station = lambda x: min(
                        [tr for j,tr in enumerate(self.stream)],
                    key=lambda tr: abs(tr.stats.distance / 1e3 - x)
                    ).stats.station
                    
                    closest_offset = int(find_closest_offset(y)) # in m 
                    closest_station = find_closest_station(y)
                    
                    print(f"Added point at: Distance (km)={y}, Offset (m)={closest_offset}, Travel time (s)={x}, Station={closest_station}")
                    self.clicked_points.append((x, closest_offset, y, closest_station)) # will update later but for plotting purposes use x

                    # Add point to DataFrame
                    new_row = pd.DataFrame({
                        'Distance (km)': [y],
                        'Offset (m)': [closest_offset],
                        'Travel time (s)': [x],
                        'Station': [closest_station]
                    })
                    
                # Only concatenate if points_df is not empty or new_row is not empty
                if not self.points_df.empty or not new_row.empty:
                    self.points_df = pd.concat([self.points_df, new_row], ignore_index=True) 
                else:
                    self.points_df = new_row
                    
                self.selected_point = None
            
                # Update figure
                self.update_scatter_plot()

                # Update scatter plot and refit polynomial if it was previously fitted
                if self.has_poly_fit:
                    self.fit_polynomial()

                # Update scatter plot and refit traveltime curve if it was previously fitted
                if self.has_hwi_fit:
                    self.plot_traveltime_curve()
                    
            elif event.button == 1:  # Left single-click -> select point
                # Select the nearest point 
                if self.clicked_points:
                    nearest_index = min(range(len(self.clicked_points)), 
                                        key=lambda i: (self.clicked_points[i][0]-x)**2 + (self.clicked_points[i][2]-y)**2)
                    self.selected_point = nearest_index
                    print(f"Selected point: Distance (km)={self.clicked_points[nearest_index][0]}, Travel time (s)={self.clicked_points[nearest_index][2]}, Station={self.clicked_points[nearest_index][3]}")
            
                    # Update 
                    self.update_scatter_plot()

            elif event.button == 3:  # Right-click -> remove point from list
                # Remove the nearest point 
                if self.clicked_points:
                    nearest_index = min(range(len(self.clicked_points)), 
                                        key=lambda i: (self.clicked_points[i][0]-x)**2 + (self.clicked_points[i][2]-y)**2)
                    removed_point = self.clicked_points.pop(nearest_index)
                    print(f"Removed point: Distance (km)={removed_point[0]}, Offset (m)={removed_point[1]}, Travel time (s)={removed_point[2]}, Station={removed_point[3]}")
                    
                    # Also remove from DataFrame
                    self.points_df = self.points_df.drop(nearest_index).reset_index(drop=True)
                    self.selected_point = None
                    
                    # Update scatter plot
                    self.update_scatter_plot()
                    
                    # Update scatter plot and refit polynomial if it was previously fitted
                    if self.has_poly_fit:
                        self.fit_polynomial()

                    # Update scatter plot and refit polynomial if it was previously fitted
                    if self.has_hwi_fit:
                        self.plot_traveltime_curve()      
                        
           
    def on_key(self, event):
        """
        Handle keyboard events on the matplotlib figure for various plot operations
        and updates plot as needed
        
        Parameters:
        -----------
        event : matplotlib.backend_bases.KeyEvent
            Keyboard event object containing information about the key press.
            Key attributes used:
            - event.key : String representation of the key pressed
            - event.inaxes : Axes object where the key event occurred (None if outside axes)
            - event.canvas : The canvas where the event occurred
            - event.x, event.y : Pixel coordinates of mouse when key was pressed
            
        Keyboard Commands:
        ------------------
        - 'delete' : Remove currently selected point
        - 'f'      : Fit polynomial to clicked points
        - 'p'      : Plot seismic-derived travel time curve (requires traveltime_df)
        - 'r'      : Rescale main axis to fit current data
        - 'space'  : Close the figure
        
        Returns:
        --------
        
        """  
            
        # Delete points 
        if event.key == 'delete' and self.selected_point is not None:
            removed_point = self.clicked_points.pop(self.selected_point)
            print(f"Removed point: Distance (km)={removed_point[0]}, Offset (m)={removed_point[1]}, Travel time (s)={removed_point[2]}, Station={removed_point[3]}")
            
            # Also remove from DataFrame
            self.points_df = self.points_df.drop(self.selected_point).reset_index(drop=True)
            self.selected_point = None          
            self.update_scatter_plot()

            # Refit polynomial if it was previously fitted
            if self.has_poly_fit:
                self.fit_polynomial()
                
            if self.has_hwi_fit:
                # Check if traveltime_df exists before calling
                if hasattr(self, 'traveltime_df') and self.traveltime_df is not None:
                    self.plot_traveltime_curve()
                else:
                    print("No traveltime DataFrame available. Please provide one first.")
                         
        # Fit polynomial when 'f' is pressed
        elif event.key == 'f':
            self.fit_polynomial()
            self.has_poly_fit = False  # Prevent automatic refitting

            
        # Plot fitted curve when 'p' is pressed
        elif event.key == 'p':
            # Check if traveltime_df exists before calling
            if hasattr(self, 'traveltime_df') and self.traveltime_df is not None:
                self.plot_traveltime_curve()
            else:
                print("No traveltime DataFrame available. Please provide one first.")
                
        # Add this condition to rescale axis
        elif event.key == 'r':  # rescale axis
            self.rescale_axis() 
                        
        # Close figure 
        elif event.key == ' ':
            print("Spacebar pressed - closing figure...")
            self.figure_closed = True
            self.on_close(event)
            plt.close(self.fig)            
        
    def on_close(self, event):
        """
        Handles figure closure event, either by clicking close button or pressing
        the spacebar, and then saves any traveltime results to PNG or CSV file
        if outfile is provided
    
        Parameters:
        -----------
        event : matplotlib.backend_bases.CloseEvent
            Figure close event object automatically provided by matplotlib
            
        Returns:
        --------
            
        """
        
        # Trigger event to save figure if space key is pressed
        if self.outfile != None:
            filename = self.outfile+".png"
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Figure saved as {filename}")
            
        # Write the clicked points to a CSV file when the figure is closed
        if self.outfile != None:
            with open(self.outfile+'.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Offset (m)', 'Travel time (s)', 'Station'])
                writer.writerows(self.clicked_points[1:])
            print(f"CSV file created with {len(self.clicked_points)} points.") 


    def load_points_from_csv(self, csv_file):
        """
        Load travel time points from CSV file to add on figure
        
        Parameters:
        -----------
        csv_file : str
            CSV filename 
            
        Returns:
        --------
        
        """
        
        if not os.path.exists(csv_file):
            print(f"CSV file {csv_file} not found.")
            return
        
        try:
            # Clear existing points before loading
            self.clicked_points = []
            self.points_df = pd.DataFrame(columns=['Distance (km)', 'Offset (m)', 'Travel time (s)', 'Station'])

            # Read the CSV file into DataFrame
            loaded_df = pd.read_csv(csv_file)
            
            # Check if the required columns exist
            required_cols = ['Distance (km)', 'Offset (m)', 'Travel time (s)', 'Station']
            if not all(col in loaded_df.columns for col in required_cols):
                print(f"CSV file missing required columns. Needed: {required_cols}")
                return
            
            # Convert DataFrame to list of tuples and add to clicked_points
            for _, row in loaded_df.iterrows():
                point = (
                    row['Distance (km)'], 
                    row['Offset (m)'], 
                    row['Travel time (s)'], 
                    row['Station']
                )
                self.clicked_points.append(point)
            
            # Update the points DataFrame
            if not self.points_df.empty or not loaded_df.empty:
                self.points_df = pd.concat([self.points_df, loaded_df], ignore_index=True)
            else:
                self.points_df = loaded_df
 
            print(f"Loaded {len(loaded_df)} points from {csv_file}")
            
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")


    def add_point(self, distance_km, travel_time_s, station=None, offset_m=None):
        """
        Manually add a travel time point to the plot
             
        Parameters:
        -----------
        distance_km : float
            Distance in kilometers
        travel_time_s : float
            Travel time in seconds
        station : str, optional
            Station name. If None, will find closest station
        offset_m : int, optional
            Offset in meters. If None, will calculate from distance      
            
        Returns:
        --------
        
        """
        
        # Only proceed if we have a stream loaded
        if not hasattr(self, 'stream') or self.stream is None:
            print("No seismic stream loaded. Load stream before adding points.")
            return
        
        # Find closest station and offset if not provided
        if station is None or offset_m is None:
            try:
                find_closest_offset = lambda x: min(
                    [tr for j,tr in enumerate(self.stream)],
                    key=lambda tr: abs(tr.stats.distance / 1e3 - x)
                ).stats.distance
                
                find_closest_station = lambda x: min(
                    [tr for j,tr in enumerate(self.stream)],
                    key=lambda tr: abs(tr.stats.distance / 1e3 - x)
                ).stats.station
                
                if offset_m is None:
                    offset_m = int(find_closest_offset(distance_km))
                
                if station is None:
                    station = find_closest_station(distance_km)
                                
            except Exception as e:
                print(f"Error finding station/offset: {str(e)}")
                if station is None:
                    station = "Unknown"
                if offset_m is None:
                    offset_m = int(distance_km * 1000)  # Approximate conversion
        
        # Add the point
        if self.orientation == 'vertical':
            self.clicked_points.append((distance_km, offset_m, travel_time_s, station))

        if self.orientation == 'horizontal':
            self.clicked_points.append((travel_time_s, offset_m, distance_km, station))
        
        new_row = pd.DataFrame({
            'Distance (km)': [distance_km],
            'Offset (m)': [offset_m],
            'Travel time (s)': [travel_time_s],
            'Station': [station]
        })
        
        # Only concatenate if points_df is not empty or new_row is not empty
        if not self.points_df.empty or not new_row.empty:
            self.points_df = pd.concat([self.points_df, new_row], ignore_index=True)
        else:
            # If both are empty, just use the new row
            self.points_df = new_row
        
        print(f"Added point at: Distance (km)={distance_km}, Offset (m)={offset_m}, Travel time (s)={travel_time_s}, Station={station}")

        # Update plot if it exists
        if hasattr(self, 'fig') and self.fig is not None and not self.figure_closed:
            self.update_scatter_plot()
            
            # Refit polynomial if it was previously fitted
            if self.has_poly_fit:
                self.fit_polynomial()


    def add_points_from_list(self, points_list):
        """
        Add multiple points from a list of (distance_km, travel_time_s) tuples
        
        Parameters:
        -----------
        points_list : List of tuples (distance_km, travel_time_s) or 
                           (distance_km, travel_time_s, station, offset_m)
                           
        Returns:
        -----------  
        
        """
        
        for point in points_list:
            if len(point) == 2:
                self.add_point(point[0], point[1])
            elif len(point) == 4:
                self.add_point(point[0], point[2], point[3], point[1])
            else:
                print(f"Invalid point format: {point}. Expected (distance_km, travel_time_s) or (distance_km, offset_m, travel_time_s, station)")
    
            

    def fit_polynomial(self):
        """
        Fit a 3rd order polynomial to the user-clicked points and display the curve

        Parameters:
        -------------
        None
        
        Requirements:
        -------------
        - Minimum 4 points needed (3rd order polynomial has 4 coefficients)
        - Points must have valid x,y coordinates
        - matplotlib figure must be available for plotting  
        
        Returns:
        --------

        """
        
        if len(self.clicked_points) < 4:
            print("Need at least 4 points to fit a 3rd order polynomial")
            return
            
        try:
            # Extract x and y coordinates from clicked points
            x_points, _, y_points, _ = zip(*self.clicked_points)
            
            # Convert to numpy arrays
            x = np.array(x_points)
            y = np.array(y_points)
            
            # Sort points by x-coordinate
            idx = np.argsort(x)
            x = x[idx]
            y = y[idx]
            
            # Fit 3rd order polynomial
            poly = Polynomial.fit(x, y, 3)
            coefs = poly.coef
            
            # Create a smooth curve for plotting
            x_smooth = np.linspace(min(x), max(x), 100)
            y_smooth = poly(x_smooth)
            
            # Plot the curve
            if hasattr(self, 'poly_line') and self.poly_line:
                self.poly_line.remove()
            
            self.poly_line = self.ax.plot(x_smooth, y_smooth, color='indianred', linewidth=2, zorder=4)[0]
            
            # Ensure display of polynomial fit as figure updates
            self.has_poly_fit = True
            
            # Add the polynomial coefficients to the class for later use
            self.poly_coefs = coefs

            # Check figure status and redraw figure
            if hasattr(self, 'fig') and self.fig is not None and not self.figure_closed:
                self.ax.figure.canvas.draw_idle()  # Non-blocking, safe
                
        except Exception as e:
            print(f"Error fitting polynomial: {str(e)}")
                        

    def plot_traveltime_curve(self):
        """
        Plot a fitted travel time curve on seismic trace lineup
        
        Parameters:
        ------------------
        None
        
        Data Requirements:
        ------------------
        - self.traveltime_df must exist and contain modeled travel time data
        - Required columns: 'xmodel (m)' for offset, 'ttmodel (s)' for travel time
        
        Returns:
        --------
 
        """
        
        # First check if traveltime_df is empty
        if self.traveltime_df is None:
            print("No traveltime dataframe provided.")
            return
                  
        try:
            # Check if required columns exist
            required_cols = ['xmodel (m)', 'ttmodel (s)']
            if not all(col in self.traveltime_df.columns for col in required_cols):
                print(f"Traveltime dataframe missing required columns. Needed: {required_cols}")
                available_cols = list(self.traveltime_df.columns)
                print(f"Available columns: {available_cols}")
                return
            
            # Check if we have any data to plot
            if len(self.traveltime_df) == 0:
                print("Traveltime dataframe is empty - no data to plot.")
                return   
            
            # Extract x and y coordinates from clicked points
            xmodel, ttmodel = self.traveltime_df['xmodel (m)'].dropna(), self.traveltime_df['ttmodel (s)'].dropna()

            # Save polynomial-fitted curve
            polyfit_df = pd.DataFrame({
                'Offset (m)': xmodel,
                'Travel time (s)': ttmodel
            })
            polyfit_df.to_csv(self.outfile + '-fitted-curve.csv', index=False)

            xmodel /= 1000 # m to km
            
            # Plot the curve
            if hasattr(self, 'fitted_line') and self.fitted_line:
                self.fitted_line.remove()
            
            if self.orientation == 'vertical':
                self.fitted_line = self.ax.plot(xmodel, ttmodel, color='goldenrod', linewidth=2, zorder=4)[0]
            
            elif self.orientation == 'horizontal':
                self.fitted_line = self.ax.plot(ttmodel, xmodel, color='goldenrod', linewidth=2, zorder=4)[0]
            
            # Ensure display of fitted curve as figure updates
            self.has_hwi_fit = True
            
            # Check figure status and redraw figure
            if hasattr(self, 'fig') and self.fig is not None and not self.figure_closed:
                self.ax.figure.canvas.draw_idle()  # Non-blocking, safe
                
        except Exception as e:
            print(f"Error displaying fitted curve: {str(e)}")
            
            
    def normalize_streams(self, stream1, stream2):
        """
        Normalize two streams to have the same amplitude scaling
        
        Parameters:
        -----------
        stream1 : obspy.Stream
            First seismic data stream to normalize
        stream2 : obspy.Stream  
            Second seismic data stream to normalize
            
        Returns:
        --------
        tuple : (obspy.Stream, obspy.Stream)
            Normalized copies of the input streams with same amplitude scaling
            
        """
        
        # Create copies to avoid modifying the original
        stream1_copy = stream1.copy()
        stream2_copy = stream2.copy()
        
        # Find the global maximum amplitude across both streams
        if stream1_copy:
            max_amp1 = max([max(abs(tr.data)) for tr in stream1_copy])
        else:
            max_amp1 = 0
            
        if stream2_copy:            
            max_amp2 = max([max(abs(tr.data)) for tr in stream2_copy]) 
        else: 
            max_amp2 = 0
                
        global_max = max(max_amp1, max_amp2)
        
        if global_max > 0:
            # Scale each trace to the global maximum
            for tr in stream1_copy:
                tr.data = tr.data / global_max
                
            for tr in stream2_copy:
                tr.data = tr.data / global_max
        
        return stream1_copy, stream2_copy


    def rescale_axis(self):
        """
        Rescale the y-axis for vertical orientation and x-axis for horizontal
        orientation to show travel times relative to zero offset, t0.
        It finds the estimated travel time at zero offset (t0) and adjusts
        the axis display to show times relative to this reference.
        
        Methods to estimate t0:
        ------------------------------------------------
        1. Polynomial extrapolation : Fit curve to picked points and evaluate at x=0 for t0
        2. Theoretical model : Use closest point from travel time dataframe
        3. Closest point : Use nearest picked point to zero offset
        
        Parameters:
        --------
        None 
        
        Returns:
        --------
        float or None
            Estimated time at zero offset, t0, in seconds, or None if failed
            to rescale travel time 
            
        """
    
        t0 = None

        if not hasattr(self, 'fig') or self.fig is None:
            print("No active figure to rescale.")
            return
        
        if not self.clicked_points and self.traveltime_df is None:
            print("No points to rescale. Add points first.")
            return        

        # Remove zero time line if it exists
        if hasattr(self, 'zero_time_line') and self.zero_time_line is not None:
            try:
                self.zero_time_line.remove()
                self.zero_time_text.remove()
                
                # Check figure status and redraw figure
                if hasattr(self, 'fig') and self.fig is not None and not self.figure_closed:
                    self.ax.figure.canvas.draw_idle()  # Non-blocking, safe
     
            except:
                pass 

            # self.zero_time_line = None
            # self.zero_time_text = None
                        
        # Find the point closest to zero offset or extrapolate to zero
        if self.traveltime_df is None:
            print(f"clicked_points: {len(self.clicked_points)}")
            
            if len(self.clicked_points) >= 3:
                # Fit polynomial to find intercept 
                try:
                    # Extract x and y coordinates from clicked points
                    x_points, offsets, y_points, _ = zip(*self.clicked_points)
                    print(f"offsets: {offsets}")
                    # Convert to numpy arrays
                    x = np.array(x_points)
                    y = np.array(y_points)
                    sx = np.array(offsets)
                    
                    # Sort points by x-coordinate
                    idx = np.argsort(sx)
                    sx = sx[idx]
                    x = x[idx]
                    y = y[idx]
                    
                    # If offset is under 1 m, then use traveltime as t0 
                    if sx[0] < 1:                                              
                        if self.orientation == 'vertical':
                            t0 = y[0]
                            
                        if self.orientation == 'horizontal':
                            t0 = x[0]
                        
                        print(f"Time at {sx[0]:.1f} m offset is {t0:.3f} s")
                    
                    else:
                        print("There is no receiver within 1 m of source location at 0 m offset")
                        
                except Exception as e:
                    print(f"Error finding traveltime near zero offset: {str(e)}")
                    
            else:
                print("There are not enough clicked points to accurately find traveltime near zero offset")

            
        else:
            try:
                # Check if required columns exist
                required_cols = ['xmodel (m)', 'ttmodel (s)']
                if not all(col in self.traveltime_df.columns for col in required_cols):
                    print(f"Traveltime dataframe missing required columns. Needed: {required_cols}")
                    available_cols = list(self.traveltime_df.columns)
                    print(f"Available columns: {available_cols}")
                    return

                else: 
                    # Extract x and y coordinates from dataframe
                    xmodel, ttmodel = self.traveltime_df['xmodel (m)'].dropna(), self.traveltime_df['ttmodel (s)'].dropna()
                    
                    # Check if we have any data to plot
                    if len(self.traveltime_df) == 0:
                        print("Traveltime dataframe is empty - no data to plot.")
                        return   
    
                    # Presumably traveltime curve begins at or near x=0m; otherwise, you can fit polynomial to extrapolate to 0 m
                    if len(self.traveltime_df) > 0:
                        closest_idx = np.argmin(xmodel)
                        t0 = ttmodel[closest_idx] 
                        print(f"Time at {xmodel[closest_idx]:.1f} m offset is {t0:.3f} s")
    
                    # else:
                    #     # Sort points by x-coordinate
                    #     idx = np.argsort(xmodel)
                    #     x = xmodel[idx].values.astype(float)
                    #     y = ttmodel[idx].values.astype(float)
                        
                    #     # Fit polynomial (3rd order or linear based on number of points)
                    #     degree = min(3, len(x) - 1)                    
                    #     poly = Polynomial.fit(x, y, degree)
    
                    #     # Find intercept (time at zero offset)
                    #     t0 = poly(0)
                    #     print(f"Estimated time at zero offset from polynomial: {t0:.3f} s")
                        
            except Exception as e:
                print(f"Error processing traveltime dataframe: {str(e)}")
                t0 = None             

        # Get current x- and y-axis limits and range
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()
                  
        print(f"zero_time_line {self.zero_time_line}")
        print(f"t0 is {t0}")
        
        if self.orientation == 'vertical':                              
            # Set new y-axis limits to center t0 at y=0 while maintaining the same range
            # Note: In seismic plots, time usually increases downward (y-axis is inverted)
            # so we need to be careful with the direction
            self.ax.yaxis_inverted()
            
            if t0 is not None:
                # Set new y-axis limits
                self.ax.set_yticks([y_min, t0, y_max])            
                self.ax.set_yticklabels([f"{y_min-t0:.3f}", 0, f"{y_max-t0:.3f}"])
                
                # Update the y-axis label to indicate the shift
                self.ax.set_ylabel(f"Scaled Time to {t0:.3f}s [s]")

                # Add a horizontal line at time t0 (representing time zero after scaling)
                self.zero_time_line = self.ax.axhline(t0, color='indianred', linestyle='--', linewidth=1.5, zorder=0)
                
                # Add a label for the zero time line
                self.zero_time_text = self.ax.text(
                    x_min, 
                    t0 - 0.01, 
                    " t = 0 s ", 
                    color='indianred', 
                    fontsize=18, 
                    va='center', 
                    ha='left',
                    backgroundcolor='none', 
                    alpha=1
                )
    
                # Check figure status and redraw figure
                if hasattr(self, 'fig') and self.fig is not None and not self.figure_closed:
                    self.ax.figure.canvas.draw_idle()  # Non-blocking, safe
            
                print(f"{self.orientation} axis display rescaled to show t0={t0:.3f}s")


            else:
                self.ax.set_yticks([y_min, 0, y_max])            
                self.ax.set_yticklabels([f"{y_min:.3f}", 0, f"{y_max:.3f}"])
                
        elif self.orientation == 'horizontal':                  
            # Set new x-axis limits to center t0 at x=0 while maintaining the same range
            self.ax.xaxis_inverted()

            if t0 is not None:            
                # Set new x-axis limits
                self.ax.set_xticks([x_min, t0, x_max])            
                self.ax.set_xticklabels([f"{x_min-t0:.3f}", 0, f"{x_max-t0:.3f}"])

                # Add a horizontal line at time t0 (representing time zero after scaling)
                self.zero_time_line = self.ax.axvline(t0, color='indianred', linestyle='--', linewidth=1.5, zorder=0)
                
                # Add a label for the zero time line - ROTATED for horizontal orientation
                self.zero_time_text = self.ax.text(
                    t0 - 0.01,                    # X position
                    y_min + 0.02,                 # Y position
                    " t = 0 s ",                  
                    color='indianred',            
                    fontsize=18,
                    rotation=90,                  # Rotate for horizontal orientation
                    va='center',                  # Vertical alignment: center
                    ha='center',                  # Horizontal alignment: center
                    backgroundcolor='none',       
                    alpha=1                       
                )
                
                # Check figure status and redraw figure
                if hasattr(self, 'fig') and self.fig is not None and not self.figure_closed:
                    self.ax.figure.canvas.draw_idle()  # Non-blocking, safe
                    
                print(f"X-axis display rescaled to show t0={t0:.3f}s at x=0")
            
                
            else:
                self.ax.set_xticks([x_min, 0, x_max])            
                self.ax.set_xticklabels([f"{x_min:.3f}", 0, f"{x_max:.3f}"])

            
        return t0 


    def update_scatter_plot(self):
        """
        Update the figure display of user-clicked points on the axes
        
        Parameters:
        -----------
        self.ax : matplotlib.axes.Axes
            Matplotlib figure axes object for plotting and refreshing figure with updates
        
        Requirements:
        -----------
        self.orientation : str
            Figure orientation to display seismic traces
        
        Returns:
        --------
            
        """      
        
        if self.scatter_plot:
            self.scatter_plot.remove()
        
        if self.clicked_points:
            x, _, y, _ = zip(*self.clicked_points)
            self.scatter_plot = self.ax.scatter(x, y, c='goldenrod', marker='*', s=200, zorder=5)
                
        else:
            self.scatter_plot = None
            
            # If there are no points, do not plot polynomial fit
            if hasattr(self, 'poly_line') and self.poly_line:
                self.poly_line.remove()
                self.poly_line = None
                self.has_poly_fit = False

            # If there is no traveltime dataframe, do not plot fitted traveltime curve
            if hasattr(self, 'fitted_line') and self.fitted_line:
                self.fitted_line.remove()
                self.fitted_line = None
                self.has_hwi_fit = False
                
        # Check figure status before updating
        if hasattr(self, 'fig') and self.fig is not None and not self.figure_closed:      
            self.ax.figure.canvas.draw_idle()

          
    def reset(self):
        """
        Reset the plotter state to its initial state, e.g., clearing arrival picks
        
        Parameters:
        --------
        None 
        
        Returns:
        --------
            
        """
        
        self.clicked_points = []
        self.scatter_plot = None
        self.selected_point = None
        self.points_df = pd.DataFrame(columns=['Distance (km)', 'Offset (m)', 'Travel time (s)', 'Station'])
        self.poly_line = None
        self.has_poly_fit = False
        self.fitted_line = None
        self.has_hwi_fit = False
        self.zero_time_line = None
        self.figure_closed = False
        
    def SeismicWigglePlotter(self, stream, outfile=None, scale_factor=1.0, orientation='vertical', input_points=None, traveltime_df=None):
        """
        Create an interactive seismic trace lineup plot for first break picking
        that supports both individual and stacked trace visualization
        
        Interactive Workflow:
        ---------------------
        1. Display seismic traces in vertical or horizontal section format
        2. Allow user to manually pick first break times 
        3. Support point selection, deletion, and modification
        4. Enable polynomial fitting to picked travel times
        5. Overlay seismic-derived travel time curves
        6. Save results for further analysis
        
        Visualization Features:
        -----------------------
        - Dual-channel display (individual and/or stacked traces)
        - Station markers and labels
        - Source/receiver identification
        - Interactive point picking
        - Real-time polynomial fitting
        - Seismic-derived curve overlay

        Outputs Generated:
        -----------------
        CSV Files:
            {self.outfile}.csv : Clicked points with columns
            - 'Distance (km)' : Source-receiver offset             
            - 'Offset (m)' : Source-receiver offsets
            - 'Travel time (s)' : Observed travel times  
            - 'Station' : Seismic node station ID
            
            {self.outfile + '-fitted-curve.csv'} : Polynomial fitted curve to
            observed travel-time data
            - 'Offset (m)' : Source-receiver offset 
            - 'Travel time (s)' : Polynomial fitted travel-time curve
                
        Plot Files (if plot_results=True):
            {self.outfile}.png : Trace lineup plot with seismic waveform data
        
        Parameters:
        -----------
        stream : obspy.Stream
            Seismic data containing traces to display
        outfile : str, optional
            Filename to save results (e.g., PNG figure and/or CSV data)
        scale_factor : float, default = 1.0
            Amplitude scaling factor for trace display
        orientation : str, default = 'vertical'
            Orientation to display seismic waveform traces
        input_points : list or str, optional
            Pre-existing first break points as tuples:
            [(distance_km, travel_time_s), ...] or
            [(distance_km, offset_m, travel_time_s, station), ...]
            OR ... 
            str, optional
            Path to CSV file containing pre-existing first break picks
        traveltime_df : pandas DataFrame, optional
            Seismic-derived travel time data for curve overlay
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame containing all picked points with columns:
            ['Distance (km)', 'Offset (m)', 'Travel time (s)', 'Station']
            
        """   
        
        # INITIALIZATION: Reset state and prepare for new analysis session
        # Clear any previous picks and analysis results to start fresh
        # This prevents contamination from previous datasets or sessions
        self.reset()
    
        # Close any existing matplotlib figures to prevent memory issues
        # Multiple open figures can cause performance problems and confusion
        plt.close('all')

        # Must save as instance variables to be called in on_click
        self.stream = stream 
        self.outfile = outfile
        self.orientation = orientation
        self.traveltime_df = traveltime_df
        
        # Separate stacked traces from individual traces 
        stacked_stream = Stream()
        base_stream = Stream()
        for tr in stream:
            if hasattr(tr.stats,'stacked'):
                stacked_stream.append(tr)  
            else:
                base_stream.append(tr)
                  
        # Get unique stations for labeling
        unique_stations = set()
        for tr in self.stream:
            if hasattr(tr.stats, 'station'):
                unique_stations.add(tr.stats.station)
        
        # If input_points is in list or tuple format 
        if isinstance(input_points, (list, tuple)):
            print(f"Detected list/tuple format with {len(input_points)} entries")
            self.add_points_from_list(input_points)

            # Validate that it's not an empty list
            if len(input_points) == 0:
                print("Input list is empty - no points to load")
                return
            
        # If input_points is string or path format (CSV file path)  
        elif isinstance(input_points, (str, Path)):
            print(f"Detected file path format: {input_points}")
            csv_path = str(input_points)
            
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV file not found: {csv_path}")
                
            # Validate file extension (optional warning)
            if not csv_path.lower().endswith(('.csv', '.txt')):
                print(f"Warning: File doesn't have correct extension: {csv_path}")
            
            try:
                # Load using existing CSV method
                self.load_points_from_csv(csv_path)
                print(f"Successfully loaded {len(self.clicked_points)} points from CSV")
                
            except Exception as e:
                print(f"Error loading from CSV: {e}")
                raise
    
        elif input_points is None:
            print("No input points provided")
            
        # Invalid input data type
        else:
            raise TypeError(f"Invalid input_points type: {type(input_points)}")
        
                
        # # If input_points is a pandas DataFrame format
        # if self.traveltime_df.empty:
        #     print("Input DataFrame is empty - no points to load")
        #     return          
            
        ### Setup figure to plot ###
        self.fig = plt.figure(figsize=(35,10))   
        
        plot_args = {
            'type': 'section',
            'method': 'full',
            'show': False,
            'orientation': orientation,
            'offset_min': -0.025,
            'minplot_dx': 10,
            'fig': self.fig,
            'scale': scale_factor  
        }
        
        # If we have both channels specified, plot them in different colors
        if stacked_stream and base_stream:  
            print("Both stacked and individual traces are available to display")

            ### TURN ON if you would like to have amplitude rescaling ###
            # Normalize both streams to the same scale
            # normalized_base, normalized_stacked = self.normalize_streams(base_stream, stacked_stream)
            
            ### Suggestion: consider rescaling stacked stream if it has been stacked by adding traces ###                
            # Count how many traces are within each station
            for station in unique_stations:
                numtr = len(base_stream.select(station=station))
                tr = stacked_stream.select(station=station)
                tr.data /= numtr

            # Create the plot frame with section method 
            base_stream.plot(**plot_args, linewidth=2, color='black')                                            
            stacked_stream.plot(**plot_args, linewidth=4, color='indianred')
             
            self.ax = self.fig.axes[0]
            self.ax.set_autoscale_on(False)

            legend_elements = [
                Line2D([0], [0], color='black', lw=4, label='Individual'),
                Line2D([0], [0], color='indianred', lw=2, label='Stacked')
            ]
            self.ax.legend(handles=legend_elements, loc='upper right', fontsize=20)
                
        # Fall back to single channel display if only one is specified
        elif base_stream and not stacked_stream:
            print("Only individual traces are available to display")

            base_stream.plot(**plot_args, linewidth=4, color='black')
            self.ax = self.fig.axes[0]
            self.ax.set_autoscale_on(False)

        elif stacked_stream and not base_stream:
            print("Only stacked traces are available to display")

            stacked_stream.plot(**plot_args, linewidth=4, color='black')
            self.ax = self.fig.axes[0]
            self.locked_xlim, self.locked_ylim = self.ax.get_xlim(), self.ax.get_ylim()

            self.ax.set_autoscale_on(False)
                           
        if orientation == 'vertical':
            # Station labels added to offset axis
            self.ax.invert_yaxis()
            self.ax.tick_params(axis='both', which='major', labelsize=20)
            self.ax.xaxis.label.set_size(20)
            self.ax.set_xlim(left=-0.025)
            self.ax.yaxis.label.set_size(20)
            transform = blended_transform_factory(self.ax.transData, self.ax.transAxes)    
                        
            # Create twin axis for top labels
            ax2 = self.ax.twiny()
            ax2.set_xlim(self.ax.get_xlim())
            
            # Set xticks at trace locations
            xticks = [tr.stats.distance / 1e3 for tr in self.stream]
            ax2.set_xticks(xticks)
            
            # Create marker labels (• for source, ▼ for receivers)
            labels = ['●' if int(tr.stats.distance) == 0 else '▼' for tr in self.stream]
            ax2.set_xticklabels(labels, fontsize=20)
    
            # Color the markers
            for tick in ax2.get_xticklabels():
                if tick.get_text() == '▼':
                    tick.set_color('black')
                else:
                    tick.set_color('indianred')
                 
        if orientation == 'horizontal':
            # Station labels added to offset axis
            self.ax.tick_params(axis='both', which='major', labelsize=20)
            self.ax.yaxis.label.set_size(20)
            self.ax.set_ylim(bottom=-0.025)
            self.ax.xaxis.label.set_size(20)
            transform = blended_transform_factory(self.ax.transData, self.ax.transAxes)    
                        
            # Create twin axis for top labels
            ax2 = self.ax.twinx()
            ax2.set_ylim(self.ax.get_ylim())
            
            # Set yticks at trace locations
            yticks = [tr.stats.distance / 1e3 for tr in self.stream]
            ax2.set_yticks(yticks)
            
            # Create marker labels (• for source, ▼ for receivers)
            labels = ['●' if int(tr.stats.distance) == 0 else '▼' for tr in self.stream]
            ax2.set_yticklabels(labels, fontsize=20)
    
            # Color the markers
            for tick in ax2.get_yticklabels():
                if tick.get_text() == '▼':
                    tick.set_color('black')
                else:
                    tick.set_color('indianred')

        # Add station labels
        for j,tr in enumerate(self.stream):         
            dist = tr.stats.distance
            
            if self.orientation == 'vertical':
                rotation = 0
                px = dist / 1e3
                py = 1.05
                va = "top"
                
            elif self.orientation == 'horizontal':
                rotation = 90
                py = dist / 1e3
                px = 1.02
                va = "bottom"
                
            if hasattr(tr.stats, 'station') and tr.stats.station in unique_stations:                
                if int(dist) == 0:
                    # print(f"Source {tr.stats.station} station at {dist}m")
                    label = '' # Source(s)
                    self.ax.text(px, 
                            py, 
                            label, 
                            color='indianred',
                            fontsize=20,
                            rotation=rotation,
                            va=va,
                            ha="center", 
                            transform=transform, 
                            zorder=10)
                else:
                    label = '' # Receiver(s)
                    self.ax.text(px, 
                            py, 
                            label, 
                            color='black',
                            fontsize=20,
                            rotation=rotation,
                            va=va,
                            ha="left", 
                            transform=transform, 
                            zorder=10)
                    
        # Plot any pre-loaded points
        if self.clicked_points:
            self.update_scatter_plot()
        
        # Save the figure
        if self.outfile != None:
            filename = self.outfile+".png"
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Figure saved as {filename}")
            
        print("\nInteractive Plot Instructions:")
        print("- Double left-click: Add point")
        print("- Single left-click: Select point")
        print("- Right-click: Remove nearest point")
        print("- Press DELETE: Remove selected point")
        print("- Press 'f': Fit polynomial to points. If needed, double-click 'f' to reset figure scale.")
        print("- Press 'p': Plot fitted traveltime curve. If needed, double-click 'p' to reset figure scale.")
        print("- Press 'r': Rescale main axis")
        print("- Press SPACEBAR when finished to save and continue")
        
        # Connect the click event to the handler
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.fig.canvas.mpl_connect('close_event', self.on_close)

        # Show the figure
        plt.show(block=True)        

        # Now save the data
        try:
            if hasattr(self, 'outfile') and self.outfile is not None:
                self.on_close(None)
        except Exception as e:
            print(f"Error during save: {e}")
        
        # Ensure figure is closed
        if plt.fignum_exists(self.fig.number):
            plt.close(self.fig)
            
        print("Figure closed successfully")
            
        # Return the DataFrame with the clicked points
        return self.points_df

