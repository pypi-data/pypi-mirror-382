import numpy as np
import pandas as pd
import os, time
from subprocess import Popen, PIPE
import shlex

import matplotlib.pyplot as plt
import seaborn as sns


def run_command(cmd, prn = True):
    cnt = 0
    with Popen(shlex.split(cmd), stdout=PIPE, bufsize=1, \
               universal_newlines=prn ) as p:
        for line in p.stdout:
            if (line[:14] == 'Tool returned:'):                    
                cnt += 1
            elif cnt > 0:
                pass
            else: 
                if prn:
                    print(line, end='')
                    
        exit_code = p.poll()
    return exit_code


def get_file_name_of(file_name_ext):
    
    items = file_name_ext.split('.')
    file_name = items[0]
    for item in items[1:-1]:
        file_name = file_name + '.' + item
    ext = items[-1]
    
    return file_name


def get_file_name_and_ext_of(path_file_name_ext):

    file_name_ext = path_file_name_ext.split('/')[-1]
    items = file_name_ext.split('.')
    file_name = items[0]
    for item in items[1:-1]:
        file_name = file_name + '.' + item
    ext = items[-1]
    
    return file_name, ext


def get_path_filename_and_ext_of(path_file_name_ext):

    items = path_file_name_ext.split('/')
    if len(items) == 1:
        path = ''
    else:
        path = items[0]
        for itm in items[1:-1]:
            path = path + '/%s' % itm            
    file_name_ext = items[-1]
    
    items = file_name_ext.split('.')
    file_name = items[0]
    for item in items[1:-1]:
        file_name = file_name + '.%s' % item
    ext = items[-1]
    
    return path, file_name, ext
    

################################################
### Handling Genome FASTA, GTF, and sam file ###

# import os, time
import re, copy, collections, datetime, queue, math
import scipy.optimize as op
import sklearn.linear_model as lm

##############################
### Some usefule functions ###

def which( ai, value = True ) :
    wh = []
    a = list(ai)
    for k in range(len(a)): 
        if a[k] == value: 
            wh.append(k) 
    return(wh)


def get_col(nt_lst, n):
    
    lst = []
    for item in nt_lst: lst.append(item[n]) 
    return(lst)


def get_flag(values, bpos ):
    mask = np.repeat( 1 << bpos, len(values) )
    flag = (values & mask) > 0
    return(list(flag))


####################################
### Codes to load/save genome.fa ###

class Genome:
    def __init__(self, header, seq ):
        self.name = header.split()[0]
        self.header = header
        self.seq = seq
        self.len = len(seq)


def load_genome(file_genome, verbose = False ):

    genome = dict()
    f = open(file_genome, 'r')
    cnt = 0
    for line in f :
        if line[0] == '>':
            print('\rLoading Genome ', line[1:-1].split()[0], end='       ')
            if cnt > 0: 
                # genome.append( Genome(header, ''.join(seq_lst) ) )
                chr_name = header.split()[0]
                genome[chr_name] = Genome(header, ''.join(seq_lst) )
            cnt += 1
            header = line[1:-1]
            seq_lst = []
        else :
            seq_lst.append(line[:-1].upper())

    # genome.append( Genome(header, ''.join(seq_lst) ) )
    chr_name = header.split()[0]
    genome[chr_name] = Genome(header, ''.join(seq_lst) )
    if verbose == True : print('\rNum.Chr = ', cnt, ' loaded                             ')
    f.close()
    return(genome)


def save_genome( file_genome, genome_dict, verbose = False ):
    
    f = open(file_genome, 'wt+')
    print('Saving genome ', end='')
    # for g in genome_lst :
    Keys = genome_dict.keys()
    for key in Keys:
        g = genome_dict[key]
        s = '>%s\n' % g.header
        f.writelines(s)
        n = int(np.floor(g.len/50))
        for m in range(n):
            s = '%s\n' % g.seq[(m*50):((m+1)*50)]
            f.writelines(s)
        s = '%s\n' % g.seq[(n*50):]    
        f.writelines(s)
        print('.', end='')
        
    print(' done. %i chrs.' % len(Keys) )
    f.close()
    

###############################################
## Functions and objects to handle GTF file ###
###############################################

# GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, score, strand, frame, attr')
GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, score, strand, frame, attr, gid, gname, tid, tname, eid, biotype')
CHR, SRC, FEATURE, GSTART, GEND, SCORE, STRAND, FRAME, ATTR, GID, GNAME, TID, TNAME, EID, BIOTYPE = [i for i in range(15)]

def print_gtf(line):
    print('%s, %s, %i-%i, %s-%s ' % (line.chr, line.feature, line.start, line.end, line.gid, line.tid ) )

def print_gtf_lines(lines):
    for k, line in enumerate(lines):
        print('%i: %s, %s, %i-%i, %s-%s ' % (k, line.chr, line.feature, line.start, line.end, line.gid, line.tid ) )

def print_gtf_lines_to_str(lines):
    s_lst = []
    for k, line in enumerate(lines):
        s = '%i: %s, %s, %i-%i, %s-%s ' % (k, line.chr, line.feature, line.start, line.end, line.gid, line.tid )
        s_lst.append(s)
    return s

def get_gtf_lines_from_rgns( r_lst_m, r_lst_nd ):

    gtf_line_lst = []

    for n in range(len(r_lst_m)):
        
        rs_m = r_lst_m[n]
        rs_nd = r_lst_nd[n]

        if len(rs_m.rgns) > 0:
            
            chrm = rs_m.rgns[0].chr            
            span = rs_m.get_span()
            g_id = 'StringFix.%i' % n
            attr = 'gene_id "%s";' % (g_id)
            gtf_line = GTF_line( chrm, GTF_SOURCE, 'gene', span.start, span.end, '.', \
                                 '+', '.', attr, g_id, g_id, '', '', '' )
            gtf_line_lst.append(gtf_line)
            
            pos = np.zeros( len(rs_m.rgns) )
            for k in range(len(rs_m.rgns)): pos[k] = rs_m.rgns[k].start
            odr = pos.argsort()

            for k in range(len(rs_m.rgns)):
                m = odr[k]
                rgn = rs_m.rgns[m]
                t_id = 'StringFix.%i.%i' % (n,k)
                attr = 'gene_id "%s"; transcript_id "%s"; abn "%4.1f"; length "%i";' % \
                        (g_id, t_id, rgn.ave_cvg_depth(), rgn.get_len())
                gtf_line = GTF_line( chrm, GTF_SOURCE, 'exon', rgn.start, rgn.end, '.', '+', '.', \
                                     attr, g_id, g_id, t_id, t_id, '' )
                gtf_line_lst.append(gtf_line)

    return( gtf_line_lst)

'''
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

        
'''

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
    
    ## in case, overwrite gid, gname, tid
    for item in items[:-1]:
        sub_item = item.split()
        if sub_item[0] == 'ref_gene_id':
            gid = sub_item[1].replace('"','')
        elif sub_item[0] == 'ref_gene_name':
            gname = sub_item[1].replace('"','')
        elif sub_item[0] == 'reference_id':
            tid = sub_item[1].replace('"','')
    
    return gid, gname, tid, tname, eid, biotype


def get_other_attrs_from_gtf_attr(str_attr):
    
    exon_num = -1
    cov = -1
    abn = -1
    seq = None
    event = None
    status = None
    cfrac = -1
    
    items = str_attr.split(';')
    for item in items[:-1]:
        sub_item = item.split()
        if sub_item[0] == 'exon_number':
            exon_num = int(sub_item[1].replace('"',''))
        elif sub_item[0] == 'cvg':
            cov = np.float32(sub_item[1].replace('"',''))
        elif (sub_item[0] == 'abn') | (sub_item[0] == 'cov'):
            abn = np.float32(sub_item[1].replace('"',''))
        elif sub_item[0] == 'seq':
            seq = sub_item[1].replace('"','')
        elif sub_item[0] == 'event':
            event = sub_item[1].replace('"','')
        elif sub_item[0] == 'status':
            status = sub_item[1].replace('"','')
        elif sub_item[0] == 'cfrac':
            cfrac = np.float32(sub_item[1].replace('"',''))
    
    return exon_num, cov, abn, seq, event, status, cfrac


def get_gtmap_from_gtf( gtf_lines ):
    
    feature_lst = []
    gid_lst = []
    gname_lst = []
    tid_lst = []
    tname_lst = []
    btype_lst = []
    
    cnt = 0
    for line in gtf_lines:
        if (line.feature == 'gene') | (line.feature == 'transcript'):
        #if tid not in tid_lst:
            gid, gname, tid, tname, eid, btype = get_id_and_name_from_gtf_attr(line.attr)
            gid_lst.append(gid)
            gname_lst.append(gname)
            tid_lst.append(tid)
            tname_lst.append(tname)
            btype_lst.append(btype)
            feature_lst.append(line.feature)
            cnt += 1
            
    # df = pd.DataFrame(gid=gid_lst, gname=gname_lst, tid=tid_lst, tname=tname_lst)
    df = pd.DataFrame( list(zip(feature_lst, gid_lst, gname_lst, tid_lst, tname_lst, btype_lst)), 
                       columns=['feature', 'gid', 'gname', 'tid', 'tname', 'biotype'])
    print('done %i from %i lines. ' % (cnt, len(gtf_lines)))
    
    return(df)


def get_gtemap_from_gtf( gtf_lines ):
    
    feature_lst = []
    gid_lst = []
    gname_lst = []
    tid_lst = []
    eid_lst = []
    tname_lst = []
    btype_lst = []
    
    cnt = 0
    for line in gtf_lines:
        if (line.feature == 'gene') | (line.feature == 'transcript') | (line.feature == 'exon'):
        #if tid not in tid_lst:
            gid, gname, tid, tname, eid, btype = get_id_and_name_from_gtf_attr(line.attr)
            gid_lst.append(gid)
            gname_lst.append(gname)
            tid_lst.append(tid)
            tname_lst.append(tname)
            if (line.feature == 'exon'):
                if eid == '':
                    eid = '%s_%i_%i' % (line.chr, line.start, line.end)
                else:
                    eid_lst.append(eid)
            else: 
                eid_lst.append(eid)
            btype_lst.append(btype)
            feature_lst.append(line.feature)
            cnt += 1
            
    # df = pd.DataFrame(gid=gid_lst, gname=gname_lst, tid=tid_lst, tname=tname_lst)
    df = pd.DataFrame( list(zip(feature_lst, gid_lst, gname_lst, tid_lst, tname_lst, eid_lst, btype_lst)), 
                       columns=['feature', 'gid', 'gname', 'tid', 'tname', 'eid', 'biotype'])
    print('done %i from %i lines. ' % (cnt, len(gtf_lines)))
    
    return(df)


def get_GTmap_from_gtf( gtf_file ):
    
    gtf_lines, hdr_lines = load_gtf(gtf_file)
    df_gtmap = get_gtmap_from_gtf( gtf_lines ) 
    return df_gtmap
    

def get_GTEmap_from_gtf( gtf_file ):
    
    gtf_lines, hdr_lines = load_gtf(gtf_file)
    df_gtmap = get_gtemap_from_gtf( gtf_lines ) 
    return df_gtmap
    

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


def save_gtf( fname, gtf_line_lst, hdr = None ):
    
    gtf_lines_str = []
    if isinstance( gtf_line_lst, pd.DataFrame ):
        for i in range( gtf_line_lst.shape[0] ):
            gtf_line = gtf_line_lst.iloc[i]
            s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
                (gtf_line.chr,    gtf_line.src,     gtf_line.feature, gtf_line. start, gtf_line.end, \
                 gtf_line.score,  gtf_line.strand,  gtf_line.frame,   gtf_line.attr )
            gtf_lines_str.append(s)
    else:
        for gtf_line in gtf_line_lst:
            s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
                (gtf_line.chr,    gtf_line.src,     gtf_line.feature, gtf_line. start, gtf_line.end, \
                 gtf_line.score,  gtf_line.strand,  gtf_line.frame,   gtf_line.attr )
            gtf_lines_str.append(s)
    
    f = open(fname,'w+')

    if hdr is not None:
        for line in hdr:
            f.writelines('# ' + line + '\n')

    '''
    for gtf_line in gtf_line_lst:
        s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
            (gtf_line.chr,    gtf_line.src,     gtf_line.feature, gtf_line. start, gtf_line.end, \
             gtf_line.score,  gtf_line.strand,  gtf_line.frame,   gtf_line.attr ) 
        f.writelines(s)
    '''
    f.writelines(''.join(gtf_lines_str))
    f.close()


def save_gtf2( fname, gtf_line_lst = None, hdr = None, fo = None, close = False ):
    
    if fo is None:
        f = open(fname,'w+')
    else: 
        f = fo

    if hdr is not None:
        for line in hdr:
            f.writelines('# ' + line + '\n')

    if (gtf_line_lst is not None) :
        if (len(gtf_line_lst) > 0):
            gtf_lines_str = []
            for gtf_line in gtf_line_lst:
                s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
                    (gtf_line.chr,    gtf_line.src,     gtf_line.feature, gtf_line. start, gtf_line.end, \
                     gtf_line.score,  gtf_line.strand,  gtf_line.frame,   gtf_line.attr )
                gtf_lines_str.append(s)

            f.writelines(''.join(gtf_lines_str))

    if close:
        f.close()

    return f

   
def save_gff( fname, gtf_line_lst ):
    
    gtf_lines_str = []
    for gtf_line in gtf_line_lst:
        s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
            (gtf_line.chr,    gtf_line.src,     gtf_line.feature, gtf_line. start, gtf_line.end, \
             gtf_line.score,  gtf_line.strand,  gtf_line.frame,   gtf_line.attr )
        gtf_lines_str.append(s)
        
    f = open(fname,'w+')
    '''
    for gtf_line in gtf_line_lst:            
        s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
            (gtf_line.chr,    gtf_line.src,    gtf_line.feature, gtf_line. start, gtf_line.end, \
             gtf_line.score,  gtf_line.strand, gtf_line.frame,   gtf_line.attr)
        f.writelines(s)
    '''
    f.writelines(gtf_lines_str)
    f.close()


###############################################
## Functions and objects to handle GTF file ###
###############################################

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
        
    if target == 'exon':
        tcol = 'eid'
    else:
        tcol = 'tname'

    b = df['feature'] == target
    # df = df.loc[b, ['gname', tcol, 'chr', 'start', 'end', 'strand', 'order', 'chr_num']].sort_values(by = ['chr_num', 'start', 'end'])
    df = df.loc[b, ['gname', tcol, 'chr', 'start', 'end', 'strand', 'chr_num']].sort_values(by = ['chr_num', 'start', 'end'])

    df.set_index(tcol, inplace = True)
    df = df[~df.index.duplicated(keep='first')]
    gmap = df['gname']

    return gmap


###################################
### Codes to load/save SAM file ###

SAM_line = collections.namedtuple('SAM_Line', 'qname, flag, flag_str, rname, pos, mapq, cigar, \
                                   rnext, pnext, tlen, seq, qual, cN, cD, cI, cS, xs')

QNAME, FLAG, FLAG_STR, RNAME, POS, MAPQ, CIGAR, RNEXT, PNEXT, TLEN, SEQ, QUAL, CN, CD, CI, CS = [i for i in range(16)]

def load_sam_lst( fname, n_rd_max = None, verbose = False, sdiv = 10 ):
    
    # chr_lst = list()
    # pos_lst = list()
    # qname_lst = list()
    # rgns_lst = list()
    
    slns = list()
    bytesize = os.path.getsize(fname)
    lines = []
    
    if verbose == True:
        print('Reading ',fname, ' ',end='')
        start_time = time.time()

    cN = 0
    cD = 0
    cI = 0
    cS = 0
    rd_len = 0
    cnt = 0
    n_bases = 0
    cnt_byte = 0
    qual = ' '
    flag_str = ' '
    step = np.ceil(bytesize/sdiv)
    ms = step;
    f = open(fname, 'r')
    while True:
        lines = f.readlines(1000)
        if not lines: break
        for line in lines : # range(len(x)) :
            cnt_byte += len(line)
            if line[0] != '@':
                items = line[:-1].split()
                flag_str = format(int(items[1])+4096, 'b')[::-1]
                pri = flag_str[8]

                if (pri == '0') & (items[2] != '*') & (items[5] != '*'):
                    qname = items[0]
                    flag = int(items[1])
                    rname = items[2]
                    pos = int(items[3])
                    mapq = int(items[4])
                    cigar = items[5]
                    rnext = items[6]
                    pnext = int(items[7])
                    tlen = int(items[8])
                    seq = items[9].upper()

                    XS = 0
                    if len(items) > 11:
                        if items[11][5] == '+': XS = 1
                        elif items[11][5] == '-': XS = -1
                    qual = items[10]

                    #'''
                    cN = int(cigar.count('N'))
                    cD = int(cigar.count('D'))
                    cI = int(cigar.count('I'))
                    cS = int(cigar.count('S'))
                    #'''

                    sam_line = SAM_line( qname, flag, flag_str, rname, pos, mapq, cigar, rnext, pnext, \
                                        tlen, seq, qual, cN, cD, cI, cS, XS )
                    slns.append( sam_line )

                    # chr_lst.append(rname)
                    # pos_lst.append(pos)
                    # qname_lst.append(qname)
                    # r = get_rgns_from_sam_line( sam_line )
                    # rgns_lst.append(r)

                    cnt += 1
                    n_bases += len(seq)
                    rd_len = max(rd_len,len(seq))

                    if cnt == n_rd_max :
                        break
            else:
                # if verbose == True: print(line[:-1])
                pass

            if (verbose == True) & (cnt_byte > ms): 
                elapsed_time = time.time() - start_time
                print('.', end='')
                ms += step
            
        if cnt == n_rd_max :
            break
            
    f.close()
    if verbose == True: 
        # elapsed_time = time.time() - start_time
        if n_rd_max is None:
            print(' done. %i (%i) lines (bases), read length: %i' % (cnt, n_bases, rd_len))
        else:
            print(' done. read length: %i, %i' % (rd_len, cnt))
    
    return( slns, cnt, n_bases, rd_len )


def rename(sam_line_lst):
    Len = len(sam_line_lst)
    print('Len:', Len)
    for k in range(int(Len/2)):
        qname = sam_line_lst[k*2]
        sam_line_lst[k*2+1].qname = qname
        
    return(sam_line_lst)

'''
=============================================================================
SAM flag
=============================================================================
0   1     0x1    template having multiple segments in sequencing
1   2     0x2    each segment properly aligned according to the aligner

2   4     0x4    segment unmapped
3   8     0x8    next segment in the template unmapped
4   16    0x10   SEQ being reverse complemented
5   32    0x20   SEQ of the next segment in the template being reverse complemented
6   64    0x40   the first segment in the template
7   128   0x80   the last segment in the template

8   256   0x100  secondary alignment
9   512   0x200  not passing filters, such as platform/vendor quality controls
10  1024  0x400  PCR or optical duplicate
11  2048  0x800  supplementary alignment
=============================================================================
'''

#############################################
### Codes to check alignment (SAM entry) ####

def parse_cigar( cigar_str ):
    matches = re.findall(r'(\d+)([A-Z]{1})', cigar_str)
    return(matches)

def compare_seq( s1, s2 ):
    cnt = 0
    mcnt = 0
    for k in range(len(s1)):
        if (s1[k] != ' ') & (s2[k] != ' '): 
            cnt += 1
            mcnt += (s1[k] != s2[k])
    return((mcnt,cnt))

def get_error_seq( s1, s2 ):
    cnt = 0
    mcnt = 0
    es = []
    for k in range(len(s1)):
        if (s1[k] != ' ') & (s2[k] != ' '): 
            cnt += 1
            mcnt += (s1[k] != s2[k])
            if s1[k] != s2[k]: es.append('e')
            else: es.append('_')
        elif (s1[k] == ' ') & (s2[k] != ' '): es.append('d')
        elif (s1[k] != ' ') & (s2[k] == ' '): es.append('x')
        else:
            es.append('_')
    return(''.join(es))

def get_seq_from_genome_o2(genome, sam_line):
    
    type_cnt = dict(D=0,I=0,N=0,S=0)
    Len = len(sam_line.seq) -1
    cigar = parse_cigar(sam_line.cigar)
    rseq = ''
    rpos = 0
    qseq = ''
    qpos = sam_line.pos-1
    for clen, ctype in cigar:
        if (ctype == 'D') | (ctype == 'I') | (ctype == 'N') | (ctype == 'S') :
            type_cnt[ctype] += 1
        # print(ctype,clen)
        Len = int(clen)
        if ctype == 'M': 
            qseq = qseq + genome[sam_line.rname].seq[qpos:(qpos+Len)]
            qpos += Len
            rseq = rseq + sam_line.seq[rpos:(rpos+Len)]
            rpos += Len
        elif ctype == 'S': 
            tseq = ''
            for n in range(Len): tseq = tseq + ' '
            qseq = qseq + tseq
            rseq = rseq + sam_line.seq[rpos:(rpos+Len)]
            rpos += Len
        elif ctype == 'N': 
            qseq = qseq + ' ~~ '
            rseq = rseq + ' ~~ '
            qpos += Len
        elif ctype == 'I': 
            tseq = ''
            for n in range(Len): tseq = tseq + ' '
            qseq = qseq + tseq
            rseq = rseq + sam_line.seq[rpos:(rpos+Len)]
            rpos += Len
        elif ctype == 'D': 
            tseq = ''
            for n in range(Len): tseq = tseq + ' '
            rseq = rseq + tseq
            qseq = qseq + genome[sam_line.rname].seq[qpos:(qpos+Len)]
            qpos += Len
        elif ctype == 'H': # No action
            pass
        elif ctype == 'P': # No action
            pass
        elif ctype == '=': # No action
            pass
        elif ctype == 'X': # No action
            pass
        else: 
            return(False, rseq, qseq, type_cnt)
            # print('ERROR in get_seq_from_genome()')
    '''
    (m,n) = compare_seq( rseq, qseq )
    if m > 0:
        print('Mismatch: ', m, ' among ', n)
        print('RSEQ: ', rseq, ' Len: ', len(rseq))
        print('QSEQ: ', qseq, ' Len: ', len(qseq))
    '''
    return(True, rseq, qseq, type_cnt)


#######################
### Alignment tools ###

def get_bwa_read_group_line( rid, sm = None, pl = None, pi = 1 ):
    
    if sm is None: sm = 'NA'
    if pl is None: pl = 'NA'
    if pi is None: pi = 'NA'

    RGline = '"@RG\\tID:%s\\tSM:%s\\tPL:%s\\tPI:%i"' % (rid, sm, pl, pi)
    
    return RGline


def BWA_Align_n_bam_sort( fq_left, fq_right, genome_file, out_dir, \
                          filename = 'BWA_aligned.out', suffix = None, p = 4, \
                          Read_group_line = None, add_opt = None  ):

    cmd_lst = []
    if not (os.path.isfile(fq_left) & os.path.isfile(fq_right)):
        print('Invalid input files .. %s, %s' % (fq_left, fq_right))
        return None

    if not os.path.isfile(genome_file):
        print('Invalid Ref genome .. %s' % (genome_file))       
        return None
        
    if out_dir[-1] == '/':
        out_dir = out_dir[:-1]
        
    out_file_name = '%s/%s' % (out_dir, filename)
    
    if suffix is not None:
        out_file_name = out_file_name + suffix
    
    ## Align reads to generate SAM
    start = time.time()
    print('run BWA .. ', end = '')
    
    cmd = 'bwa mem -t %i -T 0 ' % p
    cmd = cmd + '-R %s ' % Read_group_line
    cmd = cmd + '%s ' % genome_file
    cmd = cmd + '%s %s ' % (fq_left, fq_right)    
    cmd = cmd + '-o %s ' % ('%s.sam' % out_file_name)

    if (add_opt is not None) & isinstance(add_opt, str): 
        cmd = cmd + add_opt

    exit_code = run_command(cmd)
    cmd_lst.append(cmd)
    
    elapsed = time.time() - start
    if exit_code is not None:
        print('done. ExitCode: %i (%i)' % (exit_code, elapsed))
    else:
        print('done. (%i)' % elapsed)
    
    start = time.time()
    print('Converting to BAM and sort .. ', end= '')
    ## Convert SAM to BAM
    cmd = 'samtools view -bhS %s.sam -o %s_tmp.bam' % (out_file_name, out_file_name)
    run_command(cmd)
    cmd_lst.append(cmd)
    
    ## Sort BAM
    cmd = 'samtools sort -o %s.bam %s_tmp.bam' % (out_file_name, out_file_name)
    run_command(cmd)
    cmd_lst.append(cmd)
    
    ## Generate BAM index (bai)
    cmd = 'samtools index %s.bam' % (out_file_name)
    run_command(cmd)
    cmd_lst.append(cmd)
    
    run_command('rm %s_tmp.bam' % out_file_name)
    # cmd_lst.append(cmd)
    run_command('rm %s.sam' % out_file_name)
    # cmd_lst.append(cmd)
    
    elapsed = time.time() - start
    print('done. (%i)' % elapsed)
    
    return '%s.bam' % out_file_name, cmd_lst
      
    
def STAR_build_index( genome_file, gtf_file = None, out_dir = None, add_opt = '' ):

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    cmd = 'STAR --runThreadN 8 '
    cmd = cmd + '--runMode genomeGenerate '
    cmd = cmd + '--genomeDir %s ' % out_dir
    cmd = cmd + '--genomeFastaFiles %s ' % (genome_file)
    if gtf_file is not None:
        cmd = cmd + '--sjdbGTFfile %s ' % (gtf_file)
        cmd = cmd + '--sjdbOverhang 100 '
        
    if (add_opt is not None) & isinstance(add_opt, str): 
        cmd = cmd + add_opt

    run_command(cmd)  
    return cmd


def STAR_Align_n_bam_sort( fq_left, fq_right, path_to_idx, out_dir, \
                           filename = None, suffix = None, p = 4, \
                           zipped = True, add_opt = '' ):

    cmd_lst = []
    if not (os.path.isfile(fq_left) & os.path.isfile(fq_right)):
        print('Invalid input files .. %s, %s' % (fq_left, fq_right))
        return None, cmd_lst
    
    if not os.path.isdir(path_to_idx):
        print('Invalid path to Ref genome .. %s' % (path_to_idx))       
        return None, cmd_lst
        
    if out_dir[-1] != '/':
        out_dir = out_dir + '/'
        
    if filename is None:
        filename = out_dir[:-1]
    
    tmp_dir = 'STAR_tmp'
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)
    
    cmd = 'STAR --runThreadN %i ' % p
    cmd = cmd + '--genomeDir %s ' % path_to_idx
    if fq_right is None:
        cmd = cmd + '--readFilesIn %s ' % (fq_left)
    else:
        cmd = cmd + '--readFilesIn %s %s ' % (fq_left, fq_right)
    
    if zipped:
        cmd = cmd + '--readFilesCommand zcat '
        
    if tmp_dir[-1] != '/':
        tmp_dir = tmp_dir + '/'
    cmd = cmd + '--outFileNamePrefix %s ' % (tmp_dir)
    cmd = cmd + '--outSAMattributes XS NH '
    cmd = cmd + '--outSAMstrandField intronMotif '
    cmd = cmd + '--outSAMtype BAM SortedByCoordinate '
    if (add_opt is not None) & isinstance(add_opt, str): 
        cmd = cmd + add_opt

    exit_code = run_command(cmd)
    cmd_lst.append(cmd)
    
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    bam = tmp_dir + 'Aligned.sortedByCoord.out.bam'
    if suffix is None:
        sorted_bam = out_dir + '%s.bam' % (filename)
    else:
        sorted_bam = out_dir + '%s%s.bam' % (filename, suffix)
        
    cmd = 'cp %s %s' % (bam, sorted_bam)
    exit_code = run_command(cmd)
    # cmd_lst.append(cmd)
    run_command('rm %s' % bam)    
    # cmd_lst.append(cmd)
    
    return sorted_bam, cmd_lst


#############################
### GATK wrapper function ###
#############################

def GATK_MarkDuplicates_and_SortSam(bam_file_in, out_dir, \
                                    prn = False, rrn = False, clean = True):
    
    cmd_lst = []
    exit_code = 0
    
    # bam_file_name = get_file_name_of(bam_file_in)
    path, fname, fext = get_path_filename_and_ext_of(bam_file_in)
    if out_dir[-1] != '/': out_dir = out_dir + '/'
    bam_file_name = out_dir + fname

    ## Create index files if not exist
    if rrn | (not os.path.isfile(bam_file_in + '.bai')):
        print('Indexing .. ', end = '')
        cmd = 'samtools index -b %s %s.bai' % (bam_file_in, bam_file_in)
        exit_code = run_command(cmd, prn)
        cmd_lst.append(cmd)

    if not os.path.isfile(bam_file_in + '.bai'):
        print('ERROR in Creating bai. %i' % exit_code)
        exit_code = 1
        return exit_code, bam_file_in, cmd_lst
    else:
        exit_code = 0
        
    ext = '.MarkDup'
    ## Mark Duplicates
    bam_file_md = '%s%s.bam' % (bam_file_name, ext)
    if rrn | (not os.path.isfile(bam_file_md)):
        print('MarkDup .. ', end = '')
        cmd = 'gatk MarkDuplicates '
        cmd = cmd + '-I %s ' % (bam_file_in)
        cmd = cmd + '-O %s ' % (bam_file_md)
        cmd = cmd + '-M %s ' % ('%s%s.txt' % (bam_file_name, ext))        
        exit_code = run_command(cmd, prn)    
        cmd_lst.append(cmd)

    if not os.path.isfile(bam_file_md):
        print('ERROR in MarkDuplicates. %i' % exit_code)
        exit_code = 2
        return exit_code, bam_file_in, cmd_lst
    else:
        exit_code = 0
    
    ext = ext + '.SortSam'
    bam_file_md_ss = '%s%s.bam' % (bam_file_name, ext)
    if rrn | (not os.path.isfile(bam_file_md_ss)):
        print('SortSam .. ', end = '')
        cmd = 'gatk SortSam '
        cmd = cmd + '-I %s ' % (bam_file_md)
        cmd = cmd + '-O %s ' % (bam_file_md_ss)
        cmd = cmd + '-SORT_ORDER coordinate '       
        exit_code = run_command(cmd, prn)    
        cmd_lst.append(cmd)

    if not os.path.isfile(bam_file_md_ss):
        print('ERROR in SortSam. %i' % exit_code)
        exit_code = 3
        return exit_code, bam_file_md, cmd_lst
    else:
        exit_code = 0
 
    ## delete .MarkDup.bam, .MarkDup.txt
    if clean:
        if os.path.isfile(bam_file_md):
            run_command( 'rm %s' % bam_file_md )
            # cmd_lst.append(cmd)
            
        bam_file_name = get_file_name_of(bam_file_md)
        markdup_txt = '%s.txt' % (bam_file_name)
        if os.path.isfile(markdup_txt):
            run_command( 'rm %s' % markdup_txt )
            # cmd_lst.append(cmd)
            
    return 0, bam_file_md_ss, cmd_lst

    
def GATK_SplitNCigarReads(bam_file_in, ref_genome, prn = False, rrn = False):
    
    exit_code = 0
    bam_file_name = get_file_name_of(bam_file_in)
    cmd_lst = []

    ext = '.SplitN'
    bam_file_md_ss_sn = '%s%s.bam' % (bam_file_name, ext)
    if rrn | (not os.path.isfile(bam_file_md_ss_sn)):    
        print('SplitN .. ', end = '')
        cmd = 'gatk SplitNCigarReads '
        cmd = cmd + '-I %s ' % (bam_file_in)
        cmd = cmd + '-R %s ' % (ref_genome)
        cmd = cmd + '-O %s ' % (bam_file_md_ss_sn)
        exit_code = run_command(cmd, prn)  
        cmd_lst.append(cmd)

    if not os.path.isfile(bam_file_md_ss_sn):
        print('ERROR in SplitNCigarReads. %i' % exit_code)
        exit_code = 4
        return exit_code, bam_file_in, cmd_lst
    else:
        exit_code = 0
        return exit_code, bam_file_md_ss_sn, cmd_lst

    
def GATK_BaseRecal_BQSR_GetPileupSum(bam_file_in, ref_genome, \
                                     lst_vcf_gzs_BR, lst_vcf_gzs_PS, \
                                     mode = 'D', prn = False, \
                                     rrn = False, clean = True):
    
    exit_code = 0
    bam_file_name = get_file_name_of(bam_file_in)
    cmd_lst = []

    recal_tbl = '%s.recal_table' % bam_file_name
    if rrn | (not os.path.isfile(recal_tbl)):
        print('BaseRecal .. ', end = '')
        cmd = 'gatk BaseRecalibrator '
        cmd = cmd + '-I %s ' % (bam_file_in)
        cmd = cmd + '-R %s ' % (ref_genome)   
        if len(lst_vcf_gzs_BR) > 0:
            for vcf in lst_vcf_gzs_BR:
                cmd = cmd + '--known-sites %s ' % (vcf)
        cmd = cmd + '-O %s ' % (recal_tbl)
        exit_code = run_command(cmd, prn)  
        cmd_lst.append(cmd)

    '''
    if not os.path.isfile(recal_tbl):
        print('ERROR in BaseRecalibration. %i' % exit_code)
        exit_code = 5
        return exit_code, bam_file_in, ''
    else:
        exit_code = 0
    #'''
        
    ext = '.bqsr'
    bam_file_md_ss_bqsr = '%s%s.bam' % (bam_file_name, ext)
    if rrn | (not os.path.isfile(bam_file_md_ss_bqsr)):
        print('BQSR .. ', end = '')
        cmd = 'gatk ApplyBQSR '
        cmd = cmd + '-I %s ' % (bam_file_in)
        cmd = cmd + '-R %s ' % (ref_genome)
        if os.path.isfile(recal_tbl):
            cmd = cmd + '--bqsr-recal-file %s ' % (recal_tbl)
        cmd = cmd + '-O %s ' % (bam_file_md_ss_bqsr)
        exit_code = run_command(cmd, prn)    
        cmd_lst.append(cmd)
        
    if not os.path.isfile(bam_file_md_ss_bqsr):
        print('ERROR in ApplyBQSR. %i' % exit_code)
        exit_code = 6
        return exit_code, bam_file_in, '', cmd_lst
    else:
        exit_code = 0
        
    if clean:
        if os.path.isfile(recal_tbl):
            run_command('rm %s' % recal_tbl)
            # cmd_lst.append(cmd)
        
    pileupsum_tbl = '%s%s.getpileupsummaries.table' % (bam_file_name, ext)
    if rrn | (not os.path.isfile(pileupsum_tbl)):
        print('PileupSum .. ', end = '')
        cmd = 'gatk GetPileupSummaries '
        cmd = cmd + '-I %s ' % (bam_file_md_ss_bqsr)
        if len(lst_vcf_gzs_PS) > 1:
            cmd = cmd + '-V %s ' % (lst_vcf_gzs_PS[0])
            cmd = cmd + '-L %s ' % (lst_vcf_gzs_PS[1])
        cmd = cmd + '-O %s ' % (pileupsum_tbl)
        exit_code = run_command(cmd, prn)  
        cmd_lst.append(cmd)

    if not os.path.isfile(pileupsum_tbl): # exit_code != 0:
        print('ERROR in GetPileupSummaries. %i' % exit_code)
        exit_code = 7
        return exit_code, bam_file_md_ss_bqsr, '', cmd_lst
    else:
        exit_code = 0
        print('done.')
        
    return exit_code, bam_file_md_ss_bqsr, pileupsum_tbl, cmd_lst
    
    
def GATK_co_cleaning( bam_file, ref_genome, lst_vcf_gzs_br, \
                      lst_vcf_gzs_ps, out_dir, mode = 'D', \
                      prn = False, rrn = False, clean = True ):
    
    ext = ''
    cmd_lst = []
    start = time.time()
    bam_file_name = get_file_name_of(bam_file)
    # path, fname, fext = get_path_filename_and_ext_of(bam_file)
    
    
    exit_code, bam_file_md_ss, cmd_lst_tmp = \
        GATK_MarkDuplicates_and_SortSam(bam_file, out_dir, prn, rrn, clean = clean )
    cmd_lst = cmd_lst + cmd_lst_tmp
    
    if exit_code > 0:
        return exit_code, '', '', cmd_lst
    else:
        exit_code = 0
    
    if (mode == 'R') | (mode == 'RNA'):
        exit_code, bam_file_md_ss_sn, cmd_lst_tmp = GATK_SplitNCigarReads(bam_file_md_ss, \
                                               ref_genome, prn, rrn )
        cmd_lst = cmd_lst + cmd_lst_tmp
        if exit_code > 0:
            return exit_code, '', '', cmd_lst
        else:
            exit_code = 0
        
        ## delete .SortSam.bam
        if clean:
            if os.path.isfile( bam_file_md_ss):
                run_command( 'rm %s' % bam_file_md_ss )
            
    else:
        bam_file_md_ss_sn = bam_file_md_ss

        
    exit_code, bam_file_md_ss_bqsr, pileupsum_tbl, cmd_lst_tmp = \
        GATK_BaseRecal_BQSR_GetPileupSum(bam_file_md_ss_sn, \
                                    ref_genome, lst_vcf_gzs_br, \
                                    lst_vcf_gzs_ps, mode = mode, \
                                    prn = prn, rrn = rrn, clean = clean )
    cmd_lst = cmd_lst + cmd_lst_tmp

    if exit_code > 0:
        return exit_code, '', '', cmd_lst
        
    if clean:
        ## delete .SortSam.bam/bai or .SplitN.bam/bai 
        if os.path.isfile(bam_file_md_ss_sn):
            run_command( 'rm %s' % bam_file_md_ss_sn )
            # cmd_lst.append(cmd)
        file_name = get_file_name_of(bam_file_md_ss_sn)
        if os.path.isfile(file_name + '.bai'):
            run_command( 'rm %s' % (file_name + '.bai') )
            # cmd_lst.append(cmd)

    elapsed = time.time() - start
    print('%s_co_cleaning done. (%5.2f)' % (bam_file, round(elapsed,2)))
        
    return exit_code, bam_file_md_ss_bqsr, pileupsum_tbl, cmd_lst
        
    
def GATK_VarCalling_Mutect( bam_lst, pileupsum_lst, RGID_lst, normal_idx, \
                          genome_file, out_vcf, \
                          germline_res, funcotator_src, \
                          pon_vcf_gz = None, out_format = 'MAF', \
                          prn = False, rrn = False, clean = True ):

    cmd_lst = []
    exit_code = 0
    start = time.time()
    ## Run Mutect2
    tumor_somatic_vcf = out_vcf
    
    if rrn | (not os.path.isfile(tumor_somatic_vcf)):
        print('Mutect2 .. ', end = '')
        cmd = 'gatk Mutect2 -R %s ' % genome_file
        
        for bam_file in bam_lst:
            cmd = cmd + '-I %s ' % (bam_file)
                
        cmd = cmd + '-normal %s ' % RGID_lst[normal_idx] 
        cmd = cmd + '-tumor %s ' % RGID_lst[1-normal_idx] 
        cmd = cmd + '--germline-resource %s ' % germline_res 
        if pon_vcf_gz is not None:
            cmd = cmd + '--panel-of-normals %s ' % pon_vcf_gz 
        cmd = cmd + '-O %s' % (tumor_somatic_vcf)

        exit_code = run_command(cmd, prn) 
        cmd_lst.append(cmd)
        
        if not os.path.isfile(tumor_somatic_vcf):
            print('ERROR in Mutect2. %i' % exit_code)
            exit_code = 8
            return exit_code, '', cmd_lst
        else:
            exit_code = 0

        
    out_file_name = get_file_name_of(tumor_somatic_vcf)
    # print('tumor_somatic_vcf: ', tumor_somatic_vcf)
    # path_tmp, out_file_name, fext = get_path_filename_and_ext_of(tumor_somatic_vcf)
    
    ## FilterCalls
    contam_table = '%s.ContamTable' % (out_file_name)
    if rrn | (not os.path.isfile(contam_table)):
        print('CalcContamTable .. ', end = '')
        cmd = 'gatk CalculateContamination '
        cmd = cmd + '-I %s ' % (pileupsum_lst[1-normal_idx])
        cmd = cmd + '--matched-normal %s ' % (pileupsum_lst[normal_idx])
        cmd = cmd + '-O %s' % (contam_table)
    
        exit_code = run_command(cmd, prn)            
        cmd_lst.append(cmd)
        
        if not os.path.isfile(contam_table):
            print('ERROR in CalculateContamination. %i' % exit_code)
            exit_code = 9
            return exit_code, '', cmd_lst
        else:
            exit_code = 0
    
    #'''
    ## FilterCalls
    tumor_filtered_vcf = '%s_filtered.vcf' % (out_file_name)
    if rrn | (not os.path.isfile(tumor_filtered_vcf)):
        print('FilterMutectCall .. ', end = '')
        cmd = 'gatk FilterMutectCalls -R %s ' % genome_file
        cmd = cmd + '-V %s ' % (tumor_somatic_vcf)
        cmd = cmd + '--contamination-table %s ' % (contam_table)
        cmd = cmd + '-O %s' % (tumor_filtered_vcf)

        exit_code = run_command(cmd, prn)    
        cmd_lst.append(cmd)
        
        if not os.path.isfile(tumor_filtered_vcf):
            print('ERROR in FilterMutectCalls. %i' % exit_code)
            exit_code = 10
            return exit_code, '', cmd_lst
        else:
            exit_code = 0
    
    ## Annotate using Funcotator
    variant_maf = '%s_variant_funcotated.maf' % (out_file_name)
    if True: # rrn | (not os.path.isfile(variant_maf)):
        print('Funcotation .. ', end = '')
        cmd = 'gatk Funcotator --reference %s ' % genome_file
        cmd = cmd + '--variant %s ' % (tumor_filtered_vcf)
        cmd = cmd + '--ref-version %s ' % ('hg38')
        cmd = cmd + '--data-sources-path %s ' % (funcotator_src)
        cmd = cmd + '--output %s ' % (variant_maf)
        cmd = cmd + '--output-file-format %s' % (out_format)

        exit_code = run_command(cmd, prn)    
        cmd_lst.append(cmd)
        
        if not os.path.isfile(variant_maf):
            print('ERROR in Funcotation. %i' % exit_code)
            exit_code = 11
            return exit_code, '', cmd_lst
        else:
            elapsed = time.time() - start
            print('done. (%5.2f)' % elapsed)
            print('Maf saved to %s' % variant_maf )
            exit_code = 0
            
    else:
        print('done.')
        
            
    if clean:
        if os.path.isfile(tumor_somatic_vcf):
            run_command( 'rm %s' % tumor_somatic_vcf )
        if os.path.isfile(tumor_somatic_vcf + '.idx'):
            run_command( 'rm %s.idx' % tumor_somatic_vcf )
        if os.path.isfile(tumor_somatic_vcf + '.stats'):
            run_command( 'rm %s.stats' % tumor_somatic_vcf )
            
        # if os.path.isfile(tumor_filtered_vcf):
        #     run_command( 'rm %s' % tumor_filtered_vcf )
        if os.path.isfile(tumor_filtered_vcf + '.idx'):
            run_command( 'rm %s.idx' % tumor_filtered_vcf )
        if os.path.isfile(tumor_filtered_vcf + '.filteringStats.tsv'):
            run_command( 'rm %s.filteringStats.tsv' % tumor_filtered_vcf )
            
        if os.path.isfile(contam_table):
            run_command( 'rm %s' % contam_table )            

    return exit_code, variant_maf, cmd_lst


def GATK_VarCall_pair(bam_file_pair, RG_ID_lst, genome_file, \
                      out_dir, file_prefix, lst_vcf_br, lst_vcf_ps, \
                      vcf_vc, funcotator_src, pon_vcf_gz = None, \
                      Mode = 'DNA', rrn = False, clean = True):
    
    cmd_lst = []
    start = time.time()
    print('VariantCall (Pair) for ', bam_file_pair )

    bam_file_out = []
    pileup_table = []

    normal_idx = 0
    if (RG_ID_lst[0].lower() == 'tumor') or (RG_ID_lst[0].lower()[0] == 't'): normal_idx = 1
        
    path1, fname1, fext1 = get_path_filename_and_ext_of(bam_file_pair[normal_idx])
    path2, fname2, fext2 = get_path_filename_and_ext_of(bam_file_pair[1-normal_idx])
    
    if out_dir is None:
        out_dir = '%s_vs_%s' % (fname2, fname1)
        
    if file_prefix is None:
        file_prefix = '%s_vs_%s' % (fname2, fname1)
        
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    exit_code, file_out, pileupsum_tbl, cmd_lst_tmp = \
        GATK_co_cleaning( bam_file_pair[0], genome_file, \
                          lst_vcf_br, lst_vcf_ps, out_dir, \
                          mode = Mode, rrn = rrn, clean = clean )  
    cmd_lst = cmd_lst + cmd_lst_tmp
    
    bam_file_out.append(file_out)
    pileup_table.append(pileupsum_tbl)

    if exit_code > 0:
        print('ERROR in GATK_co_cleaning.')
        return None, cmd_lst

    else:
        exit_code, file_out, pileupsum_tbl, cmd_lst_tmp = \
            GATK_co_cleaning( bam_file_pair[1], genome_file, \
                              lst_vcf_br, lst_vcf_ps, out_dir, \
                              mode = Mode, rrn = rrn, clean = clean )    
        cmd_lst = cmd_lst + cmd_lst_tmp
        
        bam_file_out.append(file_out)
        pileup_table.append(pileupsum_tbl)

        if exit_code > 0:
            print('ERROR in GATK_co_cleaning.')
            return None, cmd_lst

    if exit_code == 0:

        tumor_somatic_vcf = '%s/%s_somatic.vcf' % \
                            (out_dir, file_prefix )

        normal_idx = 0
        if (RG_ID_lst[0].lower() == 'tumor') or (RG_ID_lst[0].lower()[0] == 't'): normal_idx = 1
            
        exit_code, tumor_variant_maf, cmd_lst_tmp = \
            GATK_VarCalling_Mutect( bam_file_out, pileup_table, RG_ID_lst, normal_idx, \
                              genome_file, tumor_somatic_vcf, \
                              vcf_vc, funcotator_src, \
                              pon_vcf_gz = pon_vcf_gz, out_format = 'MAF', \
                              rrn = rrn, clean = clean )   
        cmd_lst = cmd_lst + cmd_lst_tmp

        if exit_code == 0:
            tsv_file = maf_to_tsv( tumor_variant_maf )
            elapsed = time.time() - start
            print('VariantCall (Pair) for ', bam_file_pair, ' done. (%5.2f)' % elapsed)
            print('Results saved to %s' % tsv_file)
            
        if clean:
            for m in range(2):
                if os.path.isfile(bam_file_out[m]):
                    run_command('rm %s' % bam_file_out[m])
                file_name = get_file_name_of(bam_file_out[m])
                if os.path.isfile(file_name + '.bai'):
                    run_command('rm %s.bai' % file_name)                
                if os.path.isfile(pileup_table[m]):
                    run_command('rm %s' % pileup_table[m])

        return tsv_file, cmd_lst
        
    return None, cmd_lst
        
        
def GATK_VarCalling_HaplotypeCaller( bam_file, genome_file, \
                            funcotator_src, out_file_name, \
                            pon_vcf_gz = None, out_format = 'MAF', \
                            prn = False, rrn = False, clean = True ):

    cmd_lst = []
    start = time.time()
    exit_code = 0
    
    haplotype_vcf = out_file_name + '_somatic.vcf'
    if rrn | (not(os.path.isfile(haplotype_vcf))):
        
        print('HaplotypeCalling .. ', end = '')
        
        cmd = 'gatk HaplotypeCaller '
        cmd = cmd + '-R %s ' % genome_file
        cmd = cmd + '-I %s ' % (bam_file)
        cmd = cmd + '-O %s' % (haplotype_vcf)
        # cmd = cmd + '-ERC GVCF '
        # cmd = cmd + '-G Standard '

        exit_code = run_command(cmd)
        cmd_lst.append(cmd)
        
        if not os.path.isfile(haplotype_vcf):
            print('ERROR in HaplotypeCalling. %i' % exit_code)
            exit_code = 8
            return exit_code, '', cmd_lst        
        else:
            exit_code = 0
    
    haplotype_filtered_vcf = haplotype_vcf
    
    '''
    haplotype_filtered_vcf = '%s%s/%s_%s_somatic_filtered.vcf' % \
                             (src_dir, target, target, Mode)
    if (rrn | (not(os.path.isfile(haplotype_filtered_vcf)))) & \
       (len(filter_lst) > 0) & (len(filter_lst) == len(filter_exp_lst)):
        
        start = time.time()
        print('HaplotypeCalling from %s ' % bam_file_out)
        
        print('VariantFiltration ')
        
        cmd = 'gatk VariantFiltration '
        cmd = cmd + '-R reference.fasta '
        cmd = cmd + '-V input.vcf.gz '
        cmd = cmd + '-O output.vcf.gz '
        for filter, filter_expression in list(zip(filter_lst, filter_exp_lst)):
            cmd = cmd + '--filter-name filter '
            cmd = cmd + '--filter-expression filter_expression '
            
        run_command(cmd)
    '''
        
    ## Annotate using Funcotator
    out_file_name = get_file_name_of(haplotype_filtered_vcf)
    # path_tmp, out_file_name, fext = get_path_filename_and_ext_of(haplotype_filtered_vcf)
    
    haplotype_maf = out_file_name + '_variant_funcotated.maf'
    
    if True: # rrn | (not os.path.isfile(haplotype_maf)):
        
        print('Funcotation .. ', end = '')
        cmd = 'gatk Funcotator --reference %s ' % genome_file
        cmd = cmd + '--variant %s ' % (haplotype_vcf)
        cmd = cmd + '--ref-version %s ' % ('hg38')
        cmd = cmd + '--data-sources-path %s ' % (funcotator_src)
        cmd = cmd + '--output %s ' % (haplotype_maf)
        cmd = cmd + '--output-file-format %s' % (out_format)

        exit_code = run_command(cmd, prn)
        cmd_lst.append(cmd)
        
        if not os.path.isfile(haplotype_maf):
            print('ERROR in Funcotation. %i' % exit_code)
            exit_code = 10
            return exit_code, '', cmd_lst
        else:
            elapsed = time.time() - start
            print('done. (%5.2f)' % (elapsed))
            print('Maf saved to %s' % (haplotype_maf) )  
            exit_code = 0
            
    else:
        print('done.')
                        
    if clean:
        # if os.path.isfile(haplotype_vcf):
        #     run_command( 'rm %s' % haplotype_vcf )
        if os.path.isfile(haplotype_vcf + '.idx'):
            run_command( 'rm %s.idx' % haplotype_vcf )
        if os.path.isfile(haplotype_vcf + '.stats'):
            run_command( 'rm %s.stats' % haplotype_vcf )

    return exit_code, haplotype_maf, cmd_lst
    
    
def GATK_VarCall_single(bam_file, genome_file, \
                        out_dir, file_prefix, lst_vcf_br, lst_vcf_ps, \
                        vcf_vc, funcotator_src, pon_vcf_gz = None, \
                        rrn = False, clean = True) :  
    
    cmd_lst = []
    start = time.time()
    Mode = 'RNA'    
    print('VariantCall (Single) for ', bam_file )    

    path, fname, fext = get_path_filename_and_ext_of(bam_file)
    if out_dir is None:
        out_dir = path
        
    if file_prefix is None:
        file_prefix = fname

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    exit_code, bam_file_out, pileupsum_tbl, cmd_lst_tmp = \
        GATK_co_cleaning( bam_file, genome_file, \
                          lst_vcf_br, lst_vcf_ps, out_dir, \
                          mode = Mode, rrn = rrn, clean = clean ) 
    cmd_lst = cmd_lst + cmd_lst_tmp

    if exit_code == 0:

        out_file_name = '%s/%s' % (out_dir, file_prefix )

        exit_code, file_out, cmd_lst_tmp = GATK_VarCalling_HaplotypeCaller( bam_file_out, \
                                genome_file, funcotator_src, out_file_name, \
                                pon_vcf_gz = pon_vcf_gz, out_format = 'MAF', \
                                rrn = rrn, clean = clean )
        cmd_lst = cmd_lst + cmd_lst_tmp

        if exit_code == 0:
            tsv_file = maf_to_tsv( file_out )
            elapsed = time.time() - start
            print('VariantCall (Single) for ', bam_file, ' done. (%5.2f)' % elapsed)
            print('Results saved to %s' % tsv_file)

            if clean:
                if os.path.isfile(bam_file_out):
                    run_command('rm %s' % bam_file_out)
                    
                file_name = get_file_name_of(bam_file_out)                
                if os.path.isfile(file_name + '.bai'):
                    run_command('rm %s.bai' % file_name)
                
                if os.path.isfile(pileupsum_tbl):
                    run_command('rm %s' % pileupsum_tbl)

            return tsv_file, cmd_lst

    return None, cmd_lst


col_sel = ['Hugo_Symbol', 'Entrez_Gene_Id', 'Center', 'NCBI_Build',
       'Chromosome', 'Start_Position', 'End_Position', 'Strand',
       'Variant_Classification', 'Variant_Type', 'Reference_Allele',
       'Tumor_Seq_Allele1', 'Tumor_Seq_Allele2', 'dbSNP_RS',
       'dbSNP_Val_Status', 
       'Genome_Change', 'Annotation_Transcript', 'Transcript_Strand',
       'Transcript_Exon', 'Transcript_Position', 'cDNA_Change',
       'Codon_Change', 'Protein_Change', 'Other_Transcripts',
       'ref_context', 'gc_content',
       'tumor_f', 't_alt_count',
       't_ref_count', 'n_alt_count', 'n_ref_count',
       'Gencode_34_secondaryVariantClassification',
       'AC', 'AF', 'AN', 'BaseQRankSum',
       'DP', 'ExcessHet', 'FS', 'InbreedingCoeff', 'MLEAC', 'MLEAF', 'MQ',
       'MQRankSum', 'QD', 'ReadPosRankSum', 'SOR']    
    
def maf_to_tsv(maf_file):

    line_lst = []
    with open(maf_file, 'r') as f:
        for line in f:
            if line[0] != '#':
                line_lst.append(line)

    fout = maf_file + '.tsv'
    fo = open(fout, 'w')
    fo.writelines(line_lst)
    fo.close()
    
    df = pd.read_csv(fout, sep='\t')
    
    # col_selected = set(col_sel).intersection(list(df.columns.values))
    # df_sel = df.loc[:, col_selected]
    df_sel = pd.DataFrame(index = df.index.values)
    clst = list(df.columns.values)
    for c in col_sel:
        if c in clst:
            df_sel[c] = df[c]
    
    df_sel.to_csv(fout, sep = '\t')
    
    return fout

###############################
### CNVkit wrapper function ###

# import lib_bioinfo_v01 as bi
from scipy.signal import medfilt

def get_bed_from_gtf(gtf_file, feature_to_select = 'gene' ):
    
    gtf_lines, hdr_lines = load_gtf(gtf_file)
    feature = get_col(gtf_lines, FEATURE)
    wh = which(feature, feature_to_select)
    gtf_lines_sel = [gtf_lines[w] for w in wh]

    df_sel = pd.DataFrame(data=gtf_lines_sel, columns=GTF_line._fields)
    df_sel = df_sel[['chr', 'start', 'end', 'gname']]
    
    p, fn, ext = get_path_filename_and_ext_of(gtf_file)
    bed_file = '%s/%s.%s.bed' % (p, fn, feature_to_select)
    df_sel.to_csv(bed_file, sep = '\t', header = False, index = False)
    print('BED file saved to %s' % bed_file)
    
    return df_sel, bed_file


def run_CNVkit_paired( genome_fa, target_bed, t_bam, n_bam = None, 
                       out_dir = 'cnvkit_out', n_cores = 4, 
                       seq_type = 'amplicon', drop_low_cvg = True,
                       ref_cnn = None, short_names = False):
    
    cmd = 'cnvkit.py batch %s ' % (t_bam) 
    
    if (n_bam is not None) & (ref_cnn is None):
        cmd = cmd + '--normal %s ' % (n_bam) 
    elif ref_cnn is not None:
        cmd = cmd + '-r %s ' % (ref_cnn) 
        
    cmd = cmd + '-m %s ' % seq_type
    cmd = cmd + '-p %i ' % n_cores
    cmd = cmd + '--fasta %s ' % genome_fa
    cmd = cmd + '--targets %s ' % target_bed
    cmd = cmd + '--output-dir %s ' % out_dir
    
    if drop_low_cvg:
        cmd = cmd + '--drop-low-coverage ' 
    if short_names:
        cmd = cmd + '--short-names ' 
    
    return run_command(cmd)    


def get_cnvkit_summary( df_cnv, med_filter_len = 29 ):
    
    df = df_cnv
    genes = list(df['gene'].unique())

    cols = ['chr', 'start', 'end', 
            'depth_min', 'depth_mean', 'depth_median', 'depth_max', 
            'log2_min', 'log2_mean', 'log2_median', 'log2_max']

    dfg = pd.DataFrame(index = genes, columns = cols)
    for g in genes:
        b = df['gene'] == g
        dfs = df.loc[b,:]
        chrm = list(dfs['chromosome'])[0]
        start = dfs['start'].min()
        end = dfs['start'].max()
        depth_min = dfs['depth'].min()
        depth_mean = dfs['depth'].mean()
        depth_med = dfs['depth'].median()
        depth_max = dfs['depth'].max()
        log2_min = dfs['log2'].min()
        log2_mean = dfs['log2'].mean()
        log2_med = dfs['log2'].median()
        log2_max = dfs['log2'].max()

        dfg.loc[g, cols] = [chrm, start, end, depth_min, depth_mean, depth_med, depth_max,
                            log2_min, log2_mean, log2_med, log2_max ]

    dfg.sort_values(['start'], inplace = True)        
    N = med_filter_len

    filtered = list(medfilt(dfg['log2_median'], kernel_size = N))
    dfg['log2_filtered'] = filtered

    filtered = list(medfilt(dfg['depth_median'], kernel_size = N))
    dfg['depth_filtered'] = filtered   
    
    return dfg


def plot_cnvkit_summary(dfg, title = None, title_fs = 14, title_y = 0.95,
                        figsize = (12,8), dpi = 120, depth_only = True, 
                        filtered_only = False ):
    
    nr, nc = 2, 2
    lst = ['depth_median', 'depth_filtered', 'log2_median', 'log2_filtered']
    line_style = '.-.-'
    if depth_only:
        nr = 1
        lst = ['depth_median', 'depth_filtered']
        line_style = '.-'
    elif filtered_only:
        nr = 1
        lst = ['depth_filtered', 'log2_filtered']
        line_style = '----'
        
    # plt.figure(figsize = figsize, dpi = dpi)
    fig, axes = plt.subplots(nrows=nr, ncols=nc, constrained_layout=True, 
                             figsize = figsize, dpi = dpi)
    fig.tight_layout() 
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, 
                        wspace=0.25, hspace=0.25)
    if title is not None:
        fig.suptitle('%s' % title, y = title_y, fontsize = title_fs, ha = 'center')

    for j, y in enumerate(lst):

        plt.subplot(nr,nc,j+1)
        x = 'start'
        plt.plot(dfg[x], dfg[y], line_style[j], ms = 1)
        a = np.array(dfg[x])
        xp = [a[0], a[-1]]
        med = dfg[y].median()
        yp = [med, med]
        plt.plot(xp, yp, '-', ms = 1)
        q3 = np.percentile(dfg[y], 75)
        yp = [q3, q3]
        plt.plot(xp, yp, '-', ms = 1)
        q1 = np.percentile(dfg[y], 25)
        yp = [q1, q1]
        plt.plot(xp, yp, '-', ms = 1)
        plt.ylabel(y)
        plt.grid()

        if (filtered_only) | (j >= nc):
            plt.xlabel('Genomic position')

    plt.show()
    return q1, med, q3

######################################
### RSEM, DEIso, rmats ###
### Gene expression quantification ###

def RSEM_CalcExp( fq_left, fq_right = None, \
                  tr_idx_prefix = None, out_prefix = '', \
                  p = 4, zipped = True, paired = True, aligner = 'star'):

    cmd_lst = []
    if paired & (not os.path.isfile(fq_right)):
        print('ERROR: Second input is None.')
        return None
    
    if (tr_idx_prefix is None) | (not os.path.isfile(tr_idx_prefix + '.grp')):
        print('ERROR: Invalid index to Ref transcriptome .. %s' % (tr_idx_prefix))       
        return None
        
    print('rsem-calculate-expression' )

    cmd = 'rsem-calculate-expression --%s ' % aligner
    cmd = cmd + '-p %i -q ' % p
    
    if zipped:
        cmd = cmd + '--star-gzipped-read-file '
        
    if paired:
        cmd = cmd + '--paired-end '
        cmd = cmd + '%s %s ' % (fq_left, fq_right)
        cmd = cmd + '%s %s' % (tr_idx_prefix, out_prefix)
    else: 
        cmd = cmd + '%s ' % (fq_left)
        cmd = cmd + '%s %s' % (tr_idx_prefix, out_prefix)

    run_command(cmd)
    cmd_lst.append(cmd)

    file_out_gene = '%s.genes.results' % out_prefix
    file_out_tr = '%s.isoforms.results' % out_prefix

    if os.path.isfile(file_out_gene) & os.path.isfile(file_out_tr):
        print('Expression info. saved to .. ')
        print('   %s ' % file_out_gene)
        print('   %s ' % file_out_tr)
                
    return file_out_tr, cmd


def get_rsem_res_from_dir(rsem_res_dir, df_GTmap, col = 'TPM'):

    rsem_dir = rsem_res_dir
    dlst = os.listdir(rsem_dir)
    dlst.sort()
    kg = 0
    kt = 0
    for d in dlst:

        if d.endswith('.isoforms.results'):
            res = '%s/%s' % (rsem_dir, d)
            key = d.split('.')[0]        
            df = pd.read_csv(res, sep = '\t', index_col = 0)
            idx = list(df.index.values)

            if (kt == 0) :
                dft_all = pd.DataFrame(index = idx)
                dft_all['%s' % key] = df[col]
            else:
                dft_all.loc[idx, '%s' % key] = df[col]
            kt += 1

        elif d.endswith('.genes.results'):
            res = '%s/%s' % (rsem_dir, d)
            key = d.split('.')[0]        
            df = pd.read_csv(res, sep = '\t', index_col = 0)
            idx = list(df.index.values)

            if (kg == 0) :
                dfg_all = pd.DataFrame(index = idx)
                dfg_all['%s' % key] = df[col]
            else:
                dfg_all.loc[idx, '%s' % key] = df[col]
            kg += 1

    print('%i genes, %i transcripts found' % (dfg_all.shape[0], dft_all.shape[0]))
    
    ## Renames 
    df = df_GTmap # load_GTmap('hg38')

    b = df['feature'] == 'gene'
    lst1 = list(df.loc[b, 'gid'])
    lst2 = list(df.loc[b, 'gname'])
    rend_g = dict(zip(lst1, lst2))

    gids = list(dfg_all.index.values)
    gidc = list(set(lst1).intersection(gids))

    len(gidc), len(gids), len(lst1)

    dfg_all = dfg_all.loc[gidc, :]

    gns = [rend_g[g] for g in gidc]
    dfg_all['GeneName'] = gns

    # dfg_all.drop_duplicates('GeneName', inplace = True)
    dfg_all.set_index('GeneName', inplace = True)
    dfg_all = dfg_all[~dfg_all.index.duplicated(keep='first')]

    b = df['feature'] == 'transcript'
    lst1 = list(df.loc[b, 'tid'])
    lst2 = list(df.loc[b, 'tname'])
    rend_t = dict(zip(lst1, lst2))

    tids = list(dft_all.index.values)
    tidc = list(set(lst1).intersection(tids))

    len(tidc), len(tids), len(lst1)

    dft_all = dft_all.loc[tidc, :]

    tns = [rend_t[g] for g in tidc]
    dft_all['TranscriptName'] = tns

    dft_all.set_index('TranscriptName', inplace = True)
    dft_all = dft_all[~dft_all.index.duplicated(keep='first')]
    
    return dft_all, dfg_all


def run_rMATs( path_to_rMAT, b1, b2, path_to_gtf, 
              rd_type = 'paired', rd_len = 100, n_thred = 4, 
              out_dir = 'rmats_out', tmp_dir = 'rmats_tmp',
              lib_type = 'fr-firststrand' ):

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    cmd = '%s ' % path_to_rMAT
    cmd = cmd + '--gtf %s ' % path_to_gtf
    cmd = cmd + '--b1 %s ' % b1
    cmd = cmd + '--b2 %s ' % b2
    cmd = cmd + '-t %s ' % rd_type
    cmd = cmd + '--readLength %i ' % rd_len
    cmd = cmd + '--nthread %i ' % n_thred
    cmd = cmd + '--od %s ' % out_dir
    cmd = cmd + '--tmp %s ' % tmp_dir
    cmd = cmd + '--libType %s ' % lib_type
    cmd = cmd + '--allow-clipping ' 
    cmd = cmd + '--variable-read-length ' 

    run_command(cmd)  
    return cmd


def get_rmats_summary( out_dir, pval_cutoff = 0.01, 
                       as_lst = ['MXE', 'SE', 'RI', 'A3SS', 'A5SS']):

    col_sel = ['geneSymbol', 'PValue', 'FDR']

    ## Merge all the results
    cnt = 0
    df_dct = {}
    for j, s in enumerate(as_lst):
        file = out_dir + '/%s.MATS.JCEC.txt' % (s)
        df = pd.read_csv(file, sep = '\t')
        dft = df[col_sel].copy(deep = True)
        dft = dft.loc[dft['PValue'] <= pval_cutoff, :]
        dft.insert(1, column = 'AS_type', value = s )
        
        df_dct[s] = dft
        
        if dft.shape[0] > 0:
            if cnt == 0:
                dfc = dft
            else:
                dfc = pd.concat([dfc, dft], axis = 0, ignore_index=True)
            cnt += 1
   
    ## Get summary for each gene
    pcnt = dfc['geneSymbol'].value_counts()
    genes = list(pcnt.index.values)

    cols = ['pval_min', 'pval_max', 'FDR_min', 'FDR_max'] + as_lst
    dfs = pd.DataFrame( index = genes, columns = cols)

    dfs[['pval_min', 'FDR_min']] = 1.
    dfs[['pval_max', 'FDR_max']] = 0.
    dfs[as_lst] = 0

    for i in range(dfc.shape[0]):
        dct = dict(dfc.iloc[i])
        g = dct['geneSymbol']
        t = dct['AS_type']
        dfs.loc[g, 'pval_min'] = min(dfs.loc[g, 'pval_min'], dct['PValue'])
        dfs.loc[g, 'pval_max'] = max(dfs.loc[g, 'pval_max'], dct['PValue'])
        dfs.loc[g, 'FDR_min'] = min(dfs.loc[g, 'FDR_min'], dct['FDR'])
        dfs.loc[g, 'FDR_max'] = max(dfs.loc[g, 'FDR_max'], dct['FDR'])
        dfs.loc[g, t] += 1

    return dfs, df_dct


##############################
### Transcriptome assembly ###

## Functions to parse Tr. assembly results

def get_names_and_values_from_attr(attr):

    items = attr.split(';')
    items = [item.strip() for item in items]

    names = []
    values = []

    for item in items:
        nv = item.split(' ')
        if len(nv) > 1:
            names.append(nv[0])
            values.append(nv[1].strip('"'))

    return names, values

def convert_attr_to_df( gtf_tr_attr ):
    
    attr = gtf_tr_attr[0]
    names, values =  get_names_and_values_from_attr(attr)

    df = pd.DataFrame( columns = names, index = np.arange(len(gtf_tr_attr)) )
    for k, attr in enumerate(gtf_tr_attr):
        names, values =  get_names_and_values_from_attr(attr)
        df.loc[k, names] = values
        
    return df
    

def get_tr_assembly_info( gff_file ):
    
    print('   ', end='')
    gtf_lines, hdr_lines = load_gtf(gff_file)

    gtf_gn_attr = []
    gtf_tr_attr = []

    for gtf_line in gtf_lines:
        if gtf_line.feature == 'transcript':
            gtf_tr_attr.append(gtf_line.attr)
        elif gtf_line.feature == 'gene':
            gtf_gn_attr.append(gtf_line.attr)
    
    dft = convert_attr_to_df( gtf_tr_attr )
    fname = get_file_name_of( gff_file )
    file_out_tr = fname + '_tr_exp.tsv'
    dft.to_csv(file_out_tr, sep='\t')
    
    print('   Tr.info saved to %s' % file_out_tr)
    
    if len(gtf_gn_attr) > 0:
        dfg = convert_attr_to_df( gtf_gn_attr )
        file_out_gn = fname + '_gene_exp.tsv'
        dfg.to_csv(file_out_gn, sep='\t')
        print('   Gn.info saved to %s' % file_out_gn)
        
    return file_out_tr, dft
       

def run_stringtie( bam_file, gtf_file = None, \
                   out_dir = None, p = 4 ):

    assembler = 'stringtie'
    
    out_path, fname, fext = get_path_filename_and_ext_of(bam_file)
    
    if out_dir is None:
        out_dir = '%s_%s_out' % (fname, assembler)
    elif out_dir == '':
        out_dir = '%s_%s_out' % (fname, assembler)
    else:
        if (out_dir[-1] == '/') | (out_dir[-1] == '\\'): 
            out_dir = out_dir[:-1]
    
    if not os.path.isdir(out_dir): os.mkdir(out_dir)    
        
    if gtf_file is None:
        out_file_name = '%s/%s.%s.gff' % (out_dir, fname, assembler)
        exp_file_name = '%s/%s.%s.tsv' % (out_dir, fname, assembler)
    else:
        out_file_name = '%s/%s.%s_gtf_guided.gff' % (out_dir, fname, assembler)
        exp_file_name = '%s/%s.%s_gtf_guided.tsv' % (out_dir, fname, assembler)
        
    print('Run %s for %s' % (assembler, bam_file) )
    
    cmd = 'stringtie %s ' % bam_file
    cmd = cmd + '-p %i -l STRG ' % p
    cmd = cmd + '-o %s ' % out_file_name    
    
    if gtf_file is not None:
        print('   with Guide GTF: %s' % gtf_file )
        cmd = cmd + '-G %s ' % gtf_file   
        # cmd = cmd + '-e -A %s' % exp_file_name   

    exit_code = run_command(cmd)

    if not os.path.isfile(out_file_name):
        print('   ERROR: run %s failed.' % assembler)
        return None, cmd
    else:
        print('   GFF saved to %s' % out_file_name)        
        return out_file_name, cmd

    
def run_strawberry( bam_file, gtf_file = None, \
                    out_dir = None, p = 4 ):

    assembler = 'strawberry'
    out_path, fname, fext = get_path_filename_and_ext_of(bam_file)
    
    if out_dir is None:
        out_dir = '%s_%s_out' % (fname, assembler)
    elif out_dir == '':
        out_dir = '%s_%s_out' % (fname, assembler)
    else:
        if (out_dir[-1] == '/') | (out_dir[-1] == '\\'): 
            out_dir = out_dir[:-1]
    
    if not os.path.isdir(out_dir): os.mkdir(out_dir)    

    if gtf_file is None:
        out_file_name = '%s/%s.%s.gff' % (out_dir, fname, assembler)
    else:
        out_file_name = '%s/%s.%s_gtf_guided.gff' % (out_dir, fname, assembler)
        
    print('Run %s for %s' % (assembler, bam_file) )
    
    cmd = '%s ' % assembler
    
    if gtf_file is not None:
        print('   with Guide GTF: %s' % gtf_file )
        cmd = cmd + '-g %s ' % gtf_file  
        
    cmd = cmd + '-p %i ' % p
    cmd = cmd + '-o %s ' % out_file_name    
    cmd = cmd + '%s ' % bam_file    

    exit_code = run_command(cmd)

    if not os.path.isfile(out_file_name):
        print('   ERROR: run %s failed.' % assembler)
        return None, cmd
    else:
        print('   GFF saved to %s' % out_file_name)        
        return out_file_name, cmd

    
def run_scallop( bam_file, out_dir = None, verbose = 0 ):

    assembler = 'scallop'
    out_path, fname, fext = get_path_filename_and_ext_of(bam_file)
    
    if out_dir is None:
        out_dir = '%s_%s_out' % (fname, assembler)
    elif out_dir == '':
        out_dir = '%s_%s_out' % (fname, assembler)
    else:
        if (out_dir[-1] == '/') | (out_dir[-1] == '\\'): 
            out_dir = out_dir[:-1]
    
    if not os.path.isdir(out_dir): os.mkdir(out_dir)    

    out_file_name = '%s/%s.%s.gff' % (out_dir, fname, assembler)
        
    print('Run %s for %s' % (assembler, bam_file) )
    
    cmd = '%s -i %s ' % (assembler, bam_file)
    cmd = cmd + '-o %s ' % out_file_name    
    cmd = cmd + '--verbose %i ' % verbose    
    
    exit_code = run_command(cmd, prn = False)

    if not os.path.isfile(out_file_name):
        print('   ERROR: run %s failed.' % assembler)
        return None, cmd
    else:
        print('   GFF saved to %s' % out_file_name)        
        return out_file_name, cmd

    
def run_cufflinks( bam_file, gtf_file = None, \
                   out_dir = None, p = 4 ):

    assembler = 'cufflinks'
    
    out_path, fname, fext = get_path_filename_and_ext_of(bam_file)
    
    if out_dir is None:
        out_dir = '%s_%s_out' % (fname, assembler)
    elif out_dir == '':
        out_dir = '%s_%s_out' % (fname, assembler)
    else:
        if (out_dir[-1] == '/') | (out_dir[-1] == '\\'): 
            out_dir = out_dir[:-1]
    
    if not os.path.isdir(out_dir): os.mkdir(out_dir)    
        
    out_path_tmp = out_dir + '/%s' % assembler
        
    print('Run %s for %s' % (assembler, bam_file) )
    
    cmd = '%s -u %s ' % (assembler, bam_file)
    cmd = cmd + '-p %i ' % p
    cmd = cmd + '-o %s ' % out_path_tmp    
    
    if gtf_file is not None:
        print('   with Guide GTF: %s' % gtf_file )
        cmd = cmd + '-g %s ' % gtf_file   

    exit_code = run_command(cmd)

    out_file_name = out_path_tmp + '/transcripts.gtf'
    if not os.path.isfile(out_file_name):
        print('   ERROR: run %s failed.' % assembler)
        return None, cmd
    else:
        if gtf_file is None:
            out_file_name2 = out_dir + '/%s.%s.gff' % (fname, assembler)
        else:
            out_file_name2 = out_dir + '/%s.%s_gtf_guided.gff' % (fname, assembler)
            
        run_command('cp %s %s' % (out_file_name, out_file_name2))
        run_command('rm -rf %s' % out_path_tmp)
            
        print('   GFF saved to %s' % out_file_name2)        
        return out_file_name2, cmd


def run_trinity( bam_file, out_dir = None, p = 4, max_mem_GB = 32 ):

    assembler = 'Trinity'
    
    out_path, fname, fext = get_path_filename_and_ext_of(bam_file)
    
    if out_dir is None:
        out_dir = '%s_%s_out' % (fname, assembler)
    elif out_dir == '':
        out_dir = '%s_%s_out' % (fname, assembler)
    else:
        if (out_dir[-1] == '/') | (out_dir[-1] == '\\'): 
            out_dir = out_dir[:-1]
    
    if not os.path.isdir(out_dir): os.mkdir(out_dir)    
    
    out_path_tmp = out_dir + '/%s' % assembler
       
    print('Run %s for %s' % (assembler, bam_file) )
    
    cmd = '%s --seqType fq ' % assembler
    cmd = cmd + '--genome_guided_bam %s ' % bam_file
    cmd = cmd + '--output %s ' % out_path_tmp    
    cmd = cmd + '--CPU %i ' % p
    cmd = cmd + '--max_memory %iG ' % max_mem_GB
    cmd = cmd + '--full_cleanup --trimmomatic '
    cmd = cmd + '--genome_guided_max_intron 150000 '
    
    print(cmd)
    exit_code = run_command(cmd)

    out_file_name = out_path_tmp + '/Trinity-GG.fasta'
    if not os.path.isfile(out_file_name):
        print('   ERROR: run %s failed.' % assembler)
        return out_file_name, cmd
    else:
        out_file_name2 = out_dir + '/%s.%s_genome_guided.fa' % (fname, assembler)
            
        run_command('cp %s %s' % (out_file_name, out_file_name2))
        run_command('rm -rf %s' % out_path_tmp)
        
        print('   FASTA saved to %s' % out_file_name2)        
        return out_file_name2, cmd

    
def GFFread( gff_file, genome_file, file_out = None ):
    
    if file_out is None:
        fname = get_file_name_of(gff_file)
        file_out = fname + '_transcriptome.fa'

    cmd = 'gffread %s ' % gff_file
    cmd = cmd + '-w %s ' % file_out
    cmd = cmd + '-g %s ' % genome_file

    if not os.path.isfile( genome_file + '.fai' ):
        run_command('samtools faidx %s' % genome_file)
    
    exit_code = run_command(cmd)
    
    return file_out, cmd

        
def run_tr_assembly( method, bam_file, genome_file = None, gtf_file = None, \
                     out_dir = None, p = 4 ):

    cmd_lst = []
    start = time.time()
    if method == 'stringtie':
        file_out, cmd = run_stringtie( bam_file, gtf_file, out_dir, p)
        file_out_ti, df = get_tr_assembly_info( file_out )
        
    elif method == 'cufflinks':
        file_out, cmd = run_cufflinks( bam_file, gtf_file, out_dir, p)
        file_out_ti, df = get_tr_assembly_info( file_out )
        
    elif method == 'strawberry':
        file_out, cmd = run_strawberry( bam_file, gtf_file, out_dir, p)
        file_out_ti, df = get_tr_assembly_info( file_out )
        
    elif method.lower() == 'trinity':
        file_out, cmd = run_trinity( bam_file, out_dir, p)
        
    elif method == 'scallop':
        file_out, cmd = run_scallop( bam_file, out_dir)
        file_out_ti, df = get_tr_assembly_info( file_out )
       
    else:
        cmd = None
        print('ERROR: unrecogized assembler')
        return None, None, cmd_lst

    cmd_lst.append(cmd)
    
    ## Run gffread to generate transcriptome
    if (genome_file is not None) & (method.lower() != 'trinity'):
        
        file_out_fa, cmd = GFFread( file_out, genome_file )
        cmd_lst.append(cmd)
        
        if not os.path.isfile(file_out):
            print('   ERROR: run %s failed.' % method)
            return None, None, cmd_lst
        else:
            if file_out_fa is None:

                if not os.path.isfile(file_out_fa):
                    print('   ERROR: transcriptome generation failed.')
                    return file_out, None, cmd_lst
                else:
                    print('   %s' % file_out_fa) 
                    elapsed = time.time() - start
                    print('   Assembly with %s done. (%5.2f)' % (method, elapsed))
    else:
        if not os.path.isfile(file_out):
            print('   ERROR: run %s failed.' % method)
            return None, None, cmd_lst
        else:
            file_out_fa = file_out
            print('   %s' % file_out_fa) 
            elapsed = time.time() - start
            print('   Assembly with %s done. (%5.2f)' % (method, elapsed))
    
    return file_out, file_out_fa, cmd_lst
        
