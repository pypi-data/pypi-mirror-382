from scipy.optimize import fsolve
from scipy.optimize import brentq
from scipy.optimize import fmin
from sympy import Symbol, diff,Function,Derivative
from scipy.special import jv
from scipy.linalg import eigh
import numpy as np
import math
from supercoeffs import Cnlp_all,Cnlp_sum,cn_S_arr_holder,cn_S_arr,Cnlp_MN_3modes, Cnlp, Circuit
from lib.swg.sw_procedure import Hamiltonian, schrieffer_wolff_arr
from pathlib import Path
import dill as pickle  # use dill instead of pickle
import numbers
import sympy as sp







Klim = 1.00 #MHz
# der_sym_array=[]

pi=np.pi


omega_d = 2.

model_name = 'Kerr-cat'

###### Bemma-splitter params #####
omega_b0= 2.976 * 2 * pi
omega_c0 = 6.915 * 2 * pi
g_b= 0.0756 * 2* pi
g_c= 0.1349 * 2 * pi
chi_lim = 30 #Hz
non_comm_corr=False

FINAL_MONOMS = {
    "DETUNING":          ((1,),(1,)),   
    "KERR":              ((2,),(2,)),
    "2PH_SQUEEZING":    ((2,),(0,))
}

# Get the directory of the current script
current_dir = Path(__file__).resolve().parent

# Construct the full path to the data file
data_dir = current_dir / "models"
data_dir.mkdir(exist_ok=True)   # make sure 'data' exists
data_path = data_dir / f"{model_name}.pkl.gz"

# Load if exists, otherwise generate and save
if data_path.exists():
    with open(data_path, "rb") as f:
        kerr_cat_idx_arr = pickle.load(f)
    print(f"Loaded array for model '{model_name}' from file.")
else:   
    hamiltonian = Hamiltonian(f'{model_name}', 1, sw_order=1, max_order=4)
    hamiltonian.add_freqs_condition([2],[1])# the condition 2*\omega^prime=omega_d is ensured 
    kerr_cat_idx_arr =  hamiltonian.build_model(FINAL_MONOMS.values(), recalculate=False)
    with open(data_path, "wb") as f:
        pickle.dump(kerr_cat_idx_arr, f)




# def setparams(omega_d_l=0):

#     global omega_d;
    
#     if(omega_d_l!=0):
#         omega_d=omega_d_l




def effective_hamiltonian_coeff_to_latex(idx_arr, omega0sp, omegadsp):
    """
    

    Parameters
    ----------
    idx_arr : TYPE
        DESCRIPTION.
    omega0sp : TYPE
        DESCRIPTION.
    omegadsp : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    sympy_terms = []

    # Keep track of symbols already defined to avoid redefining
    defined_symbols = {}

    for elem in idx_arr:
        # Build the factors for this term
        factors = []

        # Create or reuse symbols for each C_{n,l,p}
        for indices in elem[1:]:
            n, l = int(indices[0][0][0]), int(indices[0][0][1])
            p = int(indices[1][0])
            name = f"C_{n}_{l}_{p}"

            if name not in defined_symbols:
                defined_symbols[name] = sp.symbols(name)
            factors.append(defined_symbols[name])

        # Handle the function/expression
        expr = sp.simplify(elem[0](omega0sp, omegadsp))

        factors.append(expr)

        # Multiply all factors
        term_expr = sp.Mul(*factors)
        sympy_terms.append(term_expr)

    # Sum all terms
    total_expr = sp.Add(*sympy_terms)

    # Convert to LaTeX
    latex_str = sp.latex(total_expr)
    return latex_str, total_expr

        
def effective_hamiltonian_coeff(idx_arr, model, Pi, phi_zpf_l, omega_0, omega_d):
    """
    Compute the coefficient for a given monomial of the effective Hamiltonian
    
    Parameters:
    idx(list):              symbolic array representing parametric amplitude in terms of supercoefficients from SW procedure
    mode_indices (list):    Indices defining the monimial. 
    Pi :                    effective drive amplitudes
    phi_zpf_l:              zero-point flictuations of the phase
    omega_0:                quantum mode frequency
    omega_d:                drive mode frequencies
    
    Returns:
     Effective Hamiltonian coefficient
    
    """
    
    freq_values = np.concatenate((as_array(omega_0), as_array(omega_d)))

    
    terms = []
    res = 0.
    
    for i in range(len(idx_arr)):   
        
        for elem in idx_arr[i]:

            prefactor = elem[0](*freq_values)
            
            
            supercoeff_prod = 1.0
            for k in range(1, len(elem)):
                term = get_or_compute_cnlp(model,elem[k][0], elem[k][1], Pi, phi_zpf_l)

                supercoeff_prod *= term


            res+=prefactor * supercoeff_prod

            
            
    return res


def get_or_compute_cnlp(model,mode_indices_nl, drive_indices, Pi, phi_zpf_l):
    # key = self._make_cnlp_key(mode_indices_nl, drive_indices)
    key = mode_indices_nl, drive_indices
    n, l = mode_indices_nl[0]
    p = drive_indices[0]
    return Cnlp(model, Pi, n,l, p, phi_zpf_l)



def eps2_order_1_all(model, Pi, phi_zpf_l, omega_d): # eps2 second order Shriffer-Wolff corrections
    """
    

    Parameters
    ----------
    Pi :                    effective drive amplitude
    phi_zpf_l:              zero-point flictuations of the phase
    omega_d:                drive mode frequency

    Returns
    -------
    First-order correction for two-photon squeezing parametric amplitude

    """
    return effective_hamiltonian_coeff([kerr_cat_idx_arr[FINAL_MONOMS["2PH_SQUEEZING"]][1]],model, Pi, phi_zpf_l, omega_d/2, omega_d)
    # eps2_2_all = (-2*Cnlp_all(model,Pi,0, 1, 1,phi_zpf_l)*Cnlp_all(model,Pi,0, 3, 0,phi_zpf_l) 
    #               - 6*Cnlp_all(model,Pi,0, 1, 0,phi_zpf_l)*Cnlp_all(model,Pi,0, 3, 1,phi_zpf_l) 
    #               - 6*Cnlp_all(model,Pi,0, 1, 2,phi_zpf_l)*Cnlp_all(model,Pi,0, 3, 1,phi_zpf_l)/5 
    #               - 6*Cnlp_all(model,Pi,0, 2, 1,phi_zpf_l)*Cnlp_all(model,Pi,0, 4, 0,phi_zpf_l) 
    #               - 2*Cnlp_all(model,Pi,0, 2, 0,phi_zpf_l)*Cnlp_all(model,Pi,1, 0, 1,phi_zpf_l) 
    #               + 2*Cnlp_all(model,Pi,0, 2, 2,phi_zpf_l)*Cnlp_all(model,Pi,1, 0, 1,phi_zpf_l) 
    #               - Cnlp_all(model,Pi,0, 2, 1,phi_zpf_l)*Cnlp_all(model,Pi,1, 0, 2,phi_zpf_l) 
    #               +  2*Cnlp_all(model,Pi,0, 1, 1,phi_zpf_l)*Cnlp_all(model,Pi,1, 1, 0,phi_zpf_l) 
    #               - 12*Cnlp_all(model,Pi,0, 3, 1,phi_zpf_l)*Cnlp_all(model,Pi,1, 1, 0,phi_zpf_l)
    #               - 2*Cnlp_all(model,Pi,0, 1, 0,phi_zpf_l)*Cnlp_all(model,Pi,1, 1, 1,phi_zpf_l)
    #               + 2*Cnlp_all(model,Pi,0, 1, 2,phi_zpf_l)*Cnlp_all(model,Pi,1, 1, 1,phi_zpf_l)/3 
    #               - 4*Cnlp_all(model,Pi,0, 3, 0,phi_zpf_l)*Cnlp_all(model,Pi,1, 1, 1,phi_zpf_l))/(omega_d) #*[(a**+a**+)+a*a,1) Squeezing
    # return eps2_2_all

def K_order_1_all(model, Pi,phi_zpf_l, omega_d): # K second order Shriffer-Wolff corrections
    # K2_all = -(-6*Cnlp_all(model,Pi,0, 3, 0,phi_zpf_l)**2 - 108*Cnlp_all(model,Pi,0, 3, 1,phi_zpf_l)**2/5 - 36*Cnlp_all(model,Pi,0, 4, 0,phi_zpf_l)**2
    #            - 6*Cnlp_all(model,Pi,1, 1, 0,phi_zpf_l)**2 + 4*Cnlp_all(model,Pi,1, 1, 1,phi_zpf_l)**2 
    #            - 12*Cnlp_all(model,Pi,0, 2, 0,phi_zpf_l)*Cnlp_all(model,Pi,1, 2, 0,phi_zpf_l) - 18*Cnlp_all(model,Pi,1, 2, 0,phi_zpf_l)**2)/(omega_d) #*a**+a**+aa  Kerr
    # return K2_all
    return -effective_hamiltonian_coeff([kerr_cat_idx_arr[FINAL_MONOMS["KERR"]][1]], model, Pi, phi_zpf_l, omega_d/2, omega_d)
    

def delta_order_1_all(model, Pi,phi_zpf_l, omega_d):# detuning second order Shriffer-Wolff corrections
    return effective_hamiltonian_coeff([kerr_cat_idx_arr[FINAL_MONOMS["DETUNING"]][1]], model, Pi, phi_zpf_l, omega_d/2, omega_d)
    # Delta_drive2 = (-4*Cnlp_all(model,Pi,0, 2, 0,phi_zpf_l)**2 
    #                 - 2*Cnlp_all(model,Pi,0, 2, 1,phi_zpf_l)**2 
    #                 + 8*Cnlp_all(model,Pi,0, 2, 2,phi_zpf_l)**2/3 
    #                 - 12*Cnlp_all(model,Pi,0, 3, 0,phi_zpf_l)**2 
    #                 - 216*Cnlp_all(model,Pi,0, 3, 1,phi_zpf_l)**2/5 
    #                 - 48*Cnlp_all(model,Pi,0, 4, 0,phi_zpf_l)**2
    #                 - 8*Cnlp_all(model,Pi,0, 1, 0,phi_zpf_l)*Cnlp_all(model,Pi,1, 1, 0,phi_zpf_l) 
    #                 -    4*Cnlp_all(model,Pi,1, 1, 0,phi_zpf_l)**2 
    #                 + 16*Cnlp_all(model,Pi,0, 1, 1,phi_zpf_l)*Cnlp_all(model,Pi,1, 1, 1,phi_zpf_l)/3 
    #                 + 8*Cnlp_all(model,Pi,1, 1, 1,phi_zpf_l)**2/3 
    #                 - 12*Cnlp_all(model,Pi,0, 2, 0,phi_zpf_l)*Cnlp_all(model,Pi,1, 2, 0,phi_zpf_l) 
    #                 - 6*Cnlp_all(model,Pi,1, 2, 0,phi_zpf_l)**2)/omega_d #*a**+*a Detuning
    # return Delta_drive2

def eps2_order_1_sum(model, Pi,phi_zpf_l, omega_d): # eps2 second order Shriffer-Wolff corrections
    return effective_hamiltonian_coeff([kerr_cat_idx_arr[FINAL_MONOMS["2PH_SQUEEZING"]][1]], model, Pi, phi_zpf_l, omega_d/2, omega_d)
    # eps2_2_sum = (-2*Cnlp_sum(model, Pi,0, 1, 1,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,0, 3, 0,phi_zpf_l,maxorder) 
    #               - 6*Cnlp_sum(model, Pi,0, 1, 0,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,0, 3, 1,phi_zpf_l,maxorder) 
    #               - 6*Cnlp_sum(model, Pi,0, 1, 2,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,0, 3, 1,phi_zpf_l,maxorder)/5 
    #               - 6*Cnlp_sum(model, Pi,0, 2, 1,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,0, 4, 0,phi_zpf_l,maxorder) 
    #               - 2*Cnlp_sum(model, Pi,0, 2, 0,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 0, 1,phi_zpf_l,maxorder) 
    #               + 2*Cnlp_sum(model, Pi,0, 2, 2,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 0, 1,phi_zpf_l,maxorder) 
    #               - Cnlp_sum(model, Pi,0, 2, 1,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 0, 2,phi_zpf_l,maxorder) 
    #               + 2*Cnlp_sum(model, Pi,0, 1, 1,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 1, 0,phi_zpf_l,maxorder) 
    #               - 12*Cnlp_sum(model, Pi,0, 3, 1,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 1, 0,phi_zpf_l,maxorder)
    #               - 2*Cnlp_sum(model, Pi,0, 1, 0,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 1, 1,phi_zpf_l,maxorder) 
    #               + 2*Cnlp_sum(model, Pi,0, 1, 2,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 1, 1,phi_zpf_l,maxorder)/3 
    #               - 4*Cnlp_sum(model, Pi,0, 3, 0,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 1, 1,phi_zpf_l,maxorder))/omega_d #*[(a**+a**+)+a*a,1,maxorder) Squeezing

    # return eps2_2_sum




def K_order_1_sum(model,Pi,phi_zpf_l, omega_d): # K first order Shriffer-Wolff corrections
    # K2_sum = -(-6*Cnlp_sum(model, Pi,0, 3, 0,phi_zpf_l,maxorder)**2 - 108*Cnlp_sum(model, Pi,0, 3, 1,phi_zpf_l,maxorder)**2/5 
    #            - 36*Cnlp_sum(model, Pi,0, 4, 0,phi_zpf_l,maxorder)**2 - 6*Cnlp_sum(model, Pi,1, 1, 0,phi_zpf_l,maxorder)**2 
    #            + 4*Cnlp_sum(model, Pi,1, 1, 1,phi_zpf_l,maxorder)**2 
    #            - 12*Cnlp_sum(model, Pi,0, 2, 0,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 2, 0,phi_zpf_l,maxorder) 
    #            - 18*Cnlp_sum(model, Pi,1, 2, 0,phi_zpf_l,maxorder)**2)/omega_d #*a**+a**+aa  Kerr
    # # print('K_order_1_sum:', K2_sum, effective_hamiltonian_coeff([kerr_cat_idx_arr[FINAL_MONOMS["KERR"]][1]], Pi, phi_zpf_l, omega_d/2, omega_d,  max_order=maxorder) )
    # return K2_sum
    return -effective_hamiltonian_coeff([kerr_cat_idx_arr[FINAL_MONOMS["KERR"]][1]], model, Pi, phi_zpf_l, omega_d/2, omega_d)


def delta_order_1_sum(model, Pi,phi_zpf_l, omega_d):# detuning first order Shriffer-Wolff corrections
    return effective_hamiltonian_coeff([kerr_cat_idx_arr[FINAL_MONOMS["DETUNING"]][1]], model, Pi, phi_zpf_l, omega_d/2, omega_d)
    # Delta_drive2_sum = (-4*Cnlp_sum(model, Pi,0, 2, 0,phi_zpf_l,maxorder)**2 
    #                     - 2*Cnlp_sum(model, Pi,0, 2, 1,phi_zpf_l,maxorder)**2 
    #                     + 8*Cnlp_sum(model, Pi,0, 2, 2,phi_zpf_l,maxorder)**2/3 
    #                     - 12*Cnlp_sum(model, Pi,0, 3, 0,phi_zpf_l,maxorder)**2
    #                     - 216*Cnlp_sum(model, Pi,0, 3, 1,phi_zpf_l,maxorder)**2/5 
    #                     - 48*Cnlp_sum(model, Pi,0, 4, 0,phi_zpf_l,maxorder)**2 
    #                     - 8*Cnlp_sum(model, Pi,0, 1, 0,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 1, 0,phi_zpf_l,maxorder) 
    #                     - 4*Cnlp_sum(model, Pi,1, 1, 0,phi_zpf_l,maxorder)**2 
    #                     + 16*Cnlp_sum(model, Pi,0, 1, 1,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 1, 1,phi_zpf_l,maxorder)/3 
    #                     + 8*Cnlp_sum(model, Pi,1, 1, 1,phi_zpf_l,maxorder)**2/3 
    #                     - 12*Cnlp_sum(model, Pi,0, 2, 0,phi_zpf_l,maxorder)*Cnlp_sum(model, Pi,1, 2, 0,phi_zpf_l,maxorder) 
    #                     -  6*Cnlp_sum(model, Pi,1, 2, 0,phi_zpf_l,maxorder)**2)/(omega_d) #*a**+*a Detuning
    # return Delta_drive2_sum



def calculate_omega_d(model, Pi, phi_zpf_l):
    c2 = model.cn_arr[2]#cn_S_arr_opt(M, xJ, N, alpha, phi_ext, 2, ra=asym_arr[0], rb=asym_arr[1])
    omega_0 = 2*phi_zpf_l**2*model.energy_jj*c2
    if(model.withDelta):   
        Delta_drive2_all = delta_order_1_all(model,Pi,phi_zpf_l, omega_d*(omega_0+Cnlp_all(model,Pi,1, 0, 0,phi_zpf_l)))
        return omega_d*(omega_0+Cnlp_all(model,Pi,1, 0, 0,phi_zpf_l)+Delta_drive2_all)     
    return omega_d*omega_0
   
    

def calculate_omega_d_sum(model, Pi, phi_zpf_l):
    c2 = model.cn_arr[2]#cn_S_arr_opt(M, xJ, N, alpha, phi_ext, 2, ra=asym_arr[0], rb=asym_arr[1])
    omega_0 = 2*phi_zpf_l**2*model.energy_jj*c2
    if(model.withDelta):
        Delta_drive2_sum = delta_order_1_sum(model, Pi,phi_zpf_l, omega_d*(omega_0+Cnlp(model,Pi,1, 0, 0,phi_zpf_l)))
        return omega_d*(omega_0+Cnlp(model, Pi,1, 0, 0,phi_zpf_l)+Delta_drive2_sum)
    return omega_d*omega_0



def size_full(model,x, phi_zpf_l):
    # global Pi;
    delta=0
    n_zpf_inv = 2*phi_zpf_l
    res  = np.zeros(len(x))
    for i in range(0, len(x)):        
        Pi=x[i]*n_zpf_inv
        
        if(model.withDelta):
            Delta_drive2_full = delta_order_1_all(model, Pi, phi_zpf_l, calculate_omega_d(model, Pi, phi_zpf_l))
            delta = (Cnlp_all(model,Pi,1, 0, 0,phi_zpf_l)+Delta_drive2_full) 
        K1_all = -Cnlp_all(model,Pi,2, 0, 0,phi_zpf_l)
        eps2_1_all = Cnlp_all(model,Pi,0, 2, 1,phi_zpf_l)
        # Delta_drive2_all = delta_order_1_all(model, Pi,phi_zpf_l, omega_d*phi_zpf_l**2)
        omega_d_l  = calculate_omega_d(model, Pi, phi_zpf_l)
        eps2_2_all = eps2_order_1_all(model, Pi,phi_zpf_l, omega_d_l)
        K2_all = K_order_1_all(model, Pi,phi_zpf_l, omega_d_l)
        #print(K2_all)
        res[i]=(eps2_1_all+eps2_2_all+0.5*delta)/(K1_all+K2_all)
    return res

def size_sum(model,x,phi_zpf_l):
    #TODO only works with 2-node Kerr-cat

    delta=0
    n_zpf_inv = 2*phi_zpf_l
    res  = np.zeros(len(x))
    for i in range(0, len(x)):
        
        Pi=x[i]*n_zpf_inv
        if(model.withDelta):
            Delta_drive2_sum = delta_order_1_sum(model,Pi, phi_zpf_l, calculate_omega_d_sum(model,x, phi_zpf_l))
            delta = (Cnlp(model,Pi,1, 0, 0,phi_zpf_l)+Delta_drive2_sum)
        # Delta_drive2_sum = delta_order_1_sum(model, Pi,phi_zpf_l, omega_d*phi_zpf_l**2,maxorder)
        omega_d_l  = calculate_omega_d_sum(model,Pi, phi_zpf_l)
        K2_sum = K_order_1_sum(model,Pi,phi_zpf_l, omega_d_l)
        eps2_2sum = eps2_order_1_sum(model,Pi,phi_zpf_l, omega_d_l)
        res[i]=(Cnlp(model,Pi,0, 2, 1,phi_zpf_l)+eps2_2sum+0.5*delta)/(-Cnlp(model,Pi,2, 0, 0,phi_zpf_l)+K2_sum)
    return res



# def size_approx(model,x,phi_zpf_l):
#     # global Pi;
#     # global cn_arr;
#     # cn_arr = cn_S_arr_holder(M, xJ, N, alpha, phi_ext, 4)
#     delta=0
#     n_zpf_inv = 2*phi_zpf_l
#     res  = np.zeros(len(x))
#     for i in range(0, len(x)):
#         Pi=x[i]*n_zpf_inv
# #         print('Pi: ', Pi)
#         if(model.withDelta):            
#             delta = Cnlp_sum(model, Pi,1, 0, 0,phi_zpf_l,4)
#         omega_d_l = calculate_omega_d_sum(model, Pi, phi_zpf_l,4)
#         res[i]=(Cnlp_sum(model, Pi,0, 2, 1,phi_zpf_l,4)+0.5*delta)/(-Cnlp_sum(model, Pi,2, 0, 0,phi_zpf_l,4)+(6*Cnlp_sum(model, Pi,0, 3, 0,phi_zpf_l,4)**2+6*Cnlp_sum(model, Pi,1, 1, 0,phi_zpf_l,4)**2)/omega_d_l)
#     return res

def K_full(model,x,phi_zpf_l):
    # global Pi;
    global cn_arr;
    n_zpf_inv = 2*phi_zpf_l
    res  = np.zeros(len(x))
    # c2 = cn_arr[2]
    for i in range(0, len(x)):
        
        Pi=x[i]*n_zpf_inv
        K1_all = -Cnlp_all(model,Pi,2, 0, 0,phi_zpf_l)   
        # Delta_drive2_all = delta_order_1_all(model, Pi,phi_zpf_l, omega_d*phi_zpf_l**2)
        omega_d_l  = calculate_omega_d(model, Pi, phi_zpf_l)     
        K2_all = K_order_1_all(model, Pi,phi_zpf_l, omega_d_l)        
#         print(K1_all*energy_jj*c2,K2_all*energy_jj*c2)
        res[i]=K1_all+K2_all

    return res

def K_sum(model,x,phi_zpf_l):
    # global Pi;
    # global cn_arr;
    # cn_arr = cn_S_arr_holder(M, xJ, N, alpha, phi_ext, maxorder)
    # c2 = cn_arr[2]
    n_zpf_inv = 2*phi_zpf_l
    res  = np.zeros(len(x))
#     print('In K:', M, xJ, N, alpha, phi_ext,phi_zpf_l )
    for i in range(0, len(x)):
        
        Pi=x[i]*n_zpf_inv
        
        # Delta_drive2_sum = delta_order_1_sum(model, Pi,phi_zpf_l, omega_d*phi_zpf_l**2)
        omega_d_l  = calculate_omega_d_sum(model, Pi, phi_zpf_l)
        K2_sum = K_order_1_sum(model,Pi,phi_zpf_l, omega_d_l)
        
        res[i]=(-Cnlp(model,Pi,2, 0, 0,phi_zpf_l)+K2_sum)
#         print('In K2:',Cnlp_sum(2, 0, 0,phi_zpf_l,maxorder),K2_sum )
    
    return res




# def K_approx(model,x,phi_zpf_l):
#     # global Pi;
#     # global cn_arr;
#     # cn_arr = cn_S_arr_holder(M, xJ, N, alpha, phi_ext, 4)
#     # c2 = cn_arr[2]
#     n_zpf_inv = 2*phi_zpf_l
#     res  = np.zeros(len(x))
#     for i in range(0, len(x)):
#         Pi=x[i]*n_zpf_inv
#         omega_d_l  = calculate_omega_d_sum(model, Pi, phi_zpf_l,4)        
       
#         res[i]=(-Cnlp_sum(model, Pi,2, 0, 0,phi_zpf_l,4)+(6*Cnlp_sum(model, Pi,0, 3, 0,phi_zpf_l,4)**2 + 6*Cnlp_sum(model, Pi,1, 1, 0,phi_zpf_l,4)**2)/omega_d_l)

#     return res 

def eps2_full(model,x,phi_zpf_l):
    res  = np.zeros(len(x))
    n_zpf_inv = 2*phi_zpf_l
    for i in range(0, len(x)):
        
        Pi=x[i]*n_zpf_inv

        omega_d_l  = calculate_omega_d(model, Pi, phi_zpf_l) 
        eps2_2_all = eps2_order_1_all(model, Pi,phi_zpf_l, omega_d_l)
        res[i]=(Cnlp_all(model,Pi,0, 2, 1,phi_zpf_l)+eps2_2_all)
        
    return res 


def eps2_sum(model,x,phi_zpf_l):

    res  = np.zeros(len(x))
    n_zpf_inv = 2*phi_zpf_l
    for i in range(0, len(x)):
        
        Pi=x[i]*n_zpf_inv
            

        omega_d_l  = calculate_omega_d_sum(model, Pi, phi_zpf_l) 
        eps2_2sum = eps2_order_1_sum(model, Pi,phi_zpf_l, omega_d_l)
        res[i]=(Cnlp(model, Pi,0, 2, 1,phi_zpf_l)+eps2_2sum)
              
    return res 

def eps2_approx(model, x,phi_zpf_l):
    # global Pi;
    global cn_arr;
    # cn_arr = cn_S_arr_holder(M, xJ, N, alpha,asym_arr[0], asym_arr[1], phi_ext, 4)
    # c2 = cn_arr[2]
    n_zpf_inv = 2*phi_zpf_l
    res  = np.zeros(len(x))
    for i in range(0, len(x)):
        # print(phi_zpf_l)
        Pi=x[i]*n_zpf_inv
        # print(Pi)
        res[i]=Cnlp_sum(model, Pi,0, 2, 1,phi_zpf_l,4)
        
    return res 

def delta_sum(model,x,phi_zpf_l):

    delta=0
    res  = np.zeros(len(x))
    n_zpf_inv = 2*phi_zpf_l
    for i in range(0, len(x)):
        
        Pi=x[i]*n_zpf_inv
        Delta_drive2_sum = delta_order_1_sum(model, Pi, phi_zpf_l, calculate_omega_d_sum(model, Pi, phi_zpf_l))
        delta = (Cnlp(model, Pi,1, 0, 0,phi_zpf_l)+Delta_drive2_sum)
        # Delta_drive2_sum = delta_order_1_sum(phi_zpf_l, omega_d*phi_zpf_l**2)
#         omega_d_l  = omega_d*phi_zpf_l**2#-Cnlp_sum(1, 0, 0,phi_zpf_l,maxorder)+Delta_drive2_sum        
#         eps2_2sum = eps2_order_1_sum(phi_zpf_l, omega_d_l)        
        res[i]=delta+Delta_drive2_sum        
              
    return res
def delta_approx(model,x,phi_zpf_l):
    
    res  = np.zeros(len(x))
    n_zpf_inv = 2*phi_zpf_l
    for i in range(0, len(x)):

        Pi=x[i]*n_zpf_inv
        res[i]=Cnlp_sum(model, Pi, 1, 0, 0,phi_zpf_l,4)
    return res 




############################################################
########    Optimization of Kerr-cat parameters   ##########
############################################################

def phi_ext_for_K_zero(model:Circuit, K=0):
    def temp(x):
        # global phi_ext;
        # global cn_arr;
        model.phi_ext=x
        model.update_cn_arr(forceorder=9)
        cn_arr = model.cn_arr
        c2 = cn_arr[2]
        phi_zpf = np.power(2*model.energy_c_large/(model.energy_jj*c2), 0.25)
        return K_sum(model,[1.],phi_zpf)-K

    if(np.sign(temp(0.001))==np.sign(temp(0.5))):
        return -1.
    res =  brentq(temp, 0.001,0.5)
    return res





def size_max(model:Circuit):# returns max positive kerr nnoninearity value for particular scheme

    energy_c_large = model.energy_c_large
    energy_jj = model.energy_jj
   
    Pi_l=0.5
    th_e = np.linspace(0.0001,0.5,25)
    out = np.zeros((len(th_e)+1,2))    
    idx=0
    phiK0 = phi_ext_for_K_zero(model) # ORDER 8, intial guess where to look for sought Kerr nonlinearity maximum
    for th_ext in th_e: 
        model.phi_ext = th_ext
        model.update_cn_arr()
        cn_arr = model.cn_arr
        c2 = cn_arr[2]
#         asym_drive()
        phi_zpf = np.power(2*energy_c_large/(energy_jj*c2), 0.25)
#         if(np.abs(K_sum([1.],phi_zpf))*1e3<Klim):
#             continue
        temp = np.abs(size_sum(model,[Pi_l],phi_zpf))[0]#energy_jj*c2*Cnlp_sum(2, 0, 0,phi_zpf*np.sqrt(2),8)#        
        out[idx,0] = temp #K 
        out[idx,1] = th_ext #K
        # print('size, phi_ext:',out[idx,0],out[idx,1])
        idx = idx+1
    if(phiK0>0):
        model.phi_ext = phiK0
        model.update_cn_arr()
        cn_arr = model.cn_arr
        c2 = cn_arr[2]
        phi_zpf = np.power(2*energy_c_large/(energy_jj*c2), 0.25)
        out[-1,0] =  np.abs(size_sum(model,[Pi_l],phi_zpf))[0] #K 
        out[-1,1] = phiK0 #K    
    # max_size = max(out[:,0])
    index_max = out[:,0].argmax()#tolist().index(max(max_size))
    return out[index_max,0],out[index_max,1]



def maxSize_opt2(model:Circuit,phi_e_max):# returns max positive kerr nnoninearity value for particular scheme
   
    # global phi_ext;
    # global cn_arr;
    model.phi_ext=phi_e_max
    model.update_cn_arr()
    energy_c_large = model.energy_c_large
    energy_jj = model.energy_jj
    intv = 0.000005
    Pi_l = 0.5
    
    print('alpha:',model.alpha,'xJ:',model.xJ,'M:',model.M,'N:',model.N)
    

    # Code to be timed
#     phiK0 = phi_ext_for_K_zero()
    out = np.zeros((2,2))
    cn_arr = model.cn_arr
    c2 = cn_arr[2]
#     print('c2: ',c2)
    phi_zpf_l = np.power(2*energy_c_large/(energy_jj*c2), 0.25)
#     K0=K_sum([0.0001],phi_zpf_l)
    K=K_sum(model,[Pi_l],phi_zpf_l)[0]
    if(abs(K*1e3)>=Klim):
        return np.abs(size_sum(model,[Pi_l],phi_zpf_l)[0]), model.phi_ext

    #positive K
    
    
    count=0
    while (abs(K*1e3)<Klim):
        
        phi_ext=model.phi_ext+intv
        
        if((phi_ext<0.) or (phi_ext>0.5)):
            phi_ext=phi_ext-intv
            break
        model.phi_ext= phi_ext
        model.update_cn_arr()
        cn_arr = model.cn_arr
        c2 = cn_arr[2]
        phi_zpf_l = np.power(2*energy_c_large/(energy_jj*c2), 0.25)
        K2 = K_sum(model,[Pi_l],phi_zpf_l)[0]
        diff = abs(K2-K)
        if(diff*1e3<0.125*Klim):
            intv=intv*2
        elif(diff*1e3>0.25*Klim):
            intv=intv/1.5
        K=K2    
        count=count+1
    temp = np.abs(size_sum(model,[Pi_l],phi_zpf_l)[0])

    print(model.phi_ext,count, temp,K,phi_zpf_l, 2*energy_jj*c2*phi_zpf_l**2)
    
    out[0,0]=temp if (abs(K*1e3)>=Klim) else 0
    out[0,1]=model.phi_ext
    
    #negative K
    #RESET local vars
    model.phi_ext=phi_e_max
    K=0
    count=0
    intv = 0.000005
    while (abs(K*1e3)<Klim):
#         print(phi_ext)
        phi_ext=model.phi_ext-intv 
#         print(phi_ext)
        if((phi_ext<0.) or (phi_ext>0.5)):
            phi_ext=phi_ext+intv
            break
        model.phi_ext=phi_ext
        model.update_cn_arr()
        cn_arr = model.cn_arr
        c2 = cn_arr[2]
        phi_zpf_l = np.power(2*energy_c_large/(energy_jj*c2), 0.25)
        K2 = K_sum(model,[Pi_l],phi_zpf_l)[0]
        diff = abs(K2-K)
        if(diff*1e3<0.125*Klim):
            intv=intv*2
        elif(diff*1e3>0.25*Klim):
            intv=intv/1.5
        K=K2
        count=count+1
    temp = np.abs(size_sum(model,[Pi_l],phi_zpf_l)[0])

    print(model.phi_ext,count, temp,K,phi_zpf_l, 2*energy_jj*c2*phi_zpf_l**2)
    
    out[1,0]=temp if (abs(K*1e3)>=Klim) else 0
    out[1,1]=model.phi_ext


    index_max = out[:,0].argmax()
    return out[index_max,0],out[index_max,1]




    
def maxsize2(model:Circuit, alpha, xJ):
    model.alpha=alpha
    model.xJ=xJ
    model.update_cn_arr()
    # print('model.cn_arr:', len(model.cn_arr), model.cn_arr)
    # model.print()
    max_size, phi_e_max = size_max(model)
    print('Max size and its phi_ext:', max_size, phi_e_max)
    return maxSize_opt2(model,phi_e_max)

        
vmaxSize = np.vectorize(pyfunc=maxsize2,otypes=[float,float])


############################################################
########    Optimization of beam-splitter interaction parameters   ##########
############################################################



def g_BS(x,omega_a,omega_b,omega_d,phi_zpf_arr):
    # c2=cn_arr[2]
    limit=0.2
    delta = (omega_a+omega_b-2*omega_d)/2/pi+Cnlp_MN_3modes(1,0,0,0,0,0,0,phi_zpf_arr,x)+\
        -2*pi*(4*Cnlp_MN_3modes(0,1,0,0,0,0,0,phi_zpf_arr,x)*Cnlp_MN_3modes(1,1,0,0,0,0,0,phi_zpf_arr,x)/omega_a\
        +2*Cnlp_MN_3modes(1,1,0,0,0,0,0,phi_zpf_arr,x)**2/(omega_a)\
        +(4*Cnlp_MN_3modes(0,1,0,0,0,0,1,phi_zpf_arr,x)*Cnlp_MN_3modes(1,1,0,0,0,0,1,phi_zpf_arr,x)+\
          2*Cnlp_MN_3modes(1,1,0,0,0,0,1,phi_zpf_arr,x)**2)*(1/(omega_a - omega_d)+1/(omega_a + omega_d)))       
        # +4*Cnlp_MN_3modes(0,1,0,0,0,0,2,phi_zpf_arr,x)*Cnlp_MN_3modes(1,1,0,0,0,0,2,phi_zpf_arr,x)*(1/(omega_a-2*omega_d)+1/(omega_a+2*omega_d))\
        # +2*Cnlp_MN_3modes(1,1,0,0,0,0,2,phi_zpf_arr,x)**2*(1/(omega_a - 2*omega_d)+1/(omega_a + 2*omega_d))
        # +4*Cnlp_MN_3modes(0,1,0,0,0,0,3,phi_zpf_arr,x)*Cnlp_MN_3modes(1,1,0,0,0,0,3,phi_zpf_arr,x)*(1/(omega_a - 3*omega_d)+1/(omega_a + 3*omega_d))\
        # +2*Cnlp_MN_3modes(1,1,0,0,0,0,3,phi_zpf_arr,x)**2*(1/(omega_a - 3*omega_d)+1/(omega_a + 3*omega_d))) 


    if(np.abs(2*omega_a - omega_d)/2/pi<limit or np.abs(omega_a - 2*omega_d)/2/pi<limit or np.abs(omega_a - 3*omega_d)/2/pi<limit):
        return 0.
    g_bc = Cnlp_MN_3modes(0,0,0,1,0,1,1,phi_zpf_arr,x)
    g_ab = Cnlp_MN_3modes(0,1,0,1,0,0,2,phi_zpf_arr,x)\
        -2*pi*(Cnlp_MN_3modes(0,1,0,1,0,0,2,phi_zpf_arr,x)*Cnlp_MN_3modes(0,2,0,0,0,0,0,phi_zpf_arr,x)/omega_a\
        +2*Cnlp_MN_3modes(0,1,0,1,0,0,1,phi_zpf_arr,x)*Cnlp_MN_3modes(0,2,0,0,0,0,1,phi_zpf_arr,x)/(2*omega_a - omega_d)\
        +Cnlp_MN_3modes(0,1,0,1,0,0,0,phi_zpf_arr,x)*Cnlp_MN_3modes(0,2,0,0,0,0,2,phi_zpf_arr,x)/(omega_a - 2*omega_d)\
        +2*Cnlp_MN_3modes(0,1,0,0,0,0,2,phi_zpf_arr,x)*Cnlp_MN_3modes(0,2,0,1,0,0,0,phi_zpf_arr,x)/(omega_a + 2*omega_d)\
        +2*Cnlp_MN_3modes(0,1,0,0,0,0,1,phi_zpf_arr,x)*Cnlp_MN_3modes(0,2,0,1,0,0,1,phi_zpf_arr,x)/(omega_a + omega_d)\
        +Cnlp_MN_3modes(0,1,0,1,0,0,1,phi_zpf_arr,x)*Cnlp_MN_3modes(1,0,0,0,0,0,1,phi_zpf_arr,x)/omega_d\
        +Cnlp_MN_3modes(0,1,0,0,0,0,2,phi_zpf_arr,x)*Cnlp_MN_3modes(1,0,0,1,0,0,0,phi_zpf_arr,x)/(omega_a - 2*omega_d)\
        +Cnlp_MN_3modes(0,1,0,0,0,0,1,phi_zpf_arr,x)*Cnlp_MN_3modes(1,0,0,1,0,0,1,phi_zpf_arr,x)/(omega_a - omega_d))

    g_ac = Cnlp_MN_3modes(0,1,0,0,0,1,3,phi_zpf_arr,x)\
        -2*pi*(2*Cnlp_MN_3modes(0,1,0,0,0,1,2,phi_zpf_arr,x)*Cnlp_MN_3modes(0,2,0,0,0,0,1,phi_zpf_arr,x)/(2*omega_a-omega_d)\
        +Cnlp_MN_3modes(0,1,0,0,0,1,1,phi_zpf_arr,x)*Cnlp_MN_3modes(0,2,0,0,0,0,2,phi_zpf_arr,x)/(omega_a - omega_d)\
        +2*Cnlp_MN_3modes(0,1,0,0,0,0,3,phi_zpf_arr,x)*Cnlp_MN_3modes(0,2,0,0,0,1,0,phi_zpf_arr,x)/(omega_a + 3*omega_d)\
        +2*Cnlp_MN_3modes(0,1,0,0,0,0,2,phi_zpf_arr,x)*Cnlp_MN_3modes(0,2,0,0,0,1,1,phi_zpf_arr,x)/(omega_a + 2*omega_d)\
        +Cnlp_MN_3modes(0,1,0,0,0,1,2,phi_zpf_arr,x)*Cnlp_MN_3modes(1,0,0,0,0,0,1,phi_zpf_arr,x)/omega_d\
        +Cnlp_MN_3modes(0,1,0,0,0,1,1,phi_zpf_arr,x)*Cnlp_MN_3modes(1,0,0,0,0,0,2,phi_zpf_arr,x)/(2*omega_d)\
        +Cnlp_MN_3modes(0,1,0,0,0,0,3,phi_zpf_arr,x)*Cnlp_MN_3modes(1,0,0,0,0,1,0,phi_zpf_arr,x)/(omega_a - 3*omega_d)\
        +Cnlp_MN_3modes(0,1,0,0,0,0,2,phi_zpf_arr,x)*Cnlp_MN_3modes(1,0,0,0,0,1,1,phi_zpf_arr,x)/(omega_a - 2*omega_d))

    if((np.abs(g_ab/delta)>0.25) or (np.abs(g_ac/delta)>0.25) or x>2.1):
        return -1.
    
    return (g_bc-2*g_ab*g_ac/delta)*1000 # in MHz


def chi_bc(x,omega_a,omega_d,phi_zpf_arr):
#     delta = (omega_a+omega_b-2*omega_d)/2/pi+Cnlp_all_MN_3modes(1,0,0,0,0,0,0,phi_zpf_arr,x)*energy_jj*c2
#     print('chi_bc', phi_ext)
    chi_bc_0 = Cnlp_MN_3modes(0,0,1,0,1,0,0,phi_zpf_arr,x)
    limit= 0.3
    if(np.abs(omega_a-5*omega_d)/2/pi<limit or np.abs(3*omega_a-5*omega_d)/2/pi<limit or np.abs(omega_a-omega_d)/2/pi<limit or np.abs(3*omega_a-5*omega_d)/2/pi<limit or np.abs(2*omega_a-3*omega_d)/2/pi<limit\
       or np.abs(omega_a-4*omega_d)/2/pi<limit or np.abs(3*omega_a-4*omega_d)/2/pi<limit or np.abs(3*omega_a-6*omega_d)/2/pi<limit or np.abs(omega_a-6*omega_d)/2/pi<limit):
        return 0.
       #  print(np.abs(omega_a-5*omega_d)/2/pi<limit, np.abs(3*omega_a-5*omega_d)/2/pi<limit, np.abs(omega_a-omega_d)/2/pi<limit, np.abs(3*omega_a-5*omega_d)/2/pi<limit, np.abs(2*omega_a-3*omega_d)/2/pi<limit,\
       # np.abs(omega_a-4*omega_d)/2/pi<limit, np.abs(3*omega_a-4*omega_d)/2/pi<limit, np.abs(3*omega_a-6*omega_d)/2/pi<limit) 
    chi_bc_1 =2*pi*(Cnlp_MN_3modes(0,1,0,1,0,1,0,phi_zpf_arr,x)**2*(1/(omega_a-5*omega_d)-1/(3*omega_a-5*omega_d)-1/(omega_a-omega_d)-1/(omega_a+omega_d))\
                -2*Cnlp_MN_3modes(0,1,0,0,0,1,0,phi_zpf_arr,x)*Cnlp_MN_3modes(0,1,1,0,0,1,0,phi_zpf_arr,x)*(1/(2*omega_a-3*omega_d)+1/(3*omega_d))\
                +Cnlp_MN_3modes(0,1,0,1,0,1,1,phi_zpf_arr,x)**2*(1/(omega_a-6*omega_d)-2/omega_a+1/(omega_a-4*omega_d)-1/(3*omega_a-4*omega_d)\
                                -4/(3*omega_a-6*omega_d)-1/(omega_a+2*omega_d))\
                -Cnlp_MN_3modes(0,1,0,1,0,0,0,phi_zpf_arr,x)*Cnlp_MN_3modes(0,1,0,1,1,0,0,phi_zpf_arr,x)*(1/(omega_a-omega_d)+1/(omega_d))\
                -2*Cnlp_MN_3modes(0,1,0,0,1,0,0,phi_zpf_arr,x)*Cnlp_MN_3modes(0,1,1,0,0,0,0,phi_zpf_arr,x)*(1/omega_a)\
                -2*Cnlp_MN_3modes(0,1,0,0,1,0,1,phi_zpf_arr,x)*Cnlp_MN_3modes(0,1,1,0,0,1,0,phi_zpf_arr,x)*(1/(omega_a-omega_d)+1/(omega_a+omega_d))
                )
                
    
    # print(chi_bc_0, chi_bc_1,Cnlp_MN_3modes(0,1,0,1,0,1,1,phi_zpf_arr,x),omega_d )            
    return (chi_bc_0+chi_bc_1)*1000000 #kHz




def as_array(x):
    """Convert float/int or tuple/list/ndarray into a 1D numpy array."""
    if isinstance(x, numbers.Real):   # float or int
        return np.array([x], dtype=float)
    else:
        return np.array(x, dtype=float)


