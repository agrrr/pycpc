import pandas as pd, numpy as np
import src.attacks_filters as filters

class Classificator:
    def __init__(self, attacks, paramkeys, below_margin=-3, above_margin=5, wd_consistent_threshold=0.8, min_tries=3):
        self.attacks = attacks
        self.min_tries = min_tries
        self.paramkeys = paramkeys
        self.tries = attacks['try_id'].drop_duplicates()
        self.tags = set()
        
        if(below_margin > 0):
            raise ValueError('below_margin should be non-positive!!!')
        self.below_margin = below_margin
        self.above_margin = above_margin
        self.wd_consistent_threshold = wd_consistent_threshold
        
        self.attacks['addr minus idx'] = self.attacks['address'] - self.attacks['index']
        self._tag_errors()
        self._fault_relations()
        self._validate_attacks()
        self._tag_faults()
        self._tag_writecorrupts()
        self._final_classification()

    def _tag_errors(self):
        self.attacks['detection mismatch'] = self.attacks['detected by HW'] != self.attacks['detected by SW']
        self.attacks['faulty'] = self.attacks['#bitflips'] != 0
        self.attacks['write skip'] = (self.attacks['read_data'] == self.attacks['mem_before'])
        self._tag_writeshifts()

    def _tag_writeshifts(self):
        shifted = pd.merge(
            self.attacks[self.attacks['faulty']][['try_id', 'read_data', 'address']], 
            self.attacks[['try_id', 'write_data', 'address']].rename(columns={'address':'original_address'}),
            left_on=['try_id', 'read_data'], right_on=['try_id', 'write_data'])#shifted_address
        shifted['shift'] = shifted['original_address'] - shifted['address']
        shifted['is shifted'] = True
        self.attacks = pd.merge(self.attacks, shifted[['try_id', 'address','original_address', 'shift', 'is shifted']], on=['try_id', 'address'], how='outer')
        self.attacks['shift'].fillna(np.inf, inplace=True)
        self.attacks['is shifted'].fillna(False, inplace=True)

    def _fault_relations(self):
        self.attacks['is first'] = False
        idxs = self.attacks[self.attacks['faulty']].groupby('try_id')['address'].nsmallest(n=1).index.get_level_values(1)
        self.attacks.loc[idxs, 'is first'] = True
        self.attacks['Fault Relation'] = 'Unrelated'

        self.attacks.loc[
            ((self.attacks['addr minus idx'] < self.above_margin) & (self.attacks['addr minus idx'] > self.below_margin))
            & self.attacks['is first']
            , 'Fault Relation'
        ] = 'Hit'

        on_attacks = self.attacks[self.attacks['Fault Relation'] == 'Hit']
        self.attacks = pd.merge(self.attacks, on_attacks[['try_id', 'address']].rename(columns={'address':'on_address'}), on='try_id', how='left')
        self.attacks.loc[self.attacks['address'] > self.attacks['on_address'], 'Fault Relation'] = 'After'
        self.attacks.loc[self.attacks['address'] < self.attacks['on_address'], 'Fault Relation'] = 'Before'
        self.attacks.drop(columns=['on_address'])

    def _validate_attacks(self):
        consistent_attacks = self.attacks[(self.attacks['write_data_consistent_normalized'] > self.wd_consistent_threshold)
                                            & self.attacks['mem_before_consistent_data']]
        self.valid_attacks = filters.filter_not_tested_attacks(consistent_attacks, paramkeys=self.paramkeys, min_tries=self.min_tries)
    
    def _tag_faults(self):
        self.valid_attacks['wc candidate'] = False
        self.valid_attacks.loc[self.valid_attacks['faulty'] 
                        & (self.valid_attacks['write skip'] == False)
                        & (self.valid_attacks['is shifted'] == False)
                        ,'wc candidate'] = True

    def _tag_writecorrupts(self):
        self.valid_attacks['wc fault'] = False        
        self.valid_attacks.loc[(self.valid_attacks['Fault Relation'] == 'Hit') & self.valid_attacks['wc candidate']
                                    , 'wc fault'] = True
                                    
    def _final_classification(self):
        self.valid_attacks['Class'] = 'unclassified'
        self.valid_attacks.loc[self.valid_attacks['faulty'] == False, 'Class'] = 'No fault'
        self.valid_attacks.loc[self.valid_attacks['faulty'] == True, 'Class'] = 'Unclassified fault'

        self.valid_attacks.loc[self.valid_attacks['write skip'], 'Class'] = 'Write skip'
        self.valid_attacks.loc[self.valid_attacks['is shifted'] & (self.valid_attacks['shift']>0), 'Class'] = 'Address shift (positive)'
        self.valid_attacks.loc[self.valid_attacks['is shifted'] & (self.valid_attacks['shift']<0), 'Class'] = 'Address shift (negative)'
        self.valid_attacks.loc[self.valid_attacks['wc fault'], 'Class'] = 'Write corrupt'

    def get_valid_attacks(self):
        return self.valid_attacks

    def get_write_corrupt_attacks(self):
        return self.valid_attacks[self.valid_attacks['wc fault']]
