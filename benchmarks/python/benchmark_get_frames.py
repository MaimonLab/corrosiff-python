from bench import files, run_test_on_file

from siffpy.core.flim import FLIMParams, Exp, Irf

def test_read_unregistered(reader):
    reader.get_frames(registration_dict={})

def test_read_registered(reader):
    reader.get_frames(frames = reader.im_params.flatten_by_timepoints())

def test_read_flim_unregistered(reader):
    params = FLIMParams(
        Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
        Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
        Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    )
    reader.get_frames_flim(params, registration_dict={})

def test_read_flim_registered(reader):

    params = FLIMParams(
        Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
        Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
        Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    )
    reader.get_frames_flim(params, frames = reader.im_params.flatten_by_timepoints())

for file in files:
    print(f"File: {file}")
    print(
        "Read all frames, unregistered:",
        run_test_on_file(file, test_read_unregistered, 5)
    )

    print(
        "Read all frames, registered:",
        run_test_on_file(file, test_read_registered, 5)
    )

    print(
        "Read all FLIM frames, unregistered:",
        run_test_on_file(file, test_read_flim_unregistered, 5)
    )

    print(
        "Read all FLIM frames, registered:",
        run_test_on_file(file, test_read_flim_registered, 5)
    )