#!/bin/bash

progdir=`dirname $0`
cd  ${progdir}/../src

datadir=../data/$1
dbfile=../data/$1.db
echo ${datadir}, ${dbfile}
rm ../data/worddf.adb
rm ../data/worddf_file.adb
rm ${dbfile}
python worddf.py ${datadir}
python preproc_qqtopic.py -f ${dbfile} ${datadir}
python extract_keyword.py ${dbfile}
