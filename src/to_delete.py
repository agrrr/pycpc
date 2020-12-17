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

#df = pd.DataFrame(np.random.randint(0,10, size=(1,8)))

def main():
    newlogs = datetime(2020, 7, 1)
    june_logs = datetime(2020, 8, 30)
    sort_by = [(['P(wc fault)', '#wc'], [False, False],
                10)]  # [('unique error vectors', False, 3), ('#wc', False, 3), ('P(wc fault)', False, 3), ('P(masking | wc fault)', True, 3)]
    # report_attacks = [None]*10

    for cpc in range(7, 11):
        try:
            df = pd.DataFrame(index=np.arange(1000000), columns=['cpc', 'write_data'])
            print(f'only cpc {cpc} start at {datetime.now()}')
            report = CPCReporter.CPCReporter(cpc=cpc)
            report.set_params(min_success_prob=0.01
                                , min_tries_global=4
                                , min_tries_specific=10
                                , below_margin=-3
                                , above_margin=2
                                , wd_consistent_threshold=0.5)

            report.set_sortby(sortby=sort_by)
            chip = report.cpc
            address_decoder = code.ADR(chip.k, chip.r)
            old_shifted_data = pd.read_csv(f'..\\results\\old\\all_shifted_attacks.csv')
            old_wc_data = pd.read_csv(f'..\\results\\old\\cpc {cpc}-wc_new_XORED_csv.csv',converters={'write_data': code.str2bitarray, 'err_vec': code.str2bitarray})
            df['cpc'] = cpc
            df['write_data'] = pd.DataFrame([random.randint(1, (2 ** chip.k) -1) for x in range(0, 1000000)])
            #df['write_data'] = pd.DataFrame(np.random.randint(1,((2**20) -1), size=(1000000,1),dtype=np.int256))
            df['write_data'] = df.apply(lambda x: code.int2bitarray(int(x.write_data), chip.k), axis=1)
            #old_shifted_data['original_address'] = old_shifted_data.apply(lambda x: int(x.original_address), axis=1)
            old_shifted_data = old_shifted_data[['original_address','address']]
            #old_wc_data['err_vec']=old_wc_data.apply(lambda x: x.write_data ^ x.read_data, axis=1)
            old_wc_data = old_wc_data[['err_vec']]
            #merge(df1, df2,on='key')
            old_expended_shift = expanding_df_to_size(old_shifted_data,1000000)[:1000000]
            old_extended_wc = expanding_df_to_size(old_wc_data,1000000)[:1000000]
            """taking only 1 mil for the merging by taking index<=mil"""
            #df = df.merge(old_expended_shift,how='outer')
            #df = df.merge(old_extended_wc, how='outer')
            df = df.join(old_expended_shift)
            df = df.join(old_extended_wc)
            del old_wc_data
            del old_shifted_data
            df['bin_original_address']= df.apply(lambda x: code.int2bitarray(int(x.original_address), 10), axis=1)
            df['bin_address'] = df.apply(lambda x: code.int2bitarray(int(x.address), 10), axis=1)
            df['adr_err_vec'] = df.apply(lambda x: (x.bin_original_address ^ x.bin_address), axis=1) #df['bin_original_address'] ^ df['bin_address']
            df['write_data_red'] = df.apply(lambda x: chip.encode(x.write_data), axis=1)
            df['write_ad_red'] = df.apply(lambda x: address_decoder.encode(x.write_data,x.bin_original_address), axis=1)
            df['write_total_red'] = df.apply(lambda x: (x.write_data_red ^ x.write_ad_red), axis=1)
            df['only_shift_read_ad_red'] = df.apply(lambda x: address_decoder.encode(x.write_data,x.bin_address), axis=1)
            df['only_shift_read_total_red'] = df.apply(lambda x: (x.write_data_red ^ x.only_shift_read_ad_red), axis=1) #df['write_data_red'] ^ df['only_shift-read_ad_red']
            df['only_shift_shift_detected'] = df['only_shift_read_total_red'] != df['write_total_red']
            df['write_DataRed'] = df['write_data'] + df['write_data_red']

            df['wc_read_DataRed'] = df.apply(lambda x: (x.write_DataRed ^ x.err_vec), axis=1)#df['write_DataRed'] ^ df['err_vec']
            df['wc_read_data'] = df.apply(lambda x: x.wc_read_DataRed[:chip.k], axis=1)
            df['wc_read_data_red'] = df.apply(lambda x: x.wc_read_DataRed[chip.k:], axis=1)
            df['wc_read_data_calculated_red'] = df.apply(lambda x: chip.encode(x.wc_read_data),axis=1)
            df['wc_old_detector'] = df['wc_read_data_red'] != df['wc_read_data_calculated_red']
            #new detector
            df['wc_new_read_ad_red'] = df.apply(lambda x: address_decoder.encode(x.wc_read_data,x.bin_original_address), axis=1)
            df['wc_new_read_total_red'] = df.apply(lambda x: (x.wc_read_data_red ^ x.wc_new_read_ad_red), axis=1)#df['wc_read_data_red'] ^ df['wc_new_read_ad_red']
            df['wc_new_read_total_calculated_red'] = df.apply(lambda x: (x.wc_new_read_ad_red ^ x.wc_read_data_calculated_red), axis=1)#df['wc_new_read_ad_red'] ^ df['wc_read_data_calculated_red']
            df['wc_new_AD_detector'] = df['wc_new_read_total_red']!=df['wc_new_read_total_calculated_red']
            #conbined address data & red error
            #making full new write word
            df['write_AdDataRed'] = df['bin_original_address'] + df['write_data'] + df['write_total_red']
            #making full new err_vec
            df['err_vec_AdDataRed'] = df['adr_err_vec'] + df['err_vec']
            df['read_AdDataRed']= df.apply(lambda x: (x.write_AdDataRed ^ x.err_vec_AdDataRed), axis=1)#df['write_AdDataRed'] ^ df['err_vec_AdDataRed']
            df['combined_read_bin_ad'] = df.apply(lambda x: x.read_AdDataRed[:10], axis=1)
            df['combined_read_data']=df.apply(lambda x: x.read_AdDataRed[10:10+chip.k], axis=1)
            df['combined_read_red'] = df.apply(lambda x: x.read_AdDataRed[10+chip.k:], axis=1)
            df['combined_good red'] = df['write_total_red']
            df['combined_read_calculated_ad_red']=df.apply(lambda x: address_decoder.encode(x.combined_read_data,
                                                                                            x.combined_read_bin_ad), axis=1)
            df['combined_read_calculated_data_red'] = df.apply(lambda x: chip.encode(x.combined_read_data),axis=1)
            df['combined_calculated_total_red'] = df.apply(lambda x: (x.combined_read_calculated_ad_red ^ x.combined_read_calculated_data_red), axis=1)#df['combined_read_calculated_ad_red'] ^ df['combined_read_calculated_data_red']
            df['combined_detector'] = df['combined_calculated_total_red']!=df['combined_read_red']

            #joining address and original address info

            #df = pd.concat([df,df1], ignore_index=True)
            df.to_csv(f'..\\results\\new all data for cpc {cpc}' + " random_data.csv")
            print(f'Ending time of cpc {cpc} is--> {datetime.now()}')
        except:
            print(f'error in cpc{cpc}')
        #the correct way for running a func
        #df['address'] = df.apply(lambda x: code.int2bitarray(x.address, 10), axis=1)
        #df['random']=df.apply(lambda x: random.randint(1, 10),axis=1)
        #df2 = pd.DataFrame(random.randint(0,1000000, size=(1000000,1)))
        #loading data from general file
        #make new df with good params.
        #drop duplicates equals to 0(zeros)
        #shift data treating
            #add -> original address | address | read_data | is shifted=True
        #wc data treating
            #add ->err_vec | address=original address | read_data = write^err_vec| wc fault = True
        #concating all data to one df and save as cpc data attacks
        del df
        print('end')
        print('end')

def expanding_df_to_size(df1:pd.DataFrame,size:int) -> pd.DataFrame:
    df_len=len(df1.index)
    skip=False
    while(not skip):
        df1 = pd.concat([df1,df1], ignore_index=True)
        if len(df1.index)>size:
            skip=True
    return df1


# report.attacks[report.attacks['is shifted']==True][['address','index','shift','addr minus idx','Class']]


if __name__ == '__main__':
    main()