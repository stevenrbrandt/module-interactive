# Cling alternative
import sys
try:
    from termcolor import colored
except:
    def colored(txt,_):
        return txt
verstr = "%x" % sys.hexversion
verno = int(verstr[1:3])
import os
try:
    env = get_ipython().__class__.__name__
    from IPython.core.magic import register_cell_magic
except:
    def register_cell_magic(x):
        return x
    env = "text"
home = os.environ["HOME"]
clangw = os.path.join(home, "clangw")
with open(clangw+".mk","w") as fd:
    print("OBJ = %s.o" % clangw, file=fd)
    print("PCM = %s.pcm" % clangw, file=fd)
    print("""
OBJ = /home/jovyan/clangw.o
PCM = /home/jovyan/clangw.pcm
SHARED = /home/jovyan/clangw.so
PYVER = {verno}

SRC_DIR = /usr/local/src
OBJ_SRC = $(SRC_DIR)/clangw.cpp
PCM_SRC = $(SRC_DIR)/clangw.cppm
LIB_SRC = $(SRC_DIR)/clangwpy11.cpp
SEG_H = $(SRC_DIR)/Seg.hpp
all : $(OBJ) $(PCM) $(SHARED)

$(OBJ) : $(OBJ_SRC) $(SEG_H)
	clang++ -fPIC -I/usr/include/python3.$(PYVER) -I$(SRC_DIR) -std=c++2a -fmodules-ts -o $(OBJ) -c $(OBJ_SRC) -fimplicit-modules -fimplicit-module-maps -stdlib=libc++ -stdlib=libc++ -DBOOST_DISABLE_ASSERTS

$(PCM) : $(PCM_SRC)
	clang++ -fPIC -I/usr/include/python3.$(PYVER) -I$(SRC_DIR) --std=c++2a -fmodules-ts --precompile -x c++-module -o $(PCM) -c $(PCM_SRC) -fimplicit-modules -fimplicit-module-maps -stdlib=libc++ -DBOOST_DISABLE_ASSERTS

$(SHARED) : $(OBJ)
	clang++ -I/usr/include/python3.$(PYVER) -fPIC -fmodules-ts -fimplicit-modules -fimplicit-module-maps --std=c++2a -stdlib=libc++ -lrt -shared -o $(SHARED) $(OBJ) $(LIB_SRC)

clean :
	rm -f $(OBJ) $(PCM)
""".format(verno=verno), file=fd)

import sys
from subprocess import Popen, PIPE, call 
import re
from time import time
from random import randint
p = Popen(["make","-f",clangw+".mk"],stdout=PIPE, stderr=PIPE, universal_newlines=True)
out, err = p.communicate()
#print(out, err)

session = "pid"+str(os.getpid())
sequence = 0
verbosity = 0
appflags = []
modflags = []
cxx_std = "-std=c++2a"

def expand_flags(line):
    while True:
        h = globals()
        g = re.match(r'{(\w+)}', line)
        if g:
            name = g.group(1)
            assert name in globals()
            line = line[:g.start()] + str(h[name]) + line[:g.end()]
            h[name] = ''
        else:
            return line

def showfile(fname):
    with open(fname, "r") as fd:
        contents = fd.read()
    print(colored(contents,"yellow"))

def run_cmd(args):
    if verbosity > 0:
        print(colored(" ".join(args),"cyan"))
    p = Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    out, err = p.communicate()
    if out.strip() != "":
        print(out,end='')
    if err.strip() != "":
        print(colored(err,"red"))
    return p.returncode

for fname in os.listdir("."):
    g = re.search(r'pid(\d+)', fname)
    if g:
        pid = int(g.group(1))
        try:
            os.kill(pid, 0)
        except:
            # Clean up old files
            os.remove(fname)

headers = []

def rm(fname):
    if os.path.exists(fname):
        os.remove(fname)

def rm_headers(code):
    global headers
    while True:
        g = re.search(r'^\s*(#include (<[^>]*>|"[^"]*")|\bimport (\w+|<[^>]*>);)\s*', code)
        if g:
            new_code = code[0:g.start()] + code[g.end():]
            header = g.group(0).strip()
            if header not in headers:
                headers += [header]
            code = new_code
        else:
            return code

def def_code_(line, cell):
    global sequence, headers
    sections = re.split(r'(?m)^%%lib\s*$', cell)
    code = sections[0].strip()+'\n'
    if len(sections) == 2:
        lib_code = sections[1].strip()
    else:
        lib_code = ''
    flags = re.split(r'\s+', expand_flags(line.strip()))
    has_export = re.search(r'(?m)^\s*export\b', code)
    sequence += 1
    headers_len = len(headers)
    if not has_export:
        code = rm_headers(code)
    with open('tmp%s-%d.cppm' % (session, sequence), 'w') as fd:
        print("export module tmp%d;" % sequence, file=fd)
        if sequence > 1:
            print("export import tmp%d;" % (sequence-1), file=fd)
        else:
            print("export import clangw; // initial load", file=fd)
        for h in headers:
            print(h, file=fd)
        if has_export:
            headers = headers[:headers_len]
        if not has_export:
            print("export {", file=fd)
        print(code, file=fd)
        if not has_export:
            print("}", file=fd)
    if verbosity > 1:
        showfile('tmp%s-%d.cppm' % (session, sequence))
    cmd = ["clang++","-DBOOST_DISABLE_ASSERTS",cxx_std,"-fmodules-ts","--precompile","-x","c++-module"]
    cmd += ["-c","tmp%s-%d.cppm" % (session, sequence)]
    cmd += ["-fimplicit-modules","-fimplicit-module-maps","-stdlib=libc++"]
    if sequence > 1:
        cmd += ["-fmodule-file=tmp%s-%d.pcm" % (session, sequence-1)]
    else:
        cmd += ["-fmodule-file=%s/clangw.pcm"  % home]
    cmd += modflags + flags
    r = run_cmd(cmd)
    if r != 0:
        sequence -= 1
        return
    with open('tmp%s-%d.cpp' % (session, sequence), 'w') as fd:
        if sequence > 1:
            print("import tmp%d;" % (sequence-1), file=fd)
        else:
            print("import clangw;", file=fd)
        for h in headers:
            print(h, file=fd)
        print(code, file=fd)
        print(lib_code, file=fd)
    if verbosity > 1:
        showfile('tmp%s-%d.cpp' % (session, sequence))
    exec_file = "exec_ar_%s.a" % session
    if sequence == 1: # zzz
        cmd = ["ar", "cr", exec_file, clangw+".o"]
        run_cmd(cmd)
    cmd = ["clang++","-DBOOST_DISABLE_ASSERTS",cxx_std,"-fmodules-ts"]
    cmd += ["-c","tmp%s-%d.cpp" % (session, sequence)]
    cmd += ["-fimplicit-modules","-fimplicit-module-maps","-stdlib=libc++"]
    if sequence > 1:
        if os.path.exists(exec_file):
            cmd += [exec_file, "-Wno-unused-command-line-argument"]
        cmd += ["-fmodule-file=tmp%s-%d.pcm" % (session, sequence-1)]
    else: # yyy
        cmd += ["exec_ar_%s.a" % session,"-Wno-unused-command-line-argument"]
        cmd += ["-fmodule-file=%s/clangw.pcm" % home]
        #cmd += ["%s/clangw.o" % home]
    cmd += modflags + flags
    r = run_cmd(cmd)
    if r != 0:
        sequence -= 1
        return
    cmd = ["ar","r",exec_file,"tmp%s-%d.o" % (session, sequence)]
    r = run_cmd(cmd)
    if r != 0:
        sequence -= 1

@register_cell_magic
def def_code(line, cell):
    t1 = time()
    try:
        return def_code_(line, cell)
    finally:
        rm("tmp%s-%d.o" % (session, sequence))
        t2 = time()
        print(colored("compile time: %.2f" % (t2-t1),"green"))

def run_code_(line, code):
    global sequence, headers
    flags = re.split(r'\s+', expand_flags(line.strip()))
    t1 = time()
    headers_len = len(headers)
    code = rm_headers(code)
    with open('exec_step_%s.cpp' % session, 'w') as fd:
        if sequence > 0:
            print("import tmp%d;" % sequence, file=fd)
        else:
            print("import clangw;",file=fd)
        for h in headers:
            print(h, file=fd)
        headers = headers[:headers_len]
        print("int main() {", file=fd)
        print(code, file=fd)
        print("return 0; }", file=fd)
    if verbosity > 1:
        showfile('exec_step_%s.cpp' % session)
    cmd = ["clang++","-DBOOST_DISABLE_ASSERTS",cxx_std,"-fmodules-ts","-lrt",
      "-o","exec_step_%s" % session, "exec_step_%s.cpp" % session]
    cmd += appflags + flags
    cmd += ["-fimplicit-modules","-fimplicit-module-maps","-stdlib=libc++","-lpthread"]
    if sequence > 0:
        cmd += ["-fmodule-file=tmp%s-%d.pcm" % (session, sequence), "exec_ar_%s.a" % session]
        cmd += ["-Wno-unused-command-line-argument"]
    else:# yyy
        cmd += ["-fmodule-file=%s/clangw.pcm" % home]
        cmd += ["%s/clangw.o" % home]
    r = run_cmd(cmd)
    t2 = time()
    if r == 0:
        run_cmd(["./exec_step_%s" % session])
    t3 = time()
    print(colored("compile time: %.2f" % (t2-t1),"green"))
    print(colored("run time: %.2f" % (t3-t2),"green"))

@register_cell_magic
def run_code(line, code):
    t1 = time()
    try:
        return run_code_(line, code)
    finally:
        t2 = time()

if __name__ == "__main__":
    verbosity = 2
    def_code("","""
import <functional>;
extern void runme(std::function<void()> func);
%%lib
//#include <boost/interprocess/managed_shared_memory.hpp>
void runme(std::function<void()> func) {
    func();
}
""")
    run_code("","""
import <iostream>;
runme([](){ std::cout << "hello" << std::endl; });
""")
    run_code("","""
Seg seg("foo");
""")
