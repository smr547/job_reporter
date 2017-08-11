# job_reporter
Gather job statistics from PBS stdout and stderr files and output as a CSV file

This program assumes the stderr and stdout files will be co-located in a single directory. Multiple such 
directories can be collected and summarised.

```
usage: job_reporter.py [-h] [-k KEYS] [--keys_only] [--no_keys]
                       [paths [paths ...]]

Collect and output PBS job statistics

positional arguments:
  paths                 path to PBS output directories

optional arguments:
  -h, --help            show this help message and exit
  -k KEYS, --keys KEYS  comma separated list of keys
  --keys_only           print the keys to be output
  --no_keys             supress the output of keys
```

Just list the available keys:

```
$ ./job_reporter.py --keys_only
satellite,year,submitted,finished,successful,failed,errors,ncpus_requested,ncpus_used,cpu_used,walltime_used,memory_used,service_units,cpu_utilisation,job_id,stdout_size,stderr_lines,stderr_size,dir_errors
$
```

## Extension

To adapt the ``job_reporter`` to other PBS job output files

* create a subclass of ``PbsReportParser``
* write a ``regex`` which describes the program output to ``stdout``
* use ``_parsefile(path, regex)`` in the subclass constructor
* Named groups in the regurlar expression will be available as output keys in the CSV file

##TODO
* Adapt the program to find PBS ``stdout`` and ``stderr`` pairs in a variety of locations
* Ability to plug a general file parser to provide additional info to the output CSV file
