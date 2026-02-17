def plot_results(lt, rmse, mae, fcst_eff, n, fig_dir):
    import os
    import datetime
    import time
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from scipy.optimize import curve_fit

    import domutils.legs as legs
    import domutils._py_tools as d_py


    leadtime_min = lt/60.
    leadtime_fit = np.arange(0.,  leadtime_min[-1])

    
    # model
    def exp_decay(t, A, B, C, tau):
        return 100. * (A*np.exp(-t / tau) + B*np.exp(-t / (10.*tau)) + C*np.exp(-t / (100.*tau)))

    # initial guesses help convergence
    p0 = (.5, .5, .5, 10.)
    
    params, cov = curve_fit(exp_decay, leadtime_min, fcst_eff, p0=p0, 
                            bounds=([0., 0., 0., 0.], np.inf)
                            )
    
    A, B, C, tau = params
    
    print("A =", A)
    print("B =", B)
    print("C =", C)
    print("tau =", tau)
    
    # fitted curve
    fcst_eff_fit = exp_decay(leadtime_fit, *params)




    #setup figure properties
    ratio = 0.2
    # all sizes are inches for consistency with matplotlib
    rec_w = 6.            # Horizontal size of a panel  /2.54 for dimensions in cm
    rec_h = ratio * rec_w # Vertical size of a panel
    sp_w = 2.9             # horizontal space between panels
    sp_h = 2.5             # vertical space between panels
    pal_sp = .1           # spavce between panel and palette
    pal_w = .25           # width of palette
    tit_h = 1.            # height of title
    xp = .04              # axes relative x position of image caption
    yp = 1.05             # axes relative y position of image caption
    dpi = 100             # density of pixel for figure
    #size of figure
    fig_w = 3. + 2.*(sp_w + rec_w + pal_w + pal_sp )
    fig_h = 4. + 3.*(sp_h + rec_h)
    #normalize all dimensions
    rec_w /= fig_w
    rec_h /= fig_h
    sp_w  /= fig_w
    sp_h  /= fig_h
    pal_sp/= fig_w
    pal_w /= fig_w
    tit_h /= fig_h 
    # matplotlib global settings
    mpl.rcParams.update({'font.size': 23})
    # Use this for editable text in svg
    mpl.rcParams['text.usetex']  = False
    mpl.rcParams['svg.fonttype'] = 'none'
    # Hi def figure
    mpl.rcParams['figure.dpi'] = dpi
    # pretty font in figures
    mpl.rcParams['font.family'] = 'Latin Modern Roman'

    red_cm    = legs.PalObj(range_arr=[0,1.], color_arr=['red'])
    blue_cm   = legs.PalObj(range_arr=[0,1.], color_arr=['blue'])
    green_cm  = legs.PalObj(range_arr=[0,1.], color_arr=['green'])
    orange_cm = legs.PalObj(range_arr=[0,1.], color_arr=['orange'])
    pink_cm   = legs.PalObj(range_arr=[0,1.], color_arr=['pink'])
    purple_cm = legs.PalObj(range_arr=[0,1.], color_arr=['purple'])
    yellow_cm = legs.PalObj(range_arr=[0,1.], color_arr=['yellow'])
    brown_cm  = legs.PalObj(range_arr=[0,1.], color_arr=['brown'])
    bw_cm  = legs.PalObj(range_arr=[0,1.], color_arr=['b_w'])

    # instantiate figure
    fig = plt.figure(figsize=(fig_w, fig_h))

    #print title
    dummy_ax = fig.add_axes([0,0,1,1],zorder=0)
    dummy_ax.axis('off')
    dummy_ax.annotate('Nowcast errors f(leadtime)', size=35,
                      xy=(.1, .95), xycoords='figure fraction',
                      bbox=dict(boxstyle="round", fc=[1,1,1,.85], ec=[1,1,1,0]))

    #position of this fig
    x0 = sp_w + 0.*(rec_w + sp_w)
    y0 = sp_h + 0.*(rec_h + sp_h)
    pos = [x0, y0, rec_w, rec_h]
    # setup axes
    ax_rmse = fig.add_axes(pos)
    ax_rmse.set_xlabel('Leadtime [minutes]')
    ax_rmse.set_ylabel('RMSE [mm/h]')
    ax_rmse.set_xlim(leadtime_min[0],leadtime_min[-1])
    ax_rmse.set_ylim(0., 8.)
    ax_rmse.set_title(f'RMSE')
    ax_rmse.scatter(leadtime_min, rmse)

    #position of this fig
    x0 = sp_w + 0.*(rec_w + sp_w)
    y0 = sp_h + 1.*(rec_h + sp_h)
    pos = [x0, y0, rec_w, rec_h]
    # setup axes
    ax_mae = fig.add_axes(pos)
    ax_mae.set_xlabel('Leadtime [minutes]')
    ax_mae.set_ylabel('MAE [mm/h]')
    ax_mae.set_xlim(leadtime_min[0],leadtime_min[-1])
    ax_mae.set_ylim(0., 0.33)
    ax_mae.set_title(f'MAE')
    ax_mae.scatter(leadtime_min, mae)

    #position of this fig
    x0 = sp_w + 0.*(rec_w + sp_w)
    y0 = sp_h + 2.*(rec_h + sp_h)
    pos = [x0, y0, rec_w, rec_h]
    # setup axes
    ax_eff = fig.add_axes(pos)
    ax_eff.set_xlabel('Leadtime [minutes]')
    ax_eff.set_ylabel('FCST_EFF [mm/h]')
    ax_eff.set_xlim(leadtime_min[0],leadtime_min[-1])
    ax_eff.set_ylim(1e-3, 100.)
    #ax_eff.set_yscale('log')
    ax_eff.set_title(f'FCST EFF')
    ax_eff.scatter(leadtime_min, fcst_eff)
    ax_eff.plot(leadtime_fit, fcst_eff_fit, color='pink')


    #save figure
    fig_name = fig_dir+'average_err_stats'
    plt.savefig(fig_name+ '.svg')
    plt.close(fig)
    print(f'Done with: {fig_name}')


def aggregate_scores(db_pattern):
    """
    Reads many sqlite files and averages scores by leadtime.

    Parameters
    ----------
    db_pattern : str
        Glob pattern, e.g. "results/*.sqlite"

    Returns
    -------
    leadtimes : ndarray
    rmse_mean : ndarray
    mae_mean : ndarray
    fcst_eff_mean : ndarray
    counts : ndarray   # number of samples per leadtime
    """

    import sqlite3
    import glob
    import numpy as np
    from collections import defaultdict

    files = glob.glob(db_pattern)

    # storage per leadtime
    rmse_vals = defaultdict(list)
    mae_vals = defaultdict(list)
    eff_vals = defaultdict(list)

    for fname in files:
        conn = sqlite3.connect(fname)
        cur = conn.cursor()

        for lt, rmse, mae, eff in cur.execute(
            "SELECT leadtime, rmse, mae, fcst_eff FROM scores"
        ):
            rmse_vals[lt].append(rmse)
            mae_vals[lt].append(mae)
            eff_vals[lt].append(eff)

        conn.close()

    # sort leadtimes
    leadtimes = sorted(rmse_vals.keys())

    rmse_mean = np.array([np.mean(rmse_vals[lt]) for lt in leadtimes])
    mae_mean = np.array([np.mean(mae_vals[lt]) for lt in leadtimes])
    eff_mean = np.array([np.mean(eff_vals[lt]) for lt in leadtimes])
    counts = np.array([len(rmse_vals[lt]) for lt in leadtimes])

    return (
        np.array(leadtimes),
        rmse_mean,
        mae_mean,
        eff_mean,
        counts,
    )

if __name__ == '__main__':

    day='20220605'
    #day='20220701'
    #day='20220705'
    #pattern = f'/space/hall5/sitestore/eccc/mrd/rpndat/dja001/ten_minutes_time_interpolated/error_f_deltat/{day}*.sqlite'
    pattern = f'/space/hall5/sitestore/eccc/mrd/rpndat/dja001/ten_minutes_time_interpolated/error_f_deltat_med3/{day}*.sqlite'
    lt, rmse, mae, fcst_eff, n = aggregate_scores(pattern)
    print(lt)
    print(rmse)
    print(mae)
    print(fcst_eff)

    fig_dir = f'/space/hall6/sitestore/eccc/mrd/rpndat/dja001/python_figures/combine_n_view_nowcast_stats/med3_{day}'
    plot_results(lt, rmse, mae, fcst_eff, n, fig_dir)

