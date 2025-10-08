import time, os, copy, datetime, math, random, warnings
import numpy as np
import pandas as pd
import scanpy as sc
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import cm
# from scoda.hicat import get_markers_cell_type, get_markers_minor_type2, get_markers_major_type

try:
    import plotly.graph_objects as go
except ImportError:
    print('WARNING: plotly not installed.')
    
    
### Example 
# lst = [adata_t.obs['cell_type_major_pred'], adata_t.obs['tumor_dec'], adata_t.obs['subtype']] #, 
# plot_sankey_e( lst, title = None, fs = 12, WH = (800, 600), th = 0, title_y = 0.85 )

def plot_sankey_e( lst, title = None, fs = 12, WH = (700, 800), th = 0, title_y = 0.85 ):
    
    if len(lst) < 2:
        print('ERROR: Input must have length of 2 or more.')
        return
    
    W = WH[0]
    H = WH[1]

    sall = []
    tall = []
    vall = []
    lbl_all = []
    label_lst = []
    
    nn_cnt = 0
    for nn in range(len(lst)-1):
        source_in = ['L%i_%s' % (nn+1, a) for a in list(lst[nn])]
        target_in = ['L%i_%s' % (nn+2, a)  for a in list(lst[nn+1])]
                
        source = pd.Series(source_in).astype(str)
        b = source.isna()
        source[b] = 'N/A'
        target = pd.Series(target_in).astype(str)
        b = target.isna()
        target[b] = 'N/A'

        src_lst = list(set(source))
        tgt_lst = list(set(target))
        src_lst.sort()
        tgt_lst.sort()

        if th > 0:
            bx = np.full(len(source), True)
            for k, s in enumerate(src_lst):
                bs = source == s
                for m, t in enumerate(tgt_lst):
                    bt = target == t
                    b = bs & bt
                    if np.sum(b) < th:
                        bx[b] = False
            source = source[bx]
            target = target[bx]

            src_lst = list(set(source))
            tgt_lst = list(set(target))
            src_lst.sort()
            tgt_lst.sort()

        src = []
        tgt = []
        val = []
        sl_lst = []
        tl_lst = []
        Ns = len((src_lst))
        for k, s in enumerate(src_lst):
            bs = source == s
            for m, t in enumerate(tgt_lst):
                bt = target == t
                b = bs & bt
                if (np.sum(b) > 0):
                    if s not in sl_lst:
                        sn = len(sl_lst)
                        sl_lst.append(s)
                    else:
                        for n, lbl in enumerate(sl_lst):
                            if s == lbl:
                                sn = n
                                break

                    if t not in tl_lst:
                        tn = len(tl_lst) + Ns
                        tl_lst.append(t)
                    else:
                        for n, lbl in enumerate(tl_lst):
                            if t == lbl:
                                tn = n + Ns
                                break

                    src.append(sn)
                    tgt.append(tn)
                    val.append(np.sum(b))
                    label_lst = sl_lst + tl_lst
                    nn_cnt += 1

        if (nn == 0): # | (nn_cnt == 0):
            src2 = src
            tgt2 = tgt
        else:
            lbl_ary = np.array(lbl_all)
            sseq = np.arange(len(lbl_ary))
            src2 = []
            for a in src:
                s = sl_lst[a]
                b = lbl_ary == s
                if np.sum(b) == 1:
                    m = sseq[b][0]
                    src2.append(m)
                else:
                    print('ERROR ... S')
            
            # src2 = [(a + len(lbl_all) - len(sl_lst)) for a in src]
            tgt2 = [(a + len(lbl_all) - len(sl_lst)) for a in tgt]
        
        sall = sall + copy.deepcopy(src2)
        tall = tall + copy.deepcopy(tgt2)
        vall = vall + copy.deepcopy(val)
        if nn == 0:
            lbl_all = copy.deepcopy(label_lst)
        else:
            lbl_all = lbl_all + copy.deepcopy(tl_lst)
    '''
    mat = np.array([sall,tall,vall])
    print(mat)
    print(lbl_all)
    '''      
        
    link = dict(source = sall, target = tall, value = vall)
    node = dict(label = lbl_all, pad=50, thickness=5)
    data = go.Sankey(link = link, node=node)
    layout = go.Layout(height = H, width = W)
    # plot
    fig = go.Figure(data, layout)
    if title is not None:
        fig.update_layout(
            title={
                'text': '<span style="font-size: ' + '%i' % fs + 'px;">' + title + '</span>',
                'y':title_y,
                'x':0.5,
                # 'font': 12,
                'xanchor': 'center',
                'yanchor': 'top'})    
    fig.show()   
    return



'''
### DigitalCellSorter

## df_ann = cell_type_id_using_DCS( df, name = 'DCS_tmp', batch = None, mkr = 'CIBERSORT_LM22_7', n_clust = 30 )

import urllib.request
import DigitalCellSorter
import DigitalCellSorter.ReadPrepareDataHCA as prep 
import DigitalCellSorter as DCS

def cell_type_id_using_DCS( df, name = 'DCS_tmp', batch = None,
                            mkr = 'CIBERSORT_LM22_7', n_clust = 30 ):
    
    df_exp = df.transpose()
    
    if batch is not None:
        bid = list(batch)
        cid = list(df_exp.columns.values)
        colnames = list(zip(bid,cid))
        rend = dict(zip(cid, colnames))
        df_exp.rename(columns = rend, inplace = True)
    
    # Create an instance of class DigitalCellSorter. 
    # Here we use Default parameter values for most of the parameters
    DCS = DigitalCellSorter.DigitalCellSorter(dataName=name, 
                                              # geneNamesType = 'symbol',
                                              nClusters=n_clust, 
                                              saveDir=name, 
                                              geneListFileName=mkr)

    # Validate the expression data, so that it has correct form
    DCS.prepare(df_exp)
    
    # Process the expression data, i.e. quality control, dimensionality reduction, clustering
    DCS.process()

    # Load marker genes and annotate cells
    d = DCS.annotate()
    
    cell_types = []
    for key in d.keys():
        s = d[key].split(' #')[0]
        cell_types.append(s)

    cell_types = list(set(cell_types))  

    df_ann = pd.DataFrame(index = df_exp.columns.values)
    df_ann['cell_type_pred'] = 'unassigned'
    for ct in cell_types:
        idxs = DCS.getCells(celltype=ct)
        df_ann.loc[idxs, 'cell_type_pred'] = ct

    b = df_ann['cell_type_pred'] == 'Unassigned'
    df_ann.loc[b, 'cell_type_pred'] = 'unassigned'
    
    batch_idx = df_ann.index.values
    batch, idx = zip(*batch_idx)
    rend = dict(zip(batch_idx, idx))
    df_ann.rename(index = rend, inplace = True)
    
    return df_ann 
    

## For performance evaluation

## df_perf = get_perf_ext( df_pred, cell_types_not_consider, truth = 'cell_type_true' )

def get_perf_ext( df_pred, cell_types_not_consider, truth = 'cell_type_true' ):
    
    cell_type = df_pred[truth]
    bc = np.full(len(cell_type), False)
    for ct in cell_types_not_consider:
        bc = bc | (cell_type == ct)
    df_pred = df_pred.loc[~bc,:]
        
    cols = list(df_pred.columns.values)
    if 'target_cell_types' in cols:
        cols.remove('target_cell_types')
    if truth in cols:
        cols.remove(truth)
    
    df_perf = pd.DataFrame(index = ['C', 'CUA', 'EUA', 'EA', 'E'])
    tcts = list(set(df_pred['target_cell_types']))
    
    bt = np.full( df_pred.shape[0], False )
    for k, tct in enumerate(tcts):
        b1 = df_pred['target_cell_types'] == tct
        tct_lst = tct.split(',')
        for ct in tct_lst:
            b2 = df_pred[truth] == ct
            bt = bt | (b1&b2)
                
    bz = df_pred[truth] != 'Unknown'
    df_perf['ideal'] = [np.sum(bz&bt)/np.sum(bz), \
                        np.sum(bz&(~bt))/np.sum(bz), 0,0,0]
        
    for c in cols:
        tcol = c        
        ba = np.full( df_pred.shape[0], False )
        for k, tct in enumerate(tcts):
            b1 = df_pred['target_cell_types'] == tct
            tct_lst = tct.split(',')
            for ct in tct_lst:
                b2 = df_pred[tcol] == ct
                ba = ba | (b1&b2)                
        bua = ~ba
        b_cua = ((bz) & (~bt) & (bua))
        b_ea = ((bz) & (~bt) & (ba))
        b_eua = ((bz) & (bt) & (bua))
        b_e = ((bz) & (bt) & (~bua) & (df_pred[tcol] != df_pred[truth]))
        b_c = ((bz) & (bt) & (~bua) & (df_pred[tcol] == df_pred[truth]))
        
        n_correctly_unassigned = np.sum(b_cua)/np.sum(bz)
        n_incorrectly_assigned = np.sum(b_ea)/np.sum(bz)
        n_incorrectly_unassigned = np.sum(b_eua)/np.sum(bz)
        n_incorrect = np.sum(b_e)/np.sum(bz)
        n_correct = np.sum(b_c)/np.sum(bz)
        
        df_perf[c] = [n_correct, n_correctly_unassigned, n_incorrectly_unassigned, \
                      n_incorrectly_assigned, n_incorrect]

    df_perf = df_perf*100
    df_perf = df_perf.loc[['C', 'EUA', 'E', 'EA', 'CUA'],:]
    df_perf.loc['Method',:] = list(df_perf.columns.values)
    df_perf = df_perf.T

    return df_perf
'''

### Plot_dot

## plot_dot(adata, target_lst, type_level, mkr_file, title = None, rend = None, level = 1, 
##               cutoff = 0, PNSH12 = '100000', rem_cmn = False, dot_max = 0.5, swap_ax = False,
##               to_exclude = [])

def remove_common( mkr_dict, prn = True ):

    cts = list(mkr_dict.keys())
    mkrs_all = []
    for c in cts:
        mkrs_all = mkrs_all + mkr_dict[c]
    mkrs_all = list(set(mkrs_all))
    df = pd.DataFrame(index = mkrs_all, columns = cts)
    df.loc[:,:] = 0

    for c in cts:
        df.loc[mkr_dict[c], c] = 1
    Sum = df.sum(axis = 1)
    
    to_del = []
    s = ''
    for c in cts:
        b = (df[c] > 0) & (Sum == 1)
        mkrs1 = list(df.index.values[b])
        if prn & (len(mkr_dict[c]) != len(mkrs1)):
            s = s + '%s: %i > %i, ' % (c, len(mkr_dict[c]), len(mkrs1))
        
        if len(mkrs1) == 0:
            to_del.append(c)
        else:
            mkr_dict[c] = mkrs1

    if prn & len(s) > 0:
        print(s[:-2])

    if len(to_del) > 0:
        for c in cts:
            if c in to_del:
                del mkr_dict[c]
                
    return mkr_dict


def get_markers_all(mkr_file, target_lst, pnsh12, genes = None, level = 1, rem_cmn = False):
    
    # target = 'Myeloid cell'
    if level == 0:
        mkr_dict, mkr_dict_neg = \
            get_markers_major_type(mkr_file, target_cells = target_lst, 
                                    pnsh12 = pnsh12, rem_common = False, verbose = False)
    elif level == 1:
        mkr_dict, mkr_dict_neg = \
            get_markers_minor_type2(mkr_file, target_cells = target_lst, 
                                    pnsh12 = pnsh12, rem_common = False, verbose = False)
    else:
        mkr_dict, mkr_dict_neg = \
            get_markers_cell_type(mkr_file, target_cells = target_lst, pnsh12 = pnsh12,
                          rem_common = False, verbose = False)
        
    if rem_cmn:
        mkr_dict = remove_common( mkr_dict, prn = True )
        
    mkrs_all = [] #['SELL']
    mkrs_cmn = []
    for ct in mkr_dict.keys():
        if genes is not None:
            ms = list(set(mkr_dict[ct]).intersection(genes))
        else: 
            ms = mkr_dict[ct]
        mkrs_all = mkrs_all + ms
        if len(mkrs_cmn) == 0:
            mkrs_cmn = ms
        else:
            mkrs_cmn = list(set(mkrs_cmn).intersection(ms))

    mkrs_all = list(set(mkrs_all))
    if genes is not None:
        mkrs_all = list(set(mkrs_all).intersection(genes))
    
    return mkrs_all, mkr_dict


def update_markers_dict(mkrs_all, mkr_dict, X, y, rend = None, cutoff = 0.3, 
                        Nall = 20, Npt = 20):
    
    if rend is None:
        lst = list(mkr_dict.keys())
        lst.sort()
        rend = dict(zip(lst, lst))
    else:
        lst = list(rend.keys())
        
    df = pd.DataFrame(index = lst, columns = mkrs_all)
    df.loc[:,:] = 0
        
    for ct in lst:
        b = y == ct
        ms = list(set(mkr_dict[ct]).intersection(mkrs_all))
        pe = list((X.loc[b,ms] > 0).mean(axis = 0))
        for j, m in enumerate(ms):
            df.loc[ct, m] = pe[j]

    if df.shape[0] == 1:
        mkrs_all = list(df.columns.values)
        mkrs_dict = {}
        for ct in lst:
            b = y == ct
            ms = list(set(mkr_dict[ct]).intersection(mkrs_all))
            pe = np.array((X.loc[b,ms] > 0).mean(axis = 0))
            odr = np.array(-pe).argsort()
            ms_new = []
            for o in odr:
                if (pe[o] >= cutoff):
                    ms_new.append(ms[o])

            if len(ms_new) > 0:
                mkrs_dict[rend[ct]] = ms_new[:min(Npt,len(ms_new))]
    else:
        p1 = df.max(axis = 0)
        p2 = p1.copy(deep = True)
        p2[:] = 0
        idx = df.index.values
        for m in list(df.columns.values):
            odr = np.array(-df[m]).argsort()
            p2[m] = df.loc[idx[odr[1]], m]
        nn = (df >= 0.5).sum(axis = 0)

        b0 = p1 > 0
        b1 = (p2/(p1 + 0.0001)) < 0.5
        b2 = nn < 4
        b = b0 # & b1 & b2
        df = df.loc[:,b]
        mkrs_all = list(df.columns.values)

        mkrs = [] 
        cts = [] 
        pes = [] 
        mkrs_dict = {}
        for ct in lst:
            b = y == ct
            ms = list(set(mkr_dict[ct]).intersection(mkrs_all))
            p2t = np.array(p2[ms])
            p1t = np.array(p1[ms])
            pe = np.array((X.loc[b,ms] > 0).mean(axis = 0))
            odr = np.array(-pe).argsort()
            ms_new = []
            for o in odr:
                if (pe[o] >= cutoff):
                    ms_new.append(ms[o])

            if len(ms_new) > 0:
                mkrs_dict[rend[ct]] = ms_new[:min(Npt,len(ms_new))]

    return mkrs_dict, df


def plot_dot(adata, target_lst, type_level, mkr_file, title = None, rend = None, level = 1, 
              cutoff = 0, PNSH12 = '100000', rem_cmn = False, dot_max = 0.5, swap_ax = False,
              to_exclude = [], Npt = 10):

    SCANPY = True
    try:
        import scanpy as sc
    except ImportError:
        SCANPY = False
    
    if (not SCANPY):
        print('ERROR: scanpy not installed. ')   
        return
    
    target = ','.join(target_lst)
    genes = list(adata.var.index.values)
    genes = list(set(genes) - set(to_exclude))
    mkrs_all, mkr_dict = get_markers_all(mkr_file, target_lst, 
                                         PNSH12, genes, level, rem_cmn = rem_cmn)
    target_lst2 = list(mkr_dict.keys())
    y = adata.obs[type_level]
    b = y == target_lst2[0]
    for t in target_lst2:
        b = b | (y == t)

    adata_t = adata[b,mkrs_all]
    X = adata_t.to_df()
    y = adata_t.obs[type_level]

    mkrs_dict, df = update_markers_dict(mkrs_all, mkr_dict, X, y, rend, 
                                        cutoff = cutoff, Npt = Npt)

    if ('Mac (M1)' in list(mkrs_dict.keys())) & ('Mac (M2)' in list(mkrs_dict.keys())):
        mac_common = list(set(mkrs_dict['Mac (M1)']).intersection(mkrs_dict['Mac (M2)']))
        for item in mac_common:
            mkrs_dict['Mac (M1)'].remove(item)
            mkrs_dict['Mac (M2)'].remove(item)
        if 'Mono' in list(mkrs_dict.keys()):
            mono_lst = mkrs_dict['Mono']
            del mkrs_dict['Mono']
            mkrs_dict['Mono'] = mono_lst

    plt.rc('font', size=12)          
    adata_t.obs[type_level].replace(rend, inplace = True)

    dp = sc.pl.dotplot(adata_t, mkrs_dict, groupby = type_level, 
                       log = True, var_group_rotation = 0, show = False, 
                       standard_scale = 'var', dot_max = dot_max, swap_axes = swap_ax ) 

    ax = dp['mainplot_ax']
    if title is not None:
        ax.set_title(title, pad = 40, fontsize = 16) 
    ax.tick_params(labelsize=12)
    ax.set_ylabel('Annotated', fontsize = 14)
    return
    
    
def plot_dot_s(adata, target_lst, type_level, mkr_file, title = None, rend = None, level = 1, 
              cutoff = 0, PNSH12 = '100000', rem_cmn = False, dot_max = 0.5, swap_ax = False,
              to_exclude = [], Npt = 10, figsize = (20, 4)):

    SCANPY = True
    try:
        import scanpy as sc
    except ImportError:
        SCANPY = False
    
    if (not SCANPY):
        print('ERROR: scanpy not installed. ')   
        return
    
    target = ','.join(target_lst)
    genes = list(adata.var.index.values)
    genes = list(set(genes) - set(to_exclude))
    mkrs_all, mkr_dict = get_markers_all(mkr_file, target_lst, 
                                         PNSH12, genes, level, rem_cmn = rem_cmn)
    
    target_lst2 = list(mkr_dict.keys())
    y = adata.obs[type_level]
    b = y == target_lst2[0]
    nh = 0
    if np.sum(b) > 0: nh = 1
    for t in target_lst2:
        bt = y == t
        if np.sum(bt) > 0:
            b = b | (y == t)
            nh += 1

    adata_t = adata[b,mkrs_all]
    X = adata_t.to_df()
    y = adata_t.obs[type_level]

    mkrs_dict, df = update_markers_dict(mkrs_all, mkr_dict, X, y, rend, 
                                        cutoff = cutoff, Npt = Npt*2)
    
    mkall = []
    for key in mkrs_dict.keys():
        mkall = mkall + mkrs_dict[key]

    mkall = list(set(mkall))
    nmkr = dict(zip(mkall, [0]*len(mkall)))
    for key in mkrs_dict.keys():
        for m in mkrs_dict[key]:
            nmkr[m] += 1
            
    to_del = []
    for key in nmkr.keys():
        if nmkr[key] > 2: to_del.append(key)
            
    if len(to_del) > 0:
        for m in to_del:
            for key in mkrs_dict.keys():
                if m in mkrs_dict[key]:
                    mkrs_dict[key].remove(m)
            
    for key in mkrs_dict.keys():
        ms = mkrs_dict[key]
        if len(ms) > Npt:
            mkrs_dict[key] = ms[:Npt]
    
    lst = ['T cell (Cytotoxic)', 'T cell (Naive)','T cell (Tfh)','T cell (Th1)',
           'T cell (Th2)','T cell (Th9)','T cell (Th17)', 'T cell (Th22)','T cell (Treg)']
    lst_prac = list(adata_t.obs[type_level].unique())
    if set(list(mkrs_dict.keys())) in set(lst):
        mkrs_dict2 = {}
        for m in lst:
            if m in list(mkrs_dict.keys()):
                mkrs_dict2[m] = mkrs_dict[m]
        mkrs_dict = mkrs_dict2    
    
    mkrs_dict2 = {}
    for m in mkrs_dict.keys():
        if m in lst_prac: mkrs_dict2[m] = mkrs_dict[m]
    mkrs_dict = mkrs_dict2    
    
    
    nw = 0
    for key in mkrs_dict.keys():
        nw += len(mkrs_dict[key])
    '''
    if ('Macrophage (M1)' in list(mkrs_dict.keys())) & ('Macrophage (M2)' in list(mkrs_dict.keys())):
        mac_common = list(set(mkrs_dict['Macrophage (M1)']).intersection(mkrs_dict['Macrophage (M2)']))
        for item in mac_common:
            mkrs_dict['Macrophage (M1)'].remove(item)
            mkrs_dict['Macrophage (M2)'].remove(item)
        if 'Monocyte' in list(mkrs_dict.keys()):
            mono_lst = mkrs_dict['Monocyte']
            del mkrs_dict['Monocyte']
            mkrs_dict['Monocyte'] = mono_lst
    '''

    plt.rc('font', size=12)          
    if rend is not None: adata_t.obs[type_level].replace(rend, inplace = True)

    dp = sc.pl.dotplot(adata_t, mkrs_dict, groupby = type_level, figsize = (nw*0.36, nh*0.3),
                       log = True, var_group_rotation = 0, show = False, 
                       standard_scale = 'var', dot_max = dot_max, swap_axes = swap_ax ) 

    ax = dp['mainplot_ax']
    if title is not None:
        ax.set_title(title, pad = 40, fontsize = 16) 
    ax.tick_params(labelsize=12)
    ax.set_ylabel('Annotated', fontsize = 14)
    return
    

def plot_marker_expression_profile( df_pred, X, mkr_file, pnsh12 = '100000', Npt = 10 ):

    ANNDATA = True
    try:
        from anndata import AnnData
    except ImportError:
        ANNDATA = False

    if (not ANNDATA):
        print('ERROR: anndata not installed. ')   
        return
        
    adata = AnnData(X= X, obs = df_pred)
    adata
    dot_mx = 0.5
    cutoff = 0
    rem_cmn = False
    swap_ax = False

    PNSH12 = pnsh12

    Maj_types_pred = list(set(df_pred['cell_type_major']))

    mkr_dict, mkr_dict_neg = \
        get_markers_major_type(mkr_file, target_cells = [], pnsh12 = PNSH12,
                      rem_common = False, verbose = False)

    Maj_types = list(mkr_dict.keys())
    Maj_types = list(set(Maj_types).intersection(Maj_types_pred))

    mlst_s = []
    mlst_m = []
    for m in Maj_types:

        mkr_dict_minor, mkr_dict_neg = \
            get_markers_cell_type(mkr_file, target_cells = [m], pnsh12 = PNSH12,
                          rem_common = False, verbose = False)

        Min_types = list(mkr_dict_minor.keys())
        mkr_dict, mkr_dict_neg = \
            get_markers_minor_type2(mkr_file, target_cells = Min_types, pnsh12 = PNSH12,
                      rem_common = False, verbose = False)
        if len(mkr_dict.keys()) > 1:
            # print('%s: %i' % (m, len(mkr_dict.keys())))
            mlst_m.append(m)
        else:
            # print('%s: %i' % (m, len(mkr_dict.keys())))
            mlst_s.append(m)

    ## Major 
    target_lst = mlst_s
    rend = None # dict(zip(lst, lst2))
    type_exc = []
    type_col = 'cell_type_major'
    level = 0

    title = 'Marker expression of %s' % target_lst[0]
    for t in target_lst[1:]: title = title + ',%s' % t
    
    plot_dot_s(adata, target_lst, type_col, mkr_file, title, 
              rend = rend, level = level,
              cutoff = cutoff, PNSH12 = PNSH12, rem_cmn = rem_cmn, dot_max = dot_mx, 
              swap_ax = swap_ax, to_exclude = type_exc, Npt = Npt)

    ## Subset 
    level = 1
    type_col = 'cell_type_subset'

    for m in mlst_m:
        mkr_dict_minor, mkr_dict_neg = \
            get_markers_cell_type(mkr_file, target_cells = [m], pnsh12 = '100000',
                          rem_common = False, verbose = False)
        if m[0] == 'T':
            target_lst = list(mkr_dict_minor.keys())
            t1 = []
            t2 = []
            for t in target_lst:
                if ('NK' in t.upper()) | ('ILC' in t.upper()):
                    t2.append(t)
                elif ('CD4' in t.upper()) | ('CD8' in t.upper() ):
                    t1.append(t)

            if len(t1) > 0:
                target_lst = t1
                title = 'Marker expression of %s' % target_lst[0]
                for t in target_lst[1:]: title = title + ',%s' % t
                plot_dot_s(adata, target_lst, type_col, mkr_file, title, 
                          rend = rend, level = level,
                          cutoff = cutoff, PNSH12 = PNSH12, rem_cmn = rem_cmn, dot_max = dot_mx, 
                          swap_ax = swap_ax, to_exclude = type_exc, Npt = Npt)
            if len(t2) > 0:
                target_lst = t2
                title = 'Marker expression of %s' % target_lst[0]
                for t in target_lst[1:]: title = title + ',%s' % t
                plot_dot_s(adata, target_lst, type_col, mkr_file, title, 
                          rend = rend, level = level,
                          cutoff = cutoff, PNSH12 = PNSH12, rem_cmn = rem_cmn, dot_max = dot_mx, 
                          swap_ax = swap_ax, to_exclude = type_exc, Npt = Npt)

    for m in mlst_m:
        mkr_dict_minor, mkr_dict_neg = \
            get_markers_cell_type(mkr_file, target_cells = [m], pnsh12 = '100000',
                          rem_common = False, verbose = False)
        if m[0] != 'T':
            target_lst = list(mkr_dict_minor.keys())
            title = 'Marker expression of %s' % target_lst[0]
            for t in target_lst[1:]: title = title + ',%s' % t
            plot_dot_s(adata, target_lst, type_col, mkr_file, title, 
                      rend = rend, level = level,
                      cutoff = cutoff, PNSH12 = PNSH12, rem_cmn = rem_cmn, dot_max = dot_mx, 
                      swap_ax = swap_ax, to_exclude = type_exc, Npt = Npt)
    return
                
            
def plot_dot2(adata, target_lst, type_level, type_level2, mkr_file, title = None, 
              rend = None, rend2 = None, level = 1, 
              cutoff = 0, PNSH12 = '100000', rem_cmn = False, dot_max = 0.5, swap_ax = False,
              to_exclude = []):

    target = ','.join(target_lst)
    genes = list(adata.var.index.values)
    genes = list(set(genes) - set(to_exclude))
    mkrs_all, mkr_dict = get_markers_all(mkr_file, target_lst, 
                                         PNSH12, genes, level, rem_cmn = rem_cmn)
    target_lst2 = list(mkr_dict.keys())
    y = adata.obs[type_level]
    b = y == target_lst2[0]
    for t in target_lst2:
        b = b | (y == t)

    adata_t = adata[b,mkrs_all]
    X = adata_t.to_df()
    y = adata_t.obs[type_level]

    mkrs_dict, df = update_markers_dict(mkrs_all, mkr_dict, X, y, rend, 
                                        cutoff = cutoff, Npt = 21)

    if ('Mac (M1)' in list(mkrs_dict.keys())) & ('Mac (M2)' in list(mkrs_dict.keys())):
        mac_common = list(set(mkrs_dict['Mac (M1)']).intersection(mkrs_dict['Mac (M2)']))
        for item in mac_common:
            mkrs_dict['Mac (M1)'].remove(item)
            mkrs_dict['Mac (M2)'].remove(item)
        if 'Mono' in list(mkrs_dict.keys()):
            mono_lst = mkrs_dict['Mono']
            del mkrs_dict['Mono']
            mkrs_dict['Mono'] = mono_lst

    plt.rc('font', size=12)   
    adata_t.obs[type_level2].replace(rend2, inplace = True)

    dp = sc.pl.dotplot(adata_t, mkrs_dict, groupby = type_level2, 
                       log = True, var_group_rotation = 0, show = False, 
                       standard_scale = 'var', dot_max = dot_max, swap_axes = swap_ax ) 

    ax = dp['mainplot_ax']
    if title is not None:
        ax.set_title(title, pad = 40, fontsize = 16) 
    ax.tick_params(labelsize=12)
    ax.set_ylabel('Annotated', fontsize = 14)

    return adata_t


def plot_dot3(adata, target_lst, type_level, groupby, mkr_file, title = None, rend = None, level = 1, 
              cutoff = 0, PNSH12 = '100000', rem_cmn = False, dot_max = 0.5, swap_ax = False,
              to_exclude = [], dendrogram = True):

    target = ','.join(target_lst)
    genes = list(adata.var.index.values)
    genes = list(set(genes) - set(to_exclude))
    mkrs_all, mkr_dict = get_markers_all(mkr_file, target_lst, 
                                         PNSH12, genes, level, rem_cmn = rem_cmn)
    target_lst2 = list(mkr_dict.keys())
    y = adata.obs[type_level]
    b = y == target_lst2[0]
    for t in target_lst2:
        b = b | (y == t)

    adata_t = adata[b,mkrs_all]
    X = adata_t.to_df()
    y = adata_t.obs[type_level]

    mkrs_dict, df = update_markers_dict(mkrs_all, mkr_dict, X, y, rend, 
                                        cutoff = cutoff, Npt = 21)

    if ('Mac (M1)' in list(mkrs_dict.keys())) & ('Mac (M2)' in list(mkrs_dict.keys())):
        mac_common = list(set(mkrs_dict['Mac (M1)']).intersection(mkrs_dict['Mac (M2)']))
        for item in mac_common:
            mkrs_dict['Mac (M1)'].remove(item)
            mkrs_dict['Mac (M2)'].remove(item)
        if 'Mono' in list(mkrs_dict.keys()):
            mono_lst = mkrs_dict['Mono']
            del mkrs_dict['Mono']
            mkrs_dict['Mono'] = mono_lst

    plt.rc('font', size=12)          
    adata_t.obs[type_level].replace(rend, inplace = True)

    dp = sc.pl.dotplot(adata_t, mkrs_dict, groupby = groupby, 
                       log = True, var_group_rotation = 0, show = False, 
                       standard_scale = 'var', dot_max = dot_max, swap_axes = swap_ax,
                       dendrogram = dendrogram) 

    ax = dp['mainplot_ax']
    if title is not None:
        ax.set_title(title, pad = 40, fontsize = 16) 
    ax.tick_params(labelsize=12)
    ax.set_ylabel('Annotated', fontsize = 14)
    return
    
### sc-basic proc

def X_normalize(X):    
    return X.div(X.sum(axis=1)*0.0001 + 0.0001, axis = 0)


def X_scale(X, max_val = 10):    
    m = X.mean(axis = 0)
    s = X.std(axis = 0)
    
    Xs = X.sub(m).mul((s > 0)/(s+ 0.0001))
    Xs.clip(upper = max_val, lower = -max_val, inplace = True)
    
    return Xs

#'''
def select_variable_genes(X, log_transformed = False):
    
    if log_transformed:
        Xs = 10**X
        Xs = Xs - Xs.min().min()
    else:
        Xs = X 
        
    m = Xs.mean(axis = 0)
    s = Xs.var(axis = 0)

    b = (m > 0) & (s > 0)
    m = m[b]
    s = s[b]
    Xs = Xs.loc[:,b]    
        
    # print('1 .. ', end = '', flush = True)
    lm = np.log10(m + 0.000001)
    ls = np.log10(s + 0.000001)
    
    # print('2 (%i, %i) .. ' % (len(lm), len(ls)), end = '', flush = True)
    z = np.polyfit(lm, ls, 2)
    # print('2a .. ', end = '', flush = True)
    p = np.poly1d(z)
    # print('2b .. ', end = '', flush = True)
    s_fit = 10**(p(lm))

    # print('3 .. ', end = '', flush = True)
    Xt = Xs.sub(m).mul(1/np.sqrt(s_fit))
    Xt.clip(upper = np.sqrt(Xt.shape[0]), inplace = True)

    # print('4 .. ', end = '', flush = True)
    sr = Xt.std(axis = 0)
    odr = np.array(sr).argsort()
    s_th = sr[odr[-2000]]
    genes = list(Xt.columns.values[sr >= s_th])
    
    return genes
#'''

from sklearn import cluster, mixture
from sklearn.neighbors import kneighbors_graph
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KNeighborsRegressor
try:
    from sknetwork.clustering import Louvain
except ImportError:
    print('WARNING: sknetwork not installed.')

def clustering_alg(X_pca, clust_algo = 'lv', resolution = 1, N_neighbors = 10, N_clusters = 25):
    
    if clust_algo[:2] == 'gm':
        gmm = mixture.GaussianMixture(n_components = int(N_clusters), random_state = 0)
        cluster_label = gmm.fit_predict(X_pca)
        return cluster_label, gmm
    elif clust_algo[:2] == 'km':
        km = cluster.KMeans(n_clusters = int(N_clusters), random_state = 0)
        km.fit(X_pca)
        cluster_label = km.labels_
        return cluster_label, km
    else:
        adj = kneighbors_graph(X_pca, int(N_neighbors), mode='connectivity', include_self=True)
        louvain = Louvain(resolution = resolution)
        cluster_label = louvain.fit_transform(adj)        
        return cluster_label, louvain

    return


from importlib_resources import files

def load_GTmap( target = 'hg38' ):
    
    if target in ['hg38', 'hg19', 'mm10']:
        # path = files('mlbi_at_dku_lib.data').joinpath('GTmap_%s.csv' % target)
        f = '/GTmap_%s.csv.gz' % target
        path = str( files('mlbi').joinpath('data') )
        return pd.read_csv(path + f, index_col = 0)
    else:
        print('ERROR: cannot find the data file %s.' % ('GTmap_%s.csv.gz' % target))
        print('You can choose one of hg38, hg19, mm10')
        return None
    
    return None