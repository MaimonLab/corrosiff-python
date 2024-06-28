"""
For now these just test that the methods run!
"""
import numpy as np

class FLIMParams:
    """ Dummy version of the SiffPy FLIMParams class"""
    def __init__(self, *args):
        self.params = args

    def as_units(self, units):
        return self
    
    def convert_units(self, units):
        pass
    
    @property
    def units(self):
        return 'nanoseconds'

    @property
    def tau_offset(self):
        try:
            return next(param for param in self.params if isinstance(param, Irf)).offset
        except StopIteration:
            return 0
    
    
class Exp:
    def __init__(self, tau, frac, units):
        self.tau = tau
        self.frac = frac
        self.units = units

class Irf:
    def __init__(self, offset, sigma, units):
        self.offset = offset
        self.sigma = sigma
        self.units = units

def test_read_histogram(siffreaders):

    for siffreader in siffreaders:
        
        assert (
            siffreader.get_histogram()
            == siffreader.get_histogram_by_frames().sum(axis =0)
        ).all()

def test_read_flim_frames(siffreaders):

    for siffreader in siffreaders:

        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        test_params = FLIMParams(
            Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
            Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
            Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
        )

        siffreader.flim_map(test_params, registration=None)[0]

        dummy_reg = {
            k : (
            int(np.random.uniform(low = -128, high = 128)) % 128,
            int(np.random.uniform(low = -128, high = 128)) % 128
            ) for k in range(N_FRAMES)
        }
        framelist = list(range(N_FRAMES))

        siffreader.flim_map(params = test_params, frames = framelist, registration=None)[0]

        siffreader.flim_map(params = test_params, frames = framelist, registration=dummy_reg)[0]

def test_sum_2d_mask(siffreaders):

    for siffreader in siffreaders:

        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        roi = np.random.rand(*siffreader.frame_shape()) > 0.3

        test_params = FLIMParams(
            Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
            Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
            Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
        )

        siffreader.sum_roi_flim(roi, test_params, registration=None)[0]

        dummy_reg = {
            k : (
            int(np.random.uniform(low = -128, high = 128)) % 128,
            int(np.random.uniform(low = -128, high = 128)) % 128
            ) for k in range(N_FRAMES)
        }

        framelist = list(range(N_FRAMES))

        siffreader.sum_roi_flim(roi, test_params, frames = framelist, registration=None)[0]

        NUM_MASKS = 5
        masks = np.random.rand(NUM_MASKS, *siffreader.frame_shape()) > 0.3


        lifetimes, intensities, _ = siffreader.sum_rois_flim(masks, test_params, registration=None)

        dummy_reg = {
            k : (
            int(np.random.uniform(low = -128, high = 128)) % 128,
            int(np.random.uniform(low = -128, high = 128)) % 128
            ) for k in range(N_FRAMES)
        }

        framelist = list(range(N_FRAMES))


        lifetimes, intensities, _ = siffreader.sum_rois_flim(masks, test_params, frames = framelist, registration=dummy_reg)
        #assert intensities

        siffreader.sum_rois_flim(masks, test_params, frames = framelist, registration=dummy_reg)[0]

        siffreader.sum_rois_flim(masks, test_params, frames = framelist, registration=None)[0]

def test_sum_3d_mask(siffreaders):

    for siffreader in siffreaders:
        NUM_PLANES = 7

        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        rois = [np.random.rand(k, *siffreader.frame_shape()) > 0.3 for k in range(1,NUM_PLANES)]

        #complicated_rois = [np.random.rand(11, k, *siffreader.frame_shape()) > 0.3 for k in range(1,NUM_PLANES)]

        test_params = FLIMParams(
            Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
            Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
            Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
        )

        for three_d_roi in rois:
            siffreader.sum_roi_flim(three_d_roi, test_params, registration=None)[0]

            dummy_reg = {
                k : (
                int(np.random.uniform(low = -128, high = 128)) % 128,
                int(np.random.uniform(low = -128, high = 128)) % 128
                ) for k in range(N_FRAMES)
            }

            framelist = list(range(N_FRAMES))

            siffreader.sum_roi_flim(three_d_roi, test_params, frames = framelist, registration=dummy_reg)

            siffreader.sum_roi_flim(three_d_roi, test_params, frames = framelist, registration=dummy_reg)[0]