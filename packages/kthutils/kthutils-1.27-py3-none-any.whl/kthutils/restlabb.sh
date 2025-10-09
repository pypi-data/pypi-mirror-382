#!/bin/bash

source ${HOME}/.profile
YEAR=$(date +%y)
MONTH=$(date +%m | sed "s/^0//")  # Remove leading zero
if [[ $MONTH -lt 7 ]]; then
  AC_YEAR="$((YEAR-1))/${YEAR}"
else
  AC_YEAR="${YEAR}/$((YEAR+1))"
fi
kthutils forms next restlabb${AC_YEAR} \
| grep -E "(Bosk|DD1310.*(CMAST|[CS]ITEH?)|DD131[57].*CINEK)" \
| kthutils forms rewriter rewrite restlabb
