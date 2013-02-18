#!/bin/bash

progdir=`dirname $0`
cd  ${progdir}/../src

datadir=../data/sample
dbfile=../data/sample.db
#echo ${datadir}, ${dbfile}
rm ../data/worddf_file.adb 
rm ../data/worddf.adb
rm ${dbfile}
python sample.py $1
python worddf.py ${datadir}
python preproc_qqtopic.py -f ${dbfile} ${datadir}
python extract_keyword.py ${dbfile}
