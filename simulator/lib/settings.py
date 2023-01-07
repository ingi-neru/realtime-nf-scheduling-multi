# Default files
DEFAULT_OUTFILE = "results/optimize_out.txt"

# Default SLO parameters
DEFAULT_RATE_SLO = 0
DEFAULT_DELAY_SLO = int(1e11)    # infinite delay

# Default queue size
DEFAULT_QUEUE_SIZE = 1

# Default batch size
DEFAULT_BATCH_SIZE = 1

# Default number of simulation rounds
DEFAULT_SIMULATION_ROUNDS = 20

# Interval (rounds) between task migration controller steps
DEFAULT_REALLOC_CONTROLLER_INTERVAL = 50

# Default values of constants
DEFAULT_ALPHA = 1  #The higher the more we optimize for delay
DEFAULT_DELTA = 0.01 # Tolerance parameter
DEFAULT_EPSILON = 0.00001
DEFAULT_RHO_ROUGHNESS = 0.05

# additional constants
M = 1000000000
C = 1

# Control version
# 0: old version
# 2: new version
CONTROL_VERSION = 2

LINEAR_SEARCH_TRIES = 100

# Delay estimate version
# 0: old version,
# 1: a more sophisticated one
DELAY_ESTIMATE_VERSION = 1
