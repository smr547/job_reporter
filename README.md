# job_reporter
Gather job statistics from PBS stdout and stderr files and output as a CSV file

This program assumes the stderr and stdout files will be co-located in a single directory. Multiple such 
directories can be collected and summarised.

```
usage: job_reporter.py [-h] [-k KEYS] [--keys_only] [--no_keys]
                       [paths [paths ...]]

Collect and output PBS job statistics

positional arguments:
  paths                 paths to PBS output directory

optional arguments:
  -h, --help            show this help message and exit
  -k KEYS, --keys KEYS  comma separated list of keys
  --keys_only           print the keys to be output
  --no_keys             supress the output of keys
```
