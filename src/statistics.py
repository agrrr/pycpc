import pandas as pd
import math

# TODO rational ordering

def bit_flip_prob(fattacks_set):
    """
    Returns P(flip) = P(write!=read) as function of mem_before and write_data
    # Input should have uniq attack params
    """
    cols = ['mem_before','write_data','read_data']
    triplets = pd.DataFrame(fattacks_set[cols].apply(lambda x: list(zip(x[0], x[1], x[2])), axis=1).to_list()).values.flatten()
    df = pd.DataFrame(list(triplets), columns = cols).astype(int)
    sums = df.groupby(cols).size().unstack()
    sums['P(1)'] = sums[1] / (sums[1] + sums[0])
    sums = sums['P(1)'].unstack()
    sums[1] = 1 - sums[1] # 1 -> 0

    sums['P(flip|mem bit)'] = sums.mean(axis=1) 
    sums.loc['P(flip|write bit)'] = sums.mean(axis=0) 
    return sums


def num_bit_flips_dist(fattacks_set):
    """
    Returns distribution of #bitflips of all given attacks 
    # Input should have uniq attack params
    """
    counts = fattacks_set['#bitflips'].value_counts()
    dist = counts / len(fattacks_set)
    dist = dist.sort_index()
    mx = max(fattacks_set['#bitflips'])
    dist = dist.reindex(range(mx+1), fill_value=0)
    return dist

def num_bit_flips_dist_by_param(fattacks, param, n, range_param=None):
    """
    2d heatmap
    Returns distribution of #bitflips, as function of param
    param: a column name of fattacks (can be attack parmeter, address, etc.)
    # Input shouldn't have uniq attack params
    """
    mat = fattacks.groupby(['#bitflips', param]).size().unstack().fillna(0)
    dists = mat / mat.sum()
    return fill_matrix(dists, indexes=range(n), columns=range_param, fill_columns=True, fill_rows=False)


def parmaset_describe_attacks(attacks, fattacks, paramkeys):
    """
    Counts loglines with at least one write-corrupt attack and normalise by total tries
    Returns prob as function of paramsets (indexes)
    # Input shouldn't have uniq attack params
    """
    tries = attacks[['try_id'] + paramkeys].drop_duplicates().groupby(paramkeys).count().rename(columns={'try_id':'tries'})
    ftries = fattacks[['try_id'] + paramkeys].drop_duplicates().groupby(paramkeys).count().rename(columns={'try_id':'tries'}) # may rewrite with groupby() and nunique()
    attacks_types = (ftries / tries).rename(columns={'tries': 'P(wc fault)'}).fillna(0)
    attacks_types['#wc'] = fattacks.groupby(paramkeys)['try_id'].nunique()
    attacks_types['tries'] = attacks.groupby(paramkeys)['try_id'].nunique()

    attacks_types['unique error vectors'] = fattacks.groupby(paramkeys)['err_vec'].nunique()
    Pmasking_key = 'P(masking | wc fault)'
    masking_counts = pd.merge(attacks_types.reset_index(), fattacks, how='left').fillna(-1).groupby(paramkeys)['detected by HW'].value_counts().unstack()
    if 0 not in masking_counts: masking_counts[0] = math.nan
    if 1 not in masking_counts: masking_counts[1] = math.nan
    attacks_types[Pmasking_key] = masking_counts[0] / (masking_counts[0] + masking_counts[1])
    attacks_types.loc[~masking_counts[0].isna() & masking_counts[1].isna(), Pmasking_key] = 1
    attacks_types.loc[masking_counts[0].isna() & ~masking_counts[1].isna(), Pmasking_key] = 0
    bitflips_describe = pd.merge(attacks_types.reset_index(), fattacks) \
            .groupby(paramkeys)['#bitflips'] \
            .describe()[['mean', 'std', 'min', 'max']] \
            .rename(columns=dict((k, ('#bitflips', k)) for k in ['mean', 'std', 'min', 'max']))
    all2ret = attacks_types.join(bitflips_describe)
    return all2ret


def P1_given_bitloc(binary_vectors):
    bits = binary_vectors.apply(lambda x: x.to01()).str.split(pat='', expand=True)
    bits = bits.drop([0, len(bits.columns)-1], axis=1)
    bits.columns = bits.columns - 1
    return bits.astype(int).sum().div(len(bits))

def P1_given_bitloc_and_y(binary_vectors, y, range_y=None):
    bits = binary_vectors.apply(lambda x: x.to01()).str.split(pat='', expand=True)
    bits = bits.drop([0, len(bits.columns)-1], axis=1)
    bits.columns = bits.columns - 1
    bits[y.name] = y
    mat2ret = bits.astype(int).groupby(y.name).sum() / bits.astype(int).groupby(y.name).count()
    if range_y is None:
        return mat2ret
    else:
        return fill_matrix(mat2ret, indexes=range_y, fill_rows=False, fill_columns=False)

def address_prob(attacks_set, fattacks_set):
    """
    Return the probability of an address to be in fattacks_set, normlized by itself in attacks_set
    # Input should have uniq attack params
    """
    fadrr = fattacks_set['address'].value_counts().sort_index().reindex(range(100), fill_value=0)
    adrr  =  attacks_set['address'].value_counts().sort_index().reindex(range(100), fill_value=0)
    return fadrr / adrr


def faulttype_dist_by_try(attacks):
    """
    deprecated?
    Returns DataFrame of histograms of fault types in logline (=try)
    """ 
    bytry = attacks.groupby(['try_id', 'fault_type']).size().unstack('fault_type').fillna(0).reset_index(drop=True)
    bytry.columns.name = None
    dists = bytry.apply(pd.Series.value_counts).fillna(0)
    return dists


def prob_of_detection_by_HW(fattacks_set):
    """
    Returns P(detected | error present) = p(HW_flage=1 | #bitflips > 0)
    """
    return fattacks_set['detected by HW'].sum() / len(fattacks_set)
    
def faults_stats(attacks_set):
    """
    Output for example:
    >>> stats.faults_stats(attacks)
                                                                    Occurrences
    Class                    Fault Relation detected by HW detected by SW                   
    Address shift (negative) After          False          False               101165 (5.6%)
                            Hit            False          False                788 (0.044%)
                            Unrelated      False          False                4077 (0.23%)
    Address shift (positive) After          False          False           331717 (1.8e+01%)
                            Hit            False          False                4323 (0.24%)
                            Unrelated      False          False                8336 (0.46%)
    No fault                 After          False          False           440166 (2.5e+01%)
                            Before         False          False           599399 (3.3e+01%)
                            Unrelated      False          False           224687 (1.3e+01%)
    Unclassified fault       After          False          False                18785 (1.0%)
                                            True           True                1001 (0.056%)
                            Unrelated      False          False                41342 (2.3%)
                                            True           True                 823 (0.046%)
    Write corrupt            Hit            False          False                431 (0.024%)
                                            True           True                1330 (0.074%)
    Write skip               After          False          False                4746 (0.26%)
                            Hit            False          False                8249 (0.46%)
                            Unrelated      False          False                2235 (0.12%)
    """
    a = attacks_set[['Class', 'Fault Relation', 'detected by HW', 'detected by SW']] \
        .fillna('undefined').astype({'detected by HW': bool, 'detected by SW': bool}) \
        .groupby(['Class', 'Fault Relation', 'detected by HW', 'detected by SW']).size() \
        .to_frame('number of occurrences')
    a['%'] = a['number of occurrences'] / a['number of occurrences'].sum() * 100
    a = a.apply(lambda x: f'{int(x[0])} ({x[1]:.4}%)', axis=1).to_frame('Occurrences')
    a['Class'] = a.index.get_level_values('Class')
    m = ['No fault', 'Write corrupt', 'Address shift (negative)', 'Address shift (positive)', 'Write skip', 'Unclassified fault']
    mapping = dict(zip(m, range(len(m))))
    a['sortby'] = a['Class'].map(mapping)
    a = a.sort_values('sortby').drop(columns=['Class','sortby'])
    return a

def indexXaddr_prob(attacks, fattacks):
    attacks_crosstab = pd.crosstab(attacks['address'], attacks['index'], dropna=False)
    matrix = pd.crosstab(fattacks['address'], fattacks['index'], dropna=False) / attacks_crosstab
    return fill_matrix(matrix, range(100), range(100), fill_columns=True, fill_rows=False)


def fill_matrix(df, indexes=None, columns=None, fill_columns=False, fill_rows=False):
    matrix = df + \
            pd.DataFrame(
                index = df.index if indexes is None else pd.Index(indexes, name=df.index.name),
                columns = df.columns if columns is None else pd.Index(columns, name=df.columns.name)).fillna(0)
    if fill_columns:
        idxs = df.columns
        matrix.loc[:, idxs] = matrix.loc[:, idxs].fillna(0)
    if fill_rows:
        idxs = df.index
        matrix.loc[idxs, :] = matrix.loc[idxs, :].fillna(0)
    return matrix

def marginal_distribution_of_multiindex_multivar(df, x):
    """
    : df (pd.Dataframe): a multiindex dataframe.
    : x (str): index we want to plot by.
    : Return: marginal distribution by x.
    """
    pivot = df.unstack(x).fillna(0)
    pivot.columns = pivot.columns.droplevel(0) # NOTE this assumes there was a lable on the column before the unstack @davidpel
    pivot = pivot.reset_index(drop=True)
    pivot = pivot.sum() / len(pivot)
    return pivot
    

def marginal_distribution_2d_of_multiindex_multivar(df, x, y):
    """
    : df (pd.Dataframe): a multiindex dataframe.
    : x, y (str): indexes we want to plot by.
    : Return: 2d marginal distribution by x, y.
    """
    pivot = df.unstack(x)
    pivot.columns = pivot.columns.droplevel(0) # NOTE this assumes there was a lable on the column before the unstack @davidpel
    pivot.index = pivot.index.get_level_values(y)
    pivot = pivot.groupby(y).sum() / pivot.groupby(y).count()
    return pivot

def index_hist(attacks):
    counts = attacks[['try_id','index']].drop_duplicates()['index'].value_counts().sort_index()
    zeros_in_range100 = pd.Series(index=range(100)).fillna(0)
    counts_with_zeros = (counts + zeros_in_range100).fillna(0)
    return counts_with_zeros

def address_minus_index_hist(fattacks):
    diffs = fattacks['address'] - fattacks['index']
    diffs = diffs.astype(int)
    hist = diffs.value_counts().sort_index()
    return hist

def errvec_hist(fattacks, n=10):
    return (fattacks['err_vec'].value_counts().sort_values().head(n) # take the first n 
        .reset_index(drop=False, name='idx')
        .set_index('idx')                       # exchange index and value
        .apply(lambda x: x.to01()))   # to string

def bit_read_write_summary(fattacks):
    cols = ['mem_before','write_data','read_data']
    triplets = pd.DataFrame(fattacks[cols].apply(lambda x: list(zip(x[0], x[1], x[2])), axis=1).to_list()).values.flatten()
    df = pd.DataFrame(list(triplets), columns = cols).astype(int)
    sums = df.groupby(cols).size().unstack([1,0])
    return (sums / sums.sum()).sort_index(axis=1)
