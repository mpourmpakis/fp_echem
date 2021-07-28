import pathlib

import pytest

import fpec.rxn_network

import numpy as np
from scipy.integrate.odepack import odeint

# direct solution for the following homogeneous reaction scheme
# 2[A] + [B] -> 2[C]
# [C] + [A] -> [D]

k_b = 8.617333262145E-05 # Boltzmann constant in eV/K
T = 298.15

Af_1 = 1E12
Ar_1 = 1E11
energy_1 = -0.2
barrier_1 = 0.5

actf_1 = np.max([energy_1,barrier_1])
actr_1 = barrier_1 - energy_1

kf_1 = Af_1*np.exp(-actf_1/(k_b*T))
kr_1 = Ar_1*np.exp(-actr_1/(k_b*T))

Af_2 = 1E12
Ar_2 = 1E11
energy_2 = 0.1
barrier_2 = 0.6

actf_2 = np.max([energy_2,barrier_2])
actr_2 = barrier_2 - energy_2

kf_2 = Af_2*np.exp(-actf_2/(k_b*T))
kr_2 = Ar_2*np.exp(-actr_2/(k_b*T))

A_o = 1 
B_o = 2
C_o = 0
D_o = 0

initial_comps = [A_o,B_o,C_o,D_o]

def rxn(x, t):
    return [- 0.5*kf_1*(x[0]**2)*x[1] + 0.5*kr_1*x[2]**2 - kf_2*x[2]*x[0] + kr_2*x[3],
            - kf_1*(x[0]**2)*x[1] + kr_1*x[2]**2,
            + 0.5*kf_1*(x[0]**2)*x[1] - 0.5*kr_1*x[2]**2 - kf_2*x[2]*x[0] + kr_2*x[3],
            + kf_2*x[2]*x[0] - kr_2*x[3]]

# direct solution for the following heterogeneous reaction scheme
# [A] + [*] -> [A*]
# [A*] + [A] -> [A2] + [*]

A_o = 3
A_s_o = 0
A2_o = 0
s_o = 0.001

surf_initial_comps = [A_o,A2_o,A_s_o,s_o]
def surf_rxn(x, t):
    return [- kf_1*x[0]*x[3] + kr_1*x[2] - kf_2*x[2]*x[0] + kr_2*x[1]*x[3],
            + kf_2*x[2]*x[0] - kr_2*x[1]*x[3],
            + kf_1*x[0]*x[3] - kr_1*x[2] - kf_2*x[2]*x[0] + kr_2*x[1]*x[3],
            - kf_1*x[0]*x[3] + kr_1*x[2] + kf_2*x[2]*x[0] - kr_2*x[1]*x[3]]

t = np.linspace(0,60,int(1+60/0.01))

def run(rxn = surf_rxn, initial_comps = surf_initial_comps, t = t):
    return odeint(rxn, initial_comps, t)

def test_network_solution():
    # reading in from .txt setup should yield same solution as hard code
    a, b = fpec.rxn_network.create_network(pathlib.Path(__file__).parent / 'reactions.txt')
    coupled_rxns = fpec.rxn_network.CoupledReactions(b)
    cls_sol = coupled_rxns.solve()
    dir_sol = run(rxn = rxn, initial_comps = initial_comps, t = t)
    assert np.allclose(cls_sol,dir_sol) == True

def test_surface_solution():
    # reading in from .txt setup should yield same solution as hard code
    a, b = fpec.rxn_network.create_network(pathlib.Path(__file__).parent / 'surface_rxn.txt')
    coupled_rxns = fpec.rxn_network.CoupledReactions(b)
    cls_sol = coupled_rxns.solve()
    dir_sol = run(rxn = surf_rxn, initial_comps = surf_initial_comps, t = t)
    assert np.allclose(cls_sol,dir_sol) == True
