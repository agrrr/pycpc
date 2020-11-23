from src import CPCReporter
from datetime import datetime
from itertools import product
from pprint import pprint
import src.pacific as pacific
from bitarray import bitarray
import src.codes as code
import pandas as pd
import numpy as np
from progress.bar import Bar, IncrementalBar
import sys


def main():
    pd.options.display.max_rows = 999999
# report_attacks = [None]*10
    shift_attacks = pd.read_csv(f'..\\results\\cpc {2}-shifted_XORED_csv.csv')
    wc_attacks = pd.read_csv(f'..\\results\\cpc {2}-wc_new_XORED_csv.csv')
    for x in range(1,11):
        try:
            #shift_attacks = pd.concat([shift_attacks, pd.read_csv(f'..\\results\\cpc {x}-shifted_XORED_csv.csv')])
            #shift_attacks = pd.read_csv(f'..\\results\\cpc {x}-shifted_XORED_csv.csv')
            #wc_attacks = pd.concat([wc_attacks, pd.read_csv(f'..\\results\\cpc {x}-wc_new_XORED_csv.csv')])
            #shift_attacks = shift_attacks.drop_duplicates(['full_write_word', 'full_read_word','write_red_with_ADR','read_red_with_ADR','shift_err_detected'])
            #shift_attacks.to_csv(f'..\\results\\filtered cpc {x}-shifted_XORED_csv.csv')

            wc_attacks = pd.read_csv(f'..\\results\\cpc {x}-wc_new_XORED_csv.csv')
            wc_attacks = (wc_attacks[wc_attacks['wc fault'] == True]).drop_duplicates(['full_write_word', 'full_read_word','write_red_with_ADR','read_red_with_ADR','wc_new_detected'])
            wc_attacks.to_csv(f'..\\results\\filtered cpc {x}-wc_new_XORED_csv.csv')
        except:
            print(f'cpc {x} , does not have files..')
    print(shift_attacks['cpc'].unique())
    print(wc_attacks['cpc'].unique())
    """
    to_commit = 'true'
    while to_commit!='end':
        print(shift_attacks.columns)
        con  = input("choose condition for filering: ")
        fil = shift_attacks[shift_attacks[f'{con}'] == True]
    print('end')
    """



# report.attacks[report.attacks['is shifted']==True][['address','index','shift','addr minus idx','Class']]


if __name__ == '__main__':
    main()