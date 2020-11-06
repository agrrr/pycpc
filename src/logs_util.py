import os
import pickle
import re
from bitarray import bitarray, frozenbitarray
from progress.bar import Bar, IncrementalBar
import pandas as pd
from datetime import datetime
from pathlib import Path

from src.pacific import Pacific
import src.attacks_filters as filters

import numpy as np

class ParamKeysManager:
    @staticmethod
    def parse_keys(logfile):
        raise NotImplementedError()

    @staticmethod
    def parse_all_keys(logdir):
        raise NotImplementedError()
    
    @staticmethod
    def get_keys():
        return ['cpc_vddr', 'vddcore', 'pulse-width', 'height', 'vddio', 'delay', 'cpc', 'cpc_vdd']
    
    @staticmethod
    def get_keys_intersection(x):
        return list(set(ParamKeysManager.get_keys()).intersection(x))
    """
    with open(logfile, 'r') as file:
        _ = file.readline() # _="Original data:"
        write_data_lst = file.readline().split(',')
        write_data_lst = [frozenbitarray(wd.strip()[10:-1]) for wd in write_data_lst]
        _ = file.readline() # _="Original data:"
        mem_before_write_logfile = re.split(',|, ', file.readline())
        mem_before_write_logfile = [frozenbitarray(mbw.strip()[10:-1]) for mbw in mem_before_write_logfile]

        attack_params_keys = trimall(file.readline()).split(',,')[0].split(',')
        try:
            with open(filename_param_keys, 'r+t') as f:
                saved_keys = [k.strip() for k in f.readlines() if k.strip() != '']
        except:
            saved_keys = []

        with open(filename_param_keys, 'wt') as f:
            new_keys = set(saved_keys).union(set(attack_params_keys))
            new_keys.discard('cpc_mem')
            new_keys.add('cpc')
            f.write('\n'.join(new_keys))
    
    

    def fetch_paramkeys():
        with open(filename_param_keys, 'rt') as f:
            keys = [k.strip() for k in f.readlines() if k.strip() != '']
        paramkeys = list(set(keys)) # not really need the list(set()) here, but whatever and why not
        if 'index' in paramkeys: paramkeys.remove('index')
        if 'D0_blank' in paramkeys: paramkeys.remove('D0_blank')
        if 'D_inc_blank' in paramkeys: paramkeys.remove('D_inc_blank')
        if 'D0_attack' in paramkeys: paramkeys.remove('D0_attack')
        if 'D_inc_attack' in paramkeys: paramkeys.remove('D_inc_attack')
        if 'cycles' in paramkeys: paramkeys.remove('cycles')
        if 'pulse-freq' in paramkeys: paramkeys.remove('pulse-freq')
        return paramkeys
    """

class Logline:
    def validate_line(self):
        #### some validations: ###
        N = len(self.read_data_lst) # word count
        try:
            if not (all(int(l[:10], 2) == i for i, l in enumerate(self.line[1]))
                and (len(self.line[2]) > 0 or all(int(l[:10], 2) == i for i, l in enumerate(self.line[2])))):
                # validate adrresses are ok
                self.drop_reason = 'addresses error'
                self.is_dropped = True
                return

            if self.attack_params['index'] > N: # attack out of readed data
                self.drop_reason = 'index > N'
                self.is_dropped = True
                return
                
            # padding mem_before, so if it shorter it will be OK:
            if len(self.mem_before_given) != N:
                self.drop_reason = 'mem_before length error'
                self.is_dropped = True
                return

            # validate n:
            if not all(len(rd) == self.cpc.n for rd in self.read_data_lst):
                self.drop_reason = 'n!= cpc.n'
                self.is_dropped = True
                return
            
            if len(self.read_data_lst) != len(self.write_data_given):
                self.drop_reason = 'len(read_data) != len(write_data)'
                self.is_dropped = True
                return
        except Exception as identifier:
            self.drop_reason = identifier
            self.is_dropped = True
            return   
        self.is_dropped = False

    def __init__(self, line, attack_params_keys, write_data_given, logfile_hash, idx):
        self.write_data_given = write_data_given
        self.try_id = logfile_hash + idx

        self.line = [[it.strip() for it in item.split(',')] for item in re.split(',,|, ,', line)]
        attack_params_values = [param for param in self.line[0]]
        self.attack_params = dict(zip(attack_params_keys, attack_params_values))
    
        self.new_log_format = 'D0_blank' in self.attack_params # boolean
        if self.new_log_format:
            self.D0_mem_before =  frozenbitarray(bin(int(self.attack_params.pop('D0_blank')))[2:])
            self.D_inc_mem_before = frozenbitarray(bin(int(self.attack_params.pop('D_inc_blank')))[2:])
            self.D0_write =  frozenbitarray(bin(int(self.attack_params.pop('D0_attack')))[2:])
            self.D_inc_write = frozenbitarray(bin(int(self.attack_params.pop('D_inc_attack')))[2:])

        self.attack_params = dict([a, float(x)] for a, x in self.attack_params.items())
        self.attack_params['cpc'] = int(self.attack_params.pop('cpc_mem'))
        self.cpc_num = self.attack_params['cpc']
        self.cpc = Pacific.cpc[self.cpc_num]

        # rerepresent data:
        try:
            self.mem_before_given = [frozenbitarray(data.strip()[10:-1]) for data in self.line[2]]
            self.read_data_lst = [frozenbitarray(data.strip()[10:-1]) for data in self.line[1]]
            
            self.mem_before = self.mem_before_given 
            self.write_data = self.write_data_given 
            if self.new_log_format:
                self.mem_before = filters.generate_mem_content(self.cpc, self.D0_mem_before, self.D_inc_mem_before, 100) if self.new_log_format else self.mem_before_given
                self.write_data = filters.generate_mem_content(self.cpc, self.D0_write, self.D_inc_write, 100) if self.new_log_format else self.write_data_given
        
        except Exception as identifier:
            self.drop_reason = identifier
            self.is_dropped = True

        self.validate_line()

        if not self.is_dropped:
            self.errvecs = [rd ^ wd for rd, wd in zip(self.read_data_lst, self.write_data_given)] 
        
    
    def to_dict(self):
        dict2ret = self.attack_params
        dict2ret['address'] = range(len(self.read_data_lst))
        dict2ret['read_data'] = [barr.to01() for barr in self.read_data_lst] 
        dict2ret['detected by HW'] = [int(data[-1]) for data in self.line[1]]
        dict2ret['detected by SW'] = [self.cpc.is_faulty(rd) for rd in self.read_data_lst]
        dict2ret['err_vec'] = [e.to01() for e in self.errvecs]
        dict2ret['#bitflips'] = [err_vec.count(1) for err_vec in self.errvecs]
        dict2ret['#bitflips data'] = [err_vec[:self.cpc.k].count(1) for err_vec in self.errvecs]
        dict2ret['#bitflips redundancy'] = [err_vec[self.cpc.k:].count(1) for err_vec in self.errvecs]
        dict2ret['try_id'] = self.try_id
        
        dict2ret['mem_before'] = self.mem_before_given

        dict2ret['write_data'] = self.write_data

        max_const_data = int(dict2ret['index'])
        dict2ret['write_data_consistent_count'] = sum(a == b for a,b in zip(self.write_data[:max_const_data], self.read_data_lst[:max_const_data]))
        dict2ret['write_data_consistent_normalized'] = dict2ret['write_data_consistent_count'] / max_const_data if max_const_data > 0 else np.inf
        dict2ret['write_data_consistent_tuple'] = frozenbitarray(a == b for a,b in zip(self.write_data[:max_const_data], self.read_data_lst[:max_const_data])).to01()

        dict2ret['mem_before_consistent_data'] = [a[:self.cpc.k] == b[:self.cpc.k] for a, b in zip(self.mem_before, self.mem_before_given)]
        dict2ret['line_mem_before_consistent_data'] = any(dict2ret['mem_before_consistent_data'])
        dict2ret['mem_before_consistent_red'] = [a[-self.cpc.r:] == b[-self.cpc.r:] for a, b in zip(self.mem_before, self.mem_before_given)]
        dict2ret['line_mem_before_consistent_red'] = any(dict2ret['mem_before_consistent_red'])
        
        return dict2ret

    def to_frame(self):
        if self.is_dropped:
            raise Exception('line dropped! don\'t you understand?')
        return pd.DataFrame(self.to_dict())

class LogFile:
    def __init__(self, filename):
        self.filename = filename
        self.logfile_hash = hash(self.filename)
        with open(self.filename, 'r') as file:
            _ = file.readline() # _="Original data:"
            write_data_lst = file.readline().split(',')
            write_data_lst = [frozenbitarray(wd.strip()[10:-1]) for wd in write_data_lst]
            _ = file.readline() # _="Original data:"
            mem_before_write_logfile = re.split(',|, ', file.readline())
            mem_before_write_logfile = [frozenbitarray(mbw.strip()[10:-1]) for mbw in mem_before_write_logfile]

            attack_params_keys = file.readline()
            attack_params_keys = ''.join(attack_params_keys.split())
            attack_params_keys = attack_params_keys.split(',,')[0].split(',')

            lines = file.readlines()
            if(len(lines) < 1):
                self.Empty = True
                self.df = pd.DataFrame()
                #print(f'\nempty file: {self.filename}')
                return
            #print(f'\n{len(lines)} lines in {self.filename}')
            dfs = []
            drop_count = 0
            for i, line in enumerate(lines):
                line = Logline(line, attack_params_keys, write_data_lst, self.logfile_hash, i)
                if line.is_dropped:
                    #print(f'line {i} dropped. msg: {line.drop_reason}')
                    drop_count += 1
                    continue
                dfs.append(line.to_frame())
            self.df = pd.DataFrame().append(dfs)
            self.Empty = False
            self.lines = len(lines)
            self.dropped_lines = drop_count
    
    def to_frame(self):
        return self.df
        
    def to_file(self, pickle_filename):
        with open(pickle_filename, 'wb') as f:
            pickle.dump(self.to_frame(), f)
    
    def __str__(self):
        if self.Empty:
            return f'{self.filename.name}: empty file'
        return f'{self.filename.name}: {self.lines-self.dropped_lines}/{self.lines}'

class ProjectPaths:
        wd = Path(__file__).parent.parent
        logs_dir = wd / 'logs/attack_logs/logs_6022x'
        pickles_dir = wd / 'pickles'
        html_dir = wd / 'htmls'
        pickles_dir.mkdir(exist_ok=True)
        html_dir.mkdir(exist_ok=True)
        filename_param_keys = pickles_dir /'paramkeys.txt'

class LogsParser:
    @staticmethod
    def logs2parse():
        logs = [file.stem for file in ProjectPaths.logs_dir.iterdir()]
        pickles = [file.stem for file in ProjectPaths.pickles_dir.iterdir()]
        files = set(logs).difference(pickles)
        files = [Path(file) for file in files]
        return files
    
    @staticmethod
    def parse():
        files = LogsParser.logs2parse()
        if len(files) == 0:
            print('Already Parsed')
            return
        with Bar("Parsing logs:", max=len(files)) as bar:
            for file in files:
                try:
                    log_filename = ProjectPaths.logs_dir / (file.name + '.text')
                    pickle_filename = ProjectPaths.pickles_dir / (file.name + '.pickle')
                    log = LogFile(log_filename)
                    log.to_file(pickle_filename)
                    #print(log)
                    bar.next()
                except:
                    continue
        print('Parsed succsessfuly!')


class DataFetcher:
    @staticmethod
    def logname2datetime(filename):
        try:
            d = re.split('\.| ', filename.stem)[-1]
            return  datetime.strptime(d, '%Y%m%d_%H%M%S')
        except:
            raise Exception('invalid datetime in file name "{}"'.format(filename))

    def __init__(self, cpc=None, maxfiles=None, debug=False, from_datetime=None, to_datetime=None, parse_pickles=True):
        if parse_pickles:
            LogsParser().parse()
        self.pickle_files = list(ProjectPaths.pickles_dir.iterdir())
        self.cpc = cpc
        s = 'mem'
        if cpc is not None:
            s += str(cpc) + '_'
        self.pickle_files = [f for f in self.pickle_files if s in str(f)]

        if from_datetime is not None:
            self.pickle_files = [pickle_file for pickle_file in self.pickle_files if from_datetime < DataFetcher.logname2datetime(pickle_file)]
        if to_datetime is not None:
            self.pickle_files = [pickle_file for pickle_file in self.pickle_files if DataFetcher.logname2datetime(pickle_file) < to_datetime]
        if maxfiles is not None and len(self.pickle_files) > maxfiles:
            self.pickle_files.sort(key = lambda x: DataFetcher.logname2datetime(x), reverse=True) # Take the newest
            self.pickle_files = self.pickle_files[:maxfiles]
        if len(self.pickle_files) == 0:
            print('note: loading 0 files')
            return
        if debug:
            print('Loading files:')
            print(self.pickle_files)

    def get_frame(self):
        if self.pickle_files is None or len(self.pickle_files) == 0:
            print('No file Loaded')
            return None
            #pickle_files = list_pickles2read(cpc=cpc, maxfiles=maxfiles, debug=debug, from_datetime=from_datetime, to_datetime=to_datetime)
        self.attacks = pd.DataFrame()
        with IncrementalBar('Loading files:', max=len(self.pickle_files)) as bar:
            for filename in self.pickle_files:
                try:
                    with open(filename, 'rb') as f:
                        new_attaks = pickle.load(f)
                    self.attacks = self.attacks.append(new_attaks)
                    bar.next()
                except:
                    continue
        self.attacks.reset_index(inplace=True, drop=True)
        
        if self.attacks.empty:
            print('empty attacks...')
            return None

        self.attacks['err_vec'] = self.attacks['err_vec'].apply(lambda x: frozenbitarray(x))
        self.attacks['write_data'] = self.attacks['write_data'].apply(lambda x: frozenbitarray(x))
        self.attacks['read_data'] = self.attacks['read_data'].apply(lambda x: frozenbitarray(x))
        self.attacks['mem_before'] = self.attacks['mem_before'].apply(lambda x: frozenbitarray(x)) # TODO move to parse

        self.set_defaults()

        print(f'Loaded {len(self.attacks)} attacks in cpc{self.cpc} from {len(self.pickle_files)} files')
        return self.attacks


    def set_defaults(self):
        defaults = {'vddio': 0,
                    'pulse-width': 3.4,
                    'delay': 0,
                    'cpc_vdd': 0,
                    'vddcore': 0,
                    'height': 0,
                    'cpc': 0,
                    'cpc_vddr': 0}
        self.attacks = self.attacks.fillna(defaults)