#!/usr/bin/env python
"""
Collect results from a Stacker Run and outputs a CSV file of results

  usage: python ./reporter.py path_to_PBS_job_dir [...]

Steven Ring, Aug 2017
"""

import os
import sys
import re
import glob
from datetime import datetime
from pathlib import Path

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
        self._load_bin_file()
        self._load_o_file()
        self._load_e_file()

    def _load_bin_file(self):
        binfiles = glob.glob(self.path + "/*.bin")
        if len(binfiles) != 1:
            raise ValueError("%s must contain one .bin file" % self.path)
        self.bin_file = BinFile(binfiles[0])

    def _load_o_file(self):
        ofiles = glob.glob(self.path + "/*.o*")
        if len(ofiles) != 1:
            raise ValueError("%s must contain one *.o* file" % self.path)
        self.r_file = StackerReport(ofiles[0])

    def _load_e_file(self):
        efiles = glob.glob(self.path + "/*.e*")
        if len(efiles) != 1:
            raise ValueError("%s must contain one *.e* file" % (self.path))
        self.e_file = ErrorFile(efiles[0])

    def get_values(self):
        result = {}
        result.update(self.bin_file.__dict__)
        result.update(self.e_file.__dict__)
        result.update(self.r_file.__dict__)
        return result

class BinFile(object):
    def __init__(self, path):
        self.bin_path = path
        self.submitted = datetime.utcfromtimestamp(os.path.getmtime(path)).isoformat()
        self.job_name = Path(path).stem
        fields = self.job_name.split("_")
        self.satellite = fields[0]
        self.product = fields[1]
        self.year = fields[3]

class ErrorFile(object):
    def __init__(self, path):
        errors = 0
        pat = re.compile("- ERROR -")
        with open(path, 'r') as infile:
            for line in infile:
                if pat.search(line) is not None:
                    errors += 1
        self.errors = errors
        self.e_file_path = path
        

class PbsReport(object):
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

    def _parsefile(self, o_file_path, pattern):
        with open(o_file_path, 'r') as infile:
            content = infile.read()

        m = pattern.search(content)
        if m is not None:
            self.__dict__.update(m.groupdict())
            self.timestamp = re.sub('\s', 'T', self.timestamp)  # convert to ISO8601
        else:
            print("Content did not match")

class StackerReport(PbsReport):
    """ 
    Represents a run of the stacker
    """

    stacker_pattern = re.compile((
        "^(?P<successful>\d+) successful,\s+(?P<failed>\d+) failed$"
        ), re.MULTILINE)

    def __init__(self, o_file_path):
        super(StackerReport, self).__init__(o_file_path) 
        self._parsefile(o_file_path, self.stacker_pattern)
        self.finished = datetime.utcfromtimestamp(os.path.getmtime(o_file_path)).isoformat()
        self.job_no = Path(o_file_path).stem
        self.o_file_path = o_file_path


if __name__ == "__main__":

    default_keys = "satellite,year,submitted,finished,successful,failed,errors,cpu_used,walltime_used,memory_used,service_units,job_id"

    paths = sys.argv[1:]
    print(default_keys)
    for path in paths:
        try:
            pbs_dir = PbsJobDir(path)
            result = pbs_dir.get_values()
            line = ""
            for key in default_keys.split(","):
                if key in result:
                    line += str(result[key]) + "," 
                else:
                    line += "?,"
            print(line[:-1])
        except ValueError as e:
            sys.stderr.write(str(e)+"\n")
