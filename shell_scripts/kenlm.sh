#!/bin/bash
/Users/francob/kenlm/build/bin/lmplz -o 2 -S 1G -T $1.tmp --discount_fallback < $2 > $1.arpa
