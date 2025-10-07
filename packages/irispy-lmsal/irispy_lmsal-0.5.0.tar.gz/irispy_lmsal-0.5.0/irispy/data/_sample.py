import os
from pathlib import Path
from urllib.parse import urljoin

from sunpy import log
from sunpy.util.config import _is_writable_dir, get_and_create_sample_dir
from sunpy.util.parfive_helpers import Downloader

_BASE_URLS = (
    "https://github.com/sunpy/data/raw/main/irispy-lmsal/",
    "https://github.com/sunpy/sample-data/raw/master/irispy-lmsal/",
    "http://data.sunpy.org/irispy-lmsal/",
)
_SAMPLE_DATA = {
    "AIA_1700": "aia_20140919_060030_1700_image_lev1.fits",
    "RASTER_TAR": "iris_l2_20211001_060925_3683602040_raster.tar.gz",
    "RASTER_FITS": "iris_l2_20211001_060925_3683602040_raster_t000_r00000.fits",
    "SJI_1330": "iris_l2_20211001_060925_3683602040_SJI_1330_t000.fits.gz",
    "SJI_1400": "iris_l2_20211001_060925_3683602040_SJI_1400_t000.fits.gz",
    "SJI_2796": "iris_l2_20211001_060925_3683602040_SJI_2796_t000.fits.gz",
    "SJI_2832": "iris_l2_20211001_060925_3683602040_SJI_2832_t000.fits.gz",
}
_SAMPLE_FILES = {v: k for k, v in _SAMPLE_DATA.items()}


def _download_sample_data(base_url, sample_files, overwrite):
    """
    Downloads a list of files.

    Parameters
    ----------
    base_url : str
        Base URL for each file.
    sample_files : list of tuples
        List of tuples that are (URL_NAME, SAVE_NAME).
    overwrite : bool
        Will overwrite a file on disk if True.

    Returns
    -------
    `parfive.Results`
        Download results. Will behave like a list of files.
    """
    dl = Downloader(overwrite=overwrite, progress=True)
    for url_file_name, fname in sample_files:
        url = urljoin(base_url, url_file_name)
        dl.enqueue_file(url, filename=fname)
    return dl.download()


def _retry_sample_data(results, new_url_base):
    # In case we have a broken file on disk, overwrite it.
    dl = Downloader(overwrite=True, progress=True)
    for err in results.errors:
        file_name = err.url.split("/")[-1]
        log.debug(f"Failed to download {_SAMPLE_FILES[file_name]} from {err.url}: {err.exception}")
        # Update the url to a mirror and requeue the file.
        new_url = urljoin(new_url_base, file_name)
        log.debug(f"Attempting redownload of {_SAMPLE_FILES[file_name]} using {new_url}")
        dl.enqueue_file(new_url, filename=err.filepath_partial)
    extra_results = dl.download()
    # Make a new results object which contains all the successful downloads
    # from the previous results object and this retry, and all the errors from
    # this retry.
    new_results = results + extra_results
    new_results._errors = extra_results._errors
    return new_results


def _handle_final_errors(results):
    for err in results.errors:
        file_name = err.url.split("/")[-1]
        log.debug(
            f"Failed to download {_SAMPLE_FILES[file_name]} from {err.url}: {err.exception}",
        )
        log.error(
            f"Failed to download {_SAMPLE_FILES[file_name]} from all mirrors, the file will not be available.",
        )


def _get_sampledata_dir():
    # Workaround for tox only. This is not supported as a user option
    sampledata_dir = os.environ.get("SUNPY_SAMPLEDIR", "")
    if sampledata_dir:
        sampledata_dir = Path(sampledata_dir).expanduser().resolve()
        _is_writable_dir(sampledata_dir)
    else:
        # Creating the directory for sample files to be downloaded
        sampledata_dir = Path(get_and_create_sample_dir())
    return sampledata_dir


def _get_sample_files(filename_list, *, no_download=False, force_download=False):
    """
    Returns a list of disk locations corresponding to a list of filenames for
    sample data, downloading the sample data files as necessary.

    Parameters
    ----------
    filename_list : `list` of `str`
        List of filenames for sample data
    no_download : `bool`
        If ``True``, do not download any files, even if they are not present.
        Default is ``False``.
    force_download : `bool`
        If ``True``, download all files, and overwrite any existing ones.
        Default is ``False``.

    Returns
    -------
    `list` of `pathlib.Path`
        List of disk locations corresponding to the list of filenames.  An entry
        will be ``None`` if ``no_download == True`` and the file is not present.

    Raises
    ------
    RuntimeError
        Raised if any of the files cannot be downloaded from any of the mirrors.
    """
    sampledata_dir = _get_sampledata_dir()
    fullpaths = [sampledata_dir / fn for fn in filename_list]
    if no_download:
        fullpaths = [fp if fp.exists() else None for fp in fullpaths]
    else:
        to_download = zip(filename_list, fullpaths, strict=False)
        if not force_download:
            to_download = [(fn, fp) for fn, fp in to_download if not fp.exists()]
        if to_download:
            results = _download_sample_data(_BASE_URLS[0], to_download, overwrite=force_download)
            # Try the other mirrors for any download errors
            if results.errors:
                for next_url in _BASE_URLS[1:]:
                    results = _retry_sample_data(results, next_url)
                    if not results.errors:
                        break
                else:
                    _handle_final_errors(results)
                    raise RuntimeError
    return fullpaths
