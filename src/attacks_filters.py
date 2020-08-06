import pandas as pd
from pacific import Pacific
from bitarray import bitarray, util as bit_util


def filter_param_set(attacks, paramsets: pd.DataFrame):
    """
    paramsets is a DataFrame (regular indexing).
    (if it multi-indexed, use paramsets.index.to_frame().reset_index(drop=True))
    """
    return pd.merge(attacks, paramsets, on=paramsets.columns.to_list())

def filter_not_tested_attacks(attacks, paramkeys, min_tries=10):
    tries = attacks[['try_id'] + paramkeys].drop_duplicates().groupby(paramkeys).count().rename(columns={'try_id':'tries'})
    to_save = tries[tries['tries'] >= min_tries].reset_index().drop(columns=['tries'])
    return pd.merge(attacks, to_save, on=paramkeys).reset_index(drop=True)

def generate_mem_content(code, initial : bitarray, delta : bitarray, N=100):
    initial = bit_util.ba2int(initial)
    delta = bit_util.ba2int(delta)
    overlap = 2**(code.k)
    data = [x % overlap for x in range(initial, initial + N * delta, delta)]

    ba_data = [bit_util.int2ba(d, length=code.k) for d in data]
    codewords = [code.encode_word(word) for word in ba_data]
    return codewords 
    