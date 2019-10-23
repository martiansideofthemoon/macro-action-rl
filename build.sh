#!/bin/bash

for f in action_space_sarsa figar_sarsa di_sarsa conditional_figar_sarsa reg_sarsa random;
do
    cd $f
    make
    cd ..
done
