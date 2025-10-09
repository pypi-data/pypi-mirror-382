import time, os, sys, warnings, collections
import numpy as np
import pandas as pd
from scipy import stats
from multiprocessing import Pool, cpu_count
from .bistack import _pip_install, _pkg_base_name, _get_dist_version

SKLEARN = True
try:
    from sklearn.decomposition import PCA
except ImportError:
    SKLEARN = False
    print('DEiso ERROR: scikit-learn not installed.')

TQDM = True
try:
    from tqdm.auto import tqdm
except ImportError:
    spec = 'tqdm'
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
            TQDM = False

    
def DEiso_pca( dfs, n_comp = 2 ):

    rownames = ['PC%i' % (i+1) for i in range(int(n_comp))]
    pca_obj = PCA(n_components=int(n_comp))
    X_pca = pca_obj.fit_transform(dfs.transpose()).transpose()  
    df_pca = pd.DataFrame(X_pca, index = rownames, columns = dfs.columns.values)
    return df_pca


def get_mean_and_cov(dfx):
    m = dfx.mean(axis = 1)
    dfy = dfx.sub(m, axis = 0)
    C = dfy.dot(dfy.transpose())/(dfy.shape[1]-1)    
    return m, C 


def DEiso_anal_per_gene( dfs_in, groups, gr, norm = False, test = 't2', log = False,
                         n_pca_comp = 0, cn_th = 1e-10, ro = 0.01, nth = 0.8 ):
    
    dfs = dfs_in.copy(deep = True)
    if norm:
        dfs = dfs.div(dfs.sum(axis = 0), axis = 1)*100
        if log:
            dfs = np.log2(dfs + 1)
            
    if (n_pca_comp > 0) & (n_pca_comp < dfs.shape[0]):
        dfs = DEiso_pca( dfs, n_comp = min(n_pca_comp, dfs.shape[0]) )
    if (n_pca_comp == 0) & (dfs.shape[0] > (dfs.shape[1]-2)):
        dfs = DEiso_pca( dfs, n_comp = (dfs.shape[1]-2) )
    
    samples = np.array(list(dfs.columns.values))
    glst = list(groups)
    glst = list(set(glst))
    glst.sort()
    if gr in glst:
        glst.remove(gr)

    cov = {}
    mns = {}
    
    b = np.array(groups) == gr
    ssel = list(samples[b])
    
    bt = ((dfs[ssel] > 0).sum(axis = 0) > 0)
    if bt.sum() < dfs[ssel].shape[1]*nth:
        return None

    # Cr = np.array( dfs[ssel].transpose().cov() )
    # mr = np.array( dfs[ssel].mean(axis = 1) )
    mr, Cr = get_mean_and_cov(dfs[ssel])
    nr = len(ssel)
    
    res = {}
    for i, g in enumerate(glst):
        b = np.array(groups) == g
        ssel = list(samples[b])
        
        bt = ((dfs[ssel] > 0).sum(axis = 0) > 0)
        if bt.sum() >= dfs[ssel].shape[1]*nth:
        
            # Ct = np.array( dfs[ssel].transpose().cov() )
            # mt = np.array( dfs[ssel].mean(axis = 1) )
            mt, Ct = get_mean_and_cov(dfs[ssel])
            nt = len(ssel)
            
            m = mt - mr    

            # C = ((nr-1)*Cr + (nt-1)*Ct)/(nr + nt - 2)
            C = (0.5*Cr + 0.5*Ct)
            C = C + (np.diag(C).mean()*ro)*np.eye(C.shape[0])
            
            if np.linalg.det(C) < cn_th:
                c1 = 0
            else:
                C = np.linalg.inv(C)
                c1 = m.dot(C.dot(m))*(nr*nt)/(nr+nt)
                
                dofn = dfs.shape[0]
                if dofn <= (nr + nt - 2):
                    dofd = nr + nt - 1 - dofn
                else:
                    dofd = 1
                c1 = c1*(dofd)/((nr + nt - 2)*dofn)

                if test == 't2':
                    p1 = stats.f.sf(c1, dofn, dofd, loc=0, scale=1)
                else:
                    c1 = np.sqrt(c1)
                    p1 = stats.t.sf(c1, df = dofd)*2
                
                res['%s_vs_%s' % (g, gr)] = (c1, p1, dfs.shape[0], dofd)

    return res    


def DEiso_anal_single( df, gene_names, groups, ref_group, norm = True, test = 't2', log = False, 
                n_pca_comp = 0, rho = 0.1, nth = 0.8, verbose = True ):
    
    if not SKLEARN:
        print('DEiso ERROR: scikit-learn not installed.', flush=True)
        return None
    
    gr = ref_group
    glst = list(set(gene_names))
    glst.sort()
    idxs = {}
    for g in glst:
        idxs[g] = []

    ilst = list(df.index.values)
    nlst = list(gene_names)
    for g, t in zip(nlst, ilst):
        idxs[g].append(t)

    start = time.time()

    df_res = None
    cnt = 0
    for k, g in enumerate(glst):
        idx = idxs[g]
        if len(idx) >= 2:
            dfs = df.loc[idx,:]
            
            bt = ((dfs > 0).sum(axis = 0) > 1)
            if bt.sum() >= dfs.shape[1]: 
                
                # v = None
                v = DEiso_anal_per_gene( dfs, groups, gr, norm = norm, test = test, log = log,
                                        n_pca_comp = n_pca_comp, ro = rho, nth = nth )
                if v is not None:
                    if isinstance(v, dict):
                        keys = v.keys()
                        if cnt == 0:
                            df_res = {}
                            for key in keys:
                                df_res[key] = pd.DataFrame(columns = ['stat', 'pval', 'Niso', 'DoF'])

                        for key in keys:
                            if key in list(df_res.keys()):
                                df_res[key].loc[g, :] = list(v[key])
                            else:
                                df_res[key] = pd.DataFrame(columns = ['stat', 'pval', 'Niso', 'DoF'])

                    else:
                        if cnt == 0:
                            df_res = pd.DataFrame(columns = ['stat', 'pval', 'Niso', 'DoF'])
                        df_res.loc[g, :] = list(v)

                    cnt += 1

        if verbose: 
            if k%100 == 0: 
                print('DEiso Progress: %i/%i(%i)   ' % (k, len(glst), cnt), end = '\r', flush=True)

    elapsed = time.time() - start
    if verbose: print('DEiso done (%i) .. %i               ' % (elapsed, cnt), flush=True)

    if df_res is not None:
        if isinstance(df_res, dict):
            for key in df_res.keys():
                df_res[key]['pval_adj'] = df_res[key]['pval']*cnt
                b = df_res[key]['pval_adj'] > 1
                df_res[key].loc[b, 'pval_adj'] = 1
                df_res[key] = df_res[key].sort_values(['stat'], ascending = False)
        else:
            df_res['pval_adj'] = df_res['pval']*cnt
            b = df_res['pval_adj'] > 1
            df_res.loc[b, 'pval_adj'] = 1
            df_res = df_res.sort_values(['stat'], ascending = False)
       
    return df_res


def mc_core_DEiso_anal_per_gene( rs_tuple ):

    # rs_tuple.append( (dfx, groups, gr, norm, log, n_pca_comp, rho, nth, g ) )
    df, groups, gr, norm, log, n_pca_comp, rho, nth, g, test = rs_tuple
    
    df_res = DEiso_anal_single( df, g, groups, ref_group = gr, test = test, 
                         norm = norm, log = log, n_pca_comp = n_pca_comp, 
                         rho = rho, nth = nth, verbose = False )
    return df_res

        
def DEiso_anal( df, gene_names, groups, ref_group, norm = True, test = 't2', 
                log = False, n_pca_comp = 0, rho = 0.1, nth = 0.8, verbose = True, 
                n_cores = 1, chunk_size = 0 ):
    
    if not SKLEARN:
        print('DEiso ERROR: scikit-learn not installed.', flush=True)
        return None
    
    gr = ref_group
    glst = list(set(gene_names))
    glst.sort()
    idxs = {}
    for g in glst:
        idxs[g] = []

    ilst = list(df.index.values)
    nlst = list(gene_names)
    for g, t in zip(nlst, ilst):
        idxs[g].append(t)
        
    if not isinstance(gene_names, pd.Series):
        gene_names = pd.Series(gene_names, index = df.index)

    start = time.time()
    ###############################

    if (chunk_size > 0) & (n_cores > 1):
        ###############################
        ## Prepare arguments to pass ##
        df_res = None
        cnt = 0
        rs_tuple = []

        cnt = 0
        cnt_t = 0
        df_res = {}
        for k, g in enumerate(glst):
            idx = idxs[g]
            if len(idx) >= 2:
                dfs = df.loc[idx,:]

                bt = ((dfs > 0).sum(axis = 0) > 1)
                if bt.sum() >= dfs.shape[1]: 

                    if cnt == 0:
                        dfx = dfs
                        b = gene_names == g
                        gene_names_tmp = gene_names[idx]
                    else:
                        dfx = pd.concat([dfx, dfs], axis = 0)
                        gene_names_tmp = pd.concat([gene_names_tmp, gene_names[idx]], axis = 0)
                        
                    cnt += 1
                    cnt_t += 1

                    if cnt == chunk_size:
                        gns = gene_names_tmp 
                        rs_tuple.append( (dfx, groups, gr, norm, log, n_pca_comp, rho, nth, gns, test ) )
                        cnt = 0
                        
            if verbose: 
                if k%100 == 0: 
                    print('DEiso preparing: %i/%i(%i chunks)   ' % (k, len(glst), cnt_t), end = '\r', flush=True)

        if cnt > 0:
            rs_tuple.append( (dfx, groups, gr, norm, log, n_pca_comp, rho, nth, g, test ) )
        
        k += 1    
        print('DEiso preparing: %i/%i(%i chunks)   ' % (k, len(glst), len(rs_tuple)), flush=True)

        ###############################
        ## Run multicore processing ###
        #'''
        num_core = min( n_cores, (cpu_count() - 1) )
        pool = Pool(int(num_core))
        cnt = 0
        df_res = {}
        df_lst = []

        if TQDM:
            for dct in tqdm(pool.imap_unordered(mc_core_DEiso_anal_per_gene, rs_tuple), total=len(rs_tuple)):

                if dct is not None:
                    for key in dct.keys():
                        if key in list(df_res.keys()):
                            df_res[key] = pd.concat([df_res[key], dct[key]], axis = 0)
                        else:
                            df_res[key] = dct[key]
                    cnt += 1

                df_lst.append(dct)
        else:
            for dct in pool.imap_unordered(mc_core_DEiso_anal_per_gene, rs_tuple):

                if dct is not None:
                    for key in dct.keys():
                        if key in list(df_res.keys()):
                            df_res[key] = pd.concat([df_res[key], dct[key]], axis = 0)
                        else:
                            df_res[key] = dct[key]
                    cnt += 1

                df_lst.append(dct)


        pool.close()
        pool.join()
        #'''

    else:
        df_res = None
        cnt = 0
        for k, g in enumerate(glst):
            idx = idxs[g]
            if len(idx) >= 2:
                dfs = df.loc[idx,:]

                bt = ((dfs > 0).sum(axis = 0) > 1)
                if bt.sum() >= dfs.shape[1]: 

                    # v = None
                    v = DEiso_anal_per_gene( dfs, groups, gr, norm = norm, log = log,
                                            n_pca_comp = n_pca_comp, ro = rho, nth = nth )
                    if v is not None:
                        if isinstance(v, dict):
                            keys = v.keys()
                            if cnt == 0:
                                df_res = {}
                                for key in keys:
                                    df_res[key] = pd.DataFrame(columns = ['stat', 'pval', 'Niso', 'DoF'])

                            for key in keys:
                                if key in list(df_res.keys()):
                                    df_res[key].loc[g, :] = list(v[key])
                                else:
                                    df_res[key] = pd.DataFrame(columns = ['stat', 'pval', 'Niso', 'DoF'])
                                    df_res[key].loc[g, :] = list(v[key])

                        else:
                            if cnt == 0:
                                df_res = pd.DataFrame(columns = ['stat', 'pval', 'Niso', 'DoF'])
                            df_res.loc[g, :] = list(v)

                        cnt += 1

            if verbose: 
                if k%100 == 0: 
                    print('DEiso Progress: %i/%i(%i genes)   ' % (k, len(glst), cnt), end = '\r', flush=True)

    ###############################
    
    elapsed = time.time() - start
    if verbose: print('DEiso done (%i) .. %i                ' % (elapsed, cnt), flush=True)
        
    #'''
    if df_res is not None:
        if isinstance(df_res, dict):
            for key in df_res.keys():
                df_res[key]['pval_adj'] = df_res[key]['pval']*cnt
                b = df_res[key]['pval_adj'] > 1
                df_res[key].loc[b, 'pval_adj'] = 1
                df_res[key] = df_res[key].sort_values(['stat'], ascending = False)
        else:
            df_res['pval_adj'] = df_res['pval']*cnt
            b = df_res['pval_adj'] > 1
            df_res.loc[b, 'pval_adj'] = 1
            df_res = df_res.sort_values(['stat'], ascending = False)
    #'''
       
    return df_res


def save_to_excel(df_res_all, file_out, pv_cutoff = 0.1):

    cnt = 0
    for key in df_res_all.keys():

        if cnt == 0: 
            with pd.ExcelWriter(file_out, mode='w') as writer:
                b = df_res_all[key]['pval'] <= pv_cutoff
                df_res_all[key].loc[b,:].to_excel(writer, sheet_name = key)
        else: 
            with pd.ExcelWriter(file_out, mode='a', if_sheet_exists = 'replace') as writer:
                b = df_res_all[key]['pval'] <= pv_cutoff
                df_res_all[key].loc[b,:].to_excel(writer, sheet_name = key)
        cnt += 1

    return


def load_excel(file, index_col = 0):
    
    xls = pd.ExcelFile(file)
    lst = xls.sheet_names
    df_res_all = {}
    for s in lst:
        df_res_all[s] = pd.read_excel(xls, s, index_col = index_col) 
        
    return df_res_all

'''
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
import seaborn as sns
sns.set()

def plot_deiso_heatmap( dfs, file = 'plot.png', swap = False, figsize = (8,4), col_cluster = True, row_cluster = True ):
    
    if swap:
        sns_plot = sns.clustermap(dfs.transpose(), col_cluster = col_cluster, row_cluster = row_cluster, figsize = figsize)
    else:
        sns_plot = sns.clustermap(dfs, col_cluster = col_cluster, row_cluster = row_cluster, figsize = figsize)
      
    plt.tight_layout()
    sns_plot.savefig(file) 
    # plt.savefig(file)    
    # fig = sns_plot.figure()
    # fig.savefig(file)     # plt.show()
    print('Figure saved to %s.' % file)
    return
    
def plot_deiso_pca( dfs, groups, file = 'plot.png', figsize = (4,4), dpi = 100 ):
    
    df_2d = DEiso_pca( dfs, n_comp = 2 )
    df_pca = df_2d.transpose().copy(deep = True)
    df_pca['group'] = list(groups)

    plt.figure(figsize = figsize, dpi = dpi)
    sns.scatterplot(x = df_pca['PC1'], y = df_pca['PC2'], hue = df_pca['group'])
    mxv = np.abs(df_pca[['PC1', 'PC2']]).max().max()*1.1
    plt.xlim([-mxv, mxv])
    plt.ylim([-mxv, mxv])
    plt.grid()
    plt.legend(bbox_to_anchor = (1,0.5), loc = 'center left')
    plt.grid()
    plt.tight_layout()
    
    plt.savefig(file)    
    # fig = sns_plot.get_figure()
    # fig.savefig(file)     # plt.show()
    print('Figure saved to %s.' % file)
    # plt.show()        
    return
'''
    
##########################################################################
## Functions and objects to handle GTF file
##########################################################################

# GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, score, strand, frame, attr')
GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, score, strand, frame, attr, gid, gname, tid, tname, eid, biotype')
CHR, SRC, FEATURE, GSTART, GEND, SCORE, STRAND, FRAME, ATTR, GID, GNAME, TID, TNAME, EID, BIOTYPE = [i for i in range(15)]

def get_id_and_name_from_gtf_attr(str_attr):
    
    gid = ''
    gname = ''
    tid = ''
    tname = ''
    biotype = ''
    eid = ''
    
    items = str_attr.split(';')
    for item in items[:-1]:
        sub_item = item.strip().split()
        if sub_item[0] == 'gene_id':
            gid = sub_item[1].replace('"','')
        elif sub_item[0] == 'gene_name':
            gname = sub_item[1].replace('"','')
        elif sub_item[0] == 'transcript_id':
            tid = sub_item[1].replace('"','')
        elif sub_item[0] == 'transcript_name':
            tname = sub_item[1].replace('"','')
        elif sub_item[0] == 'exon_id':
            eid = sub_item[1].replace('"','')
        elif sub_item[0] == 'gene_biotype':
            biotype = sub_item[1].replace('"','')
        elif sub_item[0] == 'transcript_biotype':
            biotype = sub_item[1].replace('"','')
    
    return gid, gname, tid, tname, eid, biotype


def load_gtf( fname, verbose = True, ho = False ):
    
    gtf_line_lst = []
    hdr_lines = []
    if verbose: print('Loading GTF ... ', end='', flush = True)

    f = open(fname,'r')
    if ho:
        for line in f:
            
            if line[0] == '#':
                # line.replace('#','')
                cnt = 0
                for m, c in enumerate(list(line)):
                    if c != '#': break
                    else: cnt += 1
                hdr_lines.append(line[cnt:-1])
            else:
                break
    else:
        for line in f:
            
            if line[0] == '#':
                # line.replace('#','')
                cnt = 0
                for m, c in enumerate(list(line)):
                    if c != '#': break
                    else: cnt += 1
                hdr_lines.append(line[cnt:-1])
            else:
                items = line[:-1].split('\t')
                if len(items) >= 9:
                    chrm = items[0]
                    src = items[1]
                    feature = items[2]
                    start = int(items[3])
                    end = int(items[4])
                    score = items[5]
                    strand = items[6]
                    frame = items[7]
                    attr = items[8]
                    gid, gname, tid, tname, eid, biotype = get_id_and_name_from_gtf_attr(attr)
                    gl = GTF_line(chrm, src, feature, start, end, score, strand, frame, attr, gid, gname, tid, tname, eid, biotype)
                    gtf_line_lst.append(gl)
        
    f.close()
    if verbose: print('done %i lines. ' % len(gtf_line_lst))
    
    return(gtf_line_lst, hdr_lines)

        
def get_gene_mapping( gtf_file, target = 'exon', verbose = True):
    
    chr_lst1 = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 
                'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20',
                'chr21', 'chr22', 'chrX', 'chrY', 'chrM']

    chr_lst2 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
                '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                '21', '22', 'X', 'Y', 'M']
    
    ## Load GTF lines
    gtf_lines, hdr_lines = load_gtf(gtf_file, verbose = verbose)
    
    df = pd.DataFrame(gtf_lines)[['feature', 'gid', 'gname', 'tid', 'tname', 'eid', 'chr', 'start', 'end', 'strand']]
    # df['order'] = list(df.index.values)

    clst = list(df['chr'].unique())
    clst_c = list(set(clst).intersection(chr_lst1))
    if len(clst_c) > 10:
        chr_lst = chr_lst1
    else:
        chr_lst = chr_lst2

    b = df['chr'].isin(chr_lst)
    df = df.loc[b,:]
    
    df['chr_num'] = df['chr'].copy(deep = True)
    chr_num_lst = list(np.arange(len(chr_lst)))
    for c, cn in zip(chr_lst, chr_num_lst):
        b = df['chr'] == c
        df.loc[b, 'chr_num'] = cn
        
    if target in ['exon', 'exon_id']:
        tcol = 'eid'
        target_feature = 'exon'
    elif target in ['transcript', 'transcript_id']:
        tcol = 'tid'
        target_feature = 'transcript'
    elif target in ['transcript_name']:
        tcol = 'tname'
        target_feature = 'transcript'
    else:
        tcol = 'gid'
        target_feature = 'gene'

    b = df['feature'] == target_feature
    # df = df.loc[b, ['gname', tcol, 'chr', 'start', 'end', 'strand', 'order', 'chr_num']].sort_values(by = ['chr_num', 'start', 'end'])
    df = df.loc[b, ['gname', tcol, 'chr', 'start', 'end', 'strand', 'chr_num']].sort_values(by = ['chr_num', 'start', 'end'])

    df.set_index(tcol, inplace = True)
    df = df[~df.index.duplicated(keep='first')]
    gmap = df['gname']

    return gmap


def get_feature_mapping( gtf_file, target = 'exon', verbose = True):
    
    chr_lst1 = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 
                'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20',
                'chr21', 'chr22', 'chrX', 'chrY', 'chrM']

    chr_lst2 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
                '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                '21', '22', 'X', 'Y', 'M']
    
    ## Load GTF lines
    gtf_lines, hdr_lines = load_gtf(gtf_file, verbose = verbose)
    
    df = pd.DataFrame(gtf_lines)[['feature', 'gid', 'gname', 'tid', 'tname', 'eid', 'chr', 'start', 'end', 'strand']]
    # df['order'] = list(df.index.values)

    clst = list(df['chr'].unique())
    clst_c = list(set(clst).intersection(chr_lst1))
    if len(clst_c) > 10:
        chr_lst = chr_lst1
    else:
        chr_lst = chr_lst2

    b = df['chr'].isin(chr_lst)
    df = df.loc[b,:]
    
    df['chr_num'] = df['chr'].copy(deep = True)
    chr_num_lst = list(np.arange(len(chr_lst)))
    for c, cn in zip(chr_lst, chr_num_lst):
        b = df['chr'] == c
        df.loc[b, 'chr_num'] = cn
        
    if target in ['exon', 'exon_id']:
        tcol = 'eid'
        target_feature = 'exon'
    elif target in ['transcript', 'transcript_id']:
        tcol = 'tid'
        target_feature = 'transcript'
    elif target in ['transcript_name']:
        tcol = 'tname'
        target_feature = 'transcript'
    else:
        tcol = 'gid'
        target_feature = 'gene'
        

    b = df['feature'] == target_feature
    # df = df.loc[b, ['gname', tcol, 'chr', 'start', 'end', 'strand', 'order', 'chr_num']].sort_values(by = ['chr_num', 'start', 'end'])
    df = df.loc[b, ['gname', tcol, 'chr', 'start', 'end', 'strand', 'chr_num']].sort_values(by = ['chr_num', 'start', 'end'])

    df.set_index(tcol, inplace = True)
    df = df[~df.index.duplicated(keep='first')]
    gmap = df['gname']

    return gmap