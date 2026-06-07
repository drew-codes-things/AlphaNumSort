# test-file-gen

Small helper script that generates sample text files for sorter testing.

## Usage

```bash
cd test-file-gen
python generator.py
```

Then run the sorter against generated files:

```bash
python ../main.py --file alphabetical_test.txt --mode alpha
```
