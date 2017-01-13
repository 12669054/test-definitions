
./cyclictest -t 1 -p 99 -i 10000 -l 10000

egrep "C: +10000" log.txt \
    | awk '{printf("min pass %s ns\n", $(NF-6))}; {printf("act pass %s ns\n", $(NF-4))}; {printf("avg pass %s ns\n", $(NF-2))}; {printf("max pass %s ns\n", $NF)}'
