#!/bin/bash

die () {
    echo >&2 "$@"
    exit 1
}

DATE=`date '+%Y-%m-%d-%H:%M'`

BASE=$(cd `dirname "${BASH_SOURCE[0]}"`/.. && pwd)
REF=${BASE}/msa/reference.fasta
QRY=${BASE}/msa/query.fasta
TREE=${BASE}/tree/reference.newick
MODEL=${BASE}/tree/eval.raxml.bestModel
JPLACE=${BASE}/placed/epa_result.jplace
SC=${BASE}/script
RUNS_DIR=/data/barberpe/scrapp/runs/

NUM_THREADS=40
SEED=4242

prefix="4kspecies_"

seq_length_range=4000
prune_fract_range=0.25
pop_size_range=1e6
species_range=400
mut_rate_range=1e-8
sample_size_range=50

case "$1" in
  seq_length )
    seq_length_range="1000 2000 4000"
    ;;
  prune_fract )
    prune_fract_range="0.1 0.25 0.4"
    ;;
  pop_size )
    pop_size_range="1e5 1e6 1e7"
    ;;
  species )
    species_range="200 400 600"
    ;;
  mut_rate )
    mut_rate_range="1e-7 5e-8 1e-8"
    ;;
  sample_size )
    sample_size_range="20 50 80"
    ;;
  *)
    echo "invalid parameter ($1), aborting"
    exit 1
esac

outfile="results/${prefix}${1}.csv"
[[ -f ${outfile} ]] && die "outfile already exists!"

echo "start at `date`"
set -e
cd ${SC}
# write the csv header
echo "run,seq_length,mut_rate,species,sample_size,pop_size,prune_fract,scrapp_mode,krd,norm_krd,norm_norm_krd,norm_unit_krd,abs_err_sum,abs_err_mean,abs_err_med,rel_err_sum,rel_err_mean,rel_err_med,norm_err_sum,norm_err_mean,norm_err_med,rel_norm_err_mean" > ${outfile}

run=0
for seq_length in $seq_length_range; do
  for prune_fract in $prune_fract_range; do
    for pop_size in $pop_size_range; do
      for species in $species_range; do
        for mut_rate in $mut_rate_range; do
          for sample_size in $sample_size_range; do
            for scrapp_mode in rootings bootstrap outgroup; do
              for i in {0..4}; do
                echo "Starting run ${run}!"

                SCRAPP_SIM_CURDIR=${RUNS_DIR}/simulated/seq_length_${seq_length}/prune_fract_${prune_fract}/pop_size_${pop_size}/species_${species}/mut_rate_${mut_rate}/sample_size_${sample_size}/scrapp_mode_${scrapp_mode}/iter_${i}
                export SCRAPP_SIM_CURDIR
                mkdir -p ${SCRAPP_SIM_CURDIR}
                rm -rf ${SCRAPP_SIM_CURDIR}/* 2> /dev/null

                printf "${run},${seq_length},${mut_rate},${species},${sample_size},${pop_size},${prune_fract},${scrapp_mode}," >> ${outfile}

                echo "  generate the tree..."
                ./msprime.sh --seq-length ${seq_length} --mutation-rate ${mut_rate} --species ${species} --population-size ${pop_size} --prune ${prune_fract} --sample-size ${sample_size} 1> /dev/null
                echo "  tree done!"

                # generate the sequences and split into query and ref set
                echo "  generate the sequences..."
                ./seqgen.sh -l ${seq_length} 1> /dev/null
                echo "  sequences done!"

                # infer model params
                echo "  infer model params..."
                 # --blmin 1e-7 --blmax 5000
                ./eval_reftree.sh --threads ${NUM_THREADS} --opt-branches off --force perf 1> /dev/null
                echo "  model params done!"

                # run placement
                echo "  place..."
                ./epa.sh --threads ${NUM_THREADS} 1> /dev/null
                echo "  placement done!"

                # run scrapp
                echo "  running scrapp..."
                case "${scrapp_mode}" in
                  rootings )
                    ./scrapp.sh --num-threads ${NUM_THREADS} 1> /dev/null
                    ;;
                  bootstrap )
                    ./scrapp.sh --num-threads ${NUM_THREADS} --bootstrap 1> /dev/null
                    ;;
                  outgroup )
                    ./scrapp.sh --num-threads ${NUM_THREADS} --ref-align-outgrouping ${SCRAPP_SIM_CURDIR}/msa/reference.fasta 1> /dev/null
                    ;;
                  *)
                    echo "invalid scrapp_mode, aborting"
                    exit 1
                esac
                echo "  scrapp done!"

                # print statistic
                # echo "  printing statistic..."
                ./compare_species_counts ${SCRAPP_SIM_CURDIR}/delimit/summary.newick ${SCRAPP_SIM_CURDIR}/tree/annot_reference.newick 1 >> ${outfile}
                printf "\n" >> ${outfile}
                # echo "  statistic done!"
                echo "partial at `date`"

                let run+=1

              done # runs
            done # scrapp_mode
          done # sample_size
        done # mut_rate
      done # species
    done # pop_size
  done # prune_fract
done # seq_length

echo "end at `date`"
