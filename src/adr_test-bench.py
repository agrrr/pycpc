from src import CPCReporter
from datetime import datetime
from itertools import product
from pprint import pprint
import src.pacific as pacific
import src.codes as code
import pandas as pd

def main():
    pd.options.display.max_rows = 999999
    newlogs = datetime(2020, 7, 1)
    june_logs = datetime(2020, 7, 19)
    sort_by = [(['P(wc fault)', '#wc'], [False, False], 10)]#[('unique error vectors', False, 3), ('#wc', False, 3), ('P(wc fault)', False, 3), ('P(masking | wc fault)', True, 3)]
    #report_attacks = [None]*10

    report_attacks = pd.DataFrame()
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
            report_attacks.append(report.attacks)#appending rows
        except:
            print('error in cpc = ', cpc)


    #here we have the attacks data inside the 'report_attacks[]' array
    shift_attacks = report.attacks[report.attacks['is shifted']==True][['address','read_data','original_address','write_data','shift','Class']]
    #shift_attacks = report.attacks[report.attacks['original_address']!=True]
    #shift_attacks = report.attacks[report.attacks['original_address'] != float()]
    #shift_attacks.convert_dtypes(report.attacks['address'], object=bytearray)
    #shift_attacks['address'] = bytearray(shift_attacks['address'])
    #shift_attacks['address|data|red'] = code.int2bitarray(shift_attacks['address'], 10)
    address_decoder = code.ADR(report.cpc.k,report.cpc.r)
    flag:bool
    result = {'True': 0}
    result['False'] = 0
    for x in shift_attacks.index:
        #collect and pring read data
        bin_read_address = code.int2bitarray(int(shift_attacks['address'][x]), 10)
        bin_read_data = shift_attacks['read_data'][x]
        bin_read_red = code.get_red(bin_read_data,report.cpc.r)
        bin_full_read_word = bin_read_address + bin_read_data
        print(f'Read_data {x}:\n',bin_read_address,bin_read_data,'\n',bin_full_read_word,'\n',bin_read_red)
        #collect and print write data
        bin_write_address = code.int2bitarray(int(shift_attacks['original_address'][x]), 10)
        bin_write_data = shift_attacks['write_data'][x]
        bin_write_red = code.get_red(bin_write_data, report.cpc.r)
        coded_write_red_address = address_decoder.encode(bin_write_data[:14],bin_write_address)
        coded_read_red_address = address_decoder.encode(bin_read_data[:14], bin_read_address)
        bin_full_write_word = bin_write_address + bin_write_data
        print(f'write_data {x}:\n', bin_write_address, bin_write_data, '\n', bin_full_write_word, '\n', bin_write_red)
        #check success
        print('coded addresses:\ncoded_write:\t', coded_write_red_address,'\ncoded_read:\t',coded_read_red_address )
        flag = (coded_read_red_address == coded_write_red_address)
        result[str(flag)] += 1
        print(flag,'\n----------------------')

    #Todo: to add the ADR codec to the pacific.py file
    #in write vec we have the to write coded data.
    #Todo: to make a write vectore with the original addresses. to split fields so we have the data and the redundencies
    # to code the address using ADR and => to XOR with the redundancies bits
    # to XOR with the redundencies of the read data
    # to check by comparing.
#code.int2bitarray(shift_attacks['address'], 10) #converting address to binary
    print('end')
    print('end')
#report.attacks[report.attacks['is shifted']==True][['address','index','shift','addr minus idx','Class']]


if __name__=='__main__':
    main()