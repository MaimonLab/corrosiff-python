"""
For now these just test that the methods run!
"""
from typing import List, TYPE_CHECKING
import numpy as np
if TYPE_CHECKING:
    from corrosiffpy import SiffIO

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
    
class MultiFLIMParamsDummy:
    """ Dummy version of multi pulse"""
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
            return [param.offset for param in self.params if isinstance(param, Irf)]
        except StopIteration:
            return 0
        
    @property
    def irfs(self):
        try:
            return MultiIrf([irf for irf in self.params if isinstance(irf, Irf)])
        except StopIteration:
            return []
 
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

    @property
    def tau_offset(self):
        return self.offset

class FractionalIrf(Irf):
    def __init__(self, *args, frac = 1, **kwargs):
        self.frac = frac
        super().__init__(*args, **kwargs)

class MultiIrf:
    def __init__(self, firfs : List[FractionalIrf]):
        self.irfs = firfs


TEST_PARAMS = FLIMParams(
    Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
    Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
    Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
)

TEST_MPFPS = MultiFLIMParamsDummy(
    Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
    Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
    FractionalIrf(offset = 1.1, sigma = 0.2, frac = 0.5, units = 'nanoseconds'),
    FractionalIrf(offset = 4.1, sigma = 0.2, frac = 0.5, units = 'nanoseconds'),
)


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

        siffreader.flim_map(TEST_PARAMS, registration=None)[0]

        dummy_reg = {
            k : (
            int(np.random.uniform(low = -128, high = 128)) % 128,
            int(np.random.uniform(low = -128, high = 128)) % 128
            ) for k in range(N_FRAMES)
        }
        framelist = list(range(N_FRAMES))

        siffreader.flim_map(params = TEST_PARAMS, frames = framelist, registration=None)[0]

        siffreader.flim_map(params = TEST_PARAMS, frames = framelist, registration=dummy_reg)[0]

        siffreader.flim_map(params = TEST_MPFPS, frames = framelist, registration=dummy_reg)[0]

def test_roi_1d_flim(siffreaders):
    for siffreader in siffreaders:
        
        siffreader : SiffIO
        print(siffreader.filename)

        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        framelist = list(range(N_FRAMES))

        # flat no registration
        frames = siffreader.flim_map(
            frames = framelist,
            params = TEST_PARAMS, flim_method = 'empirical lifetime', registration=None
        )
        frames_lifetime, frames_intensity, _ = frames

        roi = np.random.rand(*siffreader.frame_shape()) > 0.3

        flat_roi = siffreader.get_roi_1d_flim(
            roi, frames = framelist, params = TEST_PARAMS, flim_method = 'empirical lifetime', registration=None
        ) 

        lifetime, intensity, _ = flat_roi

        assert (lifetime.dtype == np.float64)
        assert (intensity.dtype == np.uint16)
        assert lifetime.shape == (len(framelist), np.sum(roi))

        not_comparable = ~np.isclose(
            frames_lifetime[:, roi],
            lifetime,
            equal_nan = True,
        )

        lifetime[np.isinf(lifetime)] = np.nan

        print(
            "Example non-close value:",
            np.array([frames_lifetime[:, roi][not_comparable],
            lifetime[not_comparable]],).T
        )

        assert np.allclose(
            frames_intensity[:, roi],
            intensity,
        )

        assert np.allclose(
            frames_lifetime[:, roi],
            lifetime,
            equal_nan = True,
        )

        # volume no registration

        NUM_ROIS = 7
        roi_vol = np.random.rand(NUM_ROIS, *siffreader.frame_shape()) > 0.3

        together = siffreader.get_roi_1d_flim(roi_vol,
            frames = framelist,
            params = TEST_PARAMS, flim_method = 'empirical lifetime', registration=None
        )

        together_lifetime, together_intensity, _ = together
        assert (together_lifetime.dtype == np.float64)
        assert (together_intensity.dtype == np.uint16)
        # assert (together_phasor.shape[0] == int(siffreader.num_frames()/ NUM_ROIS))
        assert (together_lifetime.shape[0] == len(framelist) // NUM_ROIS)

        # frames_lifetime = frames_lifetime[:int(siffreader.num_frames()/ NUM_ROIS)* NUM_ROIS]
        frames_lifetime = frames_lifetime[:int(len(framelist)// NUM_ROIS) * NUM_ROIS]
        frames_lifetime = frames_lifetime.reshape(
            (
                int(len(framelist) // NUM_ROIS),
                NUM_ROIS,
                *siffreader.frame_shape()
            )
        )
        # frames_intensity = frames_intensity[:int(siffreader.num_frames()/ NUM_ROIS)* NUM_ROIS]
        frames_intensity = frames_intensity[:int(len(framelist)// NUM_ROIS) * NUM_ROIS]
        frames_intensity = frames_intensity.reshape(
            (
                int(len(framelist) // NUM_ROIS),
                NUM_ROIS,
                *siffreader.frame_shape()
            )
        )

        masked_lifetime = frames_lifetime[:, roi_vol]
        masked_intensity = frames_intensity[:, roi_vol]

        together_lifetime[np.isinf(together_lifetime)] = np.nan

        assert np.allclose(
            masked_intensity,
            together_intensity,
        )

        assert np.allclose(
            masked_lifetime,
            together_lifetime,
            equal_nan = True,
        )

def test_roi_1d_phasor(siffreaders):
    for siffreader in siffreaders:
        siffreader : SiffIO
        print(siffreader.filename)

        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        framelist = list(range(N_FRAMES))

        # flat no registration
        frames = siffreader.flim_map(
            frames = framelist,
            params = TEST_PARAMS, flim_method = 'phasor', registration=None
        )
        frames_phasor, frames_intensity, _ = frames

        roi = np.random.rand(*siffreader.frame_shape()) > 0.3

        flat_roi = siffreader.get_roi_1d_flim(
            roi, frames = framelist, params = TEST_PARAMS, flim_method = 'phasor', registration=None
        ) 

        phasor, intensity, _ = flat_roi

        assert (phasor.dtype == np.complex128)
        assert (intensity.dtype == np.uint16)
        assert phasor.shape == (len(framelist), np.sum(roi))

        masked_phasor = frames_phasor[:, roi]
        masked_intensity = frames_intensity[:, roi]

        assert np.allclose(
            masked_intensity,
            intensity,
        )
        assert np.allclose(
            masked_phasor,
            phasor,
            equal_nan = True,
        )

        # volume no registration

        NUM_ROIS = 7
        roi_vol = np.random.rand(NUM_ROIS, *siffreader.frame_shape()) > 0.3

        together = siffreader.get_roi_1d_flim(roi_vol,
            frames = framelist,
            params = TEST_PARAMS, flim_method = 'phasor', registration=None
        )

        together_phasor, together_intensity, _ = together
        assert (together_phasor.dtype == np.complex128)
        assert (together_intensity.dtype == np.uint16)
        # assert (together_phasor.shape[0] == int(siffreader.num_frames()/ NUM_ROIS))
        assert (together_phasor.shape[0] == len(framelist) // NUM_ROIS)

        # frames_phasor = frames_phasor[:int(siffreader.num_frames()/ NUM_ROIS)* NUM_ROIS]
        frames_phasor = frames_phasor[:int(len(framelist)// NUM_ROIS) * NUM_ROIS]
        frames_phasor = frames_phasor.reshape(
            (
                int(len(framelist) // NUM_ROIS),
                NUM_ROIS,
                *siffreader.frame_shape()
            )
        )
        # frames_intensity = frames_intensity[:int(siffreader.num_frames()/ NUM_ROIS)* NUM_ROIS]
        frames_intensity = frames_intensity[:int(len(framelist)// NUM_ROIS) * NUM_ROIS]
        frames_intensity = frames_intensity.reshape(
            (
                int(len(framelist) // NUM_ROIS),
                NUM_ROIS,
                *siffreader.frame_shape()
            )
        )

        masked_phasor = frames_phasor[:, roi_vol]
        masked_intensity = frames_intensity[:, roi_vol]

        assert np.allclose(
            masked_intensity,
            together_intensity,
        )

        assert np.allclose(
            masked_phasor,
            together_phasor,
            equal_nan = True,
        )

        ###### REGISTRATION #######

        rdict = {
            k : (
            int(np.random.uniform(low = -128, high = 128)) % 128,
            int(np.random.uniform(low = -128, high = 128)) % 128
            ) for k in range(siffreader.num_frames())
        }

        # Flat with registration
        frames = siffreader.flim_map(
            frames = framelist,
            params = TEST_PARAMS, flim_method = 'phasor', registration=rdict,
        )
        frames_phasor, frames_intensity, _ = frames

        roi = np.random.rand(*siffreader.frame_shape()) > 0.3

        flat_roi = siffreader.get_roi_1d_flim(
            roi, frames = framelist,
            params = TEST_PARAMS, flim_method = 'phasor', registration=rdict,
        ) 

        phasor, intensity, _ = flat_roi

        assert (phasor.dtype == np.complex128)
        assert (intensity.dtype == np.uint16)
        assert phasor.shape == (len(framelist), np.sum(roi))
        
        assert np.allclose(
            frames_intensity[:, roi],
            intensity,
        )
    
        assert np.allclose(
            frames_phasor[:, roi],
            phasor,
            equal_nan = True,
        )

        # Volume with registration
        NUM_ROIS = 7
        roi_vol = np.random.rand(NUM_ROIS, *siffreader.frame_shape()) > 0.3

        together = siffreader.get_roi_1d_flim(roi_vol,
            frames = framelist,
            params = TEST_PARAMS, flim_method = 'phasor', registration=rdict,
        )

        together_phasor, together_intensity, _ = together
        assert (together_phasor.dtype == np.complex128)
        assert (together_intensity.dtype == np.uint16)
        # assert (together_phasor.shape[0] == int(siffreader.num_frames()/ NUM_ROIS))
        assert (together_phasor.shape[0] == len (framelist) // NUM_ROIS)
        # frames_phasor = frames_phasor[:int(siffreader.num_frames()/ NUM_ROIS)* NUM_ROIS]
        frames_phasor = frames_phasor[:int(len(framelist)// NUM_ROIS) * NUM_ROIS]
        frames_phasor = frames_phasor.reshape(
            (
                int(len(framelist) // NUM_ROIS),
                NUM_ROIS,
                *siffreader.frame_shape()
            )
        )

        frames_intensity = frames_intensity[:int(len(framelist)// NUM_ROIS) * NUM_ROIS]
        frames_intensity = frames_intensity.reshape(
            (
                int(len(framelist) // NUM_ROIS),
                NUM_ROIS,
                *siffreader.frame_shape()
            )
        )

        masked_phasor = frames_phasor[:, roi_vol]
        masked_intensity = frames_intensity[:, roi_vol]

        assert np.allclose(
            masked_intensity,
            together_intensity,
        )

        assert np.allclose(
            masked_phasor,
            together_phasor,
            equal_nan = True,
        )


def test_sum_2d_mask(siffreaders):

    for siffreader in siffreaders:
        siffreader : SiffIO
        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        framelist = list(range(N_FRAMES))

        roi = np.random.rand(*siffreader.frame_shape()) > 0.3

        test_params = FLIMParams(
            Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
            Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
            Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
        )

        lifetime_full, intensity_full, _ = siffreader.flim_map(roi, test_params, frames = framelist, registration=None)
        lifetime, intensity, _ = siffreader.sum_roi_flim(roi, test_params, frames = framelist, registration=None)

        assert np.allclose(
            intensity_full[:, roi].sum(axis = 1),
            intensity,
        )

        assert np.allclose(
            (
                (lifetime_full[:, roi] * intensity_full[:, roi]).sum(axis = 1, keepdims=True)
                / intensity_full[:, roi].sum(axis = 1, keepdims=True)
            ).flatten(),
            lifetime,
        )

        dummy_reg = {
            k : (
            int(np.random.uniform(low = -128, high = 128)) % 128,
            int(np.random.uniform(low = -128, high = 128)) % 128
            ) for k in range(N_FRAMES)
        }

        framelist = list(range(N_FRAMES))

        siffreader.sum_roi_flim(roi, test_params, frames = framelist, registration=None)

        NUM_MASKS = 5
        masks = np.random.rand(NUM_MASKS, *siffreader.frame_shape()) > 0.3


        lifetimes, intensities, _ = siffreader.sum_rois_flim(masks, test_params, frames = framelist, registration=None)

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

        dummy_mpfp = MultiFLIMParamsDummy(
            Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
            Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
            FractionalIrf(offset = 1.1, sigma = 0.2, frac = 0.5, units = 'nanoseconds'),
            FractionalIrf(offset = 4.1, sigma = 0.2, frac = 0.5, units = 'nanoseconds'),
        )

        siffreader.sum_rois_flim(masks, dummy_mpfp, frames = framelist, registration=dummy_reg)[0]

        siffreader.sum_rois_flim(masks, dummy_mpfp, frames = framelist, registration=None)[0]

        lifetimes, intensities, _ = siffreader.sum_rois_flim(masks, dummy_mpfp, frames = framelist, registration=dummy_reg)

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

        dummy_mpfps = MultiFLIMParamsDummy(
            Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
            Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
            FractionalIrf(offset = 1.1, sigma = 0.2, frac = 0.5, units = 'nanoseconds'),
            FractionalIrf(offset = 4.1, sigma = 0.2, frac = 0.5, units = 'nanoseconds'),
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

            siffreader.sum_roi_flim(three_d_roi, dummy_mpfps, frames = framelist, registration=dummy_reg)[0]

            siffreader.sum_roi_flim(three_d_roi, dummy_mpfps, frames = framelist, registration=None)[0]
