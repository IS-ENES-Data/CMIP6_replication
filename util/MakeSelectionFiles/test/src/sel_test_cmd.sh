#! /bin/bash
p_base=${0%/*/*/*}
p_test_src=$p_base/test/src
p_test_res=$p_base/test/results
p_test_activity=$p_test_res/Activity2

# t-0
cmd[${#cmd[*]}]="--group"
txt[${#txt[*]}]="written to $p_base/Selection by default"

# t-1
cmd[${#cmd[*]}]="-a CMIP -i AWI -m AWI-CM-1-1-HR -e amip --activity-path=$p_test_activity --p_out=$p_test_res/test1"
txt[${#txt[*]}]=''

# t-2
cmd[${#cmd[*]}]="-a CMIP -i AWI -m AWI-CM-1-1-HR -e amip --p_out=$p_test_res/test2"
txt[${#txt[*]}]=''

# t-3
cmd[${#cmd[*]}]="-i AWI -m AWI-CM-1-1-HR --p_out=$p_test_res/test3"
txt[${#txt[*]}]=''

# t-4
cmd[${#cmd[*]}]="-i AWI -m AWI-CM-1-1-HR -e amip --p_out=$p_test_res/test4"
txt[${#txt[*]}]=''

# t-5
cmd[${#cmd[*]}]=" -m MPI-ESM1-2-HR --p_out=$p_test_res/test5"
txt[${#txt[*]}]=''

# t-6
cmd[${#cmd[*]}]=" -e historical --p_out=$p_test_res/test6"
txt[${#txt[*]}]=''

# t-7
cmd[${#cmd[*]}]=" -e historical,amip --p_out=$p_test_res/test7"
txt[${#txt[*]}]=''

# t-8
cmd[${#cmd[*]}]=" --p_out=$p_test_res/test8 -e historical,amip --frequency=fx,day --realm=atmos,ocean" # -v "\"var1 var2\"
txt[${#txt[*]}]=''

# t-9
cmd[${#cmd[*]}]=" --p_out=$p_test_res/test8 -e historical,amip --frequency=fx,day " # realm="atmos ocean" variable="var1 var2"
txt[${#txt[*]}]=''

# t-10
cmd[${#cmd[*]}]=" -e historical,amip --p_out=$p_test_res/test10 latest=true replica=true protocol=gridftp "variable[atmos]="var1 var2"
txt[${#txt[*]}]='searched for all MIPS, only defined for CMIP'

# t-11
cmd[${#cmd[*]}]="-i MPI-M -e historical,rcp45 -o Oops -v $p_test_src/set_test_var.lst --p_out=$p_test_res/test11"
txt[${#txt[*]}]='rcp45 ist not defined for CMIP6, results written to file Oops, Oops.1, Oops.2; over-writing prevented'

# t-12
cmd[${#cmd[*]}]="-a CMIP --tier=1 --p_out=$p_test_res/test12"
txt[${#txt[*]}]='all Tier1 experiments of CMIP'

# t-13
cmd[${#cmd[*]}]="--add=CMIP,ABS,M-ABS-1,historical,T5 --activity-path=$p_test_activity"
txt[${#txt[*]}]="tail of $p_test_activity/CMIP.csv; append entry from cmd-line" 

# t-14
cmd[${#cmd[*]}]="--add=$p_test_src/sel_test_add_1 --activity-path=$p_test_activity"
txt[${#txt[*]}]="tail of $p_test_activity/CMIP.csv; append two lines from list-file"

# t-15
cmd[${#cmd[*]}]="--edit=$p_test_src/sel_test_edit_1 --activity-path=$p_test_activity"
txt[${#txt[*]}]="tail of $p_test_activity/CMIP.csv; change one entry from list.file"

# t-16
cmd[${#cmd[*]}]="--stdout -a CMIP -i AWI -m AWI-CM-1-1-HR -e amip"
txt[${#txt[*]}]='no test directory; plain output'

# t-17
#cmd[${#cmd[*]}]="--set-dn=my-data-node -a CMIP -i ABS -m M-ABS-1 --activity-path=$p_test_activity"
#txt[${#txt[*]}]='no test directory; change of an entry of the corresponding activity file.'


if [ $# -eq 0 ] ; then
   for(( i=0 ; i < ${#cmd[*]} ; ++i )) ; do
     num[${#num[*]}]=$i
   done
elif [ ${1--1} -lt 0 ] ; then
   echo 'negative index'
   exit
elif [ $1 -gt ${#cmd[*]} ] ; then
  echo "maximum test number: $(( ${#cmd[*]} -1 ))"
  exit
fi

if [ ! -d ${p_base} ] ; then
  echo "no such directory $p_base"
  exit
fi

test ! ${num} && num=( $1 )

mkdir -p $p_test_res

if [ ! -d $p_test_activity ] ; then
  mkdir -p $p_test_activity
  cp $p_base/Activity/* $p_test_activity
fi


for n in ${num[*]} ; do
  if [ $n -eq 8 ] ; then
    echo -e "\ntest-${n}:" ${cmd[${n}]} -v \"var1 var2\"
    python $p_base/make_selection_file.py ${cmd[${n}]} -v "var1 var2"
  elif [ $n -eq 9 ] ; then
    echo -e "\ntest-${n}:" ${cmd[${n}]} realm=\"atmos ocean\" -v \"var1 var2\"
    python $p_base/make_selection_file.py ${cmd[${n}]} -v "var1 var2"
  else
    echo -e "\ntest-${n}:" ${cmd[${n}]}
    python $p_base/make_selection_file.py ${cmd[${n}]}
  fi

  test ${#txt[n]} -gt 0 && echo ${txt[n]}
  test "${txt[n]:0:4}" = tail && tail -n 4 $p_test_activity/CMIP.csv
done
