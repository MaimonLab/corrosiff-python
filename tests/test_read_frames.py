import numpy as np

def test_read_frames(siffreaders):

    for siffreader in siffreaders:
        siffreader.get_frames(registration=None)

        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        dummy_reg = {
            k : (
            int(np.random.uniform(low = -128, high = 128)) % 128,
            int(np.random.uniform(low = -128, high = 128)) % 128
            ) for k in range(N_FRAMES)
        }
        framelist = list(range(N_FRAMES))

        siffreader.get_frames(frames = framelist, registration=dummy_reg)

def test_sum_2d_mask(siffreaders):

    for siffreader in siffreaders:

        roi = np.random.rand(*siffreader.frame_shape()) > 0.3
        siffreader.sum_roi(roi, registration=None)

        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        dummy_reg = {
            k : (
            int(np.random.uniform(low = -128, high = 128)) % 128,
            int(np.random.uniform(low = -128, high = 128)) % 128
            ) for k in range(N_FRAMES)
        }
        framelist = list(range(N_FRAMES))

        siffreader.sum_roi(roi, frames = framelist, registration=dummy_reg)

        NUM_ROIS = 7
        rois = np.random.rand(NUM_ROIS, *siffreader.frame_shape()) > 0.3

        siffreader.sum_rois(rois, registration=None)
        together = siffreader.sum_rois(rois, frames = framelist, registration=dummy_reg)

        for k in range(NUM_ROIS):
            assert (
                together[k] == siffreader.sum_roi(rois[k], frames = framelist, registration=dummy_reg)
            ).all()

def test_sum_3d_mask(siffreaders):

    for siffreader in siffreaders:

        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        NUM_PLANES = 7

        rois = [np.random.rand(k, *siffreader.frame_shape()) > 0.3 for k in range(1,NUM_PLANES)]

        # Validate that they both cycle through the same way
        # Seems like more of a `SiffPy` test than a `corrosiffpy` test
        for k in range(1,NUM_PLANES):

            N_FRAMES_P = N_FRAMES - N_FRAMES % k
            this_roi = rois[k-1]

            # Rust API is consistent
            assert (
                np.array([
                    siffreader.sum_roi(this_roi[p], frames = list(range(p, N_FRAMES_P ,k)),registration=None)
                    for p in range(k)
                ]).T.flatten()
                == siffreader.sum_roi(
                    this_roi, frames = list(range(N_FRAMES_P)), registration=None
                ).flatten()
            ).all()


def test_sum_2d_masks(siffreaders):

    for siffreader in siffreaders:
        NUM_MASKS = 7

        rois_list = [np.random.rand(k, *siffreader.frame_shape()) > 0.3 for k in range(1,NUM_MASKS+1)]

        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        for n_masks, rois in enumerate(rois_list):
            N_FRAMES_R = N_FRAMES - N_FRAMES % NUM_MASKS
          
            # Rust API is consistent
            assert (
                np.array([
                    siffreader.sum_roi(rois[k], frames = list(range(N_FRAMES_R)) ,registration=None)
                    for k in range(n_masks+1)
                ]).flatten()
                == siffreader.sum_rois(
                    rois, frames = list(range(N_FRAMES_R)), registration=None
                ).flatten()
            ).all()

def test_sum_3d_masks(siffreaders):

    for siffreader in siffreaders:
        NUM_MASKS = 7
        N_PLANES = 3

        rois_list = [np.random.rand(k, N_PLANES, *siffreader.frame_shape()) > 0.3 for k in range(1,NUM_MASKS+1)]

        N_FRAMES = min(
            siffreader.num_frames(),
            10000
        )

        for n_masks, rois in enumerate(rois_list):

            N_FRAMES_PM = N_FRAMES - N_FRAMES % (NUM_MASKS* N_PLANES)

            # Rust API is consistent
            assert (
                np.array([
                    siffreader.sum_roi(rois[k].squeeze(), frames = list(range(N_FRAMES_PM)) ,registration=None)
                    for k in range(n_masks+1)
                ]).flatten()
                == siffreader.sum_rois(
                    rois, frames = list(range(N_FRAMES_PM)), registration=None
                ).flatten()
            ).all()