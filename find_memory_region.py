from utils import vmmap, enc, search, int_to_bytes, b
import mach


PROGRAM_PID = 42549
u = 0x100442bc8
u_uhp = 4299436936

data_region_start = 4299014144
data_region_offset_of_u = 422792



vmap = vmmap(PROGRAM_PID)

found_in = []
for i in vmap.mem:
    if i.start <= u_uhp <= i.end:
        found_in.append(i)


print(f"Matched with region: {found_in}")