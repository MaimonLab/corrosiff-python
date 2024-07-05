from bench import files, run_test_on_file
import timeit
import numpy as np
from siffpy import SiffReader
import corrosiffpy

def test_get_start_and_end_timestamps_with_siffpy(reader: 'SiffReader'):
    reader.get_time(frames = [reader.all_frames[0], reader.all_frames[-1]], reference_time = 'epoch')

def open_and_get_start_and_end_with_siffpy(filename : str):
    reader = SiffReader(filename)
    test_get_start_and_end_timestamps_with_siffpy(reader)

def test_get_start_and_end_timestamps_with_corrosiffpy(filename : str):
    corrosiffpy.get_start_and_end_timestamps(filename)

def test_get_start_timestamps_with_corrosiffpy(filename : str):
    corrosiffpy.get_start_timestamp(filename)

for file in files:
    print(f"File: {file}")
    sr = SiffReader(file)
    from_sp = sr.get_time(frames = [sr.all_frames[0], sr.all_frames[-1]], reference_time = 'epoch')
    from_cp = corrosiffpy.get_start_and_end_timestamps(file)
    print(from_cp)
    # print(
    #     "Get start and end timestamps naive with siffpy:",
    #     run_test_on_file(file, test_get_start_and_end_timestamps_with_siffpy, 15)
    # )
    print(
        "Scan first timestamp",
        [x/100 for x in timeit.repeat(
            stmt = f"test_get_start_timestamps_with_corrosiffpy('{file}')",
            setup = "from __main__ import test_get_start_timestamps_with_corrosiffpy",
            number = 100
        )]
    )

    print(
        "Open and get start and with corrosiff only",
        timeit.repeat(
            stmt = f"test_get_start_and_end_timestamps_with_corrosiffpy('{file}')",
            setup = "from __main__ import test_get_start_and_end_timestamps_with_corrosiffpy",
            number = 5
        )
    )
    print(
        "Open and get start and with siffpy Rust only",
        timeit.repeat(
            stmt = f"open_and_get_start_and_end_with_siffpy('{file}')",
            setup = "from __main__ import open_and_get_start_and_end_with_siffpy",
            number = 5
        )
    )
