rm -rf d1

python3 ./searcher.py --root d1 init

python3 ./searcher.py --root d1 add testdata/file1.txt
python3 ./searcher.py --root d1 add testdata/file2.txt

# При появлении новых слов должен сохраняться алфавитный порядок слов в файле.


