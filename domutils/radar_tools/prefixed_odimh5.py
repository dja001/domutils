class PrefixedODimH5:
    """Context manager that opens an ODim-HDF5 file with h5py.

    Handles the MSC telex-style text header (e.g. 'SDCN01 CWAO ...') that is
    prepended to archived CAS radar files: the HDF5 payload is relocated to a
    temporary file that is removed on exit. Files with the HDF5 signature at
    byte 0 are opened directly, with no copy.

    Self-contained: nothing outside the class is required, so it can be
    copied as-is into any module.

    Usage:
        with PrefixedODimH5(path) as h5:
            print(h5['where/latitude/value'][()])

        # or without a with-block:
        h5 = PrefixedODimH5(path)
        h5.open()
        ...  # h5['...'], h5.close()
        h5.close()

    Args:
        path:    file to open
        scan:    how many leading bytes to search for the HDF5 magic
        tmp_dir: directory for the stripped copy (default: system temp dir)
    """

    HDF5_MAGIC = b'\x89HDF\r\n\x1a\n'

    def __init__(self, path, scan=1024, tmp_dir=None):
        import os

        self._path = str(path)
        self._tmp_dir = tmp_dir
        self._handle = None
        self._tmp_path = None

        if not os.path.isfile(self._path):
            raise FileNotFoundError(self._path)
        with open(self._path, 'rb') as fst:
            head = fst.read(scan)
        self._offset = head.find(self.HDF5_MAGIC)
        if self._offset < 0:
            raise ValueError(
                f'no HDF5 signature in first {scan} bytes of {self._path!r}')

    def __enter__(self):
        import h5py
        import os
        import shutil
        import tempfile

        if self._offset == 0:
            self._handle = h5py.File(self._path, 'r')
            return self._handle

        fd, self._tmp_path = tempfile.mkstemp(suffix='.odimh5', dir=self._tmp_dir)
        try:
            with os.fdopen(fd, 'wb') as tmp, open(self._path, 'rb') as src:
                src.seek(self._offset)
                shutil.copyfileobj(src, tmp, length=1 << 20)
        except Exception:
            os.unlink(self._tmp_path)
            self._tmp_path = None
            raise
        self._handle = h5py.File(self._tmp_path, 'r')
        return self._handle

    def __exit__(self, *exc):
        import os

        if self._handle is not None:
            self._handle.close()
            self._handle = None
        if self._tmp_path and os.path.exists(self._tmp_path):
            os.unlink(self._tmp_path)
        return False

    def open(self):
        if self._handle is not None:
            return self._handle
        return self.__enter__()

    def close(self):
        self.__exit__(None, None, None)

    def __getitem__(self, key):
        return self._handle[key]

    def __getattr__(self, name):
        handle = self.__dict__.get('_handle')
        if handle is None:
            raise AttributeError(name)
        return getattr(handle, name)
