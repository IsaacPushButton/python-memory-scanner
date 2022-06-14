from typing import List, Union, Set, Literal

from pydantic import BaseModel
import mach
import subprocess
from ast import literal_eval

BIT = 16
ENDIANNESS = "big"
INT_LEN = BIT // 8

class RegionRecurseOutput(BaseModel):
    offset: int
    size: int
    nest: int
    vbr: int
    vbrcount: int

class MemoryMapRow(BaseModel):
    name: str
    start: int
    end: int

class MemoryMap(BaseModel):
    port: int
    pid: int
    mem: List[MemoryMapRow]

def vmmap(pid: int) -> MemoryMap:
    bashCommand = f"vmmap {pid}"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        raise Exception(error)
    return parse_vmmap_output(pid, output)

def parse_vmmap_output(pid: int, vmmap_output: bytes) -> MemoryMap:
    out = str(vmmap_output)
    writable_start = out.index("Writable regions for process")
    writable_end = out.index("==== Legend")
    writable = out[writable_start:writable_end].split("\\n")[3:]
    regions = []
    port = mach.task_for_pid(pid)
    name_counter = {}
    for row in [i.split("  ") for i in writable]:
        if not [i for i in row if i]:
            continue

        lines = [i for i in row if i]
        start, end = lines[1].strip().split("-")
        name = lines[0]
        if name_counter.get(name):
            name_counter[name] = name_counter[name] + 1
        regions.append(MemoryMapRow(
            name=f"{name}{name_counter.get(name,'')}",
            start=literal_eval(f"0x{start}"),
            end=literal_eval(f"0x{end.split(' ')[0]}")
        ))

    region_recurse = memory_region(task=port, pid=pid)
    regions.append(MemoryMapRow(
        name="VM REGION RECURSE",
        start=region_recurse.offset,
        end=region_recurse.offset + region_recurse.size
    ))
    return MemoryMap(
        port=port,
        pid=pid,
        mem=regions
    )


def memory_region(task: int, pid:int) -> RegionRecurseOutput:
    offset, size, nest, vbr, vbrcount = mach.vm_region_recurse(task)

    return RegionRecurseOutput(
        offset=offset,
        size=size,
        nest=nest,
        vbr=vbr,
        vbrcount=vbrcount
    )

def enc(s: Union[str,int]):
    try:
        return int(s)
    except ValueError:
        return s

def b(s: Union[str,int]):
    if isinstance(s, int):
        return int_to_bytes(s, length=INT_LEN)
    else:
        return s.encode("utf-8")

def find_all_instances(mem: bytes, find: bytes):
    indexes = []
    done = False
    start = 0
    while not done:
        try:
            start = mem.index(find, start + 1)
            indexes.append(start)
        except ValueError as e:
            done = True
    return indexes

def read_memory_map(port: int, mem: MemoryMapRow):
    return mach.vm_read(port, mem.start, mem.end - mem.start)

def search(value: any, map: MemoryMap):
    found_in = {}
    for v in variations(value):
        print(f"Searching for {v}")
        for map_location in map.mem:
            try:
                matches = find_all_instances(read_memory_map(map.port, map_location), v)
                if matches:
                    found_in[f"{map_location.name}"] = set([i + map_location.start for i in matches])
            except mach.MachError as e:
                print(f"failed to load {map_location.name}: {e}")
    return found_in

def read_all_memory(map: MemoryMap):
    memory = []
    for map_location in map.mem:
        memory.append(read_memory_map(map.port, map_location))
    return b''.join(memory)

def save_memory(memory_lump : bytes):
    with open('output', 'wb+') as f:
        f.write(memory_lump)




def variations(i: Union[str,int, bytes]) :
    if isinstance(i, bytes):
        return [i]
    if isinstance(i, int):
        return [
            int_to_bytes(i, signed=True, length=INT_LEN),
           # int_to_bytes(i, signed=False),
           # int_to_bytes(i, signed=True, byteorder="little"),
           # int_to_bytes(i, signed=False, byteorder="little"),
        ]
    else:
        return [i.encode("utf-8"), i.encode("ascii")]

def int_to_bytes(i: int, *, signed: bool = False, byteorder: Literal["big", "little"] = ENDIANNESS, length=None) -> bytes:
    if not length:
        length = ((i + ((i * signed) < 0)).bit_length() + 7 + signed) // 8
    return i.to_bytes(length, byteorder=byteorder, signed=signed)

def bytes_to_int(b: bytes, *, signed: bool = False, byteorder: Literal["big", "little"] = ENDIANNESS) -> int:
    return int.from_bytes(b, byteorder=byteorder, signed=signed)
