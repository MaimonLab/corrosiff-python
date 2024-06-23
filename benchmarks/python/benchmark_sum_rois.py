from bench import files, run_test_on_file
from typing import TYPE_CHECKING
import numpy as np

from siffpy.core.flim import FLIMParams, Exp, Irf

if TYPE_CHECKING:
    from siffpy import SiffReader

def test_one_2droi_all_frames(reader : 'SiffReader'):
    roi = np.random.rand(*reader.im_params.shape) > 0.3
    reader.sum_mask(roi, registration_dict={})

def test_ten_2drois_all_frames(reader : 'SiffReader'):
    roi = np.random.rand(10, *reader.im_params.shape) > 0.3
    reader.sum_masks(roi, registration_dict={})

def test_one_3droi_all_frames(reader : 'SiffReader'):
    roi = np.random.rand(reader.im_params.num_slices, *reader.im_params.shape) > 0.3
    reader.sum_mask(roi, registration_dict={})

def test_ten_3drois_all_frames(reader : 'SiffReader'):
    roi = np.random.rand(10, reader.im_params.num_slices, *reader.im_params.shape) > 0.3
    reader.sum_masks(roi, registration_dict={})

def test_flim_one_2droi_all_frames(reader : 'SiffReader'):
    roi = np.random.rand(*reader.im_params.shape) > 0.3

    flim_params = FLIMParams(
        Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
        Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
        Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    )

    with flim_params.as_units('countbins'):
        reader.sum_mask_flim(flim_params, roi, registration_dict={})

def test_flim_ten_2drois_all_frames(reader : 'SiffReader'):
    roi = np.random.rand(10, *reader.im_params.shape) > 0.3

    flim_params = FLIMParams(
        Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
        Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
        Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    )

    with flim_params.as_units('countbins'):
        reader.sum_masks_flim(flim_params, roi, registration_dict={})

def test_flim_one_3droi_all_frames(reader : 'SiffReader'):
    roi = np.random.rand(reader.im_params.num_slices, *reader.im_params.shape) > 0.3

    flim_params = FLIMParams(
        Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
        Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
        Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    )

    with flim_params.as_units('countbins'):
        reader.sum_mask_flim(flim_params, roi, registration_dict={})

def test_flim_ten_3drois_all_frames(reader : 'SiffReader'):
    roi = np.random.rand(10, reader.im_params.num_slices, *reader.im_params.shape) > 0.3

    flim_params = FLIMParams(
        Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
        Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
        Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    )

    with flim_params.as_units('countbins'):
        reader.sum_masks_flim(flim_params, roi, registration_dict={})

for file in files:
    print(f"File: {file}")
    print(
        "Sum one 2D ROI over all frames:",
        run_test_on_file(file, test_one_2droi_all_frames, 5)
    )

    print(
        "Sum ten 2D ROIs over all frames:",
        run_test_on_file(file, test_ten_2drois_all_frames, 5)
    )

    print(
        "Sum one 3D ROI over all frames:",
        run_test_on_file(file, test_one_3droi_all_frames, 5)
    )

    print(
        "Sum ten 3D ROIs over all frames:",
        run_test_on_file(file, test_ten_3drois_all_frames, 5)
    )