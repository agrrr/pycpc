import CPCReporter
from datetime import datetime
from itertools import product
from pprint import pprint
import pacific as pacific
from bitarray import bitarray
import codes as code
import pandas as pd
import numpy as np
from progress.bar import Bar, IncrementalBar
import sys
import random

pd.options.mode.chained_assignment = None  # default='warn'



def main():
    newlogs = datetime(2020, 7, 1)
    june_logs = datetime(2020, 8, 30)
    sort_by = [(['P(wc fault)', '#wc'], [False, False],
                10)]  # [('unique error vectors', False, 3), ('#wc', False, 3), ('P(wc fault)', False, 3), ('P(masking | wc fault)', True, 3)]
    # report_attacks = [None]*10
    for cpc in range(10, 11):
        print(f'only cpc {cpc}')
        report = CPCReporter.CPCReporter(cpc=cpc)
        report.set_params(min_success_prob=0.01
                            , min_tries_global=4
                            , min_tries_specific=10
                            , below_margin=-3
                            , above_margin=2
                            , wd_consistent_threshold=0.5)

        report.set_sortby(sortby=sort_by)
        chip = report.cpc

        #loading data from general file
        #make new df with good params.
        #drop duplicates equals to 0(zeros)
        #shift data treating
            #add -> original address | address | read_data | is shifted=True
        #wc data treating
            #add ->err_vec | address=original address | read_data = write^err_vec| wc fault = True
        #concating all data to one df and save as cpc data attacks

    print('end')
    print('end')


# report.attacks[report.attacks['is shifted']==True][['address','index','shift','addr minus idx','Class']]


if __name__ == '__main__':
    main()