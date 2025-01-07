use corrosiff;

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

    Ok(())
}