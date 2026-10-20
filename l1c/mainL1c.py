
# MAIN FUNCTION TO CALL THE L1C MODULE

from l1c.src.l1c import l1c

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\Users\Osama\Documents\GitHub\Earth Observation - Osama\auxiliary'
# GM dir + L1B dir
indir = (
    r'C:\Users\Osama\Desktop\Earth Observation\EODP_TER_2021-20260910T154749Z-1-001\EODP_TER_2021\EODP-TS-GEO\output'
    + ','
    + r'C:\Users\Osama\Desktop\Earth Observation\EODP_TER_2021-20260910T154749Z-1-001\EODP_TER_2021\EODP-TS-L1B\output'
)
outdir = r'C:\Users\Osama\Desktop\Earth Observation\EODP_TER_2021-20260910T154749Z-1-001\EODP_TER_2021\EODP-TS-L1C\MY OUTPUT'

# Initialise the ISM
myL1c = l1c(auxdir, indir, outdir)
myL1c.processModule()
