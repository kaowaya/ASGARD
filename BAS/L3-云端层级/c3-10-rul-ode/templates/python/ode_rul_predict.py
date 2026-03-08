# templates/python/ode_rul_predict.py
"""
ASGARD C3.10 Cloud RUL Prediction (Semi-Empirical ODE)

Uses a semi-empirical Ordinary Differential Equation based on Arrhenius kinetics 
and SEI growth (sqrt(t) dependence) to integrate forward in time and predict 
Remaining Useful Life (RUL) under a specified load profile.

Usage:
    python ode_rul_predict.py --current_soh 92.0 --profile standard --output rul_result.json
"""

import argparse
import numpy as np
import json
import logging
import os
from scipy.integrate import solve_ivp

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Constants for LFP cell (mock values for demonstration)
E_a = 40000     # Activation Energy J/mol
R_gas = 8.314   # Gas constant J/(mol*K)
k1 = 2e6        # Pre-exponential factor
n_i = 1.0       # Current dependence exponent (Peukert-like)

def ode_degradation(t, q_loss, temp_k, i_rate):
    """
    ODE System: d(Q_loss)/dt 
    Model: SEI growth is proportional to exp(-Ea/RT) * I^n / sqrt(Time)
    Rewriting in a state-space form dQ/dt = f(Q, t) for solve_ivp:
    dQ/dt = A(T, I) / sqrt(t + 1e-6) # adding small epsilon to avoid divide by zero
    Actually, a better physical model is: dQ/dt ~ 1 / Q
    This naturally yields Q ~ sqrt(t). Let's use this robust form!
    
    dq_loss/dt = ( k1 * exp(-E_a / (R_gas * temp_k)) * (i_rate)**n_i ) / max(q_loss, 1e-6)
    """
    arrhenius = np.exp(-E_a / (R_gas * temp_k))
    rate = k1 * arrhenius * (i_rate ** n_i)
    # Clamp q_loss to prevent singularity at t=0
    dq_dt = rate / max(q_loss[0], 1e-4) 
    return [dq_dt]

def predict_rul(current_soh, profile='standard'):
    """
    Forward integrates the ODE until SOH drops below 80%.
    profile: determines the daily T and I patterns.
    """
    if current_soh < 80.0:
        return {"success": False, "error": "Battery is already below 80% EOL."}
        
    # Map profile to average daily continuous conditions for simplistic ODE integration
    # Ideally, this would be a time-varying function T(t), I(t)
    if profile == 'heavy':
        temp_k = 273.15 + 35.0 # 35C average
        i_rate = 1.0 # 1C equivalent continuous cycling stress
    else:
        temp_k = 273.15 + 25.0 # 25C average
        i_rate = 0.5 # 0.5C stress
        
    # Initial state
    initial_q_loss = (100.0 - current_soh) / 100.0
    y0 = [initial_q_loss]
    
    # EOL event: Q_loss reaches 0.20 (SOH 80%)
    def hit_eol(t, y):
        return y[0] - 0.20
    hit_eol.terminal = True
    hit_eol.direction = 1
    
    # Integrate for maximum 10 years (3650 days) in seconds
    t_span = (0, 3650 * 24 * 3600)
    
    logger.info(f"Starting ODE forward integration from Q_loss={initial_q_loss:.4f} @ {temp_k-273.15}C...")
    sol = solve_ivp(
        fun=lambda t, y: ode_degradation(t, y, temp_k, i_rate),
        t_span=t_span,
        y0=y0,
        events=hit_eol,
        method='RK45', 
        max_step=24 * 3600 # Max step size 1 day
    )
    
    if sol.status == 1: # A termination event occurred
        rul_seconds = sol.t_events[0][0]
        rul_days = int(rul_seconds / (24 * 3600))
        return {
            "success": True,
            "rul_days": rul_days,
            "profile_used": profile,
            "start_soh": current_soh,
            "end_soh": 80.0
        }
    else:
        return {
            "success": True, 
            "rul_days": "> 3650 (10+ Years)",
            "message": "Did not reach 80% within 10 years under this profile."
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--current_soh', type=float, required=True)
    parser.add_argument('--profile', type=str, default='standard')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    res = predict_rul(args.current_soh, args.profile)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(res, f, indent=4)
        
    if res.get('success'):
        logger.info(f"C3.10 RUL Prediction complete. RUL: {res.get('rul_days')} days.")
    else:
        logger.error(f"Failed: {res.get('error')}")

if __name__ == '__main__':
    main()
