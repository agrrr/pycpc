import CPCReporter
from datetime import datetime
from itertools import product
from pprint import pprint

def main():
    newlogs = datetime(2020, 7, 1)
    june_logs = datetime(2020, 7, 19)
    sort_by = [(['P(wc fault)', '#wc'], [False, False], 10)]#[('unique error vectors', False, 3), ('#wc', False, 3), ('P(wc fault)', False, 3), ('P(masking | wc fault)', True, 3)]
    report_attacks = [None]*10
    for cpc in range(0,11):
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
            
            combined_report.concat([report.attacks])
            report_attacks[cpc] = report.attacks
        except:
            print('error in cpc = ',cpc)
    print('end')
    print('end')



if __name__=='__main__':
    main()