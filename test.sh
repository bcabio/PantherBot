#!/bin/bash
pep8count=`find . -name \*.py -exec pep8 --ignore=E402,E501 {} + | wc -l`

if [ $pep8count != 0 ];
	then
    	find . -name \*.py -exec pep8 --ignore=E402,E501 {} + 
   		exit 1
    else
        echo 'All good here'
        exit 0
    fi