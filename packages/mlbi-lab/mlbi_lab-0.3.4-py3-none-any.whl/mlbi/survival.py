## 필요한 패키지 불러오기
import copy, warnings, os
import anndata
import numpy as np
import pandas as pd
import scanpy as sc
import matplotlib.pyplot as plt
from .bistack import _pip_install, _pkg_base_name, _get_dist_version

LIFELINES_ = True
try:
    import lifelines
except ImportError:
    spec = 'lifelines'
    upgrade = False
    base = _pkg_base_name(spec)
    cur_v = _get_dist_version(base)

    if cur_v:
        print(f"{base}: already installed (v{cur_v})")
    else:
        rc = _pip_install(spec, quiet=True, upgrade=upgrade)
        new_v = _get_dist_version(base)
        if rc == 0 and new_v:
            tag = "upgraded" if (cur_v and upgrade) else "installed"
            print(f"{base}: {tag} (v{new_v})")
        else:
            print(f"WARNING: {base} install failed")
            LIFELINES_ = False


def plot_survival(events, times, groups, ref_group = None, title = None,
                  figsize = (5,5), title_fs = 12, label_fs = 10, 
                  tick_fs = 10, text_fs = 10, legend_fs = 10,
                  text_pos = (0.7, 0.05), grid = True, 
                  xlabel = 'Year', ylabel = 'Survival'):

    if not LIFELINES_:
        print('ERROR: lifelines not installed.')
        return 
    
    labels = list(set(groups))
    if ref_group is None:
        ref_group = labels[0]
    
    ## Kaplan-Meier Survival curves
    kmf = lifelines.KaplanMeierFitter()
    texts = ''
    for i, lbl in enumerate(labels):
        ix = np.array(groups) == lbl
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")    
            kmf.fit(times[ix], event_observed=events[ix], label=lbl)
            kmf.plot_survival_function(ci_show=False, linewidth=2, figsize = figsize ) #, color=colors[i])

            ## LogRank Test to get p-values
            if lbl != ref_group:
                ix = groups == ref_group
                jx = groups == lbl
                t_res = lifelines.statistics.logrank_test(times[ix], times[jx], events[ix], events[jx], alpha=.95)
                p_val = t_res.p_value
                texts = texts + 'p-value: %4.2e (%s vs %s)\n' % (p_val, lbl, ref_group)

    texts = texts[:-1]
    plt.text(text_pos[0],text_pos[1],texts, fontsize=text_fs )
    plt.ylim([0,1])
    plt.ylabel(ylabel, fontsize = label_fs)
    plt.xlabel(xlabel, fontsize = label_fs)
    nH = np.sum(groups == ref_group)
    nNH = np.sum(groups != ref_group)
    if title is not None:
        plt.title(title, fontsize=title_fs)

    plt.legend(fontsize = legend_fs)
    plt.yticks(fontsize = tick_fs)
    plt.xticks(fontsize = tick_fs)

    if grid: plt.grid()

    return
    