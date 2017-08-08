#!/usr/bin/env python
"""
Collect results from a Stacker Run and outputs a CSV file of results.
See ``class PbsJobDir`` for info on the expected PBS output/working directory

  usage: ./job_reporter.py path_to_PBS_job_dir [...]
  help:  ./job_reporter.py --help 

Steven Ring, Aug 2017
"""

import os
import sys
import re
import glob
import argparse
from datetime import datetime
from pathlib import Path

def convert_to_iso8601(timestamp):
    """
    Ensure timestamps have a consistent, well known format
    """
    try:
        result = re.sub('\s', 'T', self.timestamp)  # convert to ISO8601
    except:
        result = None
    return result

class PbsJobDir(object):
    """
    Represents the working diretory used by a PBS job. Files
    written to this directory are:

      - <job name>.bin  -- a binary file ???
      - <job_code>.o<job_no> -- standard out from the job
      - <job_code>.e<job_no> -- standard err from the job

    This class draws summary information from these file.
    """

    def __init__(self, path):
        self.path = path
        self.dir_errors = ""
        self.bin_file = self._get_bin_file()
        self.o_file = self._get_o_file()
        self.e_file = self._get_e_file()

    def _get_bin_file(self):
        binfiles = glob.glob(self.path + "/*.bin")
        if len(binfiles) != 1:
            self.dir_errors += "%s must contain one .bin file; " % (self.path)
            return None
        return BinFileParser(binfiles[0])

    def _get_o_file(self):
        ofiles = glob.glob(self.path + "/*.o*")
        if len(ofiles) != 1:
            self.dir_errors += "%s must contain one .o file; " % (self.path)
            return None
        return StackerStdoutParser(ofiles[0])

    def _get_e_file(self):
        efiles = glob.glob(self.path + "/*.e*")
        if len(efiles) != 1:
            self.dir_errors += "%s must contain one .e file; " % (self.path)
            return None
        return StderrParser(efiles[0])

    def get_values(self):
        result = {"dir_errors": self.dir_errors}
        if self.bin_file is not None:
            result.update(self.bin_file.__dict__)
        if self.e_file is not None:
            result.update(self.e_file.__dict__)
        if self.o_file is not None:
            result.update(self.o_file.__dict__)
       
        return result

class BinFileParser(object):
    """
    Collects some information from the .bin file in the output directory
    """
    def __init__(self, path):
        self.bin_path = path
        self.submitted = datetime.utcfromtimestamp(os.path.getmtime(path)).isoformat()
        self.job_name = Path(path).stem
        fields = self.job_name.split("_")
        self.satellite = fields[0]
        self.product = fields[1]
        self.year = fields[3]

class StderrParser(object):
    """
    Sniffs into stderr file looking for errors
    """
    pat = re.compile("ERROR")
    def __init__(self, path):
        self.errors = 0
        self.stderr_lines = 0
        with open(path, 'r') as infile:
            for line in infile:
                self.stderr_lines += 1
                if self.pat.search(line) is not None:
                    self.errors += 1
        self.e_file_path = path
        self.stderr_size = os.path.getsize(path)
        

class PbsReportParser(object):
    """ 
    Represents a run of the stacker
    """
    pbs_pattern = re.compile((
        "^(\s+)Resource Usage on (?P<timestamp>\d{4}-\d\d-\d\d"
        " \d\d:\d\d:\d\d):$"
        "(\s+)Job Id:\s*(?P<job_id>\S+)$"
        "(\s+)Project:\s*(?P<project>\S+)$"
        "(\s+)Exit Status:\s*(?P<exit_status>\S+)$"
        "(\s+)Service Units:\s*(?P<service_units>\S+)$"
        "(\s+)NCPUs Requested:\s*(?P<ncpus_requested>\d+)"
        "(\s+)NCPUs Used:\s*(?P<ncpus_used>\d+)\s*$"
        "(\s+)CPU Time Used:\s*(?P<cpu_used>\d+:\d\d:\d\d)\s*$"
        "(\s+)Memory Requested:\s*(?P<memory_requested>\S+)"
        "(\s+)Memory Used:\s*(?P<memory_used>\S+)\s*$"
        "(\s+)Walltime requested:\s*(?P<walltime_requested>\d+:\d\d:\d\d)"
        "(\s+)Walltime Used:\s*(?P<walltime_used>\d+:\d\d:\d\d)\s*$"
        "(\s+)JobFS requested:\s+(?P<jobfs_requested>\S+)"
        "(\s+)JobFS used:\s*(?P<jobfs_used>\S+)\s*$"
        ), re.MULTILINE)

    def __init__(self, o_file_path):
        self._parsefile(o_file_path, self.pbs_pattern)
        self.stdout_size = os.path.getsize(o_file_path)

    def _parsefile(self, o_file_path, pattern):
        with open(o_file_path, 'r') as infile:
            content = infile.read()

        m = pattern.search(content)
        if m is not None:
            self.__dict__.update(m.groupdict())
            self.timestamp = convert_to_iso8601(self.timestamp)
#        else:
#            print("Content did not match")

class StackerStdoutParser(PbsReportParser):
    """ 
    Extracts information reported by Stacker on stdout
    """

    stacker_pattern = re.compile((
        "^(?P<successful>\d+) successful,\s+(?P<failed>\d+) failed$"
        ), re.MULTILINE)

    def __init__(self, o_file_path):
        super(StackerStdoutParser, self).__init__(o_file_path) 
        self._parsefile(o_file_path, self.stacker_pattern)
        self.finished = datetime.utcfromtimestamp(os.path.getmtime(o_file_path)).isoformat()
        self.job_no = Path(o_file_path).stem
        self.o_file_path = o_file_path



def main():
    
    # parser the arguments

    default_keys = (
        "satellite,year,submitted,finished,successful,failed,"
        "errors,cpu_used,walltime_used,memory_used,service_units,"
        "job_id,stdout_size,stderr_lines,stderr_size,dir_errors"
    )
    parser = argparse.ArgumentParser(description='Collect and output PBS job statistics')
    parser.add_argument('-k', '--keys', help='comma separated list of keys', default=default_keys)
    parser.add_argument('--keys_only', help='print the keys to be output', action='store_true')
    parser.add_argument('--no_keys', help='supress the output of keys', action='store_true')
    parser.add_argument('paths', nargs='*', help='paths to PBS output directory')
    parser.set_defaults(no_keys=False, keys_only=False)
    args = parser.parse_args()

    # print the keys to be output

    if not args.no_keys:
        print(args.keys)
    if args.keys_only:
        sys.exit(0)

    # collect data and output results

    for path in args.paths:
        try:
            pbs_dir = PbsJobDir(path)
            result = pbs_dir.get_values()
            line = ""
            for key in args.keys.split(","):
                if key in result:
                    line += str(result[key]) + "," 
                else:
                    line += "?,"
            print(line[:-1])
        except ValueError as e:
            sys.stderr.write(str(e)+"\n")


if __name__ == "__main__":
    main()
