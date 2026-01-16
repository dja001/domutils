import pytest

@pytest.fixture
def copy_to_static():
    """ Copy test artifacts to _static for documentation purpose

        Returns a function that copies files to tmp_path and returns the destination path.

        Example:
            def test_something(copy_to_static):
                output_file = copy_to_static("results.json")
                assert output_file.exists()
    """
    def _copy(src_fig_name):
        import os
        import shutil
        import domutils
        import domutils._py_tools as py_tools

        # figure out destinaion path
        domutils_dir = os.path.dirname(domutils.__file__)
        package_dir  = os.path.dirname(domutils_dir)
        static_dir = os.path.join(package_dir, 'docs/_static')

        # make sure output dir is there
        py_tools.parallel_mkdir(static_dir)

        # the figure we are copying to
        dest_fig_name = os.path.join(static_dir, os.path.basename(src_fig_name))

        return shutil.copy(src_fig_name, dest_fig_name)

    return _copy  # No yield needed if no teardown


@pytest.fixture(scope="module")
def reset_matplotlib():
    """Reset matplotlib state at the beginning of each module"""
    import os
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import domutils

    # load comitted mpl style file for reproducible results
    plt.style.use('default')

    yield
    plt.close('all')  # Close all figures
    plt.clf()  # Clear current figure
    plt.cla()  # Clear current axes

