#!/bin/bash

HELP="
Produce code line statistics of this package.
"

printf "Running cloc per module\n"

statsdir=ti/docs/stats

if [ -d $statsdir ]; then
    rm -rf $statsdir
fi

for d in ti/*/
do
    mod=$(basename "$d")
    if [[ "$mod" == "__pycache__" || "$mod" == "stats" ]]; then
        continue
    fi
    printf "$mod\n"
    cloc --quiet --out=$statsdir/mod/$mod.txt $d
done

cloc --quiet --sum-reports --out=$statsdir/stats $statsdir/mod/*.txt
mv $statsdir/stats.lang $statsdir/all.txt
mv $statsdir/stats.file $statsdir/by-module.txt
python statshtml.py $statsdir
