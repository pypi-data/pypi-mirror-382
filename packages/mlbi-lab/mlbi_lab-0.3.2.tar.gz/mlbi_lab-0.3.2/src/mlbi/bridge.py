import os, warnings, copy, random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .bistack import _pip_install, _pkg_base_name, _get_dist_version

STATANNOTATIONS_ = True
try:
    # from statannot import add_stat_annotation
    from statannotations.Annotator import Annotator
except ImportError:
    spec = 'statannotations'
    upgrade = False
    base = _pkg_base_name(spec)
    cur_v = _get_dist_version(base)

    if cur_v:
        print(f"{base}: already installed (v{cur_v})")
        continue

    rc = _pip_install(spec, quiet=True, upgrade=upgrade)
    new_v = _get_dist_version(base)
    if rc == 0 and new_v:
        tag = "upgraded" if (cur_v and upgrade) else "installed"
        print(f"{base}: {tag} (v{new_v})")
    else:
        print(f"WARNING: {base} install failed")
        STATANNOTATIONS_ = False

import seaborn as sns
import sklearn.linear_model as lm
import sklearn.model_selection as mod_sel
import sklearn.metrics as met
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import auc, roc_curve, precision_recall_curve
from scipy import stats
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier


def evaluate_roc_auc_old( X, y, vlst, classifier, param_grid, 
                      NCV = 5, target_cls = 'Cancer', title_t = None,
                      fpr_th = 0.01, tpr_th = 0.99, 
                      bsr = 0.8, bsn = 40, vbs = 0, show_std = False):

    cv = mod_sel.StratifiedKFold(n_splits=NCV)
    plt.figure(figsize=(4, 4), dpi=100)
    legend_str = []

    df_log_x = X
    
    sens = []
    sens_all = []
    spec = []
    spec_all = []
    auc_all = []
    groups = []
    auc_mean = []
    auc_std = []
    aucs_lst = []
    
    colors_mean = ['blue', 'red', 'green', 'gold', 'navy', 'orange', 'purple', 'firebrick', 'royalblue']
    mean_fpr_lst = []
    tprs_lower_lst = []
    tprs_upper_lst = []
    for k, key in enumerate(list(vlst.keys())):
        
        df_a = df_log_x[vlst[key]]
    
        ## (4) Search grid to find best parameters
        gs = mod_sel.GridSearchCV(classifier, param_grid, cv=cv, 
                                  scoring='balanced_accuracy', 
                                  n_jobs=NCV, verbose = vbs)
    
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")    
            gs.fit(df_a,y)
    
        ## (5) Check best score and Get best paramter
        best_param = gs.best_params_
        print("Best Scroe: " + str(round(gs.best_score_,4)) + " with parameters ", end='' )
        print(gs.best_params_)
    
        ## Get the best classifiers
        classifier = gs.best_estimator_
    
        idx_all = list(df_a.index.values)
        tprs = []
        aucs = []
        coef_lst = []
        mean_fpr = np.linspace(0, 1, 100)
    
        sens_tmp = []
        spec_tmp = []
        for i in range(bsn):
            idx_sel = random.sample(idx_all, int(len(idx_all)*bsr))
            cv = mod_sel.StratifiedKFold(n_splits=NCV)
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")    
                y_dec_met = mod_sel.cross_val_predict( classifier, df_a.loc[idx_sel,:], 
                                                       y[idx_sel], cv=cv, 
                                                       method = 'decision_function', 
                                                       verbose = vbs, n_jobs = NCV )
        
            # Compute ROC curve and ROC area for each class
            # cls_lst = list(set(y))
            if classifier.classes_[0] == target_cls:
                y_dec_met = -y_dec_met
        
            fpr, tpr, _ = roc_curve(y[idx_sel].ravel(), y_dec_met.ravel(), pos_label = target_cls)
            roc_auc = auc(fpr, tpr)
        
            sn = 0
            for j, fr in enumerate(fpr):
                if fr <= fpr_th:
                  sn = tpr[j]
            sp = 0
            for j, tp in enumerate(tpr):
                if tp <= tpr_th:
                  sp = 1-fpr[j]

            sens_tmp.append(sn)
            sens_all.append(sn)
            spec_tmp.append(sp)
            spec_all.append(sp)
            auc_all.append(roc_auc)
            groups.append(key)
            
            title = "%s (AUC[%i] = %0.3f)" % (key, i, roc_auc)
    
            if False: # i < 6:
                legend_str.append(title)
                plt.plot(fpr, tpr, label=title, lw = 0.3 ) 
            
            interp_tpr = np.interp(mean_fpr, fpr, tpr)
            tprs.append(interp_tpr)
            aucs.append(roc_auc)
    
        aucs_lst.append(aucs)
        sens.append(np.mean(sens_tmp))
        spec.append(np.mean(spec_tmp))
        mean_tpr = np.mean(tprs, axis=0)
        mean_tpr[-1] = 1.0
        mean_auc = auc(mean_fpr, mean_tpr)
        std_auc = np.std(aucs)
        plt.plot(mean_fpr, mean_tpr, color=colors_mean[k],
                label='%s (AUC: %0.3f $\pm$ %0.3f)' % (key, mean_auc, std_auc),
                lw=2, alpha=.8)
        auc_mean.append(mean_auc)
        auc_std.append(std_auc)
        
        std_tpr = np.std(tprs, axis=0)
        tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
        tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
        
        if show_std:
            mean_fpr_lst.append(mean_fpr)
            tprs_lower_lst.append(tprs_lower)
            tprs_upper_lst.append(tprs_upper)
            # plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color=colors_mean[k], alpha=.2,
            #                  label=r'%s $\pm$ 1 std. dev.' % key)
    
    plt.plot([0, 1], [0, 1], color="gray", lw=2, linestyle="--", label='Chance', alpha=.8)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate = FP/(FP+TN)") #, fontsize = 11)
    plt.ylabel("True Positive Rate = TP/(TP+FN)") #, fontsize = 11)    
    #plt.title("ROC for %s classification" % target_cls )
    if title is not None: plt.title(title_t )
    # plt.legend(loc="lower left", bbox_to_anchor = (1.05, -0.075), fontsize = 9)
    plt.legend(loc="lower right", bbox_to_anchor = (1, 0), fontsize = 9)

    if show_std:
        k = 0
        for mean_fpr, tprs_lower, tprs_upper in zip(mean_fpr_lst, tprs_lower_lst, tprs_upper_lst):
            plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color=colors_mean[k], alpha=.2,
                             label=r'%s $\pm$ 1 std. dev.' % key)
            k += 1
    
    plt.show()
    df_res = pd.DataFrame({'Case': groups, 'AUC': auc_all, 
                           'Sensitivity': sens_all, 'Specificity': spec_all})

    return df_res


def evaluate_roc_auc( X, y, vlst, classifier, param_grid, 
                      NCV = 5, target_cls = 'Cancer', title_t = None,
                      fpr_th = 0.01, tpr_th = 0.99, bsr = 0.8, bsn = 40, vbs = 0,
                      legend_loc = 'lower right', bbox_to_anchor = (1,0),
                      legend_frame = True, legend_title = None,
                      title_fs = 12, label_fs = 10, legend_fs = 9, 
                      show_std = False, figsize = (4,4), dpi = 100,
                      show_legend = True, linewidth = 1.5, 
                      ylabel = None, xlabel = None ):

    cv = mod_sel.StratifiedKFold(n_splits=NCV)
    plt.figure(figsize=figsize, dpi=dpi)
    legend_str = []

    df_log_x = X
    
    sens = []
    sens_all = []
    spec = []
    spec_all = []
    auc_all = []
    ppv_all = []
    groups = []
    auc_mean = []
    auc_std = []
    aucs_lst = []
    
    with warnings.catch_warnings():   
        warnings.simplefilter("ignore")    
            
        colors_mean = ['blue', 'red', 'green', 'gold', 'navy', 'orange', 'purple', 'firebrick', 'royalblue']
        for k, key in enumerate(list(vlst.keys())):
            
            df_a = df_log_x[vlst[key]]
        
            ## (4) Search grid to find best parameters
            gs = mod_sel.GridSearchCV(classifier, param_grid, cv=cv, 
                                      scoring='balanced_accuracy', 
                                      n_jobs=NCV, verbose = vbs)
    
            gs.fit(df_a,y)
        
            ## (5) Check best score and Get best paramter
            best_param = gs.best_params_
            print("Best Scroe: " + str(round(gs.best_score_,4)) + " with parameters ", end='' )
            print(gs.best_params_)
        
            ## Get the best classifiers
            classifier = gs.best_estimator_
        
            idx_all = list(df_a.index.values)
            tprs = []
            aucs = []
            coef_lst = []
            mean_fpr = np.linspace(0, 1, 100)
        
            sens_tmp = []
            spec_tmp = []
            for i in range(bsn):
                idx_sel = random.sample(idx_all, int(len(idx_all)*bsr))
                cv = mod_sel.StratifiedKFold(n_splits=NCV)
                
                y_dec_met = mod_sel.cross_val_predict( classifier, df_a.loc[idx_sel,:], 
                                                       y[idx_sel], cv=cv, 
                                                       method = 'decision_function', 
                                                       verbose = vbs, n_jobs = NCV )
            
                # Compute ROC curve and ROC area for each class
                # cls_lst = list(set(y))
                if classifier.classes_[0] == target_cls:
                    y_dec_met = -y_dec_met
            
                fpr, tpr, thresholds = roc_curve(y[idx_sel].ravel(), y_dec_met.ravel(), pos_label = target_cls)
                roc_auc = auc(fpr, tpr)
            
                sn = 0
                for j, fr in enumerate(fpr):
                    if fr <= fpr_th:
                        sn = tpr[j]

                # j = np.argmin(np.abs(fpr - fpr_th))
                # sn = tpr[j]                        
                
                sp = 0
                for j, tp in enumerate(tpr):
                    if tp <= tpr_th:
                      sp = 1-fpr[j]
                        
                j = np.argmin(np.abs(tpr - tpr_th))
                sp = 1 - fpr[j]                        

                precision, recall, _ = precision_recall_curve(y[idx_sel].ravel(), y_dec_met.ravel(), pos_label = target_cls)
                j = np.argmin(np.abs(recall - tpr_th))
                prec_at_tpr_via_pr = precision[j]
                
                ppv_all.append(prec_at_tpr_via_pr)
                sens_tmp.append(sn)
                sens_all.append(sn)
                spec_tmp.append(sp)
                spec_all.append(sp)
                auc_all.append(roc_auc)
                groups.append(key)
                
                title = "%s (AUC[%i] = %0.3f)" % (key, i, roc_auc)
        
                if False: # i < 6:
                    legend_str.append(title)
                    plt.plot(fpr, tpr, label=title, lw = 0.3 ) 
                
                interp_tpr = np.interp(mean_fpr, fpr, tpr)
                tprs.append(interp_tpr)
                aucs.append(roc_auc)
        
            aucs_lst.append(aucs)
            sens.append(np.mean(sens_tmp))
            spec.append(np.mean(spec_tmp))
            mean_tpr = np.mean(tprs, axis=0)
            mean_tpr[-1] = 1.0
            mean_auc = auc(mean_fpr, mean_tpr)
            std_auc = np.std(aucs)
            if show_std:
                plt.plot(mean_fpr, mean_tpr, color=colors_mean[k],
                        label='%s (AUC: %0.3f $\pm$ %0.3f)' % (key, mean_auc, std_auc),
                        lw=linewidth, alpha=.8)
            else:
                plt.plot(mean_fpr, mean_tpr, color=colors_mean[k],
                        label='%s (AUC: %0.3f)' % (key, mean_auc),
                        lw=linewidth, alpha=.8)
                
            auc_mean.append(mean_auc)
            auc_std.append(std_auc)
            
            std_tpr = np.std(tprs, axis=0)
            tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
            tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
            if show_std:
                plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color=colors_mean[k], alpha=.2) 
                                 # label=r'%s $\pm$ 1 std. dev.' % key)
    
    plt.plot([0, 1], [0, 1], color="gray", lw=linewidth, linestyle="--", alpha=.8)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    if xlabel is not None:
        plt.xlabel(xlabel, fontsize = label_fs)
    else:
        plt.xlabel("False Positive Rate", fontsize = label_fs)
        
    if ylabel is not None:
        plt.ylabel(ylabel, fontsize = label_fs)    
    else:
        plt.ylabel("True Positive Rate", fontsize = label_fs)    
        
    if title is not None: plt.title(title_t, fontsize = title_fs )

    if show_legend:
        legend = plt.legend(loc=legend_loc, bbox_to_anchor = bbox_to_anchor, fontsize = legend_fs)

        if not legend_frame:
            legend.get_frame().set_edgecolor('none')

        if legend_title is not None:
            legend.set_title(legend_title)

    res = stats.ttest_ind(aucs_lst[0], 
                          aucs_lst[-1], axis=0, 
                          equal_var=False,  
                          nan_policy='omit', 
                          permutations=None, 
                          random_state=None, 
                          alternative='two-sided', 
                          trim=0) #, keepdims=False)
    pv = res.pvalue
    
    plt.show()
    sens1 = copy.deepcopy(sens)
    df_res = pd.DataFrame({'Case': groups, 'AUC': auc_all, 
                           'Sensitivity': sens_all, 'Specificity': spec_all,
                           'PPV': ppv_all })

    return df_res
    

def plot_pct_box_old( df_pct, sg_map, ncols, figsize = None, dpi = 100,
                  title = None, title_y_pos = 1.05, title_fs = 14, 
                  label_fs = 11, tick_fs = 10, xtick_rot = 0, xtick_ha = 'center', group_order = None,
                  annot = True, annot_ref = None, annot_fmt = 'simple', annot_fs = 10, 
                  ws_hs = (0.3, 0.3), ylabel = None, xlabel = None, 
                  stripplot = True, dot_size = 5, jitter = 2 ):

    title2_fs = None
    if title2_fs is None:
        title2_fs = title_fs - 2
    df = df_pct.copy(deep = True)
    # nr, nc = nr_nc
    nc = ncols
    nr = int(np.ceil(df.shape[1]/nc))
    if figsize is None:
        figsize = (3*nc,3*nr)
    else:
        figsize = (figsize[0]*nc,figsize[1]*nr)
        
    ws, hs = ws_hs
    fig, axes = plt.subplots(figsize = figsize, dpi=dpi, nrows=nr, ncols=nc)
    plt.subplots_adjust(wspace=ws, hspace=hs)

    if title is not None:
        fig.suptitle('%s' % title, x = 0.5, y = title_y_pos, fontsize = title_fs, ha = 'center')

    items = list(df.columns.values)

    df['Group'] = list(df.index.values)
    df['Group'].replace(sg_map, inplace = True)

    lst = df['Group'].unique()

    for kk, item in enumerate(items):
        plt.subplot(nr,nc,kk+1)
        b = df[item].isnull()
        pcnt = df.loc[~b,'Group'].value_counts()
        b1 = pcnt > 1
        group_sel = pcnt.index.values[b1].tolist()

        if len(group_sel) > 1:
            b = (~b) & df['Group'].isin(group_sel)
            
            lst = df.loc[b, 'Group'].unique()
            lst_pair = []
            if annot_ref in lst:
                for k, l1 in enumerate(lst):
                    if l1 != annot_ref:
                        lst_pair.append((annot_ref, l1))
            else:
                for k, l1 in enumerate(lst):
                    for j, l2 in enumerate(lst):
                        if j <  k:
                            lst_pair.append((l1, l2))
        
            ax = sns.boxplot(data = df.loc[b,:], x = 'Group', y = item, order = group_order)
            if stripplot:
                sns.stripplot(x='Group', y=item, data=df.loc[b,:], jitter=jitter, 
                              color="black", order = group_order, size = dot_size )

            '''
            if kk < (nr*nc - nc):
                # plt.xticks([])
                plt.xticks(rotation = xtick_rot, ha = xtick_ha, fontsize = tick_fs)
                plt.yticks(fontsize = tick_fs)
            else:
                plt.xticks(rotation = xtick_rot, ha = xtick_ha, fontsize = tick_fs)
                plt.yticks(fontsize = tick_fs)
            #'''
            
            '''
            if (kk%nc == 0) & (ylabel is not None): 
                ax.set_ylabel(ylabel, fontsize = label_fs)                
            else: 
                ax.set_ylabel(None)
            #'''
            ax.set_ylabel(item, fontsize = label_fs)
                
            if kk >= nc*(nr-1): 
                x_tick_lst = [item.get_text() for item in ax.get_xticklabels()]
                ax.set_xticks(x_tick_lst, x_tick_lst, rotation = xtick_rot, ha = xtick_ha, fontsize = tick_fs)
            else: 
                ax.set_xticks([])
                
            if xlabel is not None: 
                ax.set_xlabel(xlabel, fontsize = label_fs)
            else: 
                ax.set_xlabel(None)
                
            ax.set_title(item, fontsize = title_fs)

            if annot:
                add_stat_annotation(ax, data=df.loc[b,:], x = 'Group', y = item, 
                                    order = group_order,
                            box_pairs=lst_pair, loc='inside', fontsize = annot_fs,
                            test='t-test_ind', text_format=annot_fmt, verbose=0)
            #'''
    
    if (len(items) < (nr*nc)) & (nr > 1):
        for k in range(nr*nc - len(items)):
            axes[nr-1][len(items)%nc + k].axis("off")
        
    plt.show()
    return 


def plot_pct_box( df_pct, sg_map = None, ncols = 3, figsize = None, dpi = 100,
                  title = None, title_y_pos = 1.05, title_fs = 14, rename_cells = None,
                  label_fs = 11, tick_fs = 10, xtick_rot = 0, xtick_ha = 'center', group_order = None,
                  annot = True, annot_ref = None, annot_fmt = 'simple', annot_fs = 10, 
                  ws_hs = (0.3, 0.3), ylabel = None, cmap = 'tab10',
                  stripplot = True, stripplot_ms = 1, stripplot_jitter = True ):

    title2_fs = None
    if title2_fs is None:
        title2_fs = title_fs - 2
        
    df = df_pct.copy(deep = True)
    if 'Group' in list(df.columns.values):
        sg_map = dict(zip( df.index.values, df['Group'] ))
        df = df.drop( columns = ['Group'] )
    elif isinstance(sg_map, pd.Series):
        sg_map = dict(zip( df.index.values, sg_map ))
    
    ## index 이름에서 '--'를 '\n'로 대체
    idx_org = list(df.columns.values)
    idx_new = [s.replace('--', '\n') for s in idx_org]
    rend = dict(zip(idx_org, idx_new))
    df = df.rename(columns = rend)
        
    # nr, nc = nr_nc
    nc = ncols
    nr = int(np.ceil(df.shape[1]/nc))
    if figsize is None:
        figsize = (3*nc,3*nr)
    else:
        figsize = (figsize[0]*nc,figsize[1]*nr)
        
    ws, hs = ws_hs
    fig, axes = plt.subplots(figsize = figsize, dpi=dpi, nrows=nr, ncols=nc, constrained_layout=False)
    fig.tight_layout() # Or equivalently,  "plt.tight_layout()"
    if title is not None:
        fig.suptitle('%s' % title, x = 0.5, y = title_y_pos, fontsize = title_fs, ha = 'center')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=ws, hspace=hs)

    items = list(df.columns.values)

    df['Group'] = list(df.index.values)
    df['Group'] = df['Group'].replace(sg_map)

    lst = df['Group'].unique()

    cnt = 0
    for kk, item in enumerate(items):
        plt.subplot(nr,nc,cnt+1)
        b = df[item].isnull()
        pcnt = df.loc[~b,'Group'].value_counts()
        b1 = pcnt > 1
        group_sel = pcnt.index.values[b1].tolist()

        if len(group_sel) > 1:
            b = (~b) & df['Group'].isin(group_sel)
            
            lst = df.loc[b, 'Group'].unique()
            lst_pair = []
            if annot_ref in lst:
                for k, l1 in enumerate(lst):
                    if l1 != annot_ref:
                        lst_pair.append((annot_ref, l1))
            else:
                for k, l1 in enumerate(lst):
                    for j, l2 in enumerate(lst):
                        if j <  k:
                            lst_pair.append((l1, l2))
        
            ax = sns.boxplot(data = df.loc[b,:], x = 'Group', y = item, order = group_order,
                             hue = 'Group', palette=cmap )
            if stripplot:
                sns.stripplot(x='Group', y=item, data=df.loc[b,:],  
                              color="black", order = group_order, size = stripplot_ms, 
                              jitter = stripplot_jitter )
            if cnt%nc == 0: 
                ax.set_ylabel(ylabel, fontsize = label_fs)                
            else: 
                ax.set_ylabel(None)
                
            if cnt >= nc*(nr-1): 
                ax.set_xlabel('Condition', fontsize = label_fs)
            else: 
                ax.set_xlabel(None)

            title = item
            if (rename_cells is not None) & isinstance(rename_cells, dict):
                for key in rename_cells.keys():
                    title = title.replace(key, rename_cells[key])
            ax.set_title(title, fontsize = title2_fs)
            
            if cnt < (nr*nc - nc):
                # plt.xticks([])
                plt.xticks(rotation = xtick_rot, ha = xtick_ha, fontsize = tick_fs)
                plt.yticks(fontsize = tick_fs)
            else:
                plt.xticks(rotation = xtick_rot, ha = xtick_ha, fontsize = tick_fs)
                plt.yticks(fontsize = tick_fs)
    
            if annot:
                '''
                add_stat_annotation(ax, data=df.loc[b,:], x = 'Group', y = item, 
                                    order = group_order,
                            box_pairs=lst_pair, loc='inside', fontsize = annot_fs,
                            test='t-test_ind', text_format=annot_fmt, verbose=0)
                '''
                annotator = Annotator(ax, pairs=lst_pair, data=df.loc[b,:], 
                                      x="Group", y=item, order=group_order)
                annotator.configure(test='t-test_ind', text_format=annot_fmt, 
                                    loc='inside', verbose=False, show_test_name=False,
                                    fontsize = annot_fs)
                annotator.apply_and_annotate()   

            cnt += 1
            #'''
    
    if (cnt < (nr*nc)):
        if (nr == 1):
            for k in range(nr*nc - cnt):
                axes[cnt%nc + k].axis("off")
        else:
            for k in range(nr*nc - cnt):
                r = nr - int(k/nc)
                axes[r-1][nc - k%nc -1].axis("off")
        
    plt.show()
    return 
