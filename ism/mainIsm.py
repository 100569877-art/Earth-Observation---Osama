
# MAIN FUNCTION TO CALL THE ISM MODULE

from ism.src.ism import ism

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\\Users\\Osama\\Documents\\GitHub\\Earth Observation - Osama\\auxiliary'
indir = r"C:\\Users\\Osama\\Desktop\\Earth Observation\\EODP_TER_2021-20260910T154749Z-1-001\\EODP_TER_2021\\EODP-TS-ISM\\input\\gradient_alt100_act150" # small scene
outdir = r"C:\\Users\\Osama\\Desktop\\Earth Observation\\EODP_TER_2021-20260910T154749Z-1-001\\EODP_TER_2021\\EODP-TS-ISM\\Output test 2"

# Initialise the ISM
myIsm = ism(auxdir, indir, outdir)
myIsm.processModule()
