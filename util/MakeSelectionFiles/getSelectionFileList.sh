#! /bin/bash

getExps()
{
  local curr_act=$1
  eval test \${${curr_act}_exps} && return

  local count=0
  local act line is_act

  while read line ; do
    if [ ${count} -lt 2 ] ; then
       count=$(( count +1 ))
       continue
    fi

    e=$( expr match ${line} ' \{8\}"\(.*\)":{' )
    if [ $e ] ; then
       exp=$e
       continue
    fi

    if [ ${line// /} = '"activity_id":[' ] ; then
      while read line ; do
        line=${line// /}
        test "${line}" = '],' && break

        act=$( expr match ${line} ' *"\(.*\)"' )
        if [ ${curr_act} = $act ] ; then
          eval ${act}_exps=\${${act}_exps}${exp},
          is_act=t
        fi
      done

      continue
    fi

    t=$( expr match ${line} ' *"tier":"\(.*\)"' )
    if [ ${#t} -gt 0 -a ${is_act:-f} = t ] ; then
      eval ${act}_tier=\${${act}_tier}T${t},
      is_act=f
    fi

   done < /hdh/hdh/QA_Tables/tables/projects/CMIP6/CMIP6_CVs/CMIP6_experiment_id.json

   return
}

IFS=''

set -x
csv=''
count=0
acts=()

test ! -d /hdh/hdh/Selection/Activity && mkdir -p /hdh/hdh/Selection/Activity
cd /hdh/hdh/Selection/Activity

\rm -f *.csv

while read line ; do
  if [ ${count} -lt 2 ] ; then
     count=$(( count +1 ))
     continue
  fi

  m=$( expr match ${line} ' \{8\}"\(.*\)":{' )
  if [ ! ${model} ] ; then
     model=$m
     continue
  fi

  if [ ${line// /} = '"activity_participation":[' ] ; then
    while read line ; do
      line=${line// /}
      test "${line}" = '],' && break

      acts[${#acts[*]}]=$( expr match ${line} ' *"\(.*\)"' )
    done
  fi

  if [ ${line// /} = '"institution_id":[' ] ; then
    while read line ; do
      line=${line// /}
      test "${line}" = '],' && break

      inst=$( expr match ${line} ' *"\(.*\)"' )

      for act in ${acts[*]} ; do
         getExps ${act} # executed only once for each activity

         eval act_str=\${${act}_exps}
         eval tier_str=\${${act}_tier}

         if [ ${act_str} ] ; then
           act_last=$(( ${#act_str} -1 ))
           act_str=${act_str:0:act_last}  # strip trailing ,

           tier_last=$(( ${#tier_str} -1 ))
           tier_str=${tier_str:0:tier_last}  # strip trailing ,

           while [ ${act_str} ] ; do
              a=${act_str%%,*}
              act_str=${act_str#*,}
              b=${tier_str%%,*}
              tier_str=${tier_str#*,}
              echo "${act},${inst},${model},${a},${b}" >> ${act}.csv

              test "$a" = "${act_str}" && break
           done
         else
            for(( i=0 ; i < ${#empty_act[*]} ; ++i )) ; do
              test $act == ${empty_act[i]} && break
            done
            if [ $i -eq ${#empty_act[*]} ] ; then
              empty_act[${#empty_act[*]}]=$act
              echo "act without any experiment: ${act}"
            fi
         fi
      done
    done

    model=''
    acts=()
  fi


#count=$(( count +1 ))
#test ${count} -gt 20 && exit

done < /hdh/hdh/QA_Tables/tables/projects/CMIP6/CMIP6_CVs/CMIP6_source_id.json

