import os
from ast import literal_eval

from utils import vmmap, enc, search, int_to_bytes, b
import mach


secret_value = "Godfrey"
secret_value2 = "Morbog"
secret_value3 = 12345678

PROGRAM_PID =28347 # 24927 #

VALUE = 10


vmap = vmmap(PROGRAM_PID)
repeats = {}
found = None
i = 0
while not found:
    VALUE = literal_eval(f"""b'{input("Enter changed value: ")}'""")
    assert isinstance(VALUE, bytes)
    if VALUE == "*":
        matches = [v for k,v in locations.items()]
        found = []
        [found.extend(list(i)) for i in matches]
        break
    locations = search(VALUE, vmap)
    print(f"Value found in {len(locations)} locations: {locations}")
    if not repeats:

        repeats = locations
    else:
        new_repeats = {}
        for k,v in repeats.items():
            if new_locations := locations.get(k):
                matches = v.intersection(new_locations)
                if matches:
                    new_repeats[k] = matches
        repeats = new_repeats
        if not repeats:
            print("No intersection found, restarting search")
        else:
            print(new_repeats)

        if len(new_repeats) == 1 and len(list(repeats.items())[0][1]) == 1:
            print(f"Isolated value at {list(repeats.items())[0][0]} : {list(repeats.items())[0][1]}")
            found = list(repeats.items())[0][1]
    i = i + 1

while True:
    new_value = literal_eval(f"""b'{input("Enter new value: ")}'""")
    if not new_value:
        continue
    for i in found:
        print(f"Writing {new_value} to {i}")
        mach.vm_protect(vmap.port, i, len(new_value), 0)
        mach.vm_write(vmap.port, i, new_value)
        confirm = mach.vm_read(vmap.port, i, len(new_value))
        assert new_value == confirm
        print(confirm)




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