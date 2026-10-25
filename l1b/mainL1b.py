
# MAIN FUNCTION TO CALL THE L1B MODULE

from l1b.src.l1b import l1b

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\Users\Osama\Documents\GitHub\Earth Observation - Osama\auxiliary'
indir = r'C:\Users\Osama\Desktop\EODP_E2E_RUN\ism_out'
outdir = r'C:\Users\Osama\Desktop\EODP_E2E_RUN\l1b_out'
# Initialise the ISM
myL1b = l1b(auxdir, indir, outdir)
myL1b.processModule()


