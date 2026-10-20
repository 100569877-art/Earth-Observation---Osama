
# MAIN FUNCTION TO CALL THE L1C MODULE

from l1c.src.l1c import l1c

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = '/home/luss/EODP/eodp/auxiliary'
# GM dir + L1B dir
indir = '/home/luss/my_shared_folder/gm_out/gm_alt100_act_150/,/home/luss/EODP/eodp/l1b/test/ut02/output'
outdir = C://Users//Osama//Desktop//Earth Observation//EODP_TER_2021-20260910T154749Z-1-001//EODP_TER_2021//EODP-TS-L1C

# Initialise the ISM
myL1c = l1c(auxdir, indir, outdir)
myL1c.processModule()
