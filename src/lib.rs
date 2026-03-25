use corrosiff;

use ndarray::{Axis, s};
use ndarray::parallel::prelude::*;
use numpy::ndarray::{ArrayView, ArrayViewMut, ArrayD, Dimension, ArrayBase, OwnedRepr};
use numpy::{PyArray, PyArrayDyn, PyArrayMethods, PyReadonlyArrayDyn, PyReadwriteArrayDyn};
use pyo3::PyTypeCheck;
use pyo3::prelude::*;

mod siffio;
use crate::siffio::SiffIO;

#[pymodule]
#[pyo3(name = "corrosiffpy")]
/// CorrosiffPy
/// -----------
///
/// `corrosiffpy` is a `Python` wrapper for the `Rust` `corrosiff` package,
/// used for reading and parsing data from the FLIM-data `.siff` filetype.
///
/// Its primary tool is the `SiffIO` class, which wraps `corrosiff`'s
/// `SiffReader` struct. There are a few minorly questionable design
/// decisions here made to remain consistent with the `C++`-based
/// `siffreadermodule` extension module.
fn corrosiff_python<'py>(_py: Python<'py>, m: &Bound<'py, PyModule>)
    -> PyResult<()> {

    m.add_class::<SiffIO>()?;

    /// Opens a .siff or .tiff file using the `corrosiff` library,
    /// returning a `SiffIO` object in `Python` that wraps the `Rust`
    /// interface.
    /// 
    /// ## Arguments
    /// 
    /// * `file_path` : str - The path to the file to open.
    /// 
    /// ## Returns
    /// 
    /// * `SiffIO` - A `Python` object that wraps the `Rust` interface
    /// to the `SiffReader` object.
    /// 
    /// ## Raises
    /// 
    /// * `PyIOError` - If the file cannot be opened.
    /// 
    /// ## Example
    /// 
    /// ```python
    /// import corrosiff_python
    /// from pathlib import Path
    /// 
    /// my_path = Path("source_directory")
    /// my_path /= 'another_dir'
    /// my_path /= 'target_file.siff'
    /// 
    /// siffio = corrosiff_python.open_file(str(my_path))
    /// print(siffio.filename)
    /// 
    /// >>> "source_directory/another_dir/target_file.siff"
    /// ```
    #[pyfn(m)]
    #[pyo3(name = "open_file")]
    fn open_file_py<'py>(py : Python<'py>, file_path: &str) ->
        PyResult<Bound<'py, SiffIO>> {

        let reader = corrosiff::open_siff(file_path).map_err(|e| 
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e))
        )?;
        Ok( Bound::new(py, SiffIO::new_from_reader(reader) )? )
    }

    /// Converts a .siff file to a .tiff file using the `corrosiff` library.
    #[pyfn(m)]
    #[pyo3(
        name = "siff_to_tiff",
        signature = (sourcepath, savepath = None, mode = "ScanImage")
    )]
    fn siff_to_tiff_py<'py>(
        _py : Python<'py>,
        sourcepath : &str,
        savepath : Option<&str>,
        mode : Option<&str>,
    ) -> PyResult<()> {
        let mode = mode.unwrap_or("ScanImage");
        let savepath = savepath.map(|s| s.to_string());
        let mode = corrosiff::TiffMode::from_string_slice(mode)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("{}", e)) )?;

        corrosiff::siff_to_tiff(sourcepath, mode, savepath.as_ref())
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)) )?;
        Ok(())
    }

    /// Scans a .siff file for just the first timestamp using the `corrosiff` library.
    #[pyfn(m)]
    #[pyo3(name = "get_start_timestamp", signature = (file_path))]
    fn get_start_timestamp<'py>(_py : Python<'py>, file_path: &str) -> PyResult<u64> {
        let start = corrosiff::scan_first_timestamp(&file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)) )?;
        Ok(start)
    }

    /// Scans a .siff file for its start and end timestamps
    /// using the `corrosiff` library.
    #[pyfn(m)]
    #[pyo3(name = "get_start_and_end_timestamps", signature = (file_path))]
    fn get_start_and_end_timestamps<'py>(
        _py: Python<'py>,
        file_path: &str
    ) -> PyResult<(u64, u64)> {
        let (start, end) = corrosiff::scan_timestamps(&file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("{}", e)) )?;
        Ok((start, end))
    }

    /// Calls the `corrosiff` library's `par_dfof` function
    /// to compute dF/F on large arrays with some parallelism
    /// to make it a little faster and require fewer allocations
    /// of big arrays.
    #[pyfn(m)]
    #[pyo3(name = "par_dfof", signature = (data, baseline, axis = -1, out = None))]
    fn par_dfof_py<'py>(
        _py: Python<'py>,
        data: &Bound<'py, PyAny>,
        baseline: &Bound<'py, PyAny>,
        axis : isize,
        out : Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, numpy::PyArrayDyn<PyAny>>> {

        // If it's `f32`, do it in `f32`
        if PyArrayDyn::<f32>::type_check(data) {
            if !PyArrayDyn::<f32>::type_check(baseline) {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "data and baseline must be of the same type",
                ));
            }

            let data = data.extract::<PyReadonlyArrayDyn<f32>>()?;
            let data = data.as_array();
            let baseline = baseline.extract::<PyReadonlyArrayDyn<f32>>()?;

            let baseline = baseline.as_array();

            if axis >= data.ndim() as isize || axis < -(data.ndim() as isize) {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "axis out of bounds for array",
                ));
            }
            
            let axis = match axis < 0 {
                // Convert negative axis to positive
                true => (data.ndim() as isize + axis) as usize,
                false => axis as usize,
            };

            // if out.is_some() {
            //     let o = out.unwrap().extract::<PyReadwriteArrayDyn<f32>>()?;
            //     let mut o = unsafe { o.as_array_mut() };
            //     par_dfof_rs(data, baseline, axis, out);
            //     return Ok(o.to_owned().to_pyarray(_py));
            // }

            // let mut owned : Option<ArrayViewMut<f32, _>>;
            // let mut out : ArrayViewMut<f32, _> = match out {
            //     Some(o) => {
            //         let o = o.extract::<PyReadonlyArrayDyn<f32>>()?;
            //         unsafe { o.as_array_mut() }
            //     },
            //     None => {
            //         let shape = data.shape();
            //         let mut temp = numpy::ndarray::ArrayD::<f32>::zeros(shape);
            //         owned = Some(temp.view_mut());
            //         owned.as_mut().unwrap().view_mut()
            //     }
            // };

            return Err(PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
                "par_dfof for f32 not implemented yet",
            ))
        }

        // If it's `f64`, do it in `f64`
        if PyArrayDyn::<f64>::type_check(data) {
            if !PyArrayDyn::<f64>::type_check(baseline) {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "data and baseline must be of the same type",
                ));
            }

            // Do the operation in f64

            let data = data.extract::<PyReadonlyArrayDyn<f64>>()?;
            let data = data.as_array();
            let baseline = baseline.extract::<PyReadonlyArrayDyn<f64>>()?;
            let baseline = baseline.as_array();

            if axis >= data.ndim() as isize || axis < -(data.ndim() as isize) {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "axis out of bounds for array",
                ));
            }

            let axis = match axis < 0 {
                // Convert negative axis to positive
                true => (data.ndim() as isize + axis) as usize,
                false => axis as usize,
            };

            return Err(PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
                "par_dfof for f64 not implemented yet",
            ))
        }


        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "data and baseline must be `f32` or `f64` arrays",
        ))
    }
    Ok(())
}

/// Subtracts `baseline` from `data` and divides by `baseline`,
/// storing the result in `out`.
fn par_dfof_rs<T, D, F>(
    data : ArrayView<T, D>,
    baseline : ArrayView<T, F>,
    axis : usize,
    mut out : ArrayViewMut<T, D>
) -> ()
where
    T : Send + Sync,
    D : Dimension,
    F : Dimension,
{
    // Check that data and baseline are arrays of the same shape
    if data.shape() != baseline.shape() {
        panic!("Data and baseline must have the same shape");
    }

    let chunk_size = 2500;
    let data_chunks = data.axis_chunks_iter(Axis(axis), chunk_size);

    // Compute dF/F
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_dfof() {
        // Test shared F0 across columns (scalar)

        // Test per-column F0 (1D array)

        // Test rolling F0 (2D array)
        
    }
}