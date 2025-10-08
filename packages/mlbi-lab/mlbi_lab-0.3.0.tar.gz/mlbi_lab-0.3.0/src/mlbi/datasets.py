import pkg_resources
import os
import pandas as pd
from scipy.sparse import csr_matrix

ANNDATA_ = True
try:
    import anndata 
except ImportError:
    print('WARNING: AnnData not installed. ')
    ANNDATA_ = False

def load_CCLE(Dir = 'data'):
    
    print('Loading CCLE data .. ', end='')
    if len(Dir) > 0: Dir = Dir + '/'
    df_exp = pd.read_csv(Dir + 'CCLE_cellline_gene_exp.csv', index_col = 0)
    df_pd = pd.read_csv(Dir + 'CCLE_cellline_info.csv', index_col = 0)
    df_auc = pd.read_csv(Dir + 'CCLE_drug_response_auc.csv', index_col = 0)
    df_ec50 = pd.read_csv(Dir + 'CCLE_drug_response_ec50.csv', index_col = 0)
    df_drug_info = pd.read_csv(Dir + 'CCLE_drug_info.csv', index_col = 0)
    print('done')

    return df_exp, df_pd, df_auc, df_ec50, df_drug_info
    

description = 'A data frame containing 753 observations on 21 variables.\n \
    \n\
    Variables\n\
    participation: Factor. Did the individual participate in the labor force in 1975? (This is essentially wage > 0 or hours > 0.)\n\
    hours: Wife\'s hours of work in 1975.\n\
    youngkids: Number of children less than 6 years old in household.\n\
    oldkids: Number of children between ages 6 and 18 in household.\n\
    age: Wife\'s age in years.\n\
    education: Wife\'s education in years.\n\
    wage: Wife\'s average hourly wage, in dollars.\n\
    repwage: Wife\'s wage reported at the time of the 1976 interview (not the same as the 1975 estimated wage). To use the subsample with this wage, one needs to select 1975 workers with participation == "yes", then select only those women with non-zero wage. Only 325 women work in 1975 and have a non-zero wage in 1976.\n\
    hhours: Husband\'s hours worked in 1975.\n\
    hage: Husband\'s age in years.\n\
    heducation: Husband\'s education in years.\n\
    hwage: Husband\'s wage, in dollars.\n\
    fincome: Family income, in dollars. (This variable is used to construct the property income variable.)\n\
    tax: Marginal tax rate facing the wife, and is taken from published federal tax tables (state and local income taxes are excluded). The taxable income on which this tax rate is calculated includes Social Security, if applicable to wife.\n\
    meducation: Wife\'s mother\'s educational attainment, in years.\n\
    feducation: Wife\'s father\'s educational attainment, in years.\n\
    unemp: Unemployment rate in county of residence, in percentage points. (This is taken from bracketed ranges.)\n\
    city: Factor. Does the individual live in a large city?\n\
    experience: Actual years of wife\'s previous labor market experience.\n\
    college: Factor. Did the individual attend college?\n\
    hcollege: Factor. Did the individual\'s husband attend college?\n\
    \n\
    Source: Online complements to Greene (2003). Table F4.1. https://pages.stern.nyu.edu/~wgreene/Text/tables/tablelist5.htm\n\
    \n\
    References\n\
    Greene, W.H. (2003). Econometric Analysis, 5th edition. Upper Saddle River, NJ: Prentice Hall.\n\
    McCullough, B.D. (2004). Some Details of Nonlinear Estimation. In: Altman, M., Gill, J., and McDonald, M.P.: Numerical Issues in Statistical Computing for the Social Scientist. Hoboken, NJ: John Wiley, Ch. 8, 199–218.\n\
    Mroz, T.A. (1987). The Sensitivity of an Empirical Model of Married Women\'s Hours of Work to Economic and Statistical Assumptions. Econometrica, 55, 765–799.\n\
    Winkelmann, R., and Boes, S. (2009). Analysis of Microdata, 2nd ed. Berlin and Heidelberg: Springer-Verlag.\n\
    Wooldridge, J.M. (2002). Econometric Analysis of Cross-Section and Panel Data. Cambridge, MA: MIT Press.'


def load_data( dataset = None ):

    data_folder = pkg_resources.resource_filename('mlbi', 'data')
    dlst = ['scores', 'time-series', 'time-series2', 'tcga-brca', 
            'metabric', 'cancerseek', 'ccle-ctrpv2', 'PSID1976']
    
    if dataset == 'scores':
        df = pd.read_csv( data_folder + '/scores.csv' )
        return df
        
    elif dataset == 'time-series':
        df = pd.read_csv( data_folder + '/Time_series.csv' )
        return df
        
    elif dataset == 'time-series2':
        df = pd.read_csv( data_folder + '/Time_series_rev.csv' )
        return df
        
    elif dataset == 'metabric':
        print('Loading METABRIC data .. ', end='')
        # file = '/metabric_data_expression_median.csv'
        # df_gep = pd.read_csv(data_folder + file, index_col=0).transpose().iloc[1:]
        file = '/metabric_gene_expression.csv'
        df_gep = pd.read_csv(data_folder + file, index_col=0)
        df_gep = (df_gep + 150)/30
        file = '/metabric_clinical_data_used.csv'
        df_clinical = pd.read_csv(data_folder + file, index_col=0)

        idx2 = list(df_clinical.index.values)
        idx3 = []
        for i in idx2:
            s = i.replace('.', '-')
            idx3.append(s)
        
        rend = dict(zip(idx2, idx3))
        df_clinical.rename(index = rend, inplace = True)
        
        idx1 = list(df_gep.index.values)
        idx2 = list(df_clinical.index.values)
        idxc = list(set(idx1).intersection(idx2))

        df_gep = df_gep.loc[idxc,:]
        df_clinical = df_clinical.loc[idxc,:]
        print('done')
        
        return { 'gene_expression':  df_gep, 'clinical_info': df_clinical }

    elif dataset == 'tcga-brca':
        print('Loading TCGA-BRCA data .. ', end='')
        file = '/TCGA_BRCA_gene_exp.csv'
        df_gep = pd.read_csv(data_folder + file, index_col=0)
        
        file = '/TCGA_BRCA_clinical_info.csv'
        df_clinical = pd.read_csv(data_folder + file, index_col=0)
        print('done')
        
        return { 'gene_expression':  df_gep, 'clinical_info': df_clinical }

    elif dataset == 'cancerseek':
        file = '/CancerSEEK_protein.csv'
        df_gep = pd.read_csv(data_folder + file, index_col=0)
        file = '/CancerSEEK_clinical_info.csv'
        df_clinical = pd.read_csv(data_folder + file, index_col=0)

        return { 'protein_expression':  df_gep, 'clinical_info': df_clinical }
   
    elif dataset == 'ccle-ctrpv2':
        df_gep, df_pd, df_auc, df_ec50, df_drug_info = load_CCLE(Dir = data_folder)

        return { 'gene_expression':  df_gep, 'cellline_info': df_pd,
                 'auc':  df_auc, 'ec50': df_ec50, 'drug_info': df_drug_info}
   
    elif dataset == 'PSID1976':
        df = pd.read_csv( data_folder + '/PSID1976.csv' )
        return {'DESCRIPTION': description, 'data': df}
   
    else:
        if dataset is not None:
            print('%s dataset not found.' % dataset)
        print('You can select one of .', dlst )
            
        return None


def load_anndata( dataset = None ):

    if not ANNDATA_:
        print('ERROR: AnnData not installed. Install AnnData to use this function. ')
        return None
    
    data = load_data(dataset)
    if dataset == 'metabric':
        genes = data['gene_expression'].columns.values.tolist()
        df_var = pd.DataFrame( {'gene': genes}, index = genes )
        adata = anndata.AnnData( X = csr_matrix(data['gene_expression']), obs = data['clinical_info'], var = df_var )
        return adata

    elif dataset == 'tcga-brca':
        genes = data['gene_expression'].columns.values.tolist()
        df_var = pd.DataFrame( {'gene': genes}, index = genes )
        adata = anndata.AnnData( X = csr_matrix(data['gene_expression']), obs = data['clinical_info'], var = df_var )
        return adata

    elif dataset == 'cancerseek':
        genes = data['protein_expression'].columns.values.tolist()
        df_var = pd.DataFrame( {'gene': genes}, index = genes )
        adata = anndata.AnnData( X = csr_matrix(data['protein_expression']), obs = data['clinical_info'], var = df_var )
        return adata

    elif dataset == 'ccle-ctrpv2':
        genes = data['gene_expression'].columns.values.tolist()
        df_var = pd.DataFrame( {'gene': genes}, index = genes )
        adata = anndata.AnnData( X = csr_matrix(data['gene_expression']), obs = data['cellline_info'], var = df_var )
        adata.obsm['auc'] = data['auc']
        adata.obsm['ec50'] = data['ec50']
        adata.uns['drug_info'] = data['drug_info']
        return adata
   
    else:
        return data

