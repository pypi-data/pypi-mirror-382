#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import numpy as np
import pandas as pd
idx = pd.IndexSlice
import functools
import matplotlib.pyplot as plt
import scipy
from scipy import interpolate,integrate 

class inversion:
    """
    This class performs diving wave analysis to calculate the depth-velocity 
    and depth-density profiles from first refracted arrivals based on Herglotz-
    Wiechert inversion. It has applications to shallow over-snow seismic 
    refraction surveys.
    
    Based on Julian Scott's MATLAB implementation (British Antarctic Survey, 2008)
    and modified by Shyla Kupis (University of Tasmania, 2024)
    """
    
    def __init__(self):
        """
        Initialize inversion class 
        """        
        
        self.fig = None
        self.ax = None
        self.outputs = pd.DataFrame()     
    
    def integrand(self, x, vel):
        """
        Setup arccosh integrand for depth calcuation using the exponential 
        slowness model parameters and apparent velocity
                
        Parameters:
        -----------
        x : float or numpy.ndarray
            Epicentral distance or integration variable [m]
        vel : float
            Apparent velocity at the surface [m/ms] 
            (velocity propagating along surface)
            
        Requirements:
        -------------
        self.a : numpy.ndarray
            Array of 5 exponential model parameters [A1, A2, A3, A4, A5],
            where seismic slowness = A1*A2*exp(-A2*x) + A3*A4*exp(-A4*x) + A5
            
        Returns:
        --------
        float or numpy.ndarray
            Computed integrand value for depth [dimensionless]
        """        
        
        a = self.a
        s = a[0]*a[1]*np.exp(-a[1]*x) + a[2]*a[3]*np.exp(-a[3]*x) + a[4]
        t = s*vel # apparent velocity/velocity progating along surface
        y = np.arccosh(t)
    
        return y
    
    def zvel(self):  
        """
        Solve the integrand function for depth using exponential slowness model 
        parameters and apparent velocity
 
        Parameters:
        -----------
        None
        
        Requirements:
        -------------
        self.a : numpy.ndarray
            Fitted exponential model parameters 
            
            
        Returns:
        --------
        
        """
        
        z = []            
        Distance = np.append(np.arange(0.1,10),np.arange(10,301,1))
        Distance = np.append(np.arange(1,30),np.arange(30,1001,10))
    
        # 1/(dt(x)/dx), t(x) travel time corresponding to slowness in source-receiver offset domain
        # first derivative of uniformly sampled slowness traveltime curve
        a = self.a
        velocity = 1/(a[0]*a[1]*np.exp(-a[1]*Distance) + a[2]*a[3]*np.exp(-a[3]*Distance) + a[4])
        for vel,x in zip(velocity,Distance):
            # integrating for depth at epicentral distance for ray where apparent velocity is vp
            # outputs integral of function and absolute error
            # out = integrate.quad(functools.partial(self.integrand, vel=vel, a=a), 0, x, args=())
            integrand_with_vel = functools.partial(self.integrand, vel=vel)
            out = integrate.quad(integrand_with_vel, 0, x)
            out = (1/math.pi)*out[0]
            z = np.append(z,out)
                
        self.v = velocity #.real
        self.z = z #z.real    

    def zdensity(self):
        """
        Calculate depth-density profile from the empirical relationship that
        density has with seismic velocity (Kohnen, 1972). 
               
        
        Parameters:
        -----------
        None
        
        Returns:
        --------
        
        """
        
        # Density of ice
        roi = 917 # in kgm^-3
        # roi = 908 # in kgm^-3
    
        # Empirically-derived density calculation from Kohnen (1972)
        # Seismic velocity values from zvel() method
        Vcomplex = np.asarray((self.Vice - self.v)/2.25,dtype=complex)
        ro = roi*np.power(1+np.power(Vcomplex,1.22),-1)
        self.ro = ro.real
        # ro = (0.239*v) - 0.002 # Byrd station, Kohnen 1973) 
        
    def twoway(self):
        """
        Compute the two-way travel time as a function of depth using the 
        calculated velocity profile and extrapolate to 150 m depth. 
        
        Parameters:
        -----------
        None
        
        Returns:
        --------
        tuple : (numpy.ndarray, numpy.ndarray)
            Two-way travel times and corresponding depths
        """        
        
        # Use seismic velocity and depth values from zvel() method
        zunique, ind = np.unique(self.z, return_index=True)
        vunique = self.v[ind]
        
        zmax = np.floor(zunique[-1])
        print(zmax)
        zi = np.arange(0.5,(zmax-0.5) + 1)
        f = interpolate.interp1d(zunique, vunique, fill_value='extrapolate')
        vi = f(zi)
        
        # Now calculate the travel time for each metre travelled from the surface using the
        # velocity at the centre of each depth range
        
        twtti = 2/vi # For each step
    
        # Check size and if less than 150 m extrapolate this down to 150 m using self.Vice
        n = twtti.shape[0]
        if n < 150:
            twtti = np.append(twtti,2/self.Vice*np.ones(150-n,))
            zmax = 150
            
        # Now calculate total cumulative travel time
        self.twtt = np.cumsum(twtti) # Total culmulative
        self.ztwtt = np.arange(1,zmax+1) # Corresponding depth values
        
        return self.twtt, self.ztwtt
     
    def analyfun(self, params):
        """ 
        Find the optimal travel-time curve fitting parameters to Kirchner and 
        Bentley's (1979) exponential formulation by minimising the objective function. 
        
        Travel Time Model:
        -----------------
        t(x) = A*(1-exp(-B*x)) + C*(1-exp(-D*x)) + E*x
        
        Based on Kirchner and Bentley (1979) exponential formulation for
        seismic slowness inversion in the source-to-receiver offset domain.
        
        Parameters:
        -----------
        params : list or numpy.ndarray
            Exponential model parameters to optimize
            
        Returns:
        --------
        float
            Sum of squared errors between observed and fitted travel times
        """        
        
        A = params[0]
        B = params[1]
        C = params[2]
        D = params[3]   
        # Kirchner and Bentley (1979) exponential equation
        FittedCurve = A*(1-np.exp(-B * self.x)) + C*(1-np.exp(-D * self.x))
        if len(params) > 4:
            E = params[4]
            FittedCurve += E * self.x
            
        # Sum of squared errors using observed travel-time data
        ErrorVector = FittedCurve - self.tdata
        self.error = np.sum(ErrorVector**2)
        
        return self.error
        
    def DivingWaveAnalysis(self, df, Vice=3800/1000, plot_results=False, fpath=None):
        """
        Diving-wave analysis workflow for seismic velocity and density profiles
        from shallow seismic surveys with polar and permafrost applications
        
        This main method handles travel-time data pre-processing and curve fitting
        for calculations of seismic velocity, density, and two-way travel-time
        
        Parameters:
        -----------
        df : pandas.DataFrame
            Input travel time data with columns:
            - 'x' : Source-receiver offsets [m]
            - 't' : First arrival travel times [ms]
        Vice : float, default=3.8
            Reference velocity for glacial ice [m/ms]
            Typical range: 3.7-3.9 m/ms for Antarctic ice
        plot_results : bool, default=False
            Whether to generate and display analysis plots
        fpath : str, optional
            File path prefix for saving output files (.csv, .png, .txt)
            
        Outputs Generated:
        -----------------
        CSV Files:
        - {fpath}.csv : Observed data and HWI-derived results from diving-wave analysis 
        
        Text Files:
        - {fpath}-outputs.txt : Formatted parameter summary of fitted 
        traveltime curve parameters
        
        Plot Files (if plot_results=True):
        - {fpath}-density-depth.png : Density profile with markers at pore 
        close-off and glacial ice depth
        - {fpath}-results.png : Four-panel summary plot of fitted travel-time
        data, depth-velocity, depth-density, and two-way travel-time curve
            
        Returns:
        --------
        pandas.DataFrame
            Complete analysis results with columns:
            - 'Offset (m)' : Source-receiver offsets
            - 'tt (ms)' : Observed travel times  
            - 'xmodel (m)' : Modelled offsets
            - 'ttmodel (ms)' : Fitted travel times
            - 'z (m)' : Depth values
            - 'v (m/ms)' : Velocity profile
            - 'ro (kg/m3)' : Density profile
            - 'ztwtt (m)' : Two-way travel time depths
            - 'twtt (ms)' : Two-way travel times
        """
                
        self.df = df
        self.fpath = fpath
        self.Vice = Vice
        self.plot_results = plot_results
        
        value = self.df.copy()
        row = 0
        for k in self.df.index[:-1]:
            if self.df.loc[k,"x"] == self.df.loc[k+1,"x"]:
                value.loc[k,"x"] = self.df.loc[k,"x"]
                value.loc[k,"t"] = self.df.loc[k:k+1,"t"].mean()
                row += 1
                
            if k>1 and self.df.loc[k,"x"] == self.df.loc[k-1,"x"]:
                value.loc[row,"x"] = self.df.loc[k-1,"x"]
                value.loc[row,"t"] = self.df.loc[k-1,"t"]
                row += 1
                
            else:
                value.loc[row,"x"] = self.df.loc[k,"x"]
                value.loc[row,"t"] = self.df.loc[k,"t"]
                row += 1
        # Distance and travel times are now in vectors x and t
        value = value.drop_duplicates("x")  
        value = value.sort_values(by='x')
        x = value['x'].values
        self.x = x.astype(float)
        t = value['t'].values
        self.t = t.astype(float)
        
        a = np.zeros(5)
        p = np.array([10, 0.09, 30, 0.007],dtype=float) # Use temp parameter p
        self.tdata = self.t - self.x / self.Vice # subtracting parameter a5 because we are not changing it
        a[:4] = scipy.optimize.fmin(self.analyfun,x0=p) # uses the Nelder-Mead simplex algorithm to find the minimum
        a[4] = 1 / self.Vice
        self.a = a   
        
        # else: # for case when Vice is allowed to be optimized
        #     p = np.array([10, 0.09, 30, 0.007, 1/self.Vice],dtype=float) # Use temp parameter p for test 4
        #     self.tdata = self.t
        #     self.a = scipy.optimize.fmin(self.analyfun, x0=p) # uses the Nelder-Mead simplex algorithm to find the minimum
        
        self.analyfun(p) # curve fitting error
        print(self.a)
        
        # Give model fited values at 1 m intervals
        xi = np.arange(0, self.x[-1] + 1)
        ti = self.a[0] * (1 - np.exp(-self.a[1] * xi)) + self.a[2] * (1-np.exp(-self.a[3] * xi)) + self.a[4] * xi
        
        # Now run function zvel to give a velocity depth profile
        self.zvel()    
        
        # Now run an empirically-derived function to provide density profile
        self.zdensity()
                        
        # Now run a function to calculate two-way travel time
        self.twtt, self.ztwtt = self.twoway() 
            
        if self.plot_results:   
            
            # Only plot if PCO depth is reached
            densitydiff = self.ro - 830
            if np.max(densitydiff) >= 0: 
            
                self.fig, self.ax = plt.subplots(constrained_layout=True, figsize=(12,8))   
                self.ax.plot(self.ro, self.z, linewidth=4, color='black')

                # Add Stage I label with offset
                stage1_depth = self.z[np.argmin(np.abs(densitydiff))]    
                self.ax.plot(830,stage1_depth,color='red',markersize=25,marker='*')
                self.ax.annotate('Pore-close off depth (830 kg/m3)', 
                            xy=(830, stage1_depth),
                            xytext=(25, -10),  # offset points
                            textcoords='offset points',
                            fontsize=18,
                            va='center')
                
                # Add Stage II label if glacial ice density is reached
                densitydiff = self.ro-917
                if np.max(densitydiff) >= 0:
                    
                    stage2_depth = self.z[np.argmin(np.abs(densitydiff))]
                    self.ax.plot(917,stage2_depth,color='red',markersize=25,marker='*')
                    self.ax.annotate('Glacial ice (917 kg/m3)', 
                                xy=(917, stage2_depth),
                                xytext=(20, 0),  # offset points
                                textcoords='offset points',
                                fontsize=18,
                                va='center')
            
                self.ax.set_xlabel('Density (kg/m3)', fontsize=30)
                self.ax.set_ylabel('Depth (m)', fontsize=30)
                self.ax.tick_params(axis='both', which='major', length=10, width=2, labelsize=25)
                self.ax.tick_params(axis='both', which='minor', length=5, width=1, labelsize=25)
                outfile = self.fpath + "-pco-depth-density.png"
                self.fig.savefig(outfile, dpi=300, bbox_inches='tight')
                print(f"Figure saved as {outfile}")
                plt.show()
                
                # Reset
                self.fig = None
                self.ax = None
                
            else:
                print(f"Pore close-off depth is not reached. Max firn density is {np.max(self.ro)} kg/m3.")
                
            # Plotting travel time data    
            # Create the 2x2 subplot figure
            self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 10))
            
            self.ax1.plot(self.x, self.t,'xk')
            self.ax1.plot(xi,ti,'-k')
            self.ax1.set_xlabel('Distance (m)')
            self.ax1.set_ylabel('Travel time (ms)')
            
            self.ax2.plot(1000.* self.v, self.z)
            self.ax2.grid()
            self.ax2.set_xlabel('Velocity (m/s)')
            self.ax2.set_ylabel('Depth (m)')
            self.ax2.invert_yaxis()
            
            self.ax3.plot(self.ro, self.z) 
            self.ax3.grid()
            self.ax3.set_xlabel('Density (kg/m3)')
            self.ax3.set_ylabel('Depth (m)')
            self.ax3.invert_yaxis()
            
            self.ax4.plot(self.twtt, self.ztwtt)
            self.ax4.grid()
            self.ax4.set_xlabel('Two-way travel time (ms)')
            self.ax4.set_ylabel('Depth (m)')
            self.ax4.invert_yaxis()
            
            outfile = self.fpath + "-results.png"
            self.fig.savefig(outfile, dpi=300, bbox_inches='tight')
            plt.show()
            
        # Output as a csv file
        m1, m2, m3, m4 = len(self.x), len(xi), len(self.z), len(self.ztwtt)
        outputs = pd.DataFrame(index=np.arange(0,np.max([m1,m2,m3,m4])),
                                     columns=['Offset (m)','tt (ms)','xmodel (m)','ttmodel (ms)','z (m)','v (m/s)','ro (kg/m3)','ztwtt (m)','twtt (ms)'])
        outputs.loc[0:m1-1,'Offset (m)'] = self.x
        outputs.loc[0:m1-1,'tt (ms)'] = self.t
        outputs.loc[0:m2-1,'xmodel (m)'] = xi
        outputs.loc[0:m2-1,'ttmodel (ms)'] = ti
        outputs.loc[0:m3-1,'z (m)'] = self.z
        outputs.loc[0:m3-1,'v (m/ms)'] = self.v
        outputs.loc[0:m3-1,'ro (kg/m3)'] = self.ro
        outputs.loc[0:m4-1,'ztwtt (m)'] = self.ztwtt
        outputs.loc[0:m4-1,'twtt (ms)'] = self.twtt
        
        # Save outputs to csv file
        self.outputs = outputs
        self.outputs.to_csv(self.fpath + '.csv')
        
        # writing outputs to comma-delimited text file
        outfile = self.fpath +'fitted-traveltime-curve-parameters.txt'
        with open(outfile,'w') as file:
            # Write data to text file
            file.write('A1, A2, A3 ,A4, A5,\n')
            formatted_row = ', '.join([f'{value:8.5f}' for value in self.a])
            file.write(f'{formatted_row}\n')  
            file.write('self.Vice = 1/A5 (m/s),\n')   
            value = self.Vice * 1000
            file.write(f'{value:8.0f}\n')
            file.write('Fitting error,\n')
            file.write(f'{self.error:8.4f}\n')

        return self.outputs
       
