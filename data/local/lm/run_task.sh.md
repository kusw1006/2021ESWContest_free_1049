## run_task.sh



변경사항:   **.tar.gz**    ->   **.zip**  (corpus 압축 확장자에 맞게)

​					morfessor version :  **2.0.6**    ->   **2.0.1**

- 변경 전 (line 50~ 60)

```sh
#  split corpus into similar length around 1,000,000 line
echo 'Split corpus --------------------------------------------------------------'
numSplitedfiles=$(find $srcdir ! -name '*.tar.gz*' ! -name '.*' ! -name 'normedCorpus*' -name "*.a*" | wc -l)
if [ $numSplitedfiles -eq 0 ]; then
    find $srcdir ! -name '*.tar.gz*' ! -name '.*' ! -name 'normedCorpus*' ! -name "*.a*" -type f |\
        parallel "split -l 1000000 {} {}'.'"
else
    echo '  It seems like already splited, if not plz remove *.a* files and run again'
fi

splitedfiles=$(find $srcdir ! -name '*.tar.gz*' ! -name '.*' ! -name 'normedCorpus*' -name "*.a*")
```



- 변경 후 (line 50~ 60)

```sh
#  split corpus into similar length around 1,000,000 line
echo 'Split corpus --------------------------------------------------------------'
numSplitedfiles=$(find $srcdir ! -name '*.zip*' ! -name '.*' ! -name 'normedCorpus*' -name "*.a*" | wc -l)
if [ $numSplitedfiles -eq 0 ]; then
    find $srcdir ! -name '*.tar.gz*' ! -name '.*' ! -name 'normedCorpus*' ! -name "*.a*" -type f |\
        parallel "split -l 100 {} {}'.'"
else
    echo '  It seems like already splited, if not plz remove *.a* files and run again'
fi

splitedfiles=$(find $srcdir ! -name '*.zip*' ! -name '.*' ! -name 'normedCorpus*' -name "*.a*")
```



