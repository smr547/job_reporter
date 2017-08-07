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
        ), re.MULTILINE)

    def __init__(self, o_file_path):
        self._parsefile(o_file_path)

    def _parsefile(self, o_file_path):
        with open(o_file_path, 'r') as infile:
            content = infile.read()

      
        print(content)
        m = self.pattern.search(content)
        if m is not None:
            self.job_id = m.group("job_id")
            self.project = m.group("project")
        else:
            print("Content did not match")

if __name__ == "__main__":
    path = sys.argv[1]
    rep = Report(path)
    print(rep.job_id)
    print(rep.project)
