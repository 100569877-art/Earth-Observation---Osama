# CROSS VALIDATE L1B OUTPUTS EQUALIZED

# PLOT FROM YOUR OUTPUTS THE EQUALISED OUTPUT VERSUS NOT EQUALISED VERSUS THE TRUTH
# TRUTH = EODP-TS-L1B\input\ism_toa_isrf_VNIR-0.nc

# TO DO : Generate script that iterates and compares output files with each other ( Outputs-Output equalized-Output not equalized)
# EXPLAIN THE PLOT FIGURE 8_3 IN THE THEORY PDF , WHY BLACK LINE IS NOT BLUE LINE , THAT IS IN THE DELIVERABLE REPORT

# EXPLANATION GUIDELINE : AN INSTRUMENT IS A THING THAT RECORDS ENERGY , IN OUR CASE WE HAVE MLI MULTIBAND IMAGER , INCOMING LIGHT IN TELESPCPOE GETS THROUGH MIRRORS REACHES DETECTOR , WE ARE ACQUIRING INFO IN PARTS OF THE SPECTRUM , RECORDING INFO ,
# AND THEN WE HAVE THE DETECTION SYSTEM WHICH DIGITIZES AND RECORDS , OUR SYS IS NOT PERFECT , WE HAVE NO PERFECT FILTER , THERE ARE NOISES ,  IN ORDER TO UNDERSTAND HOW SYS BEHAVES WE CALIBRATE PERIODICALLY , BLUE LINE IS THE ACTUAL ENERGY THAT ARRIVES TO INSTRUMENT .
# IT IS THE TRUTH ^ . THE RED LINE IS THE ACTUAL OUTPUT IF YOU DO NOT CALIBRATE IMAGE , BLACK LINE IS THE RESPONSE IF YOU CALIBRATED OUTPUT. WE TRY TO GET AS CLOSE AS POSSIBLE TO TRUTH BUT THERE IS SLIGHT DELTA DIFFERENCE , IT DECLARES HOW MUCH SYS NOISE WE HAVE


# Example code : still not tested or even filled in.
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. FILE PATHS
# ============================================================

truth_file = r"C:\Users\Osama\Desktop\Earth Observation\EODP_TER_2021-20260910T154749Z-1-001\EODP_TER_2021\EODP-TS-L1B\input\ism_toa_isrf_VNIR-0.nc"

equalized_file = r"C:\Users\Osama\Desktop\Earth Observation\EODP_TER_2021-20260910T154749Z-1-001\EODP_TER_2021\EODP-TS-L1B\output\l1b_toa_eq_VNIR-0.nc"

not_equalized_file = r"C:\Users\Osama\Desktop\Earth Observation\EODP_TER_2021-20260910T154749Z-1-001\EODP_TER_2021\EODP-TS-L1B\output\l1b_toa_VNIR-0.nc"


# ============================================================
# 2. LOAD THE NETCDF FILES
# ============================================================

truth = xr.open_dataset(truth_file)
equalized = xr.open_dataset(equalized_file)
not_equalized = xr.open_dataset(not_equalized_file)


# ============================================================
# 3. SEE WHAT IS INSIDE THE FILES
# ============================================================

print("TRUTH:")
print(truth)

print("\nEQUALIZED:")
print(equalized)

print("\nNOT EQUALIZED:")
print(not_equalized)


# ============================================================
# 4. SELECT THE VARIABLE YOU WANT TO COMPARE
# ============================================================
# Replace "VARIABLE_NAME" with the actual variable name.

variable = "VARIABLE_NAME"

truth_data = truth[variable].values
equalized_data = equalized[variable].values
not_equalized_data = not_equalized[variable].values


# ============================================================
# 5. NUMERICAL COMPARISON
# ============================================================

# Difference from truth
error_equalized = equalized_data - truth_data
error_not_equalized = not_equalized_data - truth_data

# MAE
mae_equalized = np.mean(np.abs(error_equalized))
mae_not_equalized = np.mean(np.abs(error_not_equalized))

# RMSE
rmse_equalized = np.sqrt(np.mean(error_equalized**2))
rmse_not_equalized = np.sqrt(np.mean(error_not_equalized**2))

# Correlation
corr_equalized = np.corrcoef(
    truth_data.flatten(),
    equalized_data.flatten()
)[0, 1]

corr_not_equalized = np.corrcoef(
    truth_data.flatten(),
    not_equalized_data.flatten()
)[0, 1]


# ============================================================
# 6. PRINT RESULTS
# ============================================================

print("\n================ RESULTS ================")

print("\nEQUALIZED vs TRUTH")
print("MAE  :", mae_equalized)
print("RMSE :", rmse_equalized)
print("Correlation :", corr_equalized)

print("\nNOT EQUALIZED vs TRUTH")
print("MAE  :", mae_not_equalized)
print("RMSE :", rmse_not_equalized)
print("Correlation :", corr_not_equalized)


# ============================================================
# 7. PLOT
# ============================================================

plt.figure(figsize=(10, 6))

plt.plot(truth_data.flatten(), label="Truth")
plt.plot(equalized_data.flatten(), label="Equalized")
plt.plot(not_equalized_data.flatten(), label="Not equalized")

plt.xlabel("Sample")
plt.ylabel(variable)
plt.title("Equalized vs Not Equalized vs Truth")

plt.legend()
plt.grid()
plt.tight_layout()
plt.show()