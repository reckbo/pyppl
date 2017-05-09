from plumbum import cli, local
from pipelib_cli import readAndSetSrcPaths, printVertical
from pipelib_cli.params import readComboPaths
from pipelib_cli.subcmd.symlink import toSymlink
import logging
import pipelib
import sys


class Ls(cli.Application):
    csv = cli.Flag(
        ['-c', '--csv'],
        excludes=['-s'],
        help="Print subject ids and paths separated by comma")
    caseids = cli.Flag(
        ['-s', '--subjid'],
        excludes=['-c'],
        help="Print subject ids instead of paths")
    printFull = cli.Flag(
        ['-p'], excludes=['-s'], help="Print full paths instead of symlinks.")

    def main(self, *keys):
        readAndSetSrcPaths()
        for comboPaths in readComboPaths(self.parent.paramsFile):
            logging.info("## Parameter Combination {} ({} subjects)".format(
                comboPaths['paramId'], comboPaths['num']))
            printVertical(comboPaths['paramCombo'])

            for key in keys:
                if key not in comboPaths['paths'].keys():
                    raise Exception("Key '{}' not defined for this pipeline")

            if not self.csv:
                for k, vs in comboPaths['paths'].iteritems():
                    if k not in keys:
                        continue
                    existingPaths = [p
                                    for p in filter(lambda x: x.path.exists(), vs)
                                    ]
                    for p in existingPaths:
                        if self.caseids:
                            print('{}'.format(p.caseid))
                            continue
                        elif self.csv:
                            sys.stdout.write('{},'.format(p.caseid))
                        if self.printFull:
                            print(p.path)
                        else:
                            symlink = toSymlink(p.caseid, self.parent.name, k,
                                                p.path, comboPaths['paramId'])
                            print(symlink)

            else:
                for i, caseid in enumerate(comboPaths['caseids']):
                    ps = [comboPaths['paths'][key][i] for key in keys]
                    if not all(p.path.exists() for p in ps):
                        continue
                    sys.stdout.write('{}'.format(caseid))
                    for p in ps:
                        if self.printFull:
                            path = p.path
                        else:
                            path = toSymlink(p.caseid, self.parent.name, p.pipelineKey,
                                                p.path, comboPaths['paramId'])
                        sys.stdout.write(',{}'.format(path))
                    sys.stdout.write('\n')
