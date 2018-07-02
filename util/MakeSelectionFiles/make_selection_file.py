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

        self.def_act=[ 'AerChemMIP', 'CDRMIP', 'CMIP', 'DCPP', 'GeoMIP', 'HighResMIP', 'LS3MIP',
              'OMIP', 'PMIP', 'ScenarioMIP', 'C4MIP', 'CFMIP', 'DAMIP', 'FAFMIP', 'GMMIP',
              'ISMIP6', 'LUMIP', 'PAMIP', 'RFMIP', 'VolMIP' ]


    def add_entry(self):
        # already in the right format
        entries = self.get_opt('add_entry')

        for e in entries:
            if not e[0] in self.def_act:
                print 'Error: tried to add to unknown activity ' + e[0]
                sys.exit(1)

            f_name = e[0] + '.csv'
            f = os.path.join( self.get_opt('activity_path'), f_name )

            s=''
            for x in e:
                if s:
                    s += ','
                s += x

            with open(f, 'a') as fd:
                fd.write(s + '\n')

        return


    def edit_entry(self):
        # edit entries
        if self.is_opt('edit_old'):
            eo = self.get_opt('edit_old')

        if self.is_opt('edit_new'):
            en = self.get_opt('edit_new')

        for i in range(len(eo)):
            x_eo = eo[i].split(',')
            x_en = en[i].split(',')

            if x_eo[0] != x_en[0]:
                print 'Edit: new and old of different activities.'
                print "Please, be wise and edit manually."
                sys.exit(0)

            f_name = x_eo[0] + '.csv'
            f = os.path.join( self.get_opt('activity_path'), f_name )

            cmd_sed = "sed -i 's%" + eo[i] + "%" + en[i] + "%' " + f

            try:
                check_output = subprocess.check_output(cmd_sed,
                                                    shell=True,
                                                    cwd=self.get_opt('activity_path'))
            except subprocess.CalledProcessError as e:
                istatus = e.returncode

        return


    def get_entry(self):
        is_f=False
        is_r=False
        is_em=False

        if len(self.frequencies) > 1:
            is_f=True
        if len(self.realms) > 1:
            is_r=True
        if len(self.ens_mems) > 1:
            is_em=True

        entries=[]

        # concatenate variables
        v_str=''
        for v in self.variables:
            if len(v_str):
                v_str += ' '
            v_str += v

        if len(v_str):
            v_str = '"' + v_str + '"'

        # just for skipping the very first step when everthing else is empty
        is_v_all = not ( is_f or is_r or is_em )

        for f in self.frequencies:
            for r in self.realms:
                for e_m in self.ens_mems:
                    s=''
                    if is_f and len(f) > 0:
                        if len(s):
                            s += ','
                        s += 'frequency=' + f

                    if is_r and len(r) > 0:
                        if len(s):
                            s += ','
                        s += 'realm=' + r

                    if is_em and len(e_m) > 0:
                        if len(s):
                            s += ','
                        s += 'ensemble=' + e_m

                    if len(v_str) and (len(s) or is_v_all):
                        if len(s):
                            s += ','
                        s += 'variable=' + v_str

                    if len(s):
                        entries.append(s)

        return entries


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


    def mk_sel_file(self, opts, words, add_on):
        # construct lines of current selection file
        lines=[];
        lines.append('project=' + self.opts['mip_era'])
        lines.append('institute=' + words[1])
        lines.append('model=' + words[2])
        lines.append('experiment=' + words[3])

        #if self.is_opt('frequency'):
        #    lines.append('frequency=' + self.get_opt('frequency'))
        #if self.is_opt('ensemble'):
        #    lines.append('ensemble=' + self.get_opt('ensemble'))
        #if self.is_opt('realm'):
        #    lines.append('realm=' + self.get_opt('realm'))

        if self.is_opt('protocol'):
            lines.append('protocol=' + self.get_opt('protocol'))
        if self.is_opt('latest'):
            lines.append('latest=' + self.get_opt('latest'))
        if self.is_opt('replica'):
            lines.append('replica=' + self.get_opt('replica'))

        # param=value
        for p in self.opts['param']:
            lines.append(p)

        # also param=value, but from lists of frequency, realm, ensemble and variable
        post_fix=''
        for p in add_on:
            ps=p.split('=')
            if ps[0] != 'variable':
                post_fix += '_' + ps[1]

            lines.append(p)

        if self.is_opt('data_node'):
            # command-line option
            lines.append('data_node=' + self.get_opt('data_node'))
        elif len(words) == 6:
            # from the file, if any
            lines.append('data_node=' + words[5])

        if self.is_opt('stdout'):
            for line in lines:
                print line
        else:
            # write selection file
            if self.is_opt('group_activity'):
                op = os.path.join(opts['sel_file_path'], words[0])
            else:
                op = os.path.join(opts['sel_file_path'])

            if not self.mkdir(op):
                print "could not mkdir " + op
                sys.exit(0)

            if self.is_opt('sel_file_name'):
                f_name=self.get_opt('sel_file_name')
                if self.sel_file_name_count:
                    f_name += '.' + str(self.sel_file_name_count)

                self.sel_file_name_count += 1
            else:
                f_name=words[0] + '_' + words[1] + '_' + words[2] + '_' + words[3]
                if len(post_fix):
                    f_name += post_fix

            out=os.path.join(op, f_name)

            with open(out, 'w') as fd:
                #fd.write("--- # Time intervals of atomic variables.\n")

                for line in lines:
                    fd.write(line + '\n')

        return

    def run(self):
        if self.is_opt('add_entry'):
            self.add_entry()
            return

        if self.is_opt('edit_old'):
            self.edit_entry()
            return

        act=[]
        if self.is_opt('activity'):
            act = self.get_opt('activity')

        if not len(act):
            act=self.def_act

        for a in act:
            if a in self.def_act:
                self.run_activity(a)
            else:
                print "undefined activity '" + a + "'"
                sys.exit(1)

        return


    def run_activity(self, activity):
        opts = self.opts

        self.insts=[]
        self.models=[]
        self.exps=[]

        is_inst=False
        is_model=False
        is_exp=False

        if self.is_opt('institute'):
            self.insts = self.get_opt('institute')
            is_inst=True
        if self.is_opt('model'):
            self.models = self.get_opt('model')
            is_model=True
        if self.is_opt('experiment'):
            self.exps = self.get_opt('experiment')
            is_exp=True

        self.ens_mems=['']
        self.frequencies=['']
        self.realms=['']

        if self.is_opt('ens_mem'):
            self.ens_mems.extend(self.get_opt('ens_mem'))
        if self.is_opt('frequency'):
            self.frequencies.extend(self.get_opt('frequency'))
        if self.is_opt('realm'):
            self.realms.extend(self.get_opt('realm'))

        # list is going to be used later as space-separated str
        if self.is_opt('variable'):
            self.variables = self.get_opt('variable')
        else:
            self.variables=[]

        # only for a single tier, if any
        tier = self.get_opt('tier')

        # get a list of csvs for frequency, realm, ensemble and variable
        add_entries = self.get_entry()

        f_name = activity + '.csv'
        f = os.path.join( self.get_opt('activity_path'), f_name )

        if self.is_opt('sel_file_name'):
            self.sel_file_name_count=0

        count=0

        with open(f, 'r') as fd:
            for line in fd:
                line = line.rstrip()
                words = line.split(',')

                if is_inst:
                    if not words[1] in self.insts:
                        continue
                if is_model:
                    if not words[2] in self.models:
                        continue
                if is_exp:
                    if not words[3] in self.exps:
                        continue

                if tier:
                    if words[4] != 'T' + str(tier):
                        continue

                if self.is_opt('set_data_node'):
                    self.set_dn(opts, words)
                elif len(add_entries):
                    for entry in add_entries:
                        self.mk_sel_file( opts, words, entry.split(',') )
                        count += 1
                else:
                    # note that add_entries is empty
                    self.mk_sel_file(opts, words, add_entries)
                    count += 1

            if count and not self.is_opt('stdout'):
                print "generated " + str(count) + " selection files for " + activity

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

    if args.data_node     != None:  _ldo['data_node']     = args.data_node
    if args.is_latest:              _ldo['latest']        = 'true'
    if args.protocol      != None:  _ldo['protocol']      = args.protocol
    if args.sel_file_name != None:  _ldo['sel_file_name'] = args.sel_file_name
    if args.set_data_node != None:  _ldo['set_data_node'] = args.set_data_node
    if args.tier          != None:  _ldo['tier']          = args.tier

    # mix of comma- and space-separated values, perhaps a file list
    if args.activity   != None:    _ldo['activity']    = eval_param(args.activity)
    if args.ens_mem    != None:    _ldo['ens_mem']    = eval_param(args.ens_mem)
    if args.experiment    != None: _ldo['experiment']    = eval_param(args.experiment)
    if args.frequency    != None:  _ldo['frequency']    = eval_param(args.frequency)
    if args.institute    != None:  _ldo['institute']    = eval_param(args.institute)
    if args.model    != None:      _ldo['model']    = eval_param(args.model)
    if args.realm    != None:      _ldo['realm']    = eval_param(args.realm)
    if args.variable      != None: _ldo['variable'] = eval_param(args.variable)

    # convert csv parameter or each line of a file separately to activity-table entry
    if args.add_entry != None:
        _ldo['add_entry']=[]
        if os.path.isfile(args.add_entry):
            with open(args.add_entry, 'r') as fd:
                for line in fd:
                    line = line.rstrip()
                    _ldo['add_entry'].append(eval_param(line))
        else:
            _ldo['add_entry'].append(eval_param(args.add_entry))

    if args.edit_entry != None:
        if os.path.isfile(args.edit_entry):
            _ldo['edit_old']=[]
            _ldo['edit_new']=[]
            with open(args.edit_entry, 'r') as fd:
                for line in fd:
                    line = line.rstrip()
                    words = line.split(':')
                    if words[0] == 'old':
                        _ldo['edit_old'].append(words[1])
                    elif words[0] == 'new':
                        _ldo['edit_new'].append(words[1])

            if len(_ldo['edit_new']) != len(_ldo['edit_old']):
                print "Edit: old and new entry are not paired"
                sys.exit(1)

    # args.arg is always defined
    _ldo['mip_era']        = args.mip_era
    _ldo['latest']         = args.is_latest
    _ldo['replica']        = args.is_replica
    _ldo['stdout']         = args.is_stdout
    _ldo['group_activity'] = args.is_group_activity

    if args.param != None:
        _ldo['param'] = proc_plain_items(args.param)

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

    examples += "\n\ne) get selection files for an institute with changed synda default parameters"
    examples += "\n\t" + f + " -a CMIP -i CMCC replica=true protocol=http"

    examples += "\n\nf) get a single, specific selection file"
    examples += "\n\t" + f + " -a CFMIP -i CNRM-CERFACS -m CNRM-CM6-1 -e abrupt-2xCO2"

    examples += "\n\ng) get all selection files of type tier-1."
    examples += "\n\t" + f + " -t 1"

    examples += "\n\nSpecial: add a data-node to the Activity tables."
    examples += "\nNote that this does not create any selection file (in contrast to opt --dn), e.g."
    examples += "\n\t" + f + " --set-dn=esgf3.dkrz.de -a CMIP -i MPI-M"

    parser = argparse.ArgumentParser(
            formatter_class=RawTextHelpFormatter,
            prog="make_selection_file",
            description=descr,
            epilog=examples
            )

    parser.add_argument( '--add', dest='add_entry',
        help="Add a new entry to the corresponding activity file. Could be a file with multiple entries.\nSyntax: <acticity>,<institute>,<model>,<experiment>[,<Ttier>][,<data-node>]")

    parser.add_argument( '-a', '--activity', dest='activity',
        help="Activity, e.g. CMIP, ScenarioMIP; a comma-separated list if multiple.")

    parser.add_argument( '--dn', '--data_node', dest='data_node',
        help="Synda option: data_node (overruling any associated table entry).")

    parser.add_argument( '-e', '--experiment', '--exp', dest='experiment',
        help="Name of the experiment")

    parser.add_argument( '--edit', dest='edit_entry',
        help="Edit entries in corresponding activity files.\nOld and new entries have to be given by a file [multiple entries].\nPrefix old entry by key-word 'old:' and the modified one by 'mod:'.\nSee --add for the syntax.")

    parser.add_argument( '--ens', '--ensemble_member', dest='ens_mem',
        help="Name of the ensemble_member")

    parser.add_argument( '-f', '--frequency', dest='frequency',
        help="Acronym of the frequency")

    parser.add_argument( '--group-activity', '--group', dest='is_group_activity',
        action="store_true", default=False,
        help="Group generated selection files according to the 'activity', e.g. CMIP.")

    parser.add_argument( '-i', '--institution_id', dest='institute',
        help="Synda option: institution_id")

    parser.add_argument( '--latest', dest='is_latest',
        action="store_true", default=False,
        help="Synda option: latest.")

    parser.add_argument( '--mip_era', dest='mip_era', default='CMIP6',
        help="Synda option: mip_era; CMIP6 by default")

    parser.add_argument( '-m', '--model', dest='model',
        help="Synda option: Model")

    parser.add_argument( '-o', '--sel-file', dest='sel_file_name',
        help="Name of the selection file; by default: \n<activity>_<institute>_<model>_<experiment>[_<frequency>][_<realm>][_<ensemble_member>].\nNote that this is recommended when settings are identical but for different variables.\nIf more than a single selection file is to be created, then these get an extension." )

    parser.add_argument( '--p_out', '--output-path',  dest='sel_file_path',
        help="Path for generated selection files; by default directory Selection where this program is located." )

    parser.add_argument( '--protocol', dest='protocol',
        help="Synda option: protocol")

    parser.add_argument( '-r', '--realm', dest='realm',
        help="Synda option: realm")

    parser.add_argument( '--replica', dest='is_replica',
        action="store_true", default=False,
        help="Synda option: replica.")

    parser.add_argument( '-t', '--tier', dest='tier',
        help="Tier: 1-3")

    parser.add_argument( '--set-dn', '--set-data-node', dest='set_data_node',
        help="Add the name of the data-node to the pre-calculated tables.\nAt least option -i has to be provided; this is checked.")

    parser.add_argument( '--stdout', dest='is_stdout',
        action="store_true", default=False,
        help="Plain output stream of selection file(s)")

    parser.add_argument( '--tp', '--activity-path',  dest='activity_path',
        help="Path to the activity directory with list-files;\nby default directory Activity where this prog is located." )

    parser.add_argument( '-v', '--variable', dest='variable',
        help='For synda option variable.\nNote that double quotes often cause trouble, thus instead of -v "var1 var2" \nuse the equivalent without any quote: variable=var1 var2')

    parser.add_argument('param', nargs='*',
        help= '(multiple) synda parameter: parameter=value.\nNote that using --realm=value together with variable="var1 var2" would generate\ngenerally less selection files than variable[value]="var1 var2.')

    return parser


def eval_param(value):
    # a) get dict from a comma- and space-separated string
    # b) the same for all lines of a file

    t=[]
    for t1 in value.split(','):
        t.extend(t1.split())  # treat group of spaces as one

    if len(t) == 1 and os.path.isfile(t[0]):
        # file list
        f=t[0]
        t=[]
        with open(f, 'r') as fd:
            for line in fd:
                line = line.rstrip()
                for w in line.split(','):
                    t.extend(w.split())  # treat group of spaces as one

    return t

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

def proc_plain_items(d_param):
    da=[]
    d=[]
    last=len(d_param)-1

    for i in range(last+1):
        p = d_param[i].strip('"')
        x_p=p.split('=')
        if len(x_p) == 2 or i == last:
            if i == last:
                if len(x_p) == 1:
                    d.append(x_p[0])
                else:
                    d=[x_p[0], x_p[1]]

            if len(d):
                # finalise the previous item
                if len(d) == 1:
                    print 'please, check the trailing, plain parameters'
                    sys.exit(1)
                else:
                    s = d[0] + '='
                    if len(d) == 2:
                        s += d[1]
                    else:
                        s += '"'
                        for v in d[1:]:
                            s += v + ' '
                        else:
                            s = s.strip()
                            s += '"'

                    da.append(s) # save previous

            # next element starts
            if i < last:
                d=[x_p[0], x_p[1]]
        else:
            d.append(x_p[0]) # add a trailing value

        #da.append(s) # save previous

    return da


if __name__ == '__main__':
    make_selection(stand_alone=True)
    #print rev
