//! The `SiffIO` Python class is used to call
//! the corrosiff library from Rust.

use numpy::{IntoPyArray, PyArray1, PyArray2, PyArray3, PyArray4,
    PyReadonlyArray2, PyReadonlyArray3, PyReadonlyArray4,
};
use num_complex::Complex;
use pyo3::PyTypeCheck;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};
use corrosiff::{CorrosiffError, SiffReader, FramesError};

use std::collections::HashMap;

/// Almost all of the errors that can be thrown by the `corrosiff` library
/// have standard explanations that should be converted to informative
/// `Python` exceptions.
fn _to_py_error(e : CorrosiffError) -> PyErr {
    match e {
        CorrosiffError::FramesError(frames_error) => {
            match frames_error {
                FramesError::RegistrationFramesMissing => {
                   return PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Some requested frames do not have a \
                        corresponding registration value".to_string()
                    );
                },
                FramesError::DimensionsError(dim_error) => {
                    return PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        format!("Inconsistent dimensions : {:?}", dim_error)
                    );
                },
                FramesError::IOError(io_error) => {
                    return PyErr::new::<pyo3::exceptions::PyIOError, _>(
                        format!("{:?}", io_error)
                    );
                },
                FramesError::FormatError(e)=> {
                   return PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        format!("{:?}", e)
                    )
                },
            }
        },
        CorrosiffError::DimensionsError(dim_error) => {
            return PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("{:?}", dim_error)
            )
        },
        CorrosiffError::NoSystemTimestamps => {
            return PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "No system timestamps found in file".to_string()
            );
        },
        CorrosiffError::NotImplementedError => {
            return PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
                "This method is not yet implemented".to_string()
            );
        },
        CorrosiffError::FileFormatError => {
            return PyErr::new::<pyo3::exceptions::PyIOError, _>(
                "File format error -- likely invalid or incompletely-transferred .siff file".to_string()
            );
        }
        _ => PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("{:?}", e))
    }
}

/// This class is a wrapper for the Rust `corrosiff` library.
///     Controls file reading and formats data streams into
///    `numpy` arrays, `Dict`s, etc.
#[pyclass(name = "RustSiffIO", dict, module = "corrosiff_python")]
pub struct SiffIO {
    reader: SiffReader,
}

impl SiffIO {
    /// Can be called in `Rust` packages using `corrosiff`
    /// to produce a `SiffIO` object if they interface with
    /// `Python` as well.
    pub fn new_from_reader(reader: SiffReader) -> Self {
        SiffIO { reader }
    }
}

/// The default value of frames is a Vec<u64> containing
/// all of the frames in the file. `frames_default!(frames, siffio)`
macro_rules! frames_default(
    ($frames : expr, $siffio : expr) => {
        $frames.or_else(
            || Some((0 as u64..$siffio.reader.num_frames() as u64).collect())
        ).unwrap()
    };
);

#[pymethods]
impl SiffIO {

    /// Returns the name of the open file
    #[getter]
    pub fn filename(&self) -> PyResult<String> {
        Ok(self.reader.filename())
    }

    /// Returns the number of frames in the file
    /// include flyback (basically the number of
    /// IFDs).
    #[getter]
    pub fn num_frames(&self) -> u64 {
        self.reader.num_frames() as u64
    }

    /// Back-compatibility with `siffreadermodule`...
    /// 
    /// Number of frames (including flyback)
    #[pyo3(name = "num_frames")]
    pub fn get_num_frames(&self) -> u64 {
        self.num_frames()
    }

    /// Returns a dictionary containing some of the primary
    ///     metadata of the file for `Python` to access.

    ///     ## Returns

    ///     * `Dict`
    ///         A dictionary containing the metadata of the file.
    ///         Keys and values are:

    ///         - `Filename` : str
    ///             The name of the file being read.
            
    ///         - `BigTiff` : bool
    ///             Whether the file uses the BigTiff format.
            
    ///         - `IsSiff` : bool
    ///             Whether the file is a `.siff` file or a `.tiff` file.

    ///         - `Number of frames` : int
    ///             The number of frames in the file, including flyback.

    ///         - `Non-varying frame data` : str
    ///             A string containing the non-varying frame data as
    ///             one long block string with many newlines.

    ///         - `ROI string` : str
    ///             A string containing the MultiROi data of the file
    ///             file in one long string, straight from ScanImage.

    ///     ## Examples

    ///         ```python
    /// 
    ///         import corrosiffpy

    ///         # Load the file
    ///         filename = '/path/to/file.siff'
    ///         siffio = corrosiffpy.open_file(filename)

    ///         # Get the file header
    ///         header = siffio.get_file_header()
    ///         print(header)
    /// 
    ///         ```
    #[pyo3(name = "get_file_header")]
    pub fn get_file_header_py<'py>(&self, py : Python<'py>) -> PyResult<Bound<'py, PyDict>> {

        let ret_dict = PyDict::new(py);

        ret_dict.set_item("Filename", self.reader.filename())?;
        ret_dict.set_item("BigTiff", self.reader.is_bigtiff())?;
        ret_dict.set_item("IsSiff", self.reader.is_siff())?;
        ret_dict.set_item("Number of frames", self.reader.num_frames())?;
        ret_dict.set_item("Non-varying frame data", self.reader.nvfd())?;
        ret_dict.set_item("ROI string", self.reader.roi_string())?;
        
        Ok(ret_dict)
    }

    pub fn __repr__(&self) -> String {
        format!(
            "RustSiffIO(filename={})\n
            The `SiffIO` object is implemented in Rust 
            for fast parallelizable file reading operations 
            that Python is not well-suited to perform. Its job 
            is to return `Python` objects, especially `numpy` arrays, 
            for visualization and further analysis in `Python`.
            For more information, consult `siffpy.readthedocs.io` or
            the `corrosiff` repository on Github.",
            self.reader.filename()
        )
    }

    pub fn __str__(&self) -> String {
        self.__repr__() 
    }

    /// Returns the shape of the frames in the file.

    /// Raises a `ValueError` if the frames do not have a consistent
    /// shape (e.g. multiple sized ROIs).

    /// ## Example

    /// ```python

    /// import corrosiffpy

    /// # Load the file
    /// filename = '/path/to/file.siff'
    /// siffio = corrosiffpy.open_file(filename)

    /// # Get the frame shape
    /// frame_shape = siffio.frame_shape()

    /// print(frame_shape)

    /// >>> (128,128)
    /// ```
    #[pyo3(name = "frame_shape")]
    pub fn frame_shape<'py>(&self, py : Python<'py>)-> PyResult<Bound<'py, PyTuple>> {
        self.reader.image_dims().map(
            |x| {
                PyTuple::new(py, vec![x.to_tuple().0, x.to_tuple().1])
        }).unwrap_or(
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "File frames do not have a consistent shape"
            ))
        )
    }


    /**
     * The following methods are used to read metadata (timestamps,
     * text annotations, etc.) from the file.
     */

    /// Retrieves metadata for the requested frames as
    /// a list of dictionaries. If no frames are requested,
    /// retrieves metadata for all frames. This is probably
    /// the slowest method of retrieving frame-specific
    /// data, because the list of dictionaries means that
    /// it's constrained by the GIL to parse one frame
    /// at a time, rather than multithreading. Probably
    /// can be bypassed with better code -- I almost never
    /// use this method so it's not a priority for me!

    /// ## Arguments

    /// * `frames` : List[int] (optional)
    ///     A list of frames for which to retrieve metadata.
    ///     If `None`, retrieves metadata for all frames.

    /// ## Returns

    /// * `List[Dict]`
    ///     A list of dictionaries containing metadata for
    ///     each frame.

    /// ## Example

    ///     ```python
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Get the metadata for the first 1000 frames
    ///     metadata = siffio.get_frame_metadata(list(range(1000)))

    ///     # Print the metadata for the tenth frame
    ///     print(metadata[10])
    ///     >>> {'width': 128, 'height': 128, 'bits_per_sample': 64,
    ///     'compression': 1, 'photometric_interpretation': 1, 'end_of_ifd': 184645,
    ///     'data_offset': 184946, 'samples_per_pixel': 1, 'rows_per_strip': 128,
    ///     'strip_byte_counts': 15432, 'x_resolution': 0, 'y_resolution': 0,
    ///     'resolution_unit': 3, 'sample_format': 1, 'siff_tag': 0,
    ///     'Frame metadata': 'frameNumbers = 10\\nframeNumberAcquisition = 10\
    ///     \\nframeTimestamps_sec = 0.422719\\nsync Stamps = 32812\\n\
    ///     mostRecentSystemTimestamp_epoch = 1713382944962882600\\nacqTriggerTimestamps_sec = \
    ///     \\nnextFileMarkerTimestamps_sec = \\nendOfAcquisition = \\nendOfAcquisitionMode = \
    ///     \\ndcOverVoltage = 0\\nepoch = 1713382945498920800\\n'
    ///     }
    ///     ```
    #[pyo3(signature = (frames=None))]
    pub fn get_frame_metadata<'py>(&self, py : Python<'py>, frames : Option<Vec<u64>>)
    -> PyResult<Bound<'py, PyList>> {
        
        let frames = frames_default!(frames, self);
        let metadatas = self.reader.get_frame_metadata(&frames)
            .map_err(_to_py_error)?;
        
        let ret_list = PyList::empty(py);

        for metadata in metadatas {
            let py_dict = PyDict::new(py);
            // Ugly and brute force
            py_dict.set_item("width", metadata.width)?;
            py_dict.set_item("height", metadata.height)?;
            py_dict.set_item("bits_per_sample", metadata.bits_per_sample)?;
            py_dict.set_item("compression", metadata.compression)?;
            py_dict.set_item("photometric_interpretation", metadata.photometric_interpretation)?;
            py_dict.set_item("end_of_ifd", metadata.end_of_ifd)?;
            py_dict.set_item("data_offset", metadata.data_offset)?;
            py_dict.set_item("samples_per_pixel", metadata.samples_per_pixel)?;
            py_dict.set_item("rows_per_strip", metadata.rows_per_strip)?;
            py_dict.set_item("strip_byte_counts", metadata.strip_byte_counts)?;
            py_dict.set_item("x_resolution", metadata.x_resolution)?;
            py_dict.set_item("y_resolution", metadata.y_resolution)?;
            py_dict.set_item("resolution_unit", metadata.resolution_unit)?;
            py_dict.set_item("sample_format", metadata.sample_format)?;
            py_dict.set_item("siff_tag", metadata.siff_compress)?;
            py_dict.set_item("Frame metadata", metadata.metadata_string)?;
        
            ret_list.append(py_dict)?;
        }
        Ok(ret_list)
    }

    /// Returns an array of timestamps of each frame based on
    /// counting laser pulses since the start of the experiment.

    /// Units are seconds.

    /// Extremely low jitter, small amounts of drift (maybe 50 milliseconds an hour).

    /// ## Arguments

    /// * `frames` : List[int]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.float64]]`
    ///     Seconds since the beginning of the microscope acquisition.

    /// ## Example

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     time_exp = siffio.get_experiment_timestamps(frames = list(range(1000)))
    ///     print(time_exp.shape, time_exp.dtype)

    ///     >>> ((1000,), np.float64)
    ///     ```
    
    /// ## See also
    /// - `get_epoch_timestamps_laser`
    /// - `get_epoch_timestamps_system`
    /// - `get_epoch_both`
    #[pyo3(name = "get_experiment_timestamps", signature = (frames=None))]
    pub fn get_experiment_timestamps_py<'py>(&self, py : Python<'py>, frames : Option<Vec<u64>>)
    -> PyResult<Bound<'py, PyArray1<f64>>> {
        let frames = frames_default!(frames, self);

        Ok(
            self.reader
            .get_experiment_timestamps(&frames)
            .map_err(_to_py_error)?
            .into_pyarray(py)
        )
    }

    /// Returns an array of timestamps of each frame based on
    /// counting laser pulses since the start of the experiment.
    /// Extremely low jitter, small amounts of drift (maybe 50 milliseconds an hour).

    /// Can be corrected using get_epoch_timestamps_system.

    /// ## Arguments

    /// * `frames` : List[int]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.uint64]]`
    ///     Nanoseconds since epoch, counted by tallying
    ///     laser sync pulses and using an estimated sync rate.

    /// ## Example

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     time_laser = siffio.get_epoch_timestamps_laser(frames = list(range(1000)))
    ///     print(time_laser.shape, time_laser.dtype)

    ///     >>> ((1000,), np.uint64)
    ///     ```

    /// ## See also
    /// - `get_epoch_timestamps_system`
    /// - `get_epoch_both`
    #[pyo3(name = "get_epoch_timestamps_laser", signature = (frames=None))]
    pub fn get_epoch_timestamps_laser_py<'py>(&self, py : Python<'py>, frames : Option<Vec<u64>>)
    -> PyResult<Bound<'py, PyArray1<u64>>> {
        let frames = frames_default!(frames, self);

        Ok(
            self.reader
            .get_epoch_timestamps_laser(&frames)
            .map_err(_to_py_error)?
            .into_pyarray(py)
        )
    }

    /// Returns an array of timestamps of each frame based on
    /// the system clock. High jitter, but no drift.

    /// WARNING if system timestamps do not exist, the function
    /// will throw an error. Unlike `siffreadermodule`/the `C++`
    /// module, this function will not crash the Python interpreter.

    /// ## Arguments

    /// * `frames` : List[int]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.uint64]]`
    ///     Nanoseconds since epoch, measured using
    ///     the system clock of the acquiring computer.
    ///     Only called about ~1 time per second, so
    ///     this will be the same number for most successive
    ///     frames.

    /// ## Example

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     time_system = siffio.get_epoch_timestamps_system(frames = list(range(1000)))
    ///     print(time_system.shape, time_system.dtype)

    ///     >>> ((1000,), np.uint64)
    ///     ```

    /// ## See also

    /// - `get_epoch_timestamps_laser`
    /// - `get_epoch_both`
    #[pyo3(name = "get_epoch_timestamps_system", signature = (frames=None))]
    pub fn get_epoch_timestamps_system_py<'py>(&self, py : Python<'py>, frames : Option<Vec<u64>>)
    -> PyResult<Bound<'py, PyArray1<u64>>>
    {
        let frames = frames_default!(frames, self);

        Ok(
            self.reader
            .get_epoch_timestamps_system(&frames)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{:?}", e)))?
            .into_pyarray(py)
        )
    }

    /// Returns an array containing both the laser timestamps
    /// and the system timestamps.

    /// The first row is laser timestamps, the second
    /// row is system timestamps. These can be used to correct one
    /// another

    /// WARNING if system timestamps do not exist, the function
    /// will throw an error. Unlike `siffreadermodule`/the `C++`
    /// module, this function will not crash the Python interpreter!

    /// ## Arguments

    /// * `frames` : List[int]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.uint64]]`
    ///     Nanoseconds since epoch, measured using
    ///     the laser pulses in the first row and the system
    ///     clock calls in the second row.

    /// ## Example

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     time_both = siffio.get_epoch_both(frames = list(range(1000)))
    ///     print(time_both.shape, time_both.dtype)

    ///     >>> ((2, 1000), np.uint64)
    ///     ```

    /// ## See also

    /// - `get_epoch_timestamps_laser`
    /// - `get_epoch_timestamps_system`
    #[pyo3(name = "get_epoch_both", signature = (frames=None))]
    pub fn get_epoch_both_py<'py>(&self, py : Python<'py>, frames : Option<Vec<u64>>)
    -> PyResult<Bound<'py, PyArray2<u64>>> {
        let frames = frames_default!(frames, self);
        Ok(
            self.reader
            .get_epoch_timestamps_both(&frames)
            .map_err(_to_py_error)?
            .into_pyarray(py)
        )
    }

    /// Returns a list of strings containing the text appended
    /// to each frame. Only returns elements where there was appended text.
    /// If no frames are provided, searches all frames.

    /// Returns a list of tuples of (frame number, text, timestamp).

    /// For some versions of `ScanImageFLIM`, there is no timestamp entry,
    /// so the tuple for those files will be (frame number, text, None).

    /// ## Arguments

    /// * `frames` : List[int]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// ## Returns

    /// * `List[Tuple[int, str, Optional[float]]]`
    ///     A list of tuples containing the frame number, the text
    ///     appended to the frame, and the timestamp of the text
    ///     (if it exists).

    /// ## Example

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     text = siffio.get_appended_text(frames = list(range(1000)))
    ///     ```
    #[pyo3(name = "get_appended_text", signature = (frames=None))]
    pub fn get_appended_text_py<'py>(&self, py : Python<'py>, frames : Option<Vec<u64>>)
    -> PyResult<Bound<'py, PyList>> {
        let frames = frames_default!(frames, self);
        let ret_list = PyList::empty(py);
        self.reader
        .get_appended_text(&frames)
        .iter().for_each(|(frame, text, option_timestamp)| {
            match option_timestamp {
                Some(timestamp) => {
                    // infallible, so unwrapping... bad style!
                    let tuple = (
                        frame.into_pyobject(py).unwrap(),
                        text.into_pyobject(py).unwrap(),
                        timestamp.into_pyobject(py).unwrap(),
                    ).into_pyobject(py).unwrap();
                    ret_list.append(tuple).unwrap();
                
                },
                None => {
                    let tuple = (
                        frame.into_pyobject(py).unwrap(),
                        text.into_pyobject(py).unwrap(),
                    ).into_pyobject(py).unwrap();
                    ret_list.append(tuple).unwrap();
                }
            }
        });
        Ok(ret_list)
    }

/************************************************************
     * FULL-FRAME DATA
     * 
     * These methods return data that is formatted as an _image_,
     * i.e. a series of 2d arrays corresponding to true pixels
     * with consistent spacing.
*/

    /// Retrieves frames from the file without
    /// respect to dimension or flyback.

    /// ## Arguments

    /// * `frames : Optional[List[int]]`
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// * `registration : Optional[Dict]`
    ///     A dictionary containing registration information
    ///     (the keys correspond to the frame number, the values
    ///     are tuples of (y,x) offsets). If an empty dict or None, will
    ///     be treated as if no registration is required.
    ///     Otherwise will raise an error if there are requested frames
    ///     that are not in the dictionary.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.uint16]]`
    ///     A numpy array containing the frames in the
    ///     order they were requested.

    /// ## Example
        
    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Get the data as an array
    ///     frame_data = siffio.get_frames(list(range(1000)))
    ///     print(frame_data.shape, frame_data.dtype)

    ///     >>> ((1000, 512, 512), np.uint16)
    ///     ```
    #[pyo3(signature = (frames=None, registration= None))]
    pub fn get_frames<'py>(
        &self, 
        py : Python<'py>,
        frames: Option<Vec<u64>>,
        registration : Option<HashMap<u64, (i32, i32)>>,
    ) -> PyResult<Bound<'py, PyArray3<u16>>> {
        // If frames is None, then we will read all frames
        let frames = frames_default!(frames, self);

        Ok(
            self.reader
            .get_frames_intensity(&frames, registration.as_ref())
            .map_err(_to_py_error)?
            .into_pyarray(py)
        )
    }

    /// Returns a tuple of `(flim_map, intensity_map, confidence_map)`
    /// where flim_map is the empirical lifetime with the offset of
    /// params subtracted. WARNING! This is DIFFERENT from the `siffreadermodule`
    /// implementation, which returns ONLY the empirical lifetime! This
    /// returns the empirical lifetime, the intensity, and the confidence
    /// map (well, the confidence map is tbd).

    /// ## Arguments

    /// * `params` : FLIMParams
    ///     The FLIM parameters to use for the analysis. The offset
    ///     term will be subtracted from the empirical lifetime values.
    ///     If `None`, the offset will be 0.

    /// * `frames` : List[int]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// * `confidence_metric` : str
    ///     The metric to use for the confidence map. Can be 'chi_sq'
    ///     or 'p_value'. Currently not actually used!
    /// 
    /// * `flim_method` : str
    ///    The method to use for the FLIM analysis. Can be 'empirical lifetime'
    ///    or 'phasor'. Currently only 'empirical lifetime' is implemented. 
    ///
    /// * `registration` : Dict
    ///     A dictionary containing registration information
    ///     (the keys correspond to the frame number, the values
    ///     are tuples of (y,x) offsets).

    /// ## Returns

    /// * `Tuple[np.ndarray[Any, np.dtype[np.float64]], np.ndarray[Any, np.dtype[np.uint16]], np.ndarray[Any, np.dtype[np.float64]]]`
    ///     A tuple of three numpy arrays containing the lifetime data (as float64),
    ///     the intensity data (as uint16), and the confidence data (as float64 or None).

    /// ## Example

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy
    ///     from siffpy.core.flim import FLIMParams, Exp, Irf

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Get the data as an array
    ///     frame_data = siffio.get_frames(list(range(1000)))

    ///     # Get the FLIM data
    ///     test_params = FLIMParams(
    ///         Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
    ///         Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
    ///         Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    ///     )

    ///     # Empirical lifetime
    ///     flim_map, intensity_map, confidence_map = siffio.flim_map(test_params, list(range(1000)))

    ///     print(flim_map.shape, flim_map.dtype)
    ///     >>> ((1000, 512, 512), np.float64)

    ///     assert intensity_map == frame_data

    ///     ```
    #[pyo3(
        name = "flim_map",
        signature = (
            params = None,
            frames = None,
            confidence_metric = "chi_sq",
            flim_method = "empirical lifetime",
            registration = None
        )
    )]
    pub fn flim_map_py<'py>(
        &self,
        py : Python<'py>,
        params : Option<&Bound<'py,PyAny>>,
        frames : Option<Vec<u64>>,
        confidence_metric : Option<&str>,
        flim_method : Option<&str>,
        registration : Option<HashMap<u64, (i32, i32)>>,
    ) -> PyResult<Bound<'py, PyTuple>>{
        let frames = frames_default!(frames, self);
        
        let mut offset = 0.0;
        match params {
            Some(params) => {
                let old_units = params.getattr("units")?;
                params.call_method1("convert_units", ("countbins",))?;
                offset = params.getattr("tau_offset")?.extract()?;
                params.call_method1("convert_units", (old_units,))?;
            },
            None => {}
        }

        let ret_tuple;
        let flim_method = flim_method.unwrap_or("empirical lifetime");

        match flim_method { 
            "empirical lifetime" => {
                let (lifetime, intensity) = self.reader.get_frames_flim(&frames, registration.as_ref())
                    .map_err(_to_py_error)?;

                let lifetime = lifetime - offset;

                ret_tuple = (
                    lifetime.into_pyarray(py),
                    intensity.into_pyarray(py),
                    None::<Bound<'py, PyArray3<f64>>>,
                ).into_pyobject(py).unwrap();
            },
            "phasor" => {
                let (lifetime, intensity) = self.reader.get_frames_phasor(
                    &frames, registration.as_ref()
                ).map_err(_to_py_error)?;

                let histogram_length = self.reader.num_flim_bins().
                map_err(_to_py_error)?;

                let frac_offset = 2.0_f64 * std::f64::consts::PI * offset/histogram_length as f64;

                let lifetime = lifetime * Complex::new(frac_offset.cos(), frac_offset.sin());
                
                ret_tuple = (
                    lifetime.into_pyarray(py),
                    intensity.into_pyarray(py),
                    None::<Bound<'py, PyArray3<f64>>>,
                ).into_pyobject(py).unwrap();
            },
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Invalid FLIM method {}. Must be one of \
                    [`empirical lifetime`, `phasor`]" , flim_method
                    )
                ));
            }
        }

        Ok(ret_tuple)
    }

    /// Returns a full-dimensioned array:
    /// (frames, y, x, arrival_time). This is a
    /// large array -- with 20 picosecond arrival
    /// time bins and an 80 MHz laser this is 
    /// ~600x bigger than the usual image array!

    /// ## Arguments

    /// * `frames` : Optional[List[int]]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// * `registration` : Optional[Dict]
    ///     A dictionary containing registration information
    ///     (the keys correspond to the frame number, the values
    ///     are tuples of (y,x) offsets). If None, no registration
    ///     will be applied.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.uint16]]`
    ///     A numpy array containing the pixelwise arrival time
    ///     histograms for all frames requested. Dimensions are
    ///     `(frames.len(), y, x, arrival_time_bins)`

    /// ## Example

    ///     ```python
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Get the data as an array
    ///     frame_data = siffio.get_frames_full(list(range(1000)))

    ///     print(frame_data.shape, frame_data.dtype)
    ///     # This is a 330 GB array!!
    ///     >>> ((1000, 512, 512, 629), np.uint16)
    ///     ```

    /// ## See also

    /// - `get_frames` : For just the intensity data

    /// - `flim_map` : For average arrival time + intensity data.     
    #[pyo3(name = "get_frames_full", signature = (frames = None, registration = None))]
    pub fn get_frames_full_py<'py>(
        &self,
        py : Python<'py>,
        frames : Option<Vec<u64>>,
        registration : Option<HashMap<u64, (i32, i32)>>
    ) -> PyResult<Bound<'py, PyArray4<u16>>>
    {
        let frames = frames_default!(frames, self);

        Ok(
            self.reader
            .get_frames_tau_d(&frames, registration.as_ref())
            .map_err(_to_py_error)?
            .into_pyarray(py)
        )
    }

    /*******************************************************
     * 
     * 
     * MASKED OR COMPRESSED DATA
     * 
     * Methods in this section return data that is compressed
     * along some axis, e.g. a frame-wide summary (as in histogramming)
     * or an ROI-specific sum (masked operations).
     * 
     */
    
    ///  Retrieves the arrival time histogram from the
    ///  file. Width of the histogram corresponds to the
    ///  number of BINS in the histogram. All frames are compressed
    ///  onto the one axis. For the time units
    ///  of the histogram, use the metadata.

    ///  ## Arguments

    ///  * `frames` : List[int]
    ///      A list of frames to retrieve. If `None`, all frames
    ///      will be retrieved.

    ///  ## Returns

    ///  * `np.ndarray[Any, np.dtype[np.uint64]]`
    ///      A numpy array containing the histogram of dimensions
    ///      (`num_bins`, )

    ///  ## Example

    ///      ```python
    ///      import numpy as np
    ///      import corrosiffpy

    ///      # Load the file
    ///      filename = '/path/to/file.siff'
    ///      siffio = corrosiffpy.open_file(filename)

    ///      hist = siffio.get_histogram(frames = list(range(1000)))
    ///      print(hist.shape, hist.dtype)

    ///      # 629 time bins with a 20 picosecond resolution
    ///      # = 12.58 nanoseconds, ~ 80 MHz
    ///      >>> ((629,), np.uint64)

    ///      ```
     
    ///  ## See also

    ///  - `get_histogram_by_frames` : The framewise version of this function,
    ///  returns the same data but with the frames as the slowest dimension 
    ///  (this is actually what's being called from `Rust`, then it's summed into
    ///  a single axis in this function call)

    ///  - `get_histogram_masked` : The masked version of this function.
    #[pyo3(signature = (frames=None))]
    pub fn get_histogram<'py>(&self, py : Python<'py>, frames : Option<Vec<u64>>)
    -> PyResult<Bound<'py, PyAny>> {
        let frames = frames_default!(frames, self);

        let kwarg_dict = PyDict::new(py);
        kwarg_dict.set_item("axis", 0)?;
        Ok(
            self.reader
            .get_histogram(&frames)
            .map_err(_to_py_error)?
            .into_pyarray(py)
            .call_method("sum", (), Some(&kwarg_dict))
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("{:?}", e)))?
        )
    }

    /// Retrieves the arrival time histogram from the
    /// file. Width of the histogram corresponds to the
    /// number of BINS in the histogram. For the time units
    /// of the histogram, use the metadata.

    /// ## Arguments

    /// * `frames` : List[int]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.uint64]]`
    ///     A numpy array containing the histogram of dimensions
    ///     (`frames.len()`, `num_bins`)

    /// ## Example

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     hist = siffio.get_histogram_by_frames(frames = list(range(1000)))
    ///     print(hist.shape, hist.dtype)

    ///     # 629 time bins with a 20 picosecond resolution
    ///     # = 12.58 nanoseconds, ~ 80 MHz
    ///     >>> ((1000, 629), np.uint64)

    ///     ```    
    #[pyo3(name = "get_histogram_by_frames", signature = (frames=None))]
    pub fn get_histogram_by_frames<'py>(&self, py : Python<'py>, frames : Option<Vec<u64>>)
    -> PyResult<Bound<'py, PyArray2<u64>>>
    {
        let frames = frames_default!(frames, self);

        Ok(
            self.reader
            .get_histogram(&frames)
            .map_err(_to_py_error)?
            .into_pyarray(py)
        )
    }

    /// Returns a framewise histogram of the arrival
    /// times of the photons in the mask.

    /// ## Arguments

    /// * `mask` : np.ndarray[Any, np.dtype[bool]]
    ///     A boolean mask of the same shape as the frames
    ///     to be summed.

    /// * `frames` : List[int]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// * `registration` : Optional[Dict]
    ///     A dictionary containing registration information
    ///     (the keys correspond to the frame number, the values
    ///     are tuples of (y,x) offsets). If None, no registration
    ///     will be applied.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.uint64]]`
    ///     A numpy array containing the histogram of dimensions
    ///     (`frames.len()`, `num_bins`). The histogram is
    ///     of the arrival times of the photons in the mask, with
    ///     each bin corresponding to an arrival time bin (so the
    ///     metadata must be read to transform this into real time units
    ///     like nanoseconds).

    /// ## Example

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Create a mask from random numbers
    ///     roi = np.random.rand(*siffio.frame_shape()) > 0.3

    ///     hist = siffio.get_histogram_masked(roi, frames = list(range(1000)))
    ///     print(hist.shape, hist.dtype)

    ///     # 629 time bins with a 20 picosecond resolution
    ///     # = 12.58 nanoseconds, ~ 80 MHz
    ///     >>> ((1000, 629), np.uint64)
    ///     ```

    /// ## See also

    /// - `get_histogram` : The unmasked version of this function.
    #[pyo3(name = "get_histogram_masked", signature = (mask, frames=None, registration=None))]
    pub fn get_histograms_masked_py<'py>(
        &self,
        py : Python<'py>,
        mask : Bound<'py, PyAny>,
        frames : Option<Vec<u64>>,
        registration : Option<HashMap<u64, (i32, i32)>>
    ) -> PyResult<Bound<'py, PyArray2<u64>>> {

        if !PyArray2::<bool>::type_check(&mask) 
        && !PyArray3::<bool>::type_check(&mask){
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Mask must be a 2d or 3d numpy array (for now)."
            ));
        }

        let frames = frames_default!(frames, self);
        if PyArray3::<bool>::type_check(&mask) {
            let mask : PyReadonlyArray3<bool> = mask.extract()?;
            let mask = mask.as_array();
            return Ok(
                self.reader
                .get_histogram_mask_volume(&frames, &mask, registration.as_ref())
                .map_err(_to_py_error)?
                .into_pyarray(py)
            )
        }

        let mask : PyReadonlyArray2<bool> = mask.extract()?;
        let mask = mask.as_array();

        Ok(
            self.reader
            .get_histogram_mask(&frames, &mask, registration.as_ref())
            .map_err(_to_py_error)?
            .into_pyarray(py)
        )
    }

    /// Mask may have 2 or 3 dimensions, but
    /// if so then be aware that the frames will be
    /// iterated through sequentially, rather than
    /// aware of the correspondence between frame
    /// number and mask dimension. Returns a 1D
    /// array of the same length as the frames
    /// provided, regardless of mask shape.

    /// ## Arguments

    /// * `mask` : np.ndarray[Any, np.dtype[bool]]
    ///     A boolean mask of the same shape as the frames
    ///     to be summed (if to be applied to all the frames).
    ///     If it's a 3D mask, the slowest dimension is assumed
    ///     to be a `z` dimension and cycles through the frames
    ///     provided, i.e. `mask[0]` is applied to `frames[0]`,
    ///     `mask[1]` is applied to `frames[1]`, ... `mask[k]` is
    ///     applied to `frames[n]` where `k = n % mask.shape[0]`.

    /// * `frames` : Optional[List[int]]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// * `registration` : Optional[Dict]
    ///     A dictionary containing registration information
    ///     (the keys correspond to the frame number, the values
    ///     are tuples of (y,x) offsets). If None, no registration
    ///     will be applied.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.uint64]]`

    /// ## Example

    ///     A single 2D mask

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file

    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Create a mask from random numbers
    ///     roi = np.random.rand(*siffio.frame_shape()) > 0.3

    ///     # Sum the ROI
    ///     masked = siffio.sum_roi(roi, frames = list(range(1000)))

    ///     print(masked.shape, masked.dtype)
    ///     >>> ((1000,), np.uint64)
    ///     ```

    ///     A single 3D mask corresponding to
    ///     planes of the ROI.

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file

    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Create a mask from random numbers
    ///     # (10 planes)
    ///     roi = np.random.rand(10, *siffio.frame_shape()) > 0.3

    ///     # Sum the ROI
    ///     masked = siffio.sum_roi(roi, frames = list(range(1000)))

    ///     # Still the same shape -- corresponds to
    ///     each frame requested.
    ///     print(masked.shape, masked.dtype)
    ///     >>> ((1000,), np.uint64)
    ///     ```

    /// ## See also

    /// - `sum_rois` : Summing multiple ROIs (either 2D or 3D masks)
    /// in one function call. Takes only slightly longer than `sum_roi`
    /// even with many ROIs, so this gets much more efficient than repeated
    /// calls to `sum_roi` for each ROI.
    /// - `sum_roi_flim` : The FLIM version of this function.
    #[pyo3(name = "sum_roi", signature = (mask, frames = None, registration = None))]
    fn sum_roi_py<'py>(
        &self,
        py : Python<'py>,
        mask : &Bound<'py, PyAny>,
        frames : Option<Vec<u64>>,
        registration : Option<HashMap<u64, (i32, i32)>>,
    ) -> PyResult<Bound<'py, PyAny>>
    {
        // Check that mask is a PyArray2 or a PyArray3
        if !PyArray2::<bool>::type_check(mask)
        && !PyArray3::<bool>::type_check(&mask) 
        && !PyArray4::<bool>::type_check(&mask){
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Mask must be a 2d (if the same mask is applied to all frames) 
                or 3d (if the mask is a volume to be cycled through) numpy array"
            ));
        }

        if PyArray4::<bool>::type_check(&mask) {
            return self.sum_rois_py(py, mask, frames, registration)
        }

        let frames = frames_default!(frames, self);

        if PyArray2::<bool>::type_check(&mask) {
            let mask : PyReadonlyArray2<bool> = mask.extract()?;
            let mask = mask.as_array();
            return Ok(
                self.reader.sum_roi_flat(&mask, &frames, registration.as_ref())
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{:?}", e)))?
                .into_pyarray(py).into_any()
            )
        }

        let mask : PyReadonlyArray3<bool> = mask.extract()?;
        let mask = mask.as_array();
        Ok(
            self.reader.sum_roi_volume(&mask, &frames, registration.as_ref())
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{:?}", e)))?
            .into_pyarray(py).into_any()
        )

    }

    /// Masks may have 2 or 3 dimensions each, (i.e.
    /// `masks` can be 3d or 4d), but
    /// if 4d then be aware that the frames will be
    /// iterated through sequentially (see below or as in
    /// `sum_roi`). Returns a 2D
    /// array of dimensions `(len(masks), len(frames))`.

    /// ## Arguments

    /// * `masks` : np.ndarray[Any, np.dtype[bool]]
    ///     Boolean masks. The mask dimension is the slowest
    ///     dimension (the 0th axis) and the last two dimensions
    ///     correspond to the y and x dimensions of the
    ///     frames. If the array has 4 dimensions, the 1st
    ///     dimension is assumed to be the `z` dimension and
    ///     each ROI is presumed to _cycle through_ the frames
    ///     along this axis. So _for each ROI_, the first frame
    ///     will be applied to the first element on the z axis, the second frame
    ///     will be applied to the second element on the z axis,
    ///     etc.

    ///     In other words: `masks[0,0,...]` is applied to `frames[0]`,
    ///     `masks[0,1,...]` is applied to `frames[1]`, ... `masks[0,k,...]` is
    ///     applied to `frames[n]` where `k = n % masks.shape[1]`. Likewise,
    ///     `masks[1,0,...]` is applied to `frames[0]`, `masks[1,1,...]` is applied
    ///     to `frames[1]`, ... `masks[1,k,...]` is applied to `frames[n]` where
    ///     `k = n % masks.shape[1]`.

    /// * `frames` : Optional[List[int]]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// * `registration` : Optional[Dict]
    ///     A dictionary containing registration information
    ///     (the keys correspond to the frame number, the values
    ///     are tuples of (y,x) offsets). If None, no registration
    ///     will be applied.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.uint64]]`
    ///     The returned value is a 2D array corresponding to each
    ///     ROI applied to the frames requested. Is dimension
    ///     `(len(masks), len(frames))` with the `i,j`th element
    ///     corresponding to the sum of the `i`th ROI mask applied to
    ///     the `j`th element of the argument `frames`.

    /// ## Example

    /// A set of 2d masks
    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Create a list of masks from random numbers
    ///     # 7 masks, 2d masks
    ///     rois = np.random.rand(7, *siffio.frame_shape()) > 0.3

    ///     # Sum the ROIs
    ///     masked = siffio.sum_rois(rois, frames = list(range(1000)))

    ///     print(masked.shape, masked.dtype)
    ///     >>> ((7, 1000), np.uint64)
    ///     ```

    /// A set of 3d masks
    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Create a list of masks from random numbers
    ///     # 7 masks, 3d masks with 4 planes
    ///     rois = np.random.rand(7, 4, *siffio.frame_shape()) > 0.3

    ///     # Sum the ROIs
    ///     masked = siffio.sum_rois(rois, frames = list(range(1000)))

    ///     print(masked.shape, masked.dtype)
    ///     >>> ((7, 1000), np.uint64)
    ///     ```

    /// ## See also

    /// - `sum_roi` : Summing a single ROI mask.
    /// - `sum_rois_flim` : The FLIM version of this function.
    #[pyo3(name = "sum_rois", signature = (masks, frames = None, registration = None))]
    pub fn sum_rois_py<'py>(
        &self,
        py : Python<'py>,
        masks : &Bound<'py, PyAny>,
        frames : Option<Vec<u64>>,
        registration : Option<HashMap<u64, (i32, i32)>>,
    ) -> PyResult<Bound<'py, PyAny>>
    {
        // Check that mask is a PyArray2 or a PyArray3
        if !PyArray3::<bool>::type_check(masks)
        && !PyArray4::<bool>::type_check(masks) {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Mask must be a 3d (if the same masks are applied to all frames) 
                or 4d (if each mask is a volume to be cycled through) numpy array"
            ));
        }

        let frames = frames_default!(frames, self);

        if PyArray3::<bool>::type_check(&masks) {
            let masks : PyReadonlyArray3<bool> = masks.extract()?;
            let masks = masks.as_array();
            return Ok(
                self.reader.sum_rois_flat(&masks, &frames, registration.as_ref())
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{:?}", e)))?
                .into_pyarray(py).call_method0("transpose")?.into_any()
            )
        }

        let masks : PyReadonlyArray4<bool> = masks.extract()?;
        let masks = masks.as_array();
        Ok(
            self.reader.sum_rois_volume(&masks, &frames, registration.as_ref())
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{:?}", e)))?
            .into_pyarray(py).call_method0("transpose")?.into_any()
        )
    }

    /// Mask may have 2 or 3 dimensions, but
    /// if so then be aware that the frames will be
    /// iterated through sequentially, rather than
    /// aware of the correspondence between frame
    /// number and mask dimension. Returns a tuple of 1D
    /// arrays of the same length as the frames
    /// provided, regardless of mask shape.

    /// Converts the lifetime units to `countbins` in the
    /// Rust call and then converts back at the end, so
    /// the lifetime values are in `countbins` even though
    /// the `FLIMParams` argument itself might appear to
    /// stay in any other units. TODO: is this too heavy
    /// handed? Seems kind of extra to pass the `FLIMParams`
    /// into this function instead of just an `offset` float,
    /// though this lets me make it `units`-agnostic...

    /// WARNING! This is DIFFERENT from the `siffreadermodule`
    /// implementation, which returns ONLY the empirical lifetime! This
    /// returns the empirical lifetime, the intensity, and the confidence
    /// map (well, the confidence map is tbd).

    /// ## Arguments

    /// * `mask` : np.ndarray[Any, np.dtype[bool]]
    ///     A boolean mask of the same shape as the frames
    ///     to be summed (if to be applied to all the frames).
    ///     If it's a 3D mask, the slowest dimension is assumed
    ///     to be a `z` dimension and cycles through the frames
    ///     provided, i.e. `mask[0]` is applied to `frames[0]`,
    ///     `mask[1]` is applied to `frames[1]`, ... `mask[k]` is
    ///     applied to `frames[n]` where `k = n % mask.shape[0]`.
    
    /// * `params` : Optional[FLIMParams]
    ///     The FLIM parameters to use for the analysis. The offset
    ///     term will be subtracted from the empirical lifetime values.
    ///     If `None`, the offset will be 0.

    /// * `frames` : Optional[List[int]]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// * `registration` : Optional[Dict]
    ///     A dictionary containing registration information
    ///     (the keys correspond to the frame number, the values
    ///     are tuples of (y,x) offsets). If None, no registration
    ///     will be applied.

    /// ## Returns

    /// Tuple['np.ndarray[Any, np.dtype[np.float64]]', 'np.ndarray[Any, np.dtype[np.uint64]]', 'np.ndarray[Any, np.dtype[np.float64]]']
    ///     A tuple of three numpy arrays containing, in order:
    ///         1) the empirical lifetime data (as float64) in units of
    ///         arrival time bins (countbins) with the offset of
    ///         params subtracted,
    ///         2) the summed intensity data (as uint64),
    ///         3) the confidence data (as float64 or None).

    /// ## Example

    ///     A single 2D mask

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy
    ///     from siffpy.core.flim import FLIMParams, Exp, Irf

    ///     # Load the file

    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Create a mask from random numbers
    ///     roi = np.random.rand(*siffio.frame_shape()) > 0.3

    ///     params = FLIMParams(
    ///         Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
    ///         Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
    ///         Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    ///     )
    ///     # Sum the ROI.
    ///     lifetime, intensity, _ = siffio.sum_roi_flim(params, roi, frames = list(range(1000)))

    ///     print(lifetime.shape, lifetime.dtype)
    ///     >>> ((1000,), np.float64)

    ///     print(intensity.shape, intensity.dtype)
    ///     >>> ((1000,), np.uint64)

    ///     ```

    ///     A single 3D mask corresponding to
    ///     planes of the ROI.

    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file

    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Create a mask from random numbers
    ///     # (10 planes)
    ///     roi = np.random.rand(10, *siffio.frame_shape()) > 0.3

    ///     params = FLIMParams(
    ///         Exp(tau = 0.5, frac = 0.5, units = 'nanoseconds'),
    ///         Exp(tau = 2.5, frac = 0.5, units = 'nanoseconds'),
    ///         Irf(offset = 1.1, sigma = 0.2, units = 'nanoseconds'),
    ///     )

    ///     # Sum the ROI
    ///     lifetime, intensity, _ = siffio.sum_roi_flim(params, roi, frames = list(range(1000)))

    ///     # Still the same shape -- corresponds to
    ///     each frame requested.
    ///     print(lifetime.shape, lifetime.dtype)
    ///     >>> ((1000,), np.float64)

    ///     print(masked.shape, masked.dtype)
    ///     >>> ((1000,), np.uint64)
    ///     ```

    /// ## See also

    /// - `sum_rois_flim` : Summing multiple ROIs (either 2D or 3D masks)
    /// in one function call. Takes only slightly longer than `sum_roi`
    /// even with many ROIs, so this gets much more efficient than repeated
    /// calls to `sum_roi` for each ROI.
    /// - `sum_roi` : The intensity-only version of this function.
    #[pyo3(name = "sum_roi_flim",
        signature = (
            mask,
            params = None,
            frames = None,
            flim_method = "empirical lifetime",
            registration = None
        )
    )]
    pub fn sum_roi_flim_py<'py>(
        &self,
        py : Python<'py>,
        mask : &Bound<'py, PyAny>,
        params : Option<&Bound<'py,PyAny>>,
        frames : Option<Vec<u64>>,
        flim_method : Option<&str>,
        registration : Option<HashMap<u64, (i32, i32)>>,
    ) -> PyResult<Bound<'py, PyTuple>>
    {
        // Check that mask is a PyArray2 or a PyArray3
        if !PyArray2::<bool>::type_check(mask)
        && !PyArray3::<bool>::type_check(mask)
        && !PyArray4::<bool>::type_check(mask) {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Mask must be a 2d (if the same mask is applied to all frames) 
                or 3d (if the mask is a volume to be cycled through) numpy array"
            ));
        } 

        if PyArray4::<bool>::type_check(mask) {
            return self.sum_rois_flim_py(py, mask, params, frames, flim_method, registration)
        }

        let frames = frames_default!(frames, self);

        let mut offset = 0.0;
        if let Some(params) = params {
            let old_units = params.getattr("units")?;

            params.call_method1("convert_units", ("countbins",))?;
            offset = params.getattr("tau_offset")?.extract()?;
            params.call_method1("convert_units", (old_units,))?;
        }

        let flim_method = flim_method.unwrap_or("empirical lifetime");

        if PyArray2::<bool>::type_check(&mask) {
            let mask : PyReadonlyArray2<bool> = mask.extract()?;
            let mask = mask.as_array();

            let ret_tuple;
            match flim_method {
                "empirical lifetime" => {
                    let (lifetime, intensity) = self.reader.sum_roi_flim_flat(&mask, &frames, registration.as_ref())
                        .map_err(_to_py_error)?;

                    let lifetime = lifetime - offset;

                    ret_tuple = (
                        lifetime.into_pyarray(py),
                        intensity.into_pyarray(py),
                        None::<Bound<'py, PyArray3<f64>>>,
                    ).into_pyobject(py)?;
                },
                "phasor" => {
                    let (lifetime, intensity) = self.reader.sum_roi_phasor_flat(&mask, &frames, registration.as_ref())
                        .map_err(_to_py_error)?;

                    let histogram_length = self.reader.num_flim_bins().
                    map_err(_to_py_error)?;
    
                    let frac_offset = 2.0_f64 * std::f64::consts::PI * offset/histogram_length as f64;
    
                    let lifetime = lifetime / Complex::new(frac_offset.cos(), frac_offset.sin());

                    ret_tuple = (
                        lifetime.into_pyarray(py),
                        intensity.into_pyarray(py),
                        None::<Bound<'py, PyArray3<f64>>>,
                    ).into_pyobject(py)?;
                },
                _ => {
                    return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Only 'empirical lifetime' is supported as a flim_method for now."
                    ));
                }
            }

            return Ok(ret_tuple)
        }

        let mask : PyReadonlyArray3<bool> = mask.extract()?;
        let mask = mask.as_array();
        
        let ret_tuple;
            match flim_method {
                "empirical lifetime" => {
                    let (lifetime, intensity) = self.reader.sum_roi_flim_volume(&mask, &frames, registration.as_ref())
                        .map_err(_to_py_error)?;

                    let lifetime = lifetime - offset;

                    ret_tuple = (
                        lifetime.into_pyarray(py),
                        intensity.into_pyarray(py),
                        None::<Bound<'py, PyArray3<f64>>>,
                    ).into_pyobject(py)?;
                },
                "phasor" => {
                    let (lifetime, intensity) = self.reader.sum_roi_phasor_volume(&mask, &frames, registration.as_ref())
                        .map_err(_to_py_error)?;

                    let histogram_length = self.reader.num_flim_bins().
                    map_err(_to_py_error)?;
    
                    let frac_offset = 2.0_f64 * std::f64::consts::PI * offset/histogram_length as f64;
    
                    let lifetime = lifetime / Complex::new(frac_offset.cos(), frac_offset.sin());

                    ret_tuple = (
                        lifetime.into_pyarray(py),
                        intensity.into_pyarray(py),
                        None::<Bound<'py, PyArray3<f64>>>,
                    ).into_pyobject(py)?;
                },
                _ => {
                    return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Invalid `flim_method` argument."
                    ));
                }
            }
        
        Ok(ret_tuple)
    }

    /// Masks may have 2 or 3 dimensions each, (i.e.
    /// `masks` can be 3d or 4d), but
    /// if 4d then be aware that the frames will be
    /// iterated through sequentially (see below or as in
    /// `sum_roi`). Returns a 2D
    /// array of dimensions `(len(masks), len(frames))`.

    /// Converts the lifetime units to `countbins` in the
    /// Rust call and then converts back at the end, so
    /// the lifetime values are in `countbins` even though
    /// the `FLIMParams` argument itself might appear to
    /// stay in any other units. TODO: is this too heavy
    /// handed? Seems kind of extra to pass the `FLIMParams`
    /// into this function instead of just an `offset` float,
    /// though this lets me make it `units`-agnostic...

    /// ## Arguments

    /// * `masks` : np.ndarray[Any, np.dtype[bool]]
    ///     Boolean masks. The mask dimension is the slowest
    ///     dimension (the 0th axis) and the last two dimensions
    ///     correspond to the y and x dimensions of the
    ///     frames. If the array has 4 dimensions, the 1st
    ///     dimension is assumed to be the `z` dimension and
    ///     each ROI is presumed to _cycle through_ the frames
    ///     along this axis. So _for each ROI_, the first frame
    ///     will be applied to the first element on the z axis, the second frame
    ///     will be applied to the second element on the z axis,
    ///     etc.

    ///     In other words: `masks[0,0,...]` is applied to `frames[0]`,
    ///     `masks[0,1,...]` is applied to `frames[1]`, ... `masks[0,k,...]` is
    ///     applied to `frames[n]` where `k = n % masks.shape[1]`. Likewise,
    ///     `masks[1,0,...]` is applied to `frames[0]`, `masks[1,1,...]` is applied
    ///     to `frames[1]`, ... `masks[1,k,...]` is applied to `frames[n]` where
    ///     `k = n % masks.shape[1]`.

    /// * `params` : Optional[FLIMParams]
    ///     The FLIM parameters to use for the analysis. The offset
    ///     term will be subtracted from the empirical lifetime values.
    ///     If `None`, the offset will be 0.

    /// * `frames` : Optional[List[int]]
    ///     A list of frames to retrieve. If `None`, all frames
    ///     will be retrieved.

    /// * `registration` : Optional[Dict]
    ///     A dictionary containing registration information
    ///     (the keys correspond to the frame number, the values
    ///     are tuples of (y,x) offsets). If None, no registration
    ///     will be applied.

    /// ## Returns

    /// * `np.ndarray[Any, np.dtype[np.uint64]]`
    ///     The returned value is a 2D array corresponding to each
    ///     ROI applied to the frames requested. Is dimension
    ///     `(len(masks), len(frames))` with the `i,j`th element
    ///     corresponding to the sum of the `i`th ROI mask applied to
    ///     the `j`th element of the argument `frames`.

    /// ## Example

    /// A set of 2d masks
    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Create a list of masks from random numbers
    ///     # 7 masks, 2d masks
    ///     rois = np.random.rand(7, *siffio.frame_shape()) > 0.3

    ///     # Sum the ROIs
    ///     masked = siffio.sum_rois(rois, frames = list(range(1000)))

    ///     print(masked.shape, masked.dtype)
    ///     >>> ((7, 1000), np.uint64)
    ///     ```

    /// A set of 3d masks
    ///     ```python
    ///     import numpy as np
    ///     import corrosiffpy

    ///     # Load the file
    ///     filename = '/path/to/file.siff'
    ///     siffio = corrosiffpy.open_file(filename)

    ///     # Create a list of masks from random numbers
    ///     # 7 masks, 3d masks with 4 planes
    ///     rois = np.random.rand(7, 4, *siffio.frame_shape()) > 0.3

    ///     # Sum the ROIs
    ///     masked = siffio.sum_rois(rois, frames = list(range(1000)))

    ///     print(masked.shape, masked.dtype)
    ///     >>> ((7, 1000), np.uint64)
    ///     ```

    /// ## See also

    /// - `sum_roi_flim` : Summing a single ROI mask.
    /// - `sum_rois` : The intensity-only version of this function.
    #[pyo3(name = "sum_rois_flim", signature = (
        masks,
        params = None,
        frames = None,
        flim_method = "empirical lifetime",
        registration = None
    ))]
    pub fn sum_rois_flim_py<'py>(
        &self,
        py : Python<'py>,
        masks : &Bound<'py, PyAny>,
        params : Option<&Bound<'py,PyAny>>,
        frames : Option<Vec<u64>>,
        flim_method : Option<&str>,
        registration : Option<HashMap<u64, (i32, i32)>>,
    ) -> PyResult<Bound<'py, PyTuple>>
    {
        // Check that mask is a PyArray2 or a PyArray3
        if !PyArray3::<bool>::type_check(masks)
        && !PyArray4::<bool>::type_check(masks) {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Mask must be a 3d (if the same masks are applied to all frames) 
                or 4d (if each mask is a volume to be cycled through) numpy array"
            ));
        }

        let frames = frames_default!(frames, self);
        let mut offset = 0.0;
        if let Some(params) = params {
            let old_units = params.getattr("units")?;

            params.call_method1("convert_units", ("countbins",))?;
            offset = params.getattr("tau_offset")?.extract()?;
            params.call_method1("convert_units", (old_units,))?;
        }

        let flim_method = flim_method.unwrap_or("empirical lifetime");

        if PyArray3::<bool>::type_check(&masks) {
            let masks : PyReadonlyArray3<bool> = masks.extract()?;
            let masks = masks.as_array();
            
            match flim_method {
                "empirical lifetime" => {
                    let (lifetime, intensity) = self.reader.sum_rois_flim_flat(
                        &masks, &frames, registration.as_ref()
                    ).map_err(_to_py_error)?;

                    let lifetime = lifetime - offset;

                    let ret_tuple = (
                        lifetime.into_pyarray(py).call_method0("transpose")?,
                        intensity.into_pyarray(py).call_method0("transpose")?,
                        None::<Bound<'py, PyArray3<f64>>>,
                    ).into_pyobject(py)?;

                    return Ok(ret_tuple)
                },
                "phasor" => {
                    let (lifetime, intensity) = self.reader.sum_rois_phasor_flat(
                        &masks, &frames, registration.as_ref()
                    ).map_err(_to_py_error)?;

                    let histogram_length = self.reader.num_flim_bins().
                    map_err(_to_py_error)?;
    
                    let frac_offset = 2.0_f64 * std::f64::consts::PI * offset/histogram_length as f64;
    
                    let lifetime = lifetime / Complex::new(frac_offset.cos(), frac_offset.sin());

                    let ret_tuple = (
                        lifetime.into_pyarray(py).call_method0("transpose")?,
                        intensity.into_pyarray(py).call_method0("transpose")?,
                        None::<Bound<'py, PyArray3<f64>>>,
                    ).into_pyobject(py)?;

                    return Ok(ret_tuple)
                },
                _ => {
                    return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Invalid `flim_method` argument".to_string()
                    ));
                }
            }
        }
        
        let masks : PyReadonlyArray4<bool> = masks.extract()?;
        let masks = masks.as_array();

        match flim_method {
            "empirical lifetime" => {
                let (lifetime, intensity) = self.reader.sum_rois_flim_volume(
                    &masks, &frames, registration.as_ref()
                ).map_err(_to_py_error)?;

                let lifetime = lifetime - offset;

                let ret_tuple = (
                    lifetime.into_pyarray(py).call_method0("transpose")?,
                    intensity.into_pyarray(py).call_method0("transpose")?,
                    None::<Bound<'py, PyArray3<f64>>>,
                ).into_pyobject(py)?;

                return Ok(ret_tuple)
            },
            "phasor" => {
                let (lifetime, intensity) = self.reader.sum_rois_phasor_volume(
                    &masks, &frames, registration.as_ref()
                ).map_err(_to_py_error)?;

                let histogram_length = self.reader.num_flim_bins().
                map_err(_to_py_error)?;

                let frac_offset = 2.0_f64 * std::f64::consts::PI * offset/histogram_length as f64;

                let lifetime = lifetime / Complex::new(frac_offset.cos(), frac_offset.sin());

                let ret_tuple = (
                    lifetime.into_pyarray(py).call_method0("transpose")?,
                    intensity.into_pyarray(py).call_method0("transpose")?,
                    None::<Bound<'py, PyArray3<f64>>>,
                ).into_pyobject(py)?;

                return Ok(ret_tuple)
            },
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Invalid `flim_method` argument".to_string()
                ));
            }
        }
    }
}