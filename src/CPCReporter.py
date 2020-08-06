import statistics as stats
import attacks_filters as filters
from logs_util import DataFetcher, ParamKeysManager, ProjectPaths
import graph_util
from pacific import Pacific
from HTML_Report import HTML_Report
import help_strings as strings
import theoretical_stats
import pandas as pd
from itertools import combinations
import datetime
from pathlib import Path

from Classificator import Classificator

class CPCReporter:
    def __init__(self, cpc=None, name='Report for CPC{cpc}', debug=False):
        self.cpc_number = cpc
        self.cpc = Pacific.cpc[cpc]
        self.name = name.format(cpc=cpc)
        self.is_fetched = False
        self.debug = debug
        self.set_params()
        self.set_sortby()

    def set_params(self, max_files_in_debug=5, min_success_prob=0, min_tries_global=1, min_tries_specific=10, below_margin=-3, above_margin=5, wd_consistent_threshold=0.8):
        self.max_files_in_debug = max_files_in_debug
        self.min_success_prob = min_success_prob
        self.min_tries_specific = min_tries_specific
        self.min_tries_global = min_tries_global
        self.below_margin = below_margin
        self.above_margin = above_margin
        self.wd_consistent_threshold = wd_consistent_threshold
    
    def set_sortby(self, sortby=[('P(wc fault)', False, 5)]):
        self.sortby = sortby

    def plots_1d_success_probs_by_paramkeys_vdd(self, success_probs, paramkeys, vdd):
        # Single-Variable plots
        _1d_plots, axs = graph_util.setup_subplots(amount=len(paramkeys))
        for param, ax in zip(paramkeys, axs):
            dist = stats.marginal_distribution_of_multiindex_multivar(df=success_probs, x=param)
            graph_util.plot_stem(dist, show=False, ax=ax, ylabel='P(wc fault | {prm}, vdd={vdd})'.format(prm=param, vdd=vdd))
        return _1d_plots


    def plots_2d_success_probs_by_paramkeys_vdd(self, success_probs, paramkeys, vdd):
        # 2-Variable heatmaps
        #NOTE: amount of plots is (len(paramkeys) choose 2) = L(L-1)/2
        _2d_plots, axs = graph_util.setup_subplots(amount = len(paramkeys)*(len(paramkeys)-1)/2)
        for (param1, param2), ax in zip(combinations(paramkeys, r=2), axs):
            dist = stats.marginal_distribution_2d_of_multiindex_multivar(df=success_probs, x=param1, y=param2)
            graph_util.plot_heatmap_prob(dist, show=False, ax=ax, title='P(wc fault | {p1}, {p2}, vdd={vdd})'.format(p1=param1, p2=param2, vdd=vdd))
        return _2d_plots


    def plot_all_statistics(self, attacks: pd.DataFrame, fattacks: pd.DataFrame, html_out: HTML_Report, colorfulness=False):
        html_out.add_text(strings.index_address_heatmap_abstract)
        fig, axs = graph_util.setup_subplots(4)
        axs = iter(axs)
        graph_util.plot_heatmap_prob(stats.indexXaddr_prob(attacks, fattacks), vmax=None, xlabel='index', ylabel='address', title='P(write-corrupt fault | address, index)', ax=next(axs))
        graph_util.plot_heatmap_prob(stats.indexXaddr_prob(attacks, attacks[attacks['is first']]), vmax=None, xlabel='index', ylabel='address', title='P(is-first fault | address, index)', ax=next(axs))
        graph_util.plot_stem(stats.address_prob(attacks, fattacks), title='P(write-corrupt fault | address)', xlabel='address', ylabel='P', ax=next(axs))
        graph_util.plot_stem(stats.address_minus_index_hist(fattacks), xlabel='address - index', ylabel='occurrences', title='address minus index histogram', ax = next(axs))
        html_out.add_fig(fig)
        
        if True:
            html_out.add_header('Colorfulness of the test data', 4) ####################
            html_out.add_text(strings.colorfulness_abstract)
            fig, axs = graph_util.setup_subplots(2)
            axs = iter(axs)
            graph_util.plot_heatmap_prob(stats.P1_given_bitloc_and_y(attacks['mem_before'], attacks['address']), cmap='RdYlGn', title='P(memory before attack = 1)', xlabel='bit', ax=next(axs))
            graph_util.plot_heatmap_prob(stats.P1_given_bitloc_and_y(attacks['write_data'], attacks['address']), cmap='RdYlGn', title='P(data writen during the attack = 1)', xlabel='bit', ax=next(axs))
            
            html_out.add_fig(fig)
        
            html_out.add_text(strings.index_hist_abstract)
            fig, axs = graph_util.setup_subplots(1)
            axs = iter(axs)
            graph_util.plot_stem(stats.index_hist(attacks), title='index histogram', xlabel='index', ylabel='occurrences', ax=next(axs))
            html_out.add_fig(fig)

        html_out.add_header('Fault type statistics', 4) ####################
        html_out.add_df(stats.faults_stats(attacks))

        html_out.add_header('Bit flip probability', 4) ####################
        html_out.add_text('P(flip | wc fault, mem bit, write bit) = P(read &ne; write | wc fault, mem bit, write bit) table')
        html_out.add_df(stats.bit_flip_prob(fattacks))
        html_out.add_line_break()
        html_out.add_df(stats.bit_read_write_summary(fattacks))
        fig, axs = graph_util.setup_subplots(2)
        axs = iter(axs)
        bitflip_loc_prob = stats.P1_given_bitloc(fattacks['err_vec'])
        graph_util.plot_bar_prob_by_bit_pos(bitflip_loc_prob, self.cpc.r, title='P(flip in bit i | wc fault, i)', ylabel='P', ax=next(axs))
        graph_util.plot_heatmap_prob(stats.P1_given_bitloc_and_y(fattacks['err_vec'], fattacks['address'], range_y=range(100)), title='P(flip in bit i | wc fault, i, address) heatmap', xlabel='bit', ax=next(axs))
        html_out.add_fig(fig)

        html_out.add_header('How errors behave?', 4) ####################
        html_out.add_text(strings.error_behave_abstract)
        fig, axs = graph_util.setup_subplots(1)
        axs = iter(axs)
        graph_util.plot_stem(stats.num_bit_flips_dist(fattacks), title='P(#bitflips | wc fault)', xlabel='#bitflips', ylabel='P', ax=next(axs))
        html_out.add_fig(fig)
        
        html_out.add_text(strings.heatmap_bitflips_address_abstract)
        fig, axs = graph_util.setup_subplots(1)
        axs = iter(axs)
        graph_util.plot_heatmap_prob(stats.num_bit_flips_dist_by_param(fattacks, 'address', self.cpc.n, range_param=range(100)), title='P(#bitflips | wc fault, address)', xlabel='address', ax=next(axs))
        html_out.add_fig(fig)

        html_out.add_text(strings.numbitflips_bit_heatmap_abstract)
        fig, axs = graph_util.setup_subplots(2)
        axs = iter(axs)
        real = stats.P1_given_bitloc_and_y(fattacks['err_vec'], fattacks['#bitflips'], range_y=range(self.cpc.n))
        theoretical = theoretical_stats.bit_i_flipped_given_i_numbitflips(self.cpc.n)
        graph_util.plot_heatmap_prob(real, title='P(bit i flipped | wc fault, i, #bitflips)', xlabel='bit', ax=next(axs))
        graph_util.plot_heatmap_prob(real - theoretical, vmin=-1, vmax=1, cmap='PuOr', title='Difference between empirical and theoretical', xlabel='bit', ax=next(axs))
        html_out.add_fig(fig)


    def all_param_sets_report(self, html_out: HTML_Report):
        prob2plotby = 'P(wc fault)' # or 'P(masking | wc fault) by SW' 'P(wc fault)'
        html_out.add_header('Finding good attacks', 2)
        html_out.add_text(strings.general_report_abstract)
        if(len(self.fattacks) == 0):
            html_out.add_header('No wc faults found', 2)
            return
        # TODO: We assume all vdd params are equal to one another at any given point.
        vdd_params = [param for param in self.paramkeys if 'vdd' in param and 'vddio' not in param]
        vdd_vals = self.attacks[vdd_params].drop_duplicates().T.drop_duplicates()
        if len(vdd_vals) != 1:
            raise Exception( 'not all vdds are equal!' + str(vdd_vals))
        
        success_probs = stats.parmaset_describe_attacks(self.attacks, self.fattacks, self.paramkeys)[prob2plotby].to_frame()

        index_count = success_probs.index.to_frame().reset_index(drop=True).apply(pd.Series.nunique)
        var_params = index_count[index_count>1].index.to_list()

        var_vdd_params = [param for param in vdd_params if param in var_params]

        if len(var_vdd_params) != 0:
            # Output invalid attacks %
            html_out.add_header('Probability of invalid attack by VDD', 3) ####################
            vdd_param = var_vdd_params[0]
            
            all_attacks = self.classificator.attacks
            keep_prob = self.attacks[['try_id', vdd_param]].drop_duplicates().groupby(vdd_param).size() / all_attacks[['try_id', vdd_param]].drop_duplicates().groupby(vdd_param).size()
            keep_prob.index.name = 'vdd'
            keep_prob.name = 'P(valid | vdd)'
            html_out.add_df(keep_prob.to_frame())
            html_out.add_header('Probability of write-corrupt faults by VDD', 3) ####################
            html_out.add_text(strings.general_report_vdd)
            # First we show intereseting probabilities by vdd
            dist = stats.marginal_distribution_of_multiindex_multivar(success_probs, vdd_param)
            fig = graph_util.plot_stem(dist, show=False, ylabel='P(write-corrupt | vdd)').get_figure()
            html_out.add_fig(fig)
        
        html_out.add_text(strings.general_report_foreach_vdd)
        # TODO: maybe this is not the best way to iterate over the values
        for vdd in vdd_vals.values[0]:
            
            html_out.add_header(f'Report for vdd={vdd}v', 3)

            #TODO: vdd_vals.index might contain many values.
            vdd_success_probs = success_probs.xs(vdd, level=vdd_vals.index)
            
            index_count = vdd_success_probs.index.to_frame().reset_index(drop=True).apply(pd.Series.nunique)
            parms2plot_with = index_count[index_count>1].index.to_list()
            parms2plot_with = list(set(parms2plot_with).difference(vdd_params))

            if(len(parms2plot_with) < 1):
                # TODO: If there is no paramkeys to plot with it might be a bug elsewhere and we should check this case.
                print(f'GENRAL REPORT - vdd={vdd} had no params to plot with!')
                continue

            _1d_plots = self.plots_1d_success_probs_by_paramkeys_vdd(success_probs=vdd_success_probs, paramkeys=parms2plot_with, vdd=vdd)
            html_out.add_header(f'P(write-corrupt | parameter)', 4)
            html_out.add_fig(_1d_plots)

            if(len(parms2plot_with) > 1):
                _2d_plots = self.plots_2d_success_probs_by_paramkeys_vdd(success_probs=vdd_success_probs, paramkeys=parms2plot_with, vdd=vdd)
                html_out.add_header(f'P(write-corrupt | parameter1, parameter2) heatmaps', 4)
                html_out.add_fig(_2d_plots)

            # Osnat requirements:
            html_out.add_header(f'P(#bitflips | wc fault, parameter) heatmaps', 4)
            fig, axs = graph_util.setup_subplots(len(parms2plot_with))
            for ax, param in zip(axs, parms2plot_with):
                graph_util.plot_heatmap_prob(stats.num_bit_flips_dist_by_param(self.fattacks, param, self.cpc.n), title=f'P(#bitflips | wc fault, {param}, vdd={vdd}) distribution', xlabel=param, ax=ax)
            html_out.add_fig(fig)
            
        html_out.add_header('Statistics across all attacks', 3)
        html_out.add_text(strings.general_report_statistics)
        self.plot_all_statistics(attacks=self.attacks, fattacks=self.fattacks, html_out=html_out)



    def specific_attack_report(self, param_set, html_out: HTML_Report, number):
        """
        report for a specific param_set.
        NOTE: all the analyses done are "given write-corrupt"
        """
        html_out.add_header(f'Specific attack report #{number}', 3)
        html_out.add_df(param_set)
        print(param_set)

        param_set = pd.DataFrame(index=param_set.index).reset_index(drop=False)
        fattacks_set = filters.filter_param_set(self.fattacks, param_set)
        attacks_set = filters.filter_param_set(self.attacks, param_set)
        
        self.plot_all_statistics(attacks=attacks_set, fattacks=fattacks_set, html_out=html_out, colorfulness=True)



    def report_specifics(self, html_out: HTML_Report, sortby: list, max_specifics = 5, min_success_prob=0, min_tries=3):
        """
        :sortby param: list of (by, acs, n) tuples. the func will take the first n largest / smallest in the `by` column
        """
        attacks_types = stats.parmaset_describe_attacks(self.attacks, self.fattacks, self.paramkeys)
        attacks_types = attacks_types[attacks_types['tries'] >= min_tries]
        attacks_types = attacks_types[attacks_types['P(wc fault)'] >= min_success_prob]
        attacks_types_new = pd.DataFrame()
        for df in [attacks_types.sort_values(by=by, ascending=asc).head(n) for by, asc, n in sortby]:
            attacks_types_new = attacks_types_new.append(df)
        attacks_types = graph_util.sort_multindex(attacks_types_new.drop_duplicates())

        html_out.add_header('Reports for specific attacks', 2)
        html_out.add_text(strings.specific_report_abstract.format(r=self.cpc.r))
        attacks_types.columns = pd.MultiIndex.from_tuples(k if isinstance(k, tuple) else (k, '') for k in attacks_types.columns)
        # ^ add tuples in columns where there is only one index, than create multiIndex out of it
        html_out.add_df(attacks_types.head(max(20, 3 * max_specifics)))

        param_sets = attacks_types.head(max_specifics)
        for i in range(len(param_sets)):
            paramset = param_sets.iloc[i:i+1] # df and not Series
            self.specific_attack_report(paramset, html_out=html_out, number=i+1)


    def fetch_files(self, from_datetime=None, to_datetime=None, max_files=None, parse_pickles=True):
        self.data_fethcer = DataFetcher(cpc=self.cpc_number, maxfiles=max_files, from_datetime=from_datetime, to_datetime=to_datetime, parse_pickles=parse_pickles)
        self.attacks = self.data_fethcer.get_frame()
        if self.attacks is None:
            raise Exception('attacks is None.')
        self.paramkeys = ParamKeysManager.get_keys_intersection(self.attacks.columns)
        
        self.classificator = Classificator(self.attacks, self.paramkeys,
                                           below_margin=self.below_margin,
                                           above_margin=self.above_margin, 
                                           wd_consistent_threshold=self.wd_consistent_threshold,
                                           min_tries=self.min_tries_global)
        self.attacks = self.classificator.get_valid_attacks()
        self.fattacks = self.classificator.get_write_corrupt_attacks()
        if len(self.attacks) == 0:
            raise Exception(f'Not enough attacks on cpc{self.cpc_number}')
        
        if len(self.fattacks) == 0:
            raise Exception(f'Not enough write corrupt attacks on cpc{self.cpc_number}')
       
        self.is_fetched = True
    
    def generate_header_and_footer(self, html_out):
        logolink = 'https://i.ibb.co/8Y38XCt/logo.png'
        html_out.add_img(logolink)
        timestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_out.add_footer(f'Report created at {timestr} using {len(self.data_fethcer.pickle_files)} log files and {len(self.attacks)} attacks')
        html_out.add_header(f'Fault Injection on Memory Array and Countermeasures Project', 1)
        html_out.add_text(strings.report_abstract)
        html_out.add_header(f'Attack report for CPC {self.cpc_number}', 1)
        html_out.add_text(strings.report_cpc.format(cpc=self.cpc_number, codestr=str(self.cpc)))

    def print_debug_footer(self, html_out):
        html_out.add_text('Logfiles used to create this report:')
        for pickle in self.pickle_files:
            html_out.add_text(Path(pickle).name)

    def generate_report(self, general_report=False, specifics_report=0):
        if not self.is_fetched:
            self.fetch_files(max_files = self.max_files_in_debug if self.debug else None)
        print(f'Generating report for CPC {self.cpc_number}:')
        print(f'general_report={general_report}, specifics_report={specifics_report}')
        
        with HTML_Report(self.name) as html_out:
            self.generate_header_and_footer(html_out)
            if general_report:
                self.all_param_sets_report(html_out)
            if specifics_report != 0:
                self.report_specifics(html_out, sortby=self.sortby, max_specifics=specifics_report, min_success_prob=self.min_success_prob, min_tries=self.min_tries_specific)
            if self.debug:
                self.print_debug_footer(html_out)
 