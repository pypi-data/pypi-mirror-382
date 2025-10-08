#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pykonal

class pykonal_plotter:
    """
    This class plots and visualises seismic ray tracing results using PyKonal
    to solve the Eikonal equation for the traveltime field.
    
    This class provides methods for:
    - Plot 2D or 3D velocity depth models with geometry and features
    - Perform wavefront propagation
    - Solve the Eikonal equation for traveltime field 
    - Calculate ray traces for shortest ray paths, corresponding to P-wave first arrivals
    - Build synthetic velocity models
    """
    
    def __init__(self):
        """Initialize the pyKonal_plotter class"""
        pass
        
    def PlotGeometry(self):
        """
        Plot the velocity model geometry with sources and receivers.
        
        Parameters:
        --------    
        None
        
        Returns:
        --------
        None
        """
        
        plt.close("all")
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        
        self.qmesh = self.ax.pcolormesh(
            self.vmodel.nodes[:, :, 0, 0],  # along x-axis
            self.vmodel.nodes[:, :, 0, 1],  # along y-axis
            self.vmodel.values[:, :, 0],    # values at initial position
            cmap='Blues',
            vmin=self.vmin, 
            vmax=self.vmax
        )
            
        # Plot receivers with labels
        self.ax.scatter(self.rxs, np.zeros_like(self.rxs), marker="v", clip_on=False, s=128, 
                  edgecolor="k", zorder=100, label="Receivers")
        
        self.ax.scatter(self.sxs, np.zeros_like(self.sxs), marker="o", clip_on=False, s=32, 
                  edgecolor="k", zorder=100, label="Sources")
        for sx in self.sxs:
            self.ax.text(sx, -5, "Source", ha='center', va='bottom', 
                   color='indianred', fontweight='bold')

        # Update plot formatting for ray paths visualization
        self.ax.set_aspect(1)
        self.ax.invert_yaxis()
        self.ax.tick_params(axis='both', which='major', length=8, width=2)
        self.ax.tick_params(labelsize=12)
        
        # Create x- and y-tick labels
        x = int(self.solver.velocity.npts[0] * self.solver.velocity.node_intervals[0])
        xmid = int(np.round(x/2, -1))
        self.ax.set_xticks([0, xmid, x])
        
        y = int(self.solver.velocity.npts[1] * self.solver.velocity.node_intervals[1])
        ymid = int(np.round(y/2, -1))
        self.ax.set_yticks([0, ymid, y])        
        
        self.ax.set_ylabel('Depth (m)', fontsize=14)
        self.ax.set_xlabel('Offset (m)', fontsize=14)
        
        # Create colorbar
        cbar = self.fig.colorbar(self.qmesh, ax=self.ax, shrink=0.6) # play around with colorbar height
        cbar.set_label("Velocity (m/s)", fontsize=14)
        vmid = np.round((self.vmax - self.vmin) / 2, -3)
        cbar.set_ticks([self.vmin, vmid, self.vmax])
        cbar.ax.tick_params(labelsize=12)
        
        if self.fpath is not None:
            self.fig.savefig(self.fpath+".png")

    @staticmethod
    def sph2xyz(rtp, x0=0, y0=0):
        """
        Convert spherical to Cartesian coordinates.
        
        Parameters:
        -----------
        rtp : array-like
            Spherical coordinates (r, theta, phi)
        x0, y0 : float, optional
            Origin offset (default: 0, 0)
            
        Returns:
        --------
        xyz : numpy array
            Cartesian coordinates
        """
        x = x0 + rtp[..., 0] * np.cos(rtp[..., 2])
        y = y0 + rtp[..., 0] * np.sin(rtp[..., 2])
        xyz = np.stack([x, y, np.zeros_like(x)], axis=-1)
        return xyz
    
    @staticmethod
    def xyz2sph(xyz, x0=0, y0=0):
        """
        Convert Cartesian to spherical coordinates.
        
        Parameters:
        -----------
        xyz : array-like
            Cartesian coordinates
        x0, y0 : float, optional
            Origin offset (default: 0, 0)
            
        Returns:
        --------
        rtp : numpy array
            Spherical coordinates (r, theta, phi)
        """
        dx = xyz[..., 0] - x0
        dy = xyz[..., 1] - y0
        r = np.sqrt(np.square(dx) + np.square(dy))
        p = np.arctan2(dy, dx)
        rtp = np.stack([r, np.pi/2 * np.ones_like(r), p], axis=-1)
        return rtp
    
    def PropagateWavefront(self, src):
        """
        Propagate wavefront from a source through the velocity model.
        
        Parameters:
        -----------
        src : tuple
            Source position (x, y, z)
            
        Returns:
        --------
        ff : pykonal.EikonalSolver
            Far-field solver with propagated wavefront
        nf_rmin : ndarray
            Near-field minimum radius parameters
        """
        
        # Define the far-field grid
        ff = pykonal.EikonalSolver(coord_sys="cartesian")
        ff.vv.min_coords = self.vmodel.min_coords
        ff.vv.node_intervals = self.vmodel.node_intervals
        ff.vv.npts = self.vmodel.npts
        ff.vv.values = self.vmodel.values

        # Define a near-field grid centered on the source location and narrow band
        nf = pykonal.EikonalSolver(coord_sys="spherical")
        nf.vv.min_coords = 5, np.pi/2, 0
        nf.vv.node_intervals = 0.1, 1, np.pi/31
        nf.vv.npts = 1000, 1, 32
        nf_rmin = np.array([nf.vv.min_coords[0], nf.vv.node_intervals[0]])

        # Interpolate velocity from the far-field grid to the near-field grid
        xyz = self.sph2xyz(nf.vv.nodes, x0=src[0], y0=src[1])
        nf.vv.values = ff.vv.resample(xyz.reshape(-1, 3)).reshape(xyz.shape[:-1])

        # Initialize the near-field narrow-band
        for ip in range(nf.tt.npts[2]):
            idx = (0, 0, ip)
            vv = nf.vv.values[idx]
            if not np.isnan(vv):
                nf.tt.values[idx] = nf.tt.node_intervals[0] / vv
                nf.unknown[idx] = False
                nf.trial.push(*idx)

        # Propagate the wavefront across the near-field grid
        nf.solve()

        # Map the traveltime values from the near-field grid onto the far-field grid
        rtp = self.xyz2sph(ff.tt.nodes, x0=src[0], y0=src[1])
        rtp = rtp.reshape(-1, 3)
        tt = nf.tt.resample(rtp)
        tt = tt.reshape(ff.tt.npts)

        idxs = np.nonzero(np.isnan(tt))
        tt[idxs] = np.inf

        ff.tt.values = tt

        # Initialize far-field narrow band
        for idx in np.argwhere(~np.isinf(ff.tt.values)):
            idx = tuple(idx)
            ff.unknown[idx] = False
            ff.trial.push(*idx)

        # Propagate the wavefront across the remainder of the far field
        ff.solve()
        
        return ff, nf_rmin
    
    def ShortestRayPath(self, vs, rxs, sxs, nx, ny, vmin=300, vmax=4000, fpath=None):
        """
        Calculate and plot the shortest traveltime ray paths from source(s) to receiver(s).

        Parameters:
        -----------
        solver : pykonal.EikonalSolver
            PyKonal solver object
        vs : Dictionary or pandas DataFrame
            'z' (depth) and 'v' (velocity) arrays
        rxs : array-like
            Receiver positions
        sxs : array-like
            Source positions
        nx : int
            Number of grid points along x-direction in Cartesian coordinate system
        ny : int
            Number of grid points along x-direction in Cartesian coordinate system     
        vmin : float, optional 
            Lower limit for P-wave seismic velocity (default: 300 m/s)
        vmax : float, optional 
            Upper limit for P-wave seismic velocity (default: 4000 m/s)      
        fpath : str, optional
            File path to save the figure (default: None)
        
        Returns:
        --------
        data : pandas.DataFrame
            Travel time data with columns ['sxid', 'rxid', 'tt']
        """
        
        # Store parameters as instance variables for PlotGeometry method
        self.rxs = rxs
        self.sxs = sxs
        self.vmin = vmin
        self.vmax = vmax
        self.fpath = fpath 
        
        # Build synthetic velocity model     
        self.vmodel = pykonal.fields.ScalarField3D(coord_sys="cartesian")
        
        # Create velocity-depth model
        # Instantiate EikonalSolver object using Cartesian coordinates.
        self.solver = pykonal.EikonalSolver(coord_sys="cartesian") 
        self.solver.velocity.npts = nx + 1, ny + 1, 1 # number of nodes is nx, ny, nz
        
        # Setup finite element mesh in Cartestian coordinates
        self.solver.velocity.node_intervals = 0.1, 0.1, 1 # Nodal distance is dx, dy, dz, in km
        self.solver.velocity.min_coords = 0, 0, 0 # Lower bound of the computation grid

        self.vmodel.min_coords = self.solver.velocity.min_coords
        self.vmodel.node_intervals = self.solver.velocity.node_intervals
        self.vmodel.npts = self.solver.velocity.npts
        self.vmodel.values = np.interp(self.vmodel.nodes[..., 1], vs['z'], vs['v'])
        
        # Create the basic geometry plot to overlay rays onto
        self.PlotGeometry()
        
        """
        Perform ray tracing to calculate the traveltime field. Solve the Eikonal
        equation using Fast Marching Method in PyKonal to extract travel times
        at all offsets.
        """
        nrx = len(rxs)
        data = pd.DataFrame(columns=["sxid", "rxid", "tt"])
        
        for sxid, sx in enumerate(sxs):
            src = (sx, 0, 0)
            
            """ 
            Solve Eikonal equation and propagate wavefront 
            Near-field minimum radius parameters from last source, nf_rmin
            Far-field solver from last source, ff
            """
            ff, nf_rmin = self.PropagateWavefront(src)
            
            # Extract travel times at receiver locations
            tt = ff.tt.resample(np.stack([rxs, np.zeros_like(rxs), np.zeros_like(rxs)], axis=1))
            data = pd.concat(
                [
                    data,
                    pd.DataFrame(
                        dict(
                            sxid=sxid+1,
                            rxid=np.arange(1, nrx+1),
                            tt=tt
                        )
                    ),
                ],
                ignore_index=True
            )
        
        data = data.astype(dict(sxid=int, rxid=int, tt=float))
        data['tt'] *= 1000  # from s to ms
        
        # Now add ray paths to the existing plot
        for sxid, sx in enumerate(sxs):
            src = (sx, 0, 0)
            ff, nf_rmin = self.PropagateWavefront(src)
            for rx in rxs:
                # Trace the ray that ends at receiver by following steepest descent
                ray = ff.trace_ray(np.array([rx, 0, 0]))
                ray = ray[::10, :2]  # reduce mesh size for 2D plotting
                self.ax.plot(ray[:, 0], ray[:, 1], color="k", linewidth=1)
        
        # Save the final plot with ray paths
        if fpath is not None:
            self.fpath += "-shortest-ray-paths"
            self.fig.savefig(self.fpath+".png", dpi=400, bbox_inches='tight')
            
        return data