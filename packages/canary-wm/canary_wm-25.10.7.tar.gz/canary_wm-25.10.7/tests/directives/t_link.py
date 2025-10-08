# Copyright NTESS. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: MIT

import glob
import os
import sys

from _canary.util.executable import Executable
from _canary.util.filesystem import touch
from _canary.util.filesystem import working_dir


def test_link(tmpdir):
    with working_dir(tmpdir.strpath, create=True):
        touch("foo.txt")
        touch("baz.txt")
        with open("a.pyt", "w") as fh:
            fh.write("import os\n")
            fh.write("import sys\n")
            fh.write("import canary\n")
            fh.write("canary.directives.link('foo.txt', 'baz.txt')\n")
            fh.write("def test():\n")
            fh.write("    assert os.path.islink('./foo.txt')\n")
            fh.write("    assert os.path.islink('./baz.txt')\n")
            fh.write("if __name__ == '__main__':\n    sys.exit(test())\n")
        python = Executable(sys.executable)
        python("-m", "canary", "run", "-w", ".", fail_on_error=False)
        if python.returncode != 0:
            files = os.listdir("./TestResults/a")
            raise ValueError(f"test failed. files in working directory: {files}")


def test_link_rename(tmpdir):
    with working_dir(tmpdir.strpath, create=True):
        touch("foo.txt")
        touch("baz.txt")
        with open("a.pyt", "w") as fh:
            fh.write("import os\n")
            fh.write("import sys\n")
            fh.write("import canary\n")
            fh.write("canary.directives.link(src='foo.txt', dst='foo_link.txt')\n")
            fh.write("canary.directives.link(src='baz.txt', dst='baz_link.txt')\n")
            fh.write("def test():\n")
            fh.write("    assert os.path.islink('./foo_link.txt')\n")
            fh.write("    assert os.path.islink('./baz_link.txt')\n")
            fh.write("if __name__ == '__main__':\n    sys.exit(test())\n")
        python = Executable(sys.executable)
        python("-m", "canary", "run", "-w", ".", fail_on_error=False)
        if python.returncode != 0:
            files = os.listdir("./TestResults/a")
            raise ValueError(f"test failed. files in working directory: {files}")


def test_link_rename_rel(tmpdir):
    wd = os.path.join(tmpdir.strpath, "test_link_rename_rl")
    with working_dir(wd, create=True):
        touch("../foo.txt")
        touch("../baz.txt")
        with open("a.pyt", "w") as fh:
            fh.write("import os\n")
            fh.write("import sys\n")
            fh.write("import canary\n")
            fh.write("canary.directives.link(src='../foo.txt', dst='foo_link.txt')\n")
            fh.write("canary.directives.link(src='../baz.txt', dst='baz_link.txt')\n")
            fh.write("def test():\n")
            fh.write("    assert os.path.islink('./foo_link.txt')\n")
            fh.write("    assert os.path.islink('./baz_link.txt')\n")
            fh.write("if __name__ == '__main__':\n    sys.exit(test())\n")
        python = Executable(sys.executable)
        python("-m", "canary", "run", "-w", ".", fail_on_error=False)
        if python.returncode != 0:
            files = os.listdir("./TestResults/a")
            raise ValueError(f"test failed. files in working directory: {files}")


def test_link_rename_rel_vvt(tmpdir):
    wd = os.path.join(tmpdir.strpath, "test_link_rename_rl")
    with working_dir(wd, create=True):
        touch("../foo.txt")
        touch("../baz.txt")
        with open("a.vvt", "w") as fh:
            fh.write("# VVT: link (rename) : ../foo.txt,foo_link.txt\n")
            fh.write("# VVT: link (rename) : ../baz.txt,baz_link.txt\n")
            fh.write("import os\n")
            fh.write("import sys\n")
            fh.write("def test():\n")
            fh.write("    assert os.path.islink('./foo_link.txt')\n")
            fh.write("    assert os.path.islink('./baz_link.txt')\n")
            fh.write("if __name__ == '__main__':\n    sys.exit(test())\n")
        python = Executable(sys.executable)
        python("-m", "canary", "run", "-w", ".", fail_on_error=False)
        if python.returncode != 0:
            files = os.listdir("./TestResults/a")
            print(open("./TestResults/a/canary-out.txt").read())
            raise ValueError(f"test failed. files in working directory: {files}")


def test_link_when(tmpdir):
    with working_dir(tmpdir.strpath, create=True):
        touch("foo.txt")
        touch("baz.txt")
        with open("a.pyt", "w") as fh:
            fh.write(
                """\
import os
import sys
import canary
canary.directives.parameterize('a', ('baz', 'foo'))
canary.directives.parameterize('b', (1, 2))
canary.directives.link('foo.txt', when={'parameters': 'a=foo and b=1'})
canary.directives.link('baz.txt', when='parameters="a=baz and b=1"')
canary.directives.link(src='foo.txt', dst='foo-b2.txt', when={'parameters': 'a=foo and b=2'})
canary.directives.link(src='baz.txt', dst='baz-b2.txt', when='parameters="a=baz and b=2"')
def test():
    self = canary.get_instance()
    if self.parameters[('a', 'b')] == ('foo', 1):
        assert os.path.islink('foo.txt')
    elif self.parameters[('a', 'b')] == ('baz', 1):
        assert os.path.islink('baz.txt')
    elif self.parameters[('a', 'b')] == ('foo', 2):
        assert os.path.islink('foo-b2.txt')
    elif self.parameters[('a', 'b')] == ('baz', 2):
        assert os.path.islink('baz-b2.txt')
if __name__ == '__main__':
    sys.exit(test())
"""
            )

        def txtfiles(d):
            basename = os.path.basename
            files = glob.glob(os.path.join(tmpdir, d, "*.txt"))
            return sorted([basename(f) for f in files if not basename(f).startswith("canary-")])

        python = Executable(sys.executable)
        python("-m", "canary", "run", "-w", ".", fail_on_error=False)

        p = python("-m", "canary", "-C", "TestResults", "location", "a.a=foo.b=1", stdout=str)
        assert txtfiles(p.out.strip()) == ["foo.txt"]
        p = python("-m", "canary", "-C", "TestResults", "location", "a.a=foo.b=2", stdout=str)
        assert txtfiles(p.out.strip()) == ["foo-b2.txt"]
        p = python("-m", "canary", "-C", "TestResults", "location", "a.a=baz.b=1", stdout=str)
        assert txtfiles(p.out.strip()) == ["baz.txt"]
        p = python("-m", "canary", "-C", "TestResults", "location", "a.a=baz.b=2", stdout=str)
        assert txtfiles(p.out.strip()) == ["baz-b2.txt"]

        if python.returncode != 0:
            files = os.listdir("./TestResults/a")
            raise ValueError(f"test failed. files in working directory: {files}")
