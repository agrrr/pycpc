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
pd.options.mode.chained_assignment = None  # default='warn'

def main():
    pd.options.display.max_rows = 999999
    newlogs = datetime(2020, 7, 1)
    june_logs = datetime(2020, 7, 19)
    sort_by = [(['P(wc fault)', '#wc'], [False, False],
                10)]  # [('unique error vectors', False, 3), ('#wc', False, 3), ('P(wc fault)', False, 3), ('P(masking | wc fault)', True, 3)]
    # report_attacks = [None]*10

    report_attacks = pd.DataFrame()
    for cpc in range(0, 11):
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
            # report.generate_report(general_report=True, specifics_report=12)#making a report
            # report_attacks.append(report.attacks)#appending rows
            address_decoder = code.ADR(report.cpc.k, report.cpc.r)
            # here we have the attacks data inside the 'report_attacks[]' array
            # print(report.attacks['Class'].unique())
            print(f'cpc {cpc} had:{len(report.attacks)}')
            report.attacks.drop(['vddcore','cpc_vdd','cpc_vddr','vddio','delay','height','index','cycles','pulse-freq'], axis=1, inplace=True )
            report.attacks.drop_duplicates(['write_data', 'original_address','address','read_data','err_vec'],inplace=True)
            print(f'cpc {cpc} have:{len(report.attacks)}')
            shift_attacks = report.attacks[report.attacks['is shifted'] == True]
            # shift_attacks = report.attacks[report.attacks['is shifted']==True][['address','read_data','original_address','write_data','shift','Class']]
            # shift_attacks = report.attacks[['address','read_data','original_address','write_data','shift','Class']]
            # shift_attacks = report.attacks[report.attacks['original_address']!=True]
            # shift_attacks = report.attacks[report.attacks['original_address'] != float()]
            # shift_attacks.convert_dtypes(report.attacks['address'], object=bytearray)
            # shift_attacks['address'] = bytearray(shift_attacks['address'])
            # shift_attacks['address|data|red'] = code.int2bitarray(shift_attacks['address'], 10)
            chip = report.cpc
            flag: bool
            result = {'True': 0, 'False': 0}

            shift_attacks['full_write_word'] = bitarray
            shift_attacks['write_red'] = bitarray
            shift_attacks['write_address'] = bitarray
            shift_attacks['write_ad_red'] = bitarray
            shift_attacks['write_new_full_word'] = bitarray
            shift_attacks['write_new_red'] = bitarray

            shift_attacks['full_read_word'] = bitarray
            shift_attacks['read_red'] = bitarray
            shift_attacks['read_address'] = bitarray
            shift_attacks['read_new_full_word'] = bitarray
            shift_attacks['read_new_calculated_ad_red'] = bitarray

            shift_attacks['read_calculated_red'] = bitarray
            shift_attacks['write_calculated_red'] = bitarray
            shift_attacks['shift_err_detected'] = bool

            with Bar(f"analysing shift errors cpc {cpc}:", max=len(shift_attacks.index)) as bar:
                for x in shift_attacks.index:
                    # collect and pring read data
                    #for shifted the data is the same so we collect data once and compute two different red
                    #based on the address, the address is different
                    bin_write_address = code.int2bitarray(int(shift_attacks['original_address'][x]), 10)
                    bin_data = chip.get_data(shift_attacks['write_data'][x])
                    bin_red = chip.get_red(shift_attacks['write_data'][x])
                    coded_write_red_address = address_decoder.encode(bin_data, bin_write_address)
                    coded_write_red = coded_write_red_address ^ bin_red
                    bin_full_write_word = bin_write_address + bin_data + coded_write_red
                    # dict
                    shift_attacks['write_address'][x] = bin_write_address
                    shift_attacks['write_red'][x] = bin_red
                    shift_attacks['full_write_word'][x] = bin_write_address+bin_data+bin_red

                    shift_attacks['write_ad_red'][x] = coded_write_red_address
                    shift_attacks['write_new_full_word'][x] = bin_full_write_word
                    shift_attacks['write_new_red'][x] = coded_write_red
                    # read side decode
                    bin_read_address = code.int2bitarray(int(shift_attacks['address'][x]), 10)
                    coded_read_red_address = address_decoder.encode(bin_data, bin_read_address)
                    coded_read_red = coded_read_red_address ^ bin_red
                    bin_full_read_word = bin_read_address + bin_data +  coded_write_red
                    shift_attacks['read_address'][x] = bin_read_address
                    shift_attacks['read_red'][x] = bin_red
                    shift_attacks['full_read_word'][x] = bin_read_address + bin_data + bin_red

                    shift_attacks['read_new_calculated_ad_red'][x] = coded_read_red_address
                    shift_attacks['read_new_full_word'][x] = bin_read_address + bin_data + coded_write_red
                    # coded full word
                    shift_attacks['read_calculated_red'][x] = coded_read_red
                    shift_attacks['write_calculated_red'][x] = coded_write_red
                    # check success
                    flag = (coded_read_red == coded_write_red)
                    shift_attacks['shift_err_detected'][x] = not flag
                    result[str(flag)] += 1
                    bar.next()
            shift_attacks.to_csv(f'..\\results\\cpc {report.cpc_number}-' + "shifted_XORED_csv.csv")

            # wc attacks
            wc_attacks = report.attacks[report.attacks['wc candidate'] == True]
            wc_result = {'True': 0, 'False': 0}

            wc_attacks['full_old_write_word'] = bitarray
            wc_attacks['write_address'] = bitarray
            wc_attacks['write_red'] = bitarray
            wc_attacks['write_ad_red'] = bitarray
            wc_attacks['full_new_write_word'] = bitarray
            wc_attacks['write_red_with_ADR'] = bitarray
            wc_attacks['write_new_calculated_red'] = bitarray

            wc_attacks['full_old_read_word'] = bitarray
            wc_attacks['read_red'] = bitarray

            wc_attacks['full_new_read_word'] = bitarray
            wc_attacks['new_read_red'] = bitarray

            wc_attacks['calculated_address_read_red'] = bitarray
            wc_attacks['calculated_data_read_red'] = bitarray
            wc_attacks['calculated_total_red'] = bitarray

            wc_attacks['after_error_ADR_red'] = bitarray
            wc_attacks['after_error_correct_red'] = bitarray
            wc_attacks['wc_new_detected'] = bool
            with Bar(f"wc {report.cpc_number}:", max=len(wc_attacks.index)) as bar:
                for x in wc_attacks.index:
                    # collect and pring read data
                    err_vec = wc_attacks['err_vec'][x] #geting the error vectore
                    #new coded of the oiginal write
                    bin_address = code.int2bitarray(int(wc_attacks['address'][x]), 10)
                    bin_write_data = chip.get_data(wc_attacks['write_data'][x])
                    bin_original_red = chip.get_red(wc_attacks['write_data'][x])
                    write_ADR_red = address_decoder.encode(bin_write_data,bin_address)
                    new_write_red_with_ADR = write_ADR_red ^ bin_original_red
                    new_with_ADR_write_word = bin_write_data + new_write_red_with_ADR
                    full_new_write_word = bin_address + new_with_ADR_write_word

                    wc_attacks['full_old_write_word'][x] = bin_address+bin_write_data+bin_original_red
                    wc_attacks['write_address'][x] = bin_address
                    wc_attacks['write_red'][x] = bin_original_red
                    wc_attacks['write_ad_red'][x] = write_ADR_red
                    wc_attacks['write_red_with_ADR'][x] = new_write_red_with_ADR
                    wc_attacks['full_new_write_word'][x] = full_new_write_word

                    #the read side
                    wc_attacks['full_old_read_word'][x] = bin_address+wc_attacks['read_data'][x]
                    wc_attacks['read_red'][x] = chip.get_red(wc_attacks['read_data'][x])
                    bin_read_data = new_with_ADR_write_word ^ err_vec #the error is on the data and red
                    bin_read_red = chip.get_red(bin_read_data)
                    read_ADR_red = address_decoder.encode(chip.get_data(bin_read_data),bin_address)
                    coded_red_after_err = chip.encode(chip.get_data(bin_read_data))
                    new_red_after_err = read_ADR_red ^coded_red_after_err

                    wc_attacks['full_new_read_word'][x] = bin_address+bin_read_data
                    wc_attacks['new_read_red'][x] =  bin_read_red

                    wc_attacks['calculated_address_read_red'][x] = read_ADR_red
                    wc_attacks['calculated_data_read_red'][x] = coded_red_after_err
                    wc_attacks['calculated_total_red'][x] = new_red_after_err

                    wc_attacks['after_error_ADR_red'][x] = bin_read_red
                    wc_attacks['after_error_correct_red'][x] = new_red_after_err

                    # check success
                    flag = (new_red_after_err == bin_read_red)
                    wc_attacks['wc_new_detected'][x] = not flag
                    wc_result[str(flag)] += 1
                    bar.next()
            wc_attacks.to_csv(f'..\\results\\cpc {report.cpc_number}-' + "wc_new_XORED_csv.csv")
        except:
            print(f'problem with cpc{cpc}')


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