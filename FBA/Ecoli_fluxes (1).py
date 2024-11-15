#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 16:03:42 2024

@author: ricardo
"""

from cobra.io import load_model
from cobra.flux_analysis import flux_variability_analysis

model = load_model("textbook")
solution_fba = model.optimize()
print(solution_fba)
solution_fba.objective_value
fluxes=solution_fba.fluxes
print(model.summary())
SS_fluxes_FBA = fluxes

"""
Running FVA
"""
flux_variability_analysis(model, model.reactions[::], fraction_of_optimum=0.9, loopless=True)
solution_fva = model.optimize()
model.summary(fva=0.95)
fluxes=solution_fva.fluxes
SS_fluxes_FVA = fluxes
print(SS_fluxes_FVA)
dict_fluxes = dict(SS_fluxes_FVA)