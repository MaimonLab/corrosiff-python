"""
CorrosiffPy
-----------

`corrosiffpy` is a `Python` wrapper for the `Rust` `corrosiff` package,
used for reading and parsing data from the FLIM-data `.siff` filetype.

Its primary tool is the `SiffIO` class, which wraps `corrosiff`'s
`SiffReader` struct. There are a few minorly questionable design
decisions here made to remain consistent with the `C++`-based
`siffreadermodule` extension module.
"""
from typing import Any, Tuple, List, Dict, Optional, Union

import numpy as np

from siffpy import FLIMParams

def open_file(filename : str)->'SiffIO':...

class SiffIO():
    """
    This class is a wrapper for the Rust `corrosiff` library.

    Controls file reading and formats data streams into
    `numpy` arrays, `Dict`s, etc.
    """
    @property
    def filename(self)->str:
        """The name of the file being read"""
        ...

    def get_file_header(self)->Dict:
        """
        Returns a dictionary containing some of the primary
        metadata of the file for `Python` to access.

        ## Returns

        * `Dict`
            A dictionary containing the metadata of the file.
            Keys and values are:

            - `Filename` : str
                The name of the file being read.
            
            - `BigTiff` : bool
                Whether the file uses the BigTiff format.
            
            - `IsSiff` : bool
                Whether the file is a `.siff` file or a `.tiff` file.

            - `Number of frames` : int
                The number of frames in the file, including flyback.

            - `Non-varying frame data` : str
                A string containing the non-varying frame data as
                one long block string with many newlines.

            - `ROI string` : str
                A string containing the MultiROi data of the file
                file in one long string, straight from ScanImage.

        ## Examples

            ```python
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Get the file header
            header = siffio.get_file_header()
            print(header)
            ```
        
        """
        ...


    def get_num_frames(self)->int:
        """
        Number of frames (including flyback)
        """
        ...

    def frame_shape(self)->Tuple[int, int]:
        """
        Returns the shape of the frames in the file.

        Raises a `ValueError` if the frames do not have a consistent
        shape (e.g. multiple sized ROIs).

        ## Example

        ```python

        import corrosiffpy

        # Load the file
        filename = '/path/to/file.siff'
        siffio = corrosiffpy.open_file(filename)

        # Get the frame shape
        frame_shape = siffio.frame_shape()

        print(frame_shape)

        >>> (128,128)
        ```
        """

    def get_frame_metadata(self, frames : Optional[List[int]] = [])->List[Dict]:
        """
        Retrieves metadata for the requested frames as
        a list of dictionaries. If no frames are requested,
        retrieves metadata for all frames. This is probably
        the slowest method of retrieving frame-specific
        data, because the list of dictionaries means that
        it's constrained by the GIL to parse one frame
        at a time, rather than multithreading. Probably
        can be bypassed with better code -- I almost never
        use this method so it's not a priority for me!

        ## Arguments

        * `frames` : List[int] (optional)
            A list of frames for which to retrieve metadata.
            If `None`, retrieves metadata for all frames.

        ## Returns

        * `List[Dict]`
            A list of dictionaries containing metadata for
            each frame.

        ## Example

            ```python
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Get the metadata for the first 1000 frames
            metadata = siffio.get_frame_metadata(list(range(1000)))

            # Print the metadata for the tenth frame
            print(metadata[10])
            >>> {'width': 128, 'height': 128, 'bits_per_sample': 64,
            'compression': 1, 'photometric_interpretation': 1, 'end_of_ifd': 184645,
            'data_offset': 184946, 'samples_per_pixel': 1, 'rows_per_strip': 128,
            'strip_byte_counts': 15432, 'x_resolution': 0, 'y_resolution': 0,
            'resolution_unit': 3, 'sample_format': 1, 'siff_tag': 0,
            'Frame metadata': 'frameNumbers = 10\\nframeNumberAcquisition = 10\
            \\nframeTimestamps_sec = 0.422719\\nsync Stamps = 32812\\n\
            mostRecentSystemTimestamp_epoch = 1713382944962882600\\nacqTriggerTimestamps_sec = \
            \\nnextFileMarkerTimestamps_sec = \\nendOfAcquisition = \\nendOfAcquisitionMode = \
            \\ndcOverVoltage = 0\\nepoch = 1713382945498920800\\n'
            }
            ```
        """
        ...


    def get_frames(
        self,
        frames : Optional[List[int]] = None,
        registration : Optional[Dict] = {},
    )->'np.ndarray[Any, np.dtype[np.uint16]]':
        """
        Retrieves frames from the file without
        respect to dimension or flyback.

        ## Arguments

        * `frames : Optional[List[int]]`
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        * `registration : Optional[Dict]`
            A dictionary containing registration information
            (the keys correspond to the frame number, the values
            are tuples of (y,x) offsets). If an empty dict or None, will
            be treated as if no registration is required.
            Otherwise will raise an error if there are requested frames
            that are not in the dictionary.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint16]]`
            A numpy array containing the frames in the
            order they were requested.

        ## Example
            
            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Get the data as an array
            frame_data = siffio.get_frames(list(range(1000)))
            print(frame_data.shape, frame_data.dtype)

            >>> ((1000, 512, 512), np.uint16)
            ```

        """
        ...

    # def pool_frames(
    #     self,
    #     frames : List[int],
    #     flim : bool = False,
    #     registration : Optional[Dict] = None,
    # )->'np.ndarray[Any, np.dtype[np.uint16]]':
    #     """ NOT IMPLEMENTED """

    def flim_map(
        self,
        params : Optional['FLIMParams'],
        frames : Optional[List[int]],
        confidence_metric : str = 'chi_sq',
        flim_method : str = 'empirical lifetime',
        registration : Optional[Dict] = None,
    ) -> Tuple[
        Union['np.ndarray[Any, np.dtype[np.float64]]', 'np.ndarray[Any, np.dtype[np.complex128]]'],
        'np.ndarray[Any, np.dtype[np.uint16]]',
        'np.ndarray[Any, np.dtype[np.float64]]'
        ]:
        """
        Returns a tuple of `(flim_map, intensity_map, confidence_map)`
        where flim_map is the empirical lifetime with the offset of
        params subtracted. WARNING! This is DIFFERENT from the `siffreadermodule`
        implementation, which returns ONLY the empirical lifetime! This
        returns the empirical lifetime, the intensity, and the confidence
        map (well, the confidence map is tbd).

        ## Arguments

        * `params` : FLIMParams
            The FLIM parameters to use for the analysis. The offset
            term will be subtracted from the empirical lifetime values.
            If `None`, the offset will be 0.

        * `frames` : List[int]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        * `confidence_metric` : str
            The metric to use for the confidence map. Can be 'chi_sq'
            or 'p_value'. Currently not actually used!

        * `flim_method` : str
            The method to use for the FLIM analysis. Can be 'empirical lifetime'
            or 'phasor'. Currently only 'empirical lifetime' and 'phasor' are implemented.

        * `registration` : Dict
            A dictionary containing registration information
            (the keys correspond to the frame number, the values
            are tuples of (y,x) offsets).

        ## Returns

        * `Tuple[np.ndarray[Any, np.dtype[np.float64]], np.ndarray[Any, np.dtype[np.uint16]], np.ndarray[Any, np.dtype[np.float64]]]`
            A tuple of three numpy arrays containing the lifetime data (as float64 or complex128, depending on if it's
            empirical lifetime or phasor data),
            the intensity data (as uint16), and the confidence data (as float64 or None).

        ## Example

            ```python
            import numpy as np
            import corrosiffpy
            from siffpy.core.flim import FLIMParams, Exp, Irf

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Get the data as an array
            frame_data = siffio.get_frames(list(range(1000)))

            # Get the FLIM data
            test_params = FLIMParams(
                Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
                Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
                Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
            )

            flim_map, intensity_map, confidence_map = siffio.flim_map(test_params, list(range(1000)))

            print(flim_map.shape, flim_map.dtype)
            >>> ((1000, 512, 512), np.float64)

            assert intensity_map == frame_data

            ```


        """
        ...

    def get_frames_full(
        self,
        frames : Optional[List[int]] = None,
        registration : Optional[Dict] = None,
    ) -> 'np.ndarray[Any, np.dtype[np.uint16]]':
        """
        Returns a full-dimensioned array:
        (frames, y, x, arrival_time). This is a
        large array -- with 20 picosecond arrival
        time bins and an 80 MHz laser this is 
        ~600x bigger than the usual image array!

        ## Arguments

        * `frames` : Optional[List[int]]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        * `registration` : Optional[Dict]
            A dictionary containing registration information
            (the keys correspond to the frame number, the values
            are tuples of (y,x) offsets). If None, no registration
            will be applied.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint16]]`
            A numpy array containing the pixelwise arrival time
            histograms for all frames requested. Dimensions are
            `(frames.len(), y, x, arrival_time_bins)`

        ## Example

            ```python
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Get the data as an array
            frame_data = siffio.get_frames_full(list(range(1000)))

            print(frame_data.shape, frame_data.dtype)
            # This is a 330 GB array!!
            >>> ((1000, 512, 512, 629), np.uint16)
            ```

        ## See also

        - `get_frames` : For just the intensity data

        - `flim_map` : For average arrival time + intensity data. 
        """
        ...

    def sum_roi(
        self,
        mask : 'np.ndarray[Any, np.dtype[bool]]',
        *,
        frames : Optional[List[int]] = None,
        registration : Optional[Dict] = None,
    ) -> 'np.ndarray[Any, np.dtype[np.uint64]]':
        """
        Mask may have 2 or 3 dimensions, but
        if so then be aware that the frames will be
        iterated through sequentially, rather than
        aware of the correspondence between frame
        number and mask dimension. Returns a 1D
        array of the same length as the frames
        provided, regardless of mask shape.

        ## Arguments

        * `mask` : np.ndarray[Any, np.dtype[bool]]
            A boolean mask of the same shape as the frames
            to be summed (if to be applied to all the frames).
            If it's a 3D mask, the slowest dimension is assumed
            to be a `z` dimension and cycles through the frames
            provided, i.e. `mask[0]` is applied to `frames[0]`,
            `mask[1]` is applied to `frames[1]`, ... `mask[k]` is
            applied to `frames[n]` where `k = n % mask.shape[0]`.

        * `frames` : Optional[List[int]]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        * `registration` : Optional[Dict]
            A dictionary containing registration information
            (the keys correspond to the frame number, the values
            are tuples of (y,x) offsets). If None, no registration
            will be applied.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint64]]`

        ## Example

            A single 2D mask

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file

            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Create a mask from random numbers
            roi = np.random.rand(*siffio.frame_shape()) > 0.3

            # Sum the ROI
            masked = siffio.sum_roi(roi, frames = list(range(1000)))

            print(masked.shape, masked.dtype)
            >>> ((1000,), np.uint64)
            ```

            A single 3D mask corresponding to
            planes of the ROI.

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file

            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Create a mask from random numbers
            # (10 planes)
            roi = np.random.rand(10, *siffio.frame_shape()) > 0.3

            # Sum the ROI
            masked = siffio.sum_roi(roi, frames = list(range(1000)))

            # Still the same shape -- corresponds to
            each frame requested.
            print(masked.shape, masked.dtype)
            >>> ((1000,), np.uint64)
            ```

        ## See also

        - `sum_rois` : Summing multiple ROIs (either 2D or 3D masks)
        in one function call. Takes only slightly longer than `sum_roi`
        even with many ROIs, so this gets much more efficient than repeated
        calls to `sum_roi` for each ROI.
        - `sum_roi_flim` : The FLIM version of this function.
        """
        ...

    def sum_rois(
        self,
        masks : 'np.ndarray[Any, np.dtype[bool]]',
        *,
        frames : Optional[List[int]] = None,
        registration : Optional[Dict] = None,
    )->'np.ndarray[Any, np.dtype[np.uint16]]':
        """
        Masks may have 2 or 3 dimensions each, (i.e.
        `masks` can be 3d or 4d), but
        if 4d then be aware that the frames will be
        iterated through sequentially (see below or as in
        `sum_roi`). Returns a 2D
        array of dimensions `(len(masks), len(frames))`.

        ## Arguments

        * `masks` : np.ndarray[Any, np.dtype[bool]]
            Boolean masks. The mask dimension is the slowest
            dimension (the 0th axis) and the last two dimensions
            correspond to the y and x dimensions of the
            frames. If the array has 4 dimensions, the 1st
            dimension is assumed to be the `z` dimension and
            each ROI is presumed to _cycle through_ the frames
            along this axis. So _for each ROI_, the first frame
            will be applied to the first element on the z axis, the second frame
            will be applied to the second element on the z axis,
            etc.

            In other words: `masks[0,0,...]` is applied to `frames[0]`,
            `masks[0,1,...]` is applied to `frames[1]`, ... `masks[0,k,...]` is
            applied to `frames[n]` where `k = n % masks.shape[1]`. Likewise,
            `masks[1,0,...]` is applied to `frames[0]`, `masks[1,1,...]` is applied
            to `frames[1]`, ... `masks[1,k,...]` is applied to `frames[n]` where
            `k = n % masks.shape[1]`.

        * `frames` : Optional[List[int]]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        * `registration` : Optional[Dict]
            A dictionary containing registration information
            (the keys correspond to the frame number, the values
            are tuples of (y,x) offsets). If None, no registration
            will be applied.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint64]]`
            The returned value is a 2D array corresponding to each
            ROI applied to the frames requested. Is dimension
            `(len(masks), len(frames))` with the `i,j`th element
            corresponding to the sum of the `i`th ROI mask applied to
            the `j`th element of the argument `frames`.

        ## Example

        A set of 2d masks
            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Create a list of masks from random numbers
            # 7 masks, 2d masks
            rois = np.random.rand(7, *siffio.frame_shape()) > 0.3

            # Sum the ROIs
            masked = siffio.sum_rois(rois, frames = list(range(1000)))

            print(masked.shape, masked.dtype)
            >>> ((7, 1000), np.uint64)
            ```

        A set of 3d masks
            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Create a list of masks from random numbers
            # 7 masks, 3d masks with 4 planes
            rois = np.random.rand(7, 4, *siffio.frame_shape()) > 0.3

            # Sum the ROIs
            masked = siffio.sum_rois(rois, frames = list(range(1000)))

            print(masked.shape, masked.dtype)
            >>> ((7, 1000), np.uint64)
            ```

        ## See also

        - `sum_roi` : Summing a single ROI mask.
        - `sum_rois_flim` : The FLIM version of this function.
            
        """
        ...

    def sum_roi_flim(
        self,
        mask : 'np.ndarray[Any, np.dtype[bool]]',
        params : Optional['FLIMParams'],
        frames : Optional[List[int]] = None,
        flim_method : str = 'empirical lifetime',
        registration : Optional[Dict] = None,
    )->Tuple[
        Union['np.ndarray[Any, np.dtype[np.float64]]', 'np.ndarray[Any, np.dtype[np.complex128]]'],
        'np.ndarray[Any, np.dtype[np.uint64]]', 
        Optional['np.ndarray[Any, np.dtype[np.float64]]']
    ]:
        """
        Mask may have 2 or 3 dimensions, but
        if so then be aware that the frames will be
        iterated through sequentially, rather than
        aware of the correspondence between frame
        number and mask dimension. Returns a tuple of 1D
        arrays of the same length as the frames
        provided, regardless of mask shape.

        Converts the lifetime units to `countbins` in the
        Rust call and then converts back at the end, so
        the lifetime values are in `countbins` even though
        the `FLIMParams` argument itself might appear to
        stay in any other units. TODO: is this too heavy
        handed? Seems kind of extra to pass the `FLIMParams`
        into this function instead of just an `offset` float,
        though this lets me make it `units`-agnostic...

        WARNING! This is DIFFERENT from the `siffreadermodule`
        implementation, which returns ONLY the empirical lifetime! This
        returns the empirical lifetime, the intensity, and the confidence
        map (well, the confidence map is tbd).

        ## Arguments

        * `mask` : np.ndarray[Any, np.dtype[bool]]
            A boolean mask of the same shape as the frames
            to be summed (if to be applied to all the frames).
            If it's a 3D mask, the slowest dimension is assumed
            to be a `z` dimension and cycles through the frames
            provided, i.e. `mask[0]` is applied to `frames[0]`,
            `mask[1]` is applied to `frames[1]`, ... `mask[k]` is
            applied to `frames[n]` where `k = n % mask.shape[0]`.
        
        * `params` : Optional[FLIMParams]
            The FLIM parameters to use for the analysis. The offset
            term will be subtracted from the empirical lifetime values.
            If `None`, the offset will be 0.

        * `frames` : Optional[List[int]]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        * `flim_method` : str
            The method to use for the FLIM analysis. Can be 'empirical lifetime'
            or 'phasor'. Currently only 'empirical lifetime' and 'phasor' are implemented.

        * `registration` : Optional[Dict]
            A dictionary containing registration information
            (the keys correspond to the frame number, the values
            are tuples of (y,x) offsets). If None, no registration
            will be applied.

        ## Returns

        Tuple['np.ndarray[Any, np.dtype[np.float64]]', 'np.ndarray[Any, np.dtype[np.uint64]]', 'np.ndarray[Any, np.dtype[np.float64]]']
            A tuple of three numpy arrays containing, in order:
                1) the empirical lifetime data (as float64) in units of
                arrival time bins (countbins) with the offset of
                params subtracted,
                2) the summed intensity data (as uint64),
                3) the confidence data (as float64 or None).

        ## Example

            A single 2D mask

            ```python
            import numpy as np
            import corrosiffpy
            from siffpy.core.flim import FLIMParams, Exp, Irf

            # Load the file

            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Create a mask from random numbers
            roi = np.random.rand(*siffio.frame_shape()) > 0.3

            params = FLIMParams(
                Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
                Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
                Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
            )
            # Sum the ROI.
            lifetime, intensity, _ = siffio.sum_roi_flim(params, roi, frames = list(range(1000)))

            print(lifetime.shape, lifetime.dtype)
            >>> ((1000,), np.float64)

            print(intensity.shape, intensity.dtype)
            >>> ((1000,), np.uint64)

            ```

            A single 3D mask corresponding to
            planes of the ROI.

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file

            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Create a mask from random numbers
            # (10 planes)
            roi = np.random.rand(10, *siffio.frame_shape()) > 0.3

            params = FLIMParams(
                Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
                Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
                Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
            )

            # Sum the ROI
            lifetime, intensity, _ = siffio.sum_roi_flim(params, roi, frames = list(range(1000)))

            # Still the same shape -- corresponds to
            each frame requested.
            print(lifetime.shape, lifetime.dtype)
            >>> ((1000,), np.float64)

            print(masked.shape, masked.dtype)
            >>> ((1000,), np.uint64)
            ```

        ## See also

        - `sum_rois_flim` : Summing multiple ROIs (either 2D or 3D masks)
        in one function call. Takes only slightly longer than `sum_roi`
        even with many ROIs, so this gets much more efficient than repeated
        calls to `sum_roi` for each ROI.
        - `sum_roi` : The intensity-only version of this function.
        """
        ...

    def sum_rois_flim(
        self,
        masks : 'np.ndarray[Any, np.dtype[bool]]',
        params : Optional['FLIMParams'],
        frames : Optional[List[int]] = None,
        flim_method : str = 'empirical lifetime',
        registration : Optional[Dict] = None,
    ) -> Tuple[
        Union['np.ndarray[Any, np.dtype[np.float64]]', 'np.ndarray[Any, np.dtype[np.complex128]]'],
        'np.ndarray[Any, np.dtype[np.uint64]]',
        Optional['np.ndarray[Any, np.dtype[np.float64]]']
    ]:
        """
        Masks may have 2 or 3 dimensions each, (i.e.
        `masks` can be 3d or 4d), but
        if 4d then be aware that the frames will be
        iterated through sequentially (see below or as in
        `sum_roi`). Returns a 2D
        array of dimensions `(len(masks), len(frames))`.

        Converts the lifetime units to `countbins` in the
        Rust call and then converts back at the end, so
        the lifetime values are in `countbins` even though
        the `FLIMParams` argument itself might appear to
        stay in any other units. TODO: is this too heavy
        handed? Seems kind of extra to pass the `FLIMParams`
        into this function instead of just an `offset` float,
        though this lets me make it `units`-agnostic...

        ## Arguments

        * `masks` : np.ndarray[Any, np.dtype[bool]]
            Boolean masks. The mask dimension is the slowest
            dimension (the 0th axis) and the last two dimensions
            correspond to the y and x dimensions of the
            frames. If the array has 4 dimensions, the 1st
            dimension is assumed to be the `z` dimension and
            each ROI is presumed to _cycle through_ the frames
            along this axis. So _for each ROI_, the first frame
            will be applied to the first element on the z axis, the second frame
            will be applied to the second element on the z axis,
            etc.

            In other words: `masks[0,0,...]` is applied to `frames[0]`,
            `masks[0,1,...]` is applied to `frames[1]`, ... `masks[0,k,...]` is
            applied to `frames[n]` where `k = n % masks.shape[1]`. Likewise,
            `masks[1,0,...]` is applied to `frames[0]`, `masks[1,1,...]` is applied
            to `frames[1]`, ... `masks[1,k,...]` is applied to `frames[n]` where
            `k = n % masks.shape[1]`.

        * `params` : Optional[FLIMParams]
            The FLIM parameters to use for the analysis. The offset
            term will be subtracted from the empirical lifetime values.
            If `None`, the offset will be 0.

        * `frames` : Optional[List[int]]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        * `flim_method` : str
            The method to use for the FLIM analysis. Can be 'empirical lifetime'
            or 'phasor'. Currently only 'empirical lifetime' and 'phasor' are implemented.


        * `registration` : Optional[Dict]
            A dictionary containing registration information
            (the keys correspond to the frame number, the values
            are tuples of (y,x) offsets). If None, no registration
            will be applied.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint64]]`
            The returned value is a 2D array corresponding to each
            ROI applied to the frames requested. Is dimension
            `(len(masks), len(frames))` with the `i,j`th element
            corresponding to the sum of the `i`th ROI mask applied to
            the `j`th element of the argument `frames`.

        ## Example

        A set of 2d masks
            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Create a list of masks from random numbers
            # 7 masks, 2d masks
            rois = np.random.rand(7, *siffio.frame_shape()) > 0.3

            # Sum the ROIs
            masked = siffio.sum_rois(rois, frames = list(range(1000)))

            print(masked.shape, masked.dtype)
            >>> ((7, 1000), np.uint64)
            ```

        A set of 3d masks
            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Create a list of masks from random numbers
            # 7 masks, 3d masks with 4 planes
            rois = np.random.rand(7, 4, *siffio.frame_shape()) > 0.3

            # Sum the ROIs
            masked = siffio.sum_rois(rois, frames = list(range(1000)))

            print(masked.shape, masked.dtype)
            >>> ((7, 1000), np.uint64)
            ```

        ## See also

        - `sum_roi_flim` : Summing a single ROI mask.
        - `sum_rois` : The intensity-only version of this function.
            
        """
        ...

    def get_histogram(
        self,
        frames : Optional[List[int]] = None,
    )-> 'np.ndarray[Any, np.dtype[np.uint64]]':
        """
        Retrieves the arrival time histogram from the
        file. Width of the histogram corresponds to the
        number of BINS in the histogram. All frames are compressed
        onto the one axis. For the time units
        of the histogram, use the metadata.

        ## Arguments

        * `frames` : List[int]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint64]]`
            A numpy array containing the histogram of dimensions
            (`num_bins`, )

        ## Example

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            hist = siffio.get_histogram(frames = list(range(1000)))
            print(hist.shape, hist.dtype)

            # 629 time bins with a 20 picosecond resolution
            # = 12.58 nanoseconds, ~ 80 MHz
            >>> ((629,), np.uint64)

            ```
        
        ## See also

        - `get_histogram_by_frames` : The framewise version of this function,
        returns the same data but with the frames as the slowest dimension 
        (this is actually what's being called from `Rust`, then it's summed into
        a single axis in this function call)

        - `get_histogram_masked` : The masked version of this function.
        """
        ...

    def get_histogram_by_frames(
        self,
        frames : Optional[List[int]] = None,
    )-> 'np.ndarray[Any, np.dtype[np.uint64]]':
        """
        Retrieves the arrival time histogram from the
        file. Width of the histogram corresponds to the
        number of BINS in the histogram. For the time units
        of the histogram, use the metadata.

        ## Arguments

        * `frames` : List[int]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint64]]`
            A numpy array containing the histogram of dimensions
            (`frames.len()`, `num_bins`)

        ## Example

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            hist = siffio.get_histogram_by_frames(frames = list(range(1000)))
            print(hist.shape, hist.dtype)

            # 629 time bins with a 20 picosecond resolution
            # = 12.58 nanoseconds, ~ 80 MHz
            >>> ((1000, 629), np.uint64)

            ```
        """
        ...

    def get_histogram_masked(
        self,
        mask : 'np.ndarray[Any, np.dtype[bool]]',
        frames : Optional[List[int]] = None,
        registration : Optional[Dict] = None,
    )-> 'np.ndarray[Any, np.dtype[np.uint64]]':
        """
        Returns a framewise histogram of the arrival
        times of the photons in the mask.

        ## Arguments

        * `mask` : np.ndarray[Any, np.dtype[bool]]
            A boolean mask of the same shape as the frames
            to be summed.

        * `frames` : List[int]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        * `registration` : Optional[Dict]
            A dictionary containing registration information
            (the keys correspond to the frame number, the values
            are tuples of (y,x) offsets). If None, no registration
            will be applied.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint64]]`
            A numpy array containing the histogram of dimensions
            (`frames.len()`, `num_bins`). The histogram is
            of the arrival times of the photons in the mask, with
            each bin corresponding to an arrival time bin (so the
            metadata must be read to transform this into real time units
            like nanoseconds).

        ## Example

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            # Create a mask from random numbers
            roi = np.random.rand(*siffio.frame_shape()) > 0.3

            hist = siffio.get_histogram_masked(roi, frames = list(range(1000)))
            print(hist.shape, hist.dtype)

            # 629 time bins with a 20 picosecond resolution
            # = 12.58 nanoseconds, ~ 80 MHz
            >>> ((1000, 629), np.uint64)
            ```

        ## See also

        - `get_histogram` : The unmasked version of this function.
        """

    def get_experiment_timestamps(
        self,
        frames : Optional[List[int]] = None,
    )->'np.ndarray[Any, np.dtype[np.float64]]':
        """
        Returns an array of timestamps of each frame based on
        counting laser pulses since the start of the experiment.

        Units are seconds.

        Extremely low jitter, small amounts of drift (maybe 50 milliseconds an hour).

        ## Arguments

        * `frames` : List[int]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.float64]]`
            Seconds since the beginning of the microscope acquisition.

        ## Example

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            time_exp = siffio.get_experiment_timestamps(frames = list(range(1000)))
            print(time_exp.shape, time_exp.dtype)

            >>> ((1000,), np.float64)
            ```
        
        ## See also
        - `get_epoch_timestamps_laser`
        - `get_epoch_timestamps_system`
        - `get_epoch_both`
        """
        ...

    def get_epoch_timestamps_laser(
            self,
            frames : Optional[List[int]] = None,
        )->'np.ndarray[Any, np.dtype[np.uint64]]':
        """
        Returns an array of timestamps of each frame based on
        counting laser pulses since the start of the experiment.
        Extremely low jitter, small amounts of drift (maybe 50 milliseconds an hour).

        Can be corrected using get_epoch_timestamps_system.

        ## Arguments

        * `frames` : List[int]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint64]]`
            Nanoseconds since epoch, counted by tallying
            laser sync pulses and using an estimated sync rate.

        ## Example

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            time_laser = siffio.get_epoch_timestamps_laser(frames = list(range(1000)))
            print(time_laser.shape, time_laser.dtype)

            >>> ((1000,), np.uint64)
            ```

        ## See also
        - `get_epoch_timestamps_system`
        - `get_epoch_both`
        """
        ...

    def get_epoch_timestamps_system(
            self,
            frames : Optional[List[int]] = None,
        )->'np.ndarray[Any, np.dtype[np.uint64]]':
        """
        Returns an array of timestamps of each frame based on
        the system clock. High jitter, but no drift.

        WARNING if system timestamps do not exist, the function
        will throw an error. Unlike `siffreadermodule`/the `C++`
        module, this function will not crash the Python interpreter.

        ## Arguments

        * `frames` : List[int]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint64]]`
            Nanoseconds since epoch, measured using
            the system clock of the acquiring computer.
            Only called about ~1 time per second, so
            this will be the same number for most successive
            frames.

        ## Example

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            time_system = siffio.get_epoch_timestamps_system(frames = list(range(1000)))
            print(time_system.shape, time_system.dtype)

            >>> ((1000,), np.uint64)
            ```

        ## See also

        - `get_epoch_timestamps_laser`
        - `get_epoch_both`
        """
        ...

    def get_epoch_both(
            self, 
            frames : Optional[List[int]] = None,
        )->'np.ndarray[Any, np.dtype[np.uint64]]':
        """
        Returns an array containing both the laser timestamps
        and the system timestamps.

        The first row is laser timestamps, the second
        row is system timestamps. These can be used to correct one
        another

        WARNING if system timestamps do not exist, the function
        will throw an error. Unlike `siffreadermodule`/the `C++`
        module, this function will not crash the Python interpreter!

        ## Arguments

        * `frames` : List[int]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        ## Returns

        * `np.ndarray[Any, np.dtype[np.uint64]]`
            Nanoseconds since epoch, measured using
            the laser pulses in the first row and the system
            clock calls in the second row.

        ## Example

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            time_both = siffio.get_epoch_both(frames = list(range(1000)))
            print(time_both.shape, time_both.dtype)

            >>> ((2, 1000), np.uint64)
            ```

        ## See also

        - `get_epoch_timestamps_laser`
        - `get_epoch_timestamps_system`
        """
        ...

    def get_appended_text(
            self,
        )->List[Tuple[int, str, Optional[float]]]:
        """
        Returns a list of strings containing the text appended
        to each frame. Only returns elements where there was appended text.
        If no frames are provided, searches all frames.

        Returns a list of tuples of (frame number, text, timestamp).

        For some versions of `ScanImageFLIM`, there is no timestamp entry,
        so the tuple for those files will be (frame number, text, None).

        ## Arguments

        * `frames` : List[int]
            A list of frames to retrieve. If `None`, all frames
            will be retrieved.

        ## Returns

        * `List[Tuple[int, str, Optional[float]]]`
            A list of tuples containing the frame number, the text
            appended to the frame, and the timestamp of the text
            (if it exists).

        ## Example

            ```python
            import numpy as np
            import corrosiffpy

            # Load the file
            filename = '/path/to/file.siff'
            siffio = corrosiffpy.open_file(filename)

            text = siffio.get_appended_text(frames = list(range(1000)))
            ```
        """
        ...
    
def siff_to_tiff(
        sourcepath : str,
        /,
        savepath : Optional[str] = None,
        mode : Optional[str] = 'ScanImage',
    )->None:
    """
    Converts a .siff file to a .tiff file containing only intensity information.

    TODO: Contain OME-TIFF metadata for more convenient ImageJ/Fiji viewing of
    output.

    ## Arguments

    - `sourcepath` : str

        Path to a .siff file (will also work for a .tiff file, though I don't know
        why you'd try that)

    - `savepath` : str

        Path to where the .tiff should be saved. If None, will be saved
        in same directory as the .siff file.

    - `mode` : str

        Either 'ScanImage' or 'OME'. If 'ScanImage', will save the tiff
        in the same format as ScanImage, with the same metadata. For
        more info about the ScanImage tiff specification, see
        https://docs.scanimage.org/Appendix/ScanImage+BigTiff+Specification.html
        
        If 'ome',
        will save the tiff as an OME-TIFF, which is more convenient for
        viewing in Fiji/ImageJ, but contaminates the metadata of the first frame.
    """
    ...

def get_start_timestamp(file_path : str) -> int:
    """
    Returns the first timestamp of the file in nanoseconds
    since the epoch.

    ## Arguments

    * `file_path` : str
        The path to the file.

    ## Returns

    * `int`
        The first timestamp of the file in nanoseconds
        since the epoch.

    ## See also

    - `get_start_and_end_timestamps`, which returns both the first
    and last timestamps of the file. Much slower because it has to
    find the last frame.

    ## Example

        ```python
        import corrosiffpy

        corrosiffpy.get_start_timestamp('/path/to/file.siff')

        >>> 1713382945416945800
        ```
    """
    ...

def get_start_and_end_timestamps(file_path : str) -> Tuple[int, int]:
    """
    Returns the first and last timestamps of the file in nanoseconds
    since the epoch.

    ## Arguments

    * `file_path` : str
        The path to the file.

    ## Returns

    * `Tuple[int, int]`
        The first and last timestamps of the file in nanoseconds
        since the epoch.

    ## See also

    - `get_start_timestamp`, runs ~10000x faster for a few GB-sized
    `.siff` file, and the gains get better with bigger files
    because it doesn't have to crawl the whole file to find the
    last frame.

    ## Example

        ```python
        import corrosiffpy

        corrosiffpy.get_start_and_end_timestamps('/path/to/file.siff')

        >>> (1713382945416945800, 1713383893239559800)
        ```
    """
    ...