from src import CPCReporter
from datetime import datetime
from itertools import product
from pprint import pprint
import src.pacific as pacific

def main():
    newlogs = datetime(2020, 7, 1)
    june_logs = datetime(2020, 7, 19)
    sort_by = [(['P(wc fault)', '#wc'], [False, False], 10)]#[('unique error vectors', False, 3), ('#wc', False, 3), ('P(wc fault)', False, 3), ('P(masking | wc fault)', True, 3)]
    report_attacks = [None]*10
    for cpc in range(3,4):
        try:
            report = CPCReporter.CPCReporter(cpc=cpc)
            report.set_params(min_success_prob=0.01
                                , min_tries_global=4
                                , min_tries_specific=10
                                , below_margin=-3
                                , above_margin=2
                                , wd_consistent_threshold=0.5)

            report.set_sortby(sortby=sort_by)

            report.fetch_files(parse_pickles=True, to_datetime=newlogs, max_files=None)
            #report.generate_report(general_report=True, specifics_report=12)#making a report
            report_attacks[cpc] = report.attacks
        except:
            print('error in cpc = ', cpc)


    #here we have the attacks data inside the 'report_attacks[]' array
    #todo: to filter out the shift attacks.             - Done.
    #Todo: to deside what field are important for us.
    shift_attacks = report.attacks[report.attacks['is shifted']==True][['address','index','shift','addr minus idx','Class']]
    #Todo: to add the ADR codec to the pacific.py file
    #in write vec we have the to write coded data.
    #Todo: to make a write vectore with the original addresses. to split fields so we have the data and the redundencies
    # to code the address using ADR and => to XOR with the redundancies bits
    # to XOR with the redundencies of the read data
    # to check by comparing.

    print('end')
    print('end')
#report.attacks[report.attacks['is shifted']==True][['address','index','shift','addr minus idx','Class']]


if __name__=='__main__':
    main()