# ============================================================
# L1B NUMERICAL TEST
#
# Compare:
#   1. Truth ISRF
#   2. Equalized + restored L1B
#   3. Non-equalized + restored L1B
#
# The objective is to verify numerically that radiometric
# equalization improves the reconstructed signal.
# ============================================================

import os
import numpy as np
import xarray as xr


# ============================================================
# 1. PATHS
# ============================================================

# L1B test input:
# contains ism_toa_VNIR-X.nc and ism_toa_isrf_VNIR-X.nc
input_dir = (
    r"C:\Users\Osama\Desktop\Earth Observation"
    r"\EODP_TER_2021-20260910T154749Z-1-001"
    r"\EODP_TER_2021"
    r"\EODP-TS-L1B"
    r"\input"
)

# Equalization auxiliary files
eq_dir = (
    r"C:\Users\Osama\Documents\GitHub"
    r"\Earth Observation - Osama"
    r"\auxiliary"
    r"\equalization"
)


# ============================================================
# 2. BANDS
# ============================================================

bands = [
    "VNIR-0",
    "VNIR-1",
    "VNIR-2",
    "VNIR-3"
]


# ============================================================
# 3. ABSOLUTE RADIOMETRIC GAINS
#
# From config/l1bConfig.py
# ============================================================

gains = {
    "VNIR-0": 0.09209303,
    "VNIR-1": 0.06787323,
    "VNIR-2": 0.052162305,
    "VNIR-3": 0.047756273
}


# ============================================================
# 4. NETCDF READING FUNCTION
# ============================================================

def read_nc(filename):
    """
    Read the main numerical variable from a NetCDF file.

    This avoids having to manually specify the variable name.
    """

    ds = xr.open_dataset(filename)

    try:

        if len(ds.data_vars) == 0:
            raise ValueError(
                "No data variable found in " + filename
            )

        # Take first numerical data variable
        variable_name = list(ds.data_vars)[0]

        data = np.asarray(
            ds[variable_name].values,
            dtype=float
        )

    finally:
        ds.close()

    return data


# ============================================================
# 5. NUMERICAL METRICS
# ============================================================

def calculate_metrics(reference, test):
    """
    Calculate numerical differences between two matrices.
    """

    error = test - reference

    mae = np.mean(
        np.abs(error)
    )

    rmse = np.sqrt(
        np.mean(error ** 2)
    )

    max_abs_error = np.max(
        np.abs(error)
    )

    # Relative difference only where reference is not ~zero
    valid = np.abs(reference) > 1e-12

    if np.any(valid):

        relative_error = (
            np.abs(error[valid])
            / np.abs(reference[valid])
        ) * 100.0

        mean_relative = np.mean(
            relative_error
        )

        max_relative = np.max(
            relative_error
        )

    else:

        mean_relative = np.nan
        max_relative = np.nan

    # Correlation
    ref_flat = reference.flatten()
    test_flat = test.flatten()

    correlation = np.corrcoef(
        ref_flat,
        test_flat
    )[0, 1]

    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAX_ABS": max_abs_error,
        "MEAN_REL": mean_relative,
        "MAX_REL": max_relative,
        "CORR": correlation
    }


# ============================================================
# 6. RUN TEST FOR ALL FOUR BANDS
# ============================================================

print()
print("=" * 80)
print("L1B NUMERICAL CALIBRATION TEST")
print("=" * 80)

summary = []


for band in bands:

    print()
    print("-" * 80)
    print("BAND:", band)
    print("-" * 80)

    # --------------------------------------------------------
    # File names
    # --------------------------------------------------------

    dn_file = os.path.join(
        input_dir,
        "ism_toa_" + band + ".nc"
    )

    truth_file = os.path.join(
        input_dir,
        "ism_toa_isrf_" + band + ".nc"
    )

    eq_mult_file = os.path.join(
        eq_dir,
        "eq_mult_" + band + ".nc"
    )

    eq_add_file = os.path.join(
        eq_dir,
        "eq_add_" + band + ".nc"
    )

    # --------------------------------------------------------
    # Read data
    # --------------------------------------------------------

    dn = read_nc(
        dn_file
    )

    truth = read_nc(
        truth_file
    )

    eq_mult = read_nc(
        eq_mult_file
    )

    eq_add = read_nc(
        eq_add_file
    )

    gain = gains[band]

    # --------------------------------------------------------
    # Check dimensions
    # --------------------------------------------------------

    if dn.shape != truth.shape:

        raise ValueError(
            band
            + ": DN and truth matrices have different sizes: "
            + str(dn.shape)
            + " != "
            + str(truth.shape)
        )

    # --------------------------------------------------------
    # NON-EQUALIZED L1B
    #
    # Absolute radiometric restoration only
    # --------------------------------------------------------

    toa_noneq = (
        dn
        * gain
    )

    # --------------------------------------------------------
    # EQUALIZED L1B
    #
    # Equalization:
    #       DN_eq = (DN - ADD) / MULT
    #
    # Restoration:
    #       Radiance = DN_eq * gain
    # --------------------------------------------------------

    toa_eq_dn = (
        dn
        - eq_add
    ) / eq_mult

    toa_eq = (
        toa_eq_dn
        * gain
    )

    # --------------------------------------------------------
    # Calculate numerical metrics
    # --------------------------------------------------------

    metrics_eq = calculate_metrics(
        truth,
        toa_eq
    )

    metrics_noneq = calculate_metrics(
        truth,
        toa_noneq
    )

    # --------------------------------------------------------
    # Numerical calibration assessment
    # --------------------------------------------------------

    if metrics_eq["RMSE"] <= metrics_noneq["RMSE"]:

        status = "PASS"

    else:

        status = "FAIL"

    # Improvement in RMSE
    if metrics_noneq["RMSE"] != 0:

        improvement = (
            (
                metrics_noneq["RMSE"]
                - metrics_eq["RMSE"]
            )
            / metrics_noneq["RMSE"]
        ) * 100.0

    else:

        improvement = 0.0

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print()
    print("EQUALIZED vs TRUTH")
    print(
        "MAE                  :",
        metrics_eq["MAE"]
    )
    print(
        "RMSE                 :",
        metrics_eq["RMSE"]
    )
    print(
        "Maximum absolute err :",
        metrics_eq["MAX_ABS"]
    )
    print(
        "Mean relative err [%]:",
        metrics_eq["MEAN_REL"]
    )
    print(
        "Max relative err  [%]:",
        metrics_eq["MAX_REL"]
    )
    print(
        "Correlation           :",
        metrics_eq["CORR"]
    )

    print()

    print("NON-EQUALIZED vs TRUTH")
    print(
        "MAE                  :",
        metrics_noneq["MAE"]
    )
    print(
        "RMSE                 :",
        metrics_noneq["RMSE"]
    )
    print(
        "Maximum absolute err :",
        metrics_noneq["MAX_ABS"]
    )
    print(
        "Mean relative err [%]:",
        metrics_noneq["MEAN_REL"]
    )
    print(
        "Max relative err  [%]:",
        metrics_noneq["MAX_REL"]
    )
    print(
        "Correlation           :",
        metrics_noneq["CORR"]
    )

    print()
    print(
        "RMSE improvement [%] :",
        improvement
    )

    print(
        "Calibration test     :",
        status
    )

    summary.append(
        {
            "band": band,
            "rmse_eq": metrics_eq["RMSE"],
            "rmse_noneq": metrics_noneq["RMSE"],
            "improvement": improvement,
            "status": status
        }
    )


# ============================================================
# 7. FINAL SUMMARY
# ============================================================

print()
print()
print("=" * 80)
print("L1B CALIBRATION SUMMARY")
print("=" * 80)

print(
    "{:<10} {:>15} {:>15} {:>15} {:>10}".format(
        "Band",
        "RMSE EQ",
        "RMSE NO-EQ",
        "Improvement %",
        "Status"
    )
)

print("-" * 80)


for result in summary:

    print(
        "{:<10} {:>15.6f} {:>15.6f} {:>15.6f} {:>10}".format(
            result["band"],
            result["rmse_eq"],
            result["rmse_noneq"],
            result["improvement"],
            result["status"]
        )
    )


print("=" * 80)


# ============================================================
# 8. GLOBAL RESULT
# ============================================================

all_pass = all(
    result["status"] == "PASS"
    for result in summary
)

print()

if all_pass:

    print(
        "FINAL L1B CALIBRATION RESULT: PASS"
    )

    print(
        "Equalization reduces the RMSE with respect "
        "to the ISRF truth for all four VNIR bands."
    )

else:

    print(
        "FINAL L1B CALIBRATION RESULT: CHECK RESULTS"
    )

    print(
        "Equalization did not reduce the RMSE "
        "for at least one VNIR band."
    )

print()