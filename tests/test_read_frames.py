import corrosiffpy
import numpy as np

def test_read_frames(siffreader):

    assert siffreader.get_frames(registration=None)

    dummy_reg = {
        k : (
        int(np.random.uniform(low = -128, high = 128)) % 128,
        int(np.random.uniform(low = -128, high = 128)) % 128
        ) for k in range(10000)
    }
    framelist = list(range(10000))

    assert siffreader.get_frames(frames = framelist, registration=dummy_reg)

def test_sum_2d_mask(siffreader):

    roi = np.random.rand(*siffreader.frame_shape()) > 0.3
    assert siffreader.sum_roi(roi, registration=None)

    dummy_reg = {
        k : (
        int(np.random.uniform(low = -128, high = 128)) % 128,
        int(np.random.uniform(low = -128, high = 128)) % 128
        ) for k in range(10000)
    }
    framelist = list(range(10000))

    assert siffreader.sum_roi(roi, frames = framelist, registration=dummy_reg)

    NUM_ROIS = 7
    rois = np.random.rand(NUM_ROIS, *siffreader.frame_shape()) > 0.3

    assert siffreader.sum_rois(rois, registration=None)
    assert siffreader.sum_rois(rois, frames = framelist, registration=dummy_reg)

def test_sum_3d_mask(siffreader):

    NUM_PLANES = 7

    rois = [np.random.rand(k, *siffreader.frame_shape()) > 0.3 for k in range(1,NUM_PLANES)]

    complicated_rois = [np.random.rand(11, k, *siffreader.frame_shape()) > 0.3 for k in range(1,NUM_PLANES)]
    N_FRAMES = 10000
#     # Validate that they both cycle through the same way
#     # Seems like more of a `SiffPy` test than a `corrosiffpy` test
    for k in range(1,NUM_PLANES):

        # Rust API is consistent
        assert (
            np.array([
                siffreader.sum_roi(rois[k-1][p], frames = list(range(p, N_FRAMES ,k)),registration=None)
                for p in range(k)
            ]).T.flatten()
            == siffreader.sum_roi(
                rois[k-1], frames = list(range(N_FRAMES)), registration=None
            ).flatten()
        ).all()

#         # Whole volume agrees
        assert siffreader.sum_roi(rois[k-1], frames = list(range(N_FRAMES)), registration=None)
        assert siffreader.sum_rois(complicated_rois[k-1], frames = list(range(N_FRAMES)), registration=None)

    def test_sum_2d_masks(siffreader):

        NUM_MASK_MAX = 7

        rois = [np.random.rand(k, *siffreader.frame_shape()) > 0.3 for k in range(1,NUM_MASK_MAX)]

        # Validate that they both cycle through the same way
        for k in range(1,NUM_PLANES):
            N_FRAMES = 10000 - (10000 % k)
            # Rust API is consistent
            assert (
                np.array([
                    siffreader.sum_rois(rois[k-1][p], frames = list(range(p, N_FRAMES ,k)),registration=None)
                    for p in range(k)
                ]).T.flatten()
                == siffreader.sum_rois(
                    rois[k-1], frames = list(range(N_FRAMES)), registration=None
                ).flatten()
            ).all()

            # Whole volume agrees
            assert siffreader.sum_rois(rois[k-1], frames = list(range(N_FRAMES)), registration=None)