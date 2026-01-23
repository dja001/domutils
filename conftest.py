import pytest

# runs before anything else
def pytest_sessionstart(session):

    import os
    import shutil
    import glob
    from matplotlib import font_manager

    # for results consistency, we flush matplotlib's cache
    home_dir = os.environ.get('HOME')
    mpl_cache_dir = os.path.join(home_dir, '.cache/matplotlib')
    if os.path.isdir(mpl_cache_dir):
        print(f'We remove existing matplotlib cache dir {mpl_cache_dir}')
        shutil.rmtree(mpl_cache_dir)

    # dirty hack to remove latin modern fonts already available for matplotlib
    fm = font_manager.fontManager
    fm.ttflist = [
        f for f in fm.ttflist
        if not (
            "Latin Modern Roman" in f.name
            and "mpl-data" in f.fname
        )
    ]

    font_path = os.environ.get('LM_FONT_DIR')
    if not font_path:
        font_path = '/home/dja001/python/install_lm_fonts_in_conda_env/lm_otf/'
        print(f'System variable LM_FONT_PATH is not set, we use {font_path}')
    if font_path:
        if os.path.isdir(font_path):
            font_files = glob.glob(os.path.join(font_path, '*.otf'))
            for font_file in font_files: 
                if 'lmroman9-regular' in font_file:
                    font_manager.fontManager.addfont(font_file)
        else:
            print(f'Invalid font directory: {font_dir}')


@pytest.fixture(scope="module", autouse=True)
def reset_matplotlib():
    """Reset matplotlib state at the beginning of each module"""
    import os
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    # load comitted mpl style file for reproducible results
    plt.style.use('default')

    yield
    plt.close('all')  # Close all figures
    plt.clf()  # Clear current figure
    plt.cla()  # Clear current axes




@pytest.fixture(scope="session", autouse=True)
def setup_test_paths():
    import os
    import domutils
    import shutil
    import platform
    import sys
    import importlib.metadata as im
    from pathlib import Path
    from domutils import _py_tools as py_tools

    python_version = platform.python_version()

    # figure out destination paths
    domutils_dir = os.path.dirname(domutils.__file__)
    package_dir  = os.path.dirname(domutils_dir)

    # data for running the tests
    test_data_dir = os.path.join(package_dir, 'test_data')
    if not os.path.isdir(test_data_dir):
        raise ValueError(f'source test data dir: {test_data_dir} does not exist, \n consider running scripts/download_test_data.sh')

    # test results is dependent on python version
    test_results_dir = os.path.join(package_dir, f'test_results_{python_version}')
    if os.path.isdir(test_results_dir):
        print(f'We remove existing test results dir: \n {test_results_dir}')
        shutil.rmtree(test_results_dir)
    py_tools.parallel_mkdir(test_results_dir)


    # we print the versions of packages being used in a small file
    def v(pkg):
        try:
            return im.version(pkg)
        except im.PackageNotFoundError:
            return "not installed"

    info = {
        "python": sys.version.replace("\n", " "),
        "numpy": v("numpy"),
        "matplotlib": v("matplotlib"),
        "cartopy": v("cartopy"),
    }

    outfile = os.path.join(test_results_dir, "runtime_versions.txt")
    with open(outfile, 'w') as f:

        for k, val in info.items():
            f.write(f"{k}: {val}\n")


    return {'package_dir': package_dir, 
            'test_data_dir': test_data_dir, 
            'test_results_dir': test_results_dir}
