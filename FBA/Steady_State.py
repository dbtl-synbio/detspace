#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 17:31:27 2024

@author: ricardo
"""

import numpy as np
from tqdm import tqdm
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
# %matplotlib inline
import cobra
from cobra.io import load_model

def FBA():

    model = load_model('textbook') # Example with e-coli core model
    # =============================================================================
    # Set up the dynamic system
    # =============================================================================
    def add_dynamic_bounds(model, y):
        """Use external concentrations to bound the uptake flux of glucose."""
        biomass, glucose = y  # expand the boundary species
        glucose_max_import = -10 * glucose / (5 + glucose)
        model.reactions.EX_glc__D_e.lower_bound = glucose_max_import
    
    
    def dynamic_system(t, y):
        """Calculate the time derivative of external species."""
    
        biomass, glucose = y  # expand the boundary species
    
        # Calculate the specific exchanges fluxes at the given external concentrations.
        with model:
            add_dynamic_bounds(model, y)
    
            cobra.util.add_lp_feasibility(model)
            feasibility = cobra.util.fix_objective_as_constraint(model)
            lex_constraints = cobra.util.add_lexicographic_constraints(
                model, ['Biomass_Ecoli_core', 'EX_glc__D_e'], ['max', 'max'])
    
        # Since the calculated fluxes are specific rates, we multiply them by the
        # biomass concentration to get the bulk exchange rates.
        fluxes = lex_constraints.values
        fluxes *= biomass
    
        # This implementation is **not** efficient, so I display the current
        # simulation time using a progress bar.
        if dynamic_system.pbar is not None:
            dynamic_system.pbar.update(1)
            dynamic_system.pbar.set_description('t = {:.3f}'.format(t))
    
        return fluxes
    
    dynamic_system.pbar = None
    
    
    def infeasible_event(t, y):
        """
        Determine solution feasibility.
    
        Avoiding infeasible solutions is handled by solve_ivp's built-in event detection.
        This function re-solves the LP to determine whether or not the solution is feasible
        (and if not, how far it is from feasibility). When the sign of this function changes
        from -epsilon to positive, we know the solution is no longer feasible.
    
        """
    
        with model:
    
            add_dynamic_bounds(model, y)
    
            cobra.util.add_lp_feasibility(model)
            feasibility = cobra.util.fix_objective_as_constraint(model)
    
        return feasibility - infeasible_event.epsilon
    
    infeasible_event.epsilon = 1E-6
    infeasible_event.direction = 1
    infeasible_event.terminal = True
    # =============================================================================
    # Run the dynamic FBA simulation
    # =============================================================================
    ts = np.linspace(0, 15, 100)  # Desired integration resolution and interval
    y0 = [0.1, 10]
    
    with tqdm() as pbar:
        dynamic_system.pbar = pbar
    
        sol = solve_ivp(
            fun=dynamic_system,
            events=[infeasible_event],
            t_span=(ts.min(), ts.max()),
            y0=y0,
            t_eval=ts,
            rtol=1e-6,
            atol=1e-8,
            method='BDF'
        )
    sol
    
    # display_flux()
    # =============================================================================
    # Plot timelines of biomass and glucose
    # =============================================================================
    ax = plt.subplot(111)
    ax.plot(sol.t, sol.y.T[:, 0])
    ax2 = plt.twinx(ax)
    ax2.plot(sol.t, sol.y.T[:, 1], color='r')
    
    ax.set_ylabel('Biomass', color='b')
    ax2.set_ylabel('Glucose', color='r')
    
    # =============================================================================
    #  Growth media
    # =============================================================================
    model.medium
    medium = model.medium
    medium["EX_o2_e"] = 0.0 
    model.medium = medium
    
    model.medium
    model.slim_optimize()
    
    # Setting the growth medium also connects to the context 
    # manager, so you can set a specific growth medium in a 
    # reversible manner.
    
    model = load_model("textbook")
    
    with model:
        medium = model.medium
        medium["EX_o2_e"] = 0.0 # let us enforce anaerobic growth by shutting off the oxygen import.
        model.medium = medium
        print(model.slim_optimize())
    print(model.slim_optimize())
    model.medium
    
    #Minimal growth medium 
    
    from cobra.medium import minimal_medium
    
    max_growth = model.slim_optimize()
    minimal_medium(model, max_growth)
    
    minimal_medium(model, 0.8, minimize_components=8, open_exchanges=True)
    
    # Exchange reactions
    
    ecoli = load_model("iJO1366")
    ecoli.exchanges[0:5]
    
    # Demand reactions
    
    ecoli.demands
    
    # Sink reactions
    ecoli.sinks
    
    # All boundary reactions (demand, sink and exchange)
    ecoli.boundary[0:10]
    
    # _display_flux(frame: pandas.DataFrame, names: bool, threshold: float)