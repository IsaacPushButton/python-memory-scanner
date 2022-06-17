import os

from utils import vmmap, enc, search, int_to_bytes, b
import mach


PROGRAM_PID = 46012

vmap = vmmap(PROGRAM_PID)

repeats = {}
found = None
i = 0
while not found:
    VALUE = enc(input("Enter changed value: "))

    if isinstance(VALUE, str) and VALUE[0] == "*":
        if len(VALUE) == 1:
            matches = [v for k, v in new_repeats.items()]
        else:
            matches = [[v for k, v in new_repeats.items()][int(VALUE[1])]]
        found = []
        [found.extend(list(i)) for i in matches]
        break

    locations = search(VALUE, vmap)
    #print(f"Value found in {len(locations)} locations: {locations}")
    if not repeats:
        repeats = locations
    else:
        new_repeats = {}
        for k, v in repeats.items():
            if new_locations := locations.get(k):
                matches = v.intersection(new_locations)
                if matches:
                    new_repeats[k] = matches
        repeats = new_repeats
        if not repeats:
            print("No intersection found, restarting search")
        else:
            print(f"Found repeats:{repeats}")

        if len(new_repeats) == 1 and len(list(repeats.items())[0][1]) == 1:
            print(f"Isolated value at {list(repeats.items())[0][0]} : {list(repeats.items())[0][1]}")
            found = list(repeats.items())[0][1]
    i = i + 1

while True:
    new_value = enc(input("Choose new value: "))
    if not new_value:
        continue
    new_value = b(new_value)
    for i in found:
        print(f"Writing {new_value} to {i}")
        mach.vm_write(vmap.port, i, new_value)
        confirm_post = mach.vm_read(vmap.port, i, 4)
        assert new_value == confirm_post





print(locations)



#task = mach.task_for_pid(PROGRAM_PID)
#stack_start = 0x7ff7b04b8000
#stack_end = 0x7ff7b0cb8000
#mem: bytes = mach.vm_read(task, stack_start, stack_end - stack_start)





#print(f"Found string at: {indexes}")


#value = mem.decode("utf-8")
#print(value)

#mach.vm_write(task, offset + 0x00003FA4, bytes("Steph".encode()))
#print("did hax")





#f = open("output", "wb")
#f.write(mem)
#f.close()