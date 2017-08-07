#!/usr/bin/env python
import sys
import re
class Report(object):
    """ 
    Represents a run of the stacker
    """

    pattern = re.compile((
        "^(\s+)Job Id:\s*(?P<job_id>\S+)$"
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
#        "(\s+)JobFS Requested:\s+(?P<jobfs_requested>\S+)"
#        "(\s+)JobFS used:\s*(?P<jobfs_used>\S+)\s*$"
        ), re.MULTILINE)

    def __init__(self, o_file_path):
        self._parsefile(o_file_path)

    def _parsefile(self, o_file_path):
        with open(o_file_path, 'r') as infile:
            content = infile.read()

      
        print(content)
        m = self.pattern.search(content)
        if m is not None:
            self.__dict__ = m.groupdict()
        else:
            print("Content did not match")

if __name__ == "__main__":
    path = sys.argv[1]
    rep = Report(path)
    print(rep.job_id)
    print(rep.project)
    print(rep.service_units)
