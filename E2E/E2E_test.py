import os
import numpy as np
import h5py


TOLERANCE_PERCENT = 1e-3

REFERENCE_ISM = r'C:\Users\Osama\Desktop\Earth Observation\EODP-TS-E2E-20260910T154747Z-1-001\EODP-TS-E2E\ism_out'
REFERENCE_L1B = r'C:\Users\Osama\Desktop\Earth Observation\EODP-TS-E2E-20260910T154747Z-1-001\EODP-TS-E2E\l1b_out'

TEST_ISM = r'C:\Users\Osama\Desktop\EODP_E2E_RUN\ism_out'
TEST_L1B = r'C:\Users\Osama\Desktop\EODP_E2E_RUN\l1b_out'

BANDS = [
    'VNIR-0',
    'VNIR-1',
    'VNIR-2',
    'VNIR-3'
]


def read_toa(filepath):
    with h5py.File(filepath, 'r') as f:
        return np.array(f['toa'])


def compare_arrays(reference, test):

    if reference.shape != test.shape:
        return {
            'shape_match': False,
            'max_abs': np.nan,
            'max_rel_percent': np.nan,
            'mean_rel_percent': np.nan,
            'pass': False
        }

    abs_diff = np.abs(test - reference)

    rel_diff = np.zeros_like(
        abs_diff,
        dtype=np.float64
    )

    non_zero = np.abs(reference) > 0

    rel_diff[non_zero] = (
        abs_diff[non_zero]
        / np.abs(reference[non_zero])
        * 100.0
    )

    zero_reference = ~non_zero

    rel_diff[
        zero_reference & (abs_diff > 0)
    ] = np.inf

    max_abs = np.max(abs_diff)
    max_rel_percent = np.max(rel_diff)

    finite_values = rel_diff[
        np.isfinite(rel_diff)
    ]

    if finite_values.size > 0:
        mean_rel_percent = np.mean(
            finite_values
        )
    else:
        mean_rel_percent = np.inf

    passed = (
        max_rel_percent < TOLERANCE_PERCENT
    )

    return {
        'shape_match': True,
        'max_abs': max_abs,
        'max_rel_percent': max_rel_percent,
        'mean_rel_percent': mean_rel_percent,
        'pass': passed
    }


def run_test(
        module_name,
        reference_folder,
        test_folder,
        filename_prefix):

    print()
    print('=' * 90)
    print(module_name + ' CROSS-VALIDATION')
    print('=' * 90)

    print(
        f"{'Band':<10}"
        f"{'Max Abs Diff':<20}"
        f"{'Max Rel Diff [%]':<22}"
        f"{'Mean Rel Diff [%]':<22}"
        f"{'Result':<10}"
    )

    print('-' * 90)

    module_pass = True

    for band in BANDS:

        filename = (
            filename_prefix
            + band
            + '.nc'
        )

        reference_file = os.path.join(
            reference_folder,
            filename
        )

        test_file = os.path.join(
            test_folder,
            filename
        )

        if not os.path.exists(reference_file):

            print(
                f"{band:<10}"
                f"{'REFERENCE FILE MISSING':<64}"
                f"{'FAIL':<10}"
            )

            module_pass = False
            continue

        if not os.path.exists(test_file):

            print(
                f"{band:<10}"
                f"{'TEST FILE MISSING':<64}"
                f"{'FAIL':<10}"
            )

            module_pass = False
            continue

        reference = read_toa(
            reference_file
        )

        test = read_toa(
            test_file
        )

        result = compare_arrays(
            reference,
            test
        )

        if not result['shape_match']:

            print(
                f"{band:<10}"
                f"{'SHAPE MISMATCH':<64}"
                f"{'FAIL':<10}"
            )

            module_pass = False
            continue

        status = (
            'PASS'
            if result['pass']
            else 'FAIL'
        )

        if not result['pass']:
            module_pass = False

        print(
            f"{band:<10}"
            f"{result['max_abs']:<20.10e}"
            f"{result['max_rel_percent']:<22.10e}"
            f"{result['mean_rel_percent']:<22.10e}"
            f"{status:<10}"
        )

    print('-' * 90)

    print(
        module_name,
        'RESULT:',
        'PASS'
        if module_pass
        else 'FAIL'
    )

    return module_pass


print()
print('EODP END-TO-END CROSS-VALIDATION')
print(
    'Tolerance:',
    TOLERANCE_PERCENT,
    '%'
)

ism_pass = run_test(
    'ISM',
    REFERENCE_ISM,
    TEST_ISM,
    'ism_toa_'
)

l1b_pass = run_test(
    'L1B',
    REFERENCE_L1B,
    TEST_L1B,
    'l1b_toa_'
)

print()
print('=' * 90)

if ism_pass and l1b_pass:
    print('FINAL E2E RESULT: PASS')
else:
    print('FINAL E2E RESULT: FAIL')

print('=' * 90)