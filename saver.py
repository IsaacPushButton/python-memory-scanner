from utils import save_memory, vmmap, read_all_memory
import os

PROGRAM_PID = 28347
vmap = vmmap(PROGRAM_PID)

save_memory(read_all_memory(vmap))