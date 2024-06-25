import corrosiffpy
import numpy as np

from siffpy.core.flim import FLIMParams, Exp, Irf

def test_read_histogram(siffreader):

    assert (
        siffreader.get_histogram()
    )

    assert(
        siffreader.get_histogram_by_frames().sum(axis =0)
    )

def test_read_flim_frames(siffreader):

    test_params = FLIMParams(
        Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
        Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
        Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    )

    with test_params.as_units('countbins'):
        assert siffreader.flim_map(test_params, registration=None)[0]

    dummy_reg = {
        k : (
        int(np.random.uniform(low = -128, high = 128)) % 128,
        int(np.random.uniform(low = -128, high = 128)) % 128
        ) for k in range(10000)
    }
    framelist = list(range(10000))

    with test_params.as_units('countbins'):
        assert siffreader.flim_map(params = test_params, frames = framelist, registration=None)[0]

        assert siffreader.flim_map(params = test_params, frames = framelist, registration=dummy_reg)[0]

def test_sum_2d_mask(siffreader):

    roi = np.random.rand(*siffreader.frame_shape()) > 0.3

    test_params = FLIMParams(
        Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
        Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
        Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    )

    with test_params.as_units('countbins'):
        assert siffreader.sum_roi_flim(roi, test_params, registration=None)[0]

    dummy_reg = {
        k : (
        int(np.random.uniform(low = -128, high = 128)) % 128,
        int(np.random.uniform(low = -128, high = 128)) % 128
        ) for k in range(10000)
    }

    framelist = list(range(10000))

    with test_params.as_units('countbins'):
        assert siffreader.sum_roi_flim(roi, test_params, frames = framelist, registration=None)[0]

    NUM_MASKS = 5
    masks = np.random.rand(NUM_MASKS, *siffreader.frame_shape()) > 0.3

    with test_params.as_units('countbins'):

        lifetimes, intensities, _ = siffreader.sum_rois_flim(masks, test_params, registration=None)

        assert lifetimes

        assert intensities

    dummy_reg = {
        k : (
        int(np.random.uniform(low = -128, high = 128)) % 128,
        int(np.random.uniform(low = -128, high = 128)) % 128
        ) for k in range(10000)
    }

    framelist = list(range(10000))

    with test_params.as_units('countbins'):

        lifetimes, intensities, _ = siffreader.sum_rois_flim(masks, test_params, frames = framelist, registration=dummy_reg)
        assert intensities

        test_params.convert_units('countbins')
        assert siffreader.sum_rois_flim(masks, test_params, frames = framelist, registration=dummy_reg)[0]

        assert siffreader.sum_rois_flim(masks, test_params, frames = framelist, registration=None)[0]

def test_sum_3d_mask(siffreaders):
    siffreader : corrosiffpy.SiffIO = siffreaders[0]

    NUM_PLANES = 7

    rois = [np.random.rand(k, *siffreader.frame_shape()) > 0.3 for k in range(1,NUM_PLANES)]

    #complicated_rois = [np.random.rand(11, k, *siffreader.frame_shape()) > 0.3 for k in range(1,NUM_PLANES)]
    N_FRAMES = 10000

    test_params = FLIMParams(
        Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
        Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
        Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    )

    for three_d_roi in rois:
        with test_params.as_units('countbins'):
            assert siffreader.sum_roi_flim(three_d_roi, test_params, registration=None)[0]

        dummy_reg = {
            k : (
            int(np.random.uniform(low = -128, high = 128)) % 128,
            int(np.random.uniform(low = -128, high = 128)) % 128
            ) for k in range(N_FRAMES)
        }

        framelist = list(range(N_FRAMES))

        with test_params.as_units('countbins'):
            assert siffreader.sum_roi_flim(three_d_roi, test_params, frames = framelist, registration=dummy_reg)

            assert siffreader.sum_roi_flim(three_d_roi, test_params, frames = framelist, registration=dummy_reg)[0]