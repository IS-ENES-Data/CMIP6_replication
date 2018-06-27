import sys
import os

import argparse
import ConfigParser
import subprocess
from   types import *
from argparse import RawTextHelpFormatter

class MakeSelection(object):
    '''
    classdocs
    '''
    def __init__(self, stand_alone=True, opts={}, com_line_opts={}):
        self.opts = opts
        if stand_alone:
            self.opts.update( commandLineOpts( create_parser() ) )
        else:
            self.opts.update( com_line_opts )

    def get_opt(self, key, dct={}, bStr=False):
        if len(dct):
            curr_dct = dct
        else:
            curr_dct = self.opts

        val=''
        if key in curr_dct:
            val = curr_dct[key]

            if bStr:
               val = str(val)

        return val


    def is_opt(self, key, dct={}):
        # a) an option exists, then return True, but,
        # b) if the type is bool, then return the value
        if len(dct):
            curr_dct = dct
        else:
            curr_dct = self.opts

        if key in curr_dct:
            val = curr_dct[key]

            if type(val) == BooleanType:
               return val
            else:
               if not val == 'f':
                    return True

        return False

    def mkdir(self, path):
        # os.makedirs raises error when dirs already exist
        try:
            os.makedirs(path)
        except OSError:
            pass

        # test for a genuine failed making of dirs
        if not os.path.isdir(path):
            os.makedirs(path)
            return False

        return True


    def mk_sel_file(self, opts, words):
        # construct lines of current selection file
        lines=[];
        lines.append('project=' + self.opts['mip_era'])
        lines.append('institute=' + words[1])
        lines.append('model=' + words[2])
        lines.append('experiment=' + words[3])

        if self.is_opt('frequency'):
            lines.append('frequency=' + self.get_opt('frequency'))
        if self.is_opt('ensemble'):
            lines.append('ensemble=' + self.get_opt('ensemble'))
        if self.is_opt('realm'):
            lines.append('realm=' + self.get_opt('realm'))
        if self.is_opt('protocol'):
            lines.append('protocol=' + self.get_opt('protocol'))
        if self.is_opt('latest'):
            lines.append('latest=' + self.get_opt('latest'))
        if self.is_opt('replica'):
            lines.append('replica' + self.get_opt('replica'))

        if self.is_opt('data_node'):
            # command-line option
            lines.append('data_node' + self.get_opt('data_node'))
        elif len(words) == 6:
            # from the file, if any
            lines.append('data_node' + words[5])

        # param=value
        for p in self.opts['param']:
            lines.append(p)

        # write selection file
        if self.is_opt('sort_activity'):
            op = os.path.join(opts['sel_file_path'], words[0])
        else:
            op = os.path.join(opts['sel_file_path'])

        if not self.mkdir(op):
            print "could not mkdir " + op
            sys.exit(0)

        f_name=words[0] + '_' + words[1] + '_' + words[2] + '_' + words[3]
        out=os.path.join(op, f_name)

        with open(out, 'w') as fd:
            #fd.write("--- # Time intervals of atomic variables.\n")

            for line in lines:
                fd.write(line + '\n')

        return

    def run(self):
        a_a=[ 'AerChemMIP', 'CDRMIP', 'CMIP', 'DCPP', 'GeoMIP', 'HighResMIP', 'LS3MIP',
              'OMIP', 'PMIP', 'ScenarioMIP', 'C4MIP', 'CFMIP', 'DAMIP', 'FAFMIP', 'GMMIP',
              'ISMIP6', 'LUMIP', 'PAMIP', 'RFMIP', 'VolMIP' ]

        act=[]
        if self.is_opt('activity'):
            act.append( self.get_opt('activity') )

        if not len(act):
            act=a_a

        for a in act:
            if a in a_a:
                self.run_activity(a)
            else:
                print "undefined activity '" + a + "'"
                sys.exit(1)

        return


    def run_activity(self, activity):
        opts = self.opts

        inst     = self.get_opt('institute')
        model    = self.get_opt('model')
        exp      = self.get_opt('experiment')
        tier     = self.get_opt('tier')

        f_name = activity + '.csv'
        f = os.path.join( self.get_opt('activity_path'), f_name )

        is_break=False
        count=0

        with open(f, 'r') as fd:
            for line in fd:
                line = line.rstrip()
                words = line.split(',')

                if inst:
                    if words[1] != inst:
                        continue

                if model:
                    if words[2] != model:
                        continue

                if exp:
                    if words[3] != exp:
                        continue

                if tier:
                    if words[4] != tier:
                        continue

                #if len(words) == 6:
                #    data_node=words[5]

                if self.is_opt('set_data_node'):
                    self.set_dn(opts, words)
                else:
                    self.mk_sel_file(opts, words)
                    count += 1
        print "generated " + str(count) + " selection files"

        return

    def set_dn(self, opts, words):
        # reconstruct line
        o_line=''
        for i in range(5):
            if o_line:
                o_line +=','

            o_line += words[i]

        n_line = o_line
        n_line += ',' + self.get_opt('set_data_node')

        if len(words) == 6:
            o_line += ',' + words[5]

        f_name = words[0] + '.csv'

        cmd_sed = "sed -i 's%" + o_line + "%" + n_line + "%' " + f_name

        try:
            check_output = subprocess.check_output(cmd_sed,
                                                shell=True,
                                                cwd=self.get_opt('activity_path'))
        except subprocess.CalledProcessError as e:
            istatus = e.returncode

        return


def commandLineOpts(parser):

    # let's parse
    args = parser.parse_args(sys.argv[1:])

    # post-processing: namespace --> dict
    _ldo = {}

    if args.activity      != None:  _ldo['activity']      = args.activity.strip(',')
    if args.data_node     != None:  _ldo['data_node']     = args.data_node
    if args.experiment    != None:  _ldo['experiment']    = args.experiment
    if args.ens_mem       != None:  _ldo['ens_mem']       = args.ens_mem
    if args.frequency     != None:  _ldo['frequency']     = args.frequency
    if args.institute     != None:  _ldo['institute']     = args.institute
    if args.is_latest:              _ldo['latest']        = 'true'
    if args.model         != None:  _ldo['model']         = args.model
    if args.protocol      != None:  _ldo['protocol']      = args.protocol
    if args.realm         != None:  _ldo['realm']         = args.realm
    if args.set_data_node != None:  _ldo['set_data_node'] = args.set_data_node
    if args.tier          != None:  _ldo['tier']          = args.tier
    if args.variable      != None:  _ldo['variable']      = args.variable

    # if args.mip_era       != None:  _ldo['mip_era']       = args.mip_era
    _ldo['mip_era']       = args.mip_era
    _ldo['latest']        = args.is_latest
    _ldo['replica']       = args.is_replica
    _ldo['sort_activity'] = args.is_sort_activity

    _ldo['param'] = args.param

    pp, prg = os.path.split(sys.argv[0])

    if args.activity_path == None:
        _ldo['activity_path'] = os.path.join(pp, 'Activity')
    else:
        p,f = os.path.split(args.activity_path)
        if not p:
            _ldo['activity_path'] = os.path.join(pp,args.activity_path)
        else:
            _ldo['activity_path'] = args.activity_path

    if args.sel_file_path == None:
        _ldo['sel_file_path'] = os.path.join(pp, 'Selection')
    else:
        p,f = os.path.split(args.sel_file_path)
        if not p:
            _ldo['sel_file_path'] = os.path.join(pp,args.sel_file_path)
        else:
            _ldo['sel_file_path'] = args.sel_file_path

    if args.set_data_node and args.institute == None:
        print 'option --set-dn requires also option -i, i.e. institute id'
        sys.exit(1)

    return _ldo


def create_parser():

    use_path, f = os.path.split(sys.argv[0])
    act_path = os.path.join(use_path,"Activity")
    sel_path = os.path.join(use_path,"Selection")

    descr="Generate selection files from pre-calculated tables based on CMIP6_source_id.json and CMIP6_experiment_id.json."
    descr += "\nAll possibilities by default for activity, experiment, institution_id, and model, respectively."
    descr += "\nNote that the path of " + f + " is by default the path to the 'Activity' tables as well as"
    descr += "\nfor a directory containing any resulting selection files; the name of the container itself is 'Selection' by default."


    examples="Examples:\n"
    examples += "a) generate all selection files in directory " + sel_path
    examples += "\n\t" + f

    examples += "\n\nb) generate selection files for a specific activity and model"
    examples += "\n\t" + f + " -a CMIP -m BCC-ESM1"

    examples += "\n\nc) identical to b)"
    examples += "\n\t" + f + " --activity=CMIP --model=BCC-ESM1 --tp=" + act_path + " --out=" + sel_path

    yc=os.path.join("/", "path", "Your-Choice")
    examples += "\n\nd) get all selection files for a given experiment of given activity; files are stored in " + yc
    examples += "\n\t" + f + " -a ScenarioMIP -e amip --out=" + yc

    examples += "\n\ne) get selection files for an institute with changed synda parameters"
    examples += "\n\t" + f + " -a CMIP -i CMCC replica=true protocol=http"

    examples += "\n\nf) get a single, specific selection file"
    examples += "\n\t" + f + " -a CFMIP -i CNRM-CERFACS -m CNRM-CM6-1 -e abrupt-2xCO2"

    examples += "\n\ng) get all selection files of type tier-1."
    examples += "\n\t" + f + " -t 1"

    examples += "\n\nSpecial: add a data-node to the Activity tables."
    examples += "\nNote that this does not create any selection file (in contrast to opt --dn)!"
    examples += "\n\t" + f + " --set-dn=esgf3.dkrz.de -a CMIP -i MPI-M"

    parser = argparse.ArgumentParser(
            formatter_class=RawTextHelpFormatter,
            prog="make_selection_file",
            description=descr,
            epilog=examples
            )

    parser.add_argument( '-a', '--activity', dest='activity',
        help="Activity, e.g. CMIP, ScenarioMIP; a comma-separated list if multiple.")

    parser.add_argument( '--dn', '--data_node', dest='data_node',
        help="Synda option: data_node (overruling any associated table entry).")

    parser.add_argument( '-e', '--experiment', '--exp', dest='experiment',
        help="Name of the experiment")

    parser.add_argument( '--ens', '--ensemble_member', dest='ens_mem',
        help="Name of the ensemble_member")

    parser.add_argument( '-f', '--frequency', dest='frequency',
        help="Name of the frequency")

    parser.add_argument( '-i', '--institution_id', dest='institute',
        help="Synda option: institution_id")

    parser.add_argument( '--latest', dest='is_latest',
        action="store_true", default=False,
        help="Synda option: latest.")

    parser.add_argument( '--mip_era', dest='mip_era', default='CMIP6',
        help="Synda option: mip_era; CMIP6 by default")

    parser.add_argument( '-m', '--model', dest='model',
        help="Synda option: Model")

    parser.add_argument( '--out', '--output-path',  dest='sel_file_path',
        help="Path for generated selection files; by default directory Selection where Activity is." )

    parser.add_argument( '--protocol', dest='protocol',
        help="Synda option: protocol")

    parser.add_argument( '--realm', dest='realm',
        help="Synda option: realm")

    parser.add_argument( '--replica', dest='is_replica',
        action="store_true", default=False,
        help="Synda option: replica.")

    parser.add_argument( '--sort-activity', '--sort', dest='is_sort_activity',
        action="store_true", default=False,
        help="Sort generated selection file according to the 'activity', e.g. CMIP.")

    parser.add_argument( '-t', '--tier', dest='tier',
        help="Tier: 1-3")

    parser.add_argument( '--set-dn', '--set-data-node', dest='set_data_node',
        help="Add the name of the data-node to the pre-calculated tables. At least option -i has to be provided; this is checked.")

    parser.add_argument( '--tp', '--table-path',  dest='activity_path',
        help="Path to the activity-selection table [directory Activity where this prog is." )

    parser.add_argument( '-v', '--variable', dest='variable',
        help="Synda option: variable")

    parser.add_argument('param', nargs='*',
        help= "(multiple) synda parameter: parameter=value")

    return parser


def getOpt(self, key, dct={}, bStr=False):
    if len(dct):
        curr_dct = dct
    else:
        curr_dct = self.dOpts

    if key in curr_dct:
        val = curr_dct[key]

        if bStr:
            val = str(val)

        return val

    return ''

def make_selection(stand_alone=False, opts={}, com_line_opts={}):
    # 2nd param: command-line options {}
    ms = MakeSelection(stand_alone, opts=opts, com_line_opts=com_line_opts)
    ms.run()

    return


if __name__ == '__main__':
    make_selection(stand_alone=True)
    #print rev
