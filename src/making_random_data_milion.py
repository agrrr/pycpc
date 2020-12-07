from src import CPCReporter
from datetime import datetime
from itertools import product
from pprint import pprint
import src.pacific as Pacific
from bitarray import bitarray
import src.codes as code
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
    for cpc in range(0, 11):
        try:
            print(f'cpc {cpc}')
            report = CPCReporter.CPCReporter(cpc=cpc)
            report.set_params(min_success_prob=0.01
                              , min_tries_global=4
                              , min_tries_specific=10
                              , below_margin=-3
                              , above_margin=2
                              , wd_consistent_threshold=0.5)

            report.set_sortby(sortby=sort_by)
            chip = report.cpc
            df = pd.DataFrame(columns=['cpc', 'write_data'])
            with Bar(f"analysing shift errors cpc {cpc}:", max=1000000) as bar:
                for i in range(1000000):
                    df.loc[i] = [cpc] + [code.int2bitarray(random.randint(1, 2 ** (chip.k)-1), chip.k)]
                    bar.next()
                df.to_csv(f'..\\results\\cpc {cpc}-' + "random_write_data.csv")
        except:
            print(f'problem with cpc{cpc}')
            e = sys.exc_info()[0]
            print("<p>Error: %s</p>" % e)
    # Todo: to add the ADR codec to the pacific.py file ?!?
    # Todo: to make a write vectore with the original addresses. to split fields so we have the data and the redundencies
    # to code the address using ADR and => to XOR with the redundancies bits
    # to XOR with the redundencies of the read data
    # to check by comparing.
    # code.int2bitarray(shift_attacks['address'], 10) #converting address to binary
    print('end')
    print('end')


# report.attacks[report.attacks['is shifted']==True][['address','index','shift','addr minus idx','Class']]


if __name__ == '__main__':
    main()