import os, sys
import subprocess
from cStringIO import StringIO
from sets import Set
import re

arch_re_string = '(?P<archs>\[.+?\])'
vers_re_string = '(?P<version>\(.+?\))'
package_re_string = '(?P<package>\S+)'

bd_re_string = '(?P<package>\S+)\s*(?P<version>\(.+?\))*\s*(?P<archs>\[.+?\])*\s*'
#bd_re_string = '^%s\s%s*%s*$' % (package_re_string, vers_re_string, arch_re_string)
bd_re = re.compile(bd_re_string)


ARCHS = ['i386']

def get_archs(archs):
    "archs is '[foo bar i386]'"
    return archs[1:-1].split()

def getoutput(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    data = ''
    while proc.poll() is None:
        data += proc.stdout.read(1024)
    if not proc.returncode:
        return data
    else:
        raise RuntimeError, "%s returned %d" % (' '.join(cmd), proc.returncode)
    
def showsrc(package):
    cmd = ['apt-cache', 'showsrc', package]
    return getoutput(cmd)

def pkgthere(package):
    cmd = ['apt-cache', 'showpkg', package]
    proc = subprocess.Popen(cmd, stdout=file(os.devnull))
    returncode = proc.wait()
    if returncode:
        return False
    else:
        return True
    

def get_builddeps(package):
    src = StringIO(showsrc(package))
    lines = [line for line in src if line.startswith('Build-Depends')]
    deps = []
    for line in lines:
        end_fragment = line.split(':')[1]
        # strip extra white space and endl
        fragments = [f.strip() for f in end_fragment.split(',')]
        # strip
        #fragments = [f.split(',')[0] for f in fragments]
        for fragment in fragments:
            if '|' in fragment:
                subs = [f.strip() for f in fragment.split('|')]
                for sub in subs:
                    if sub:
                        deps.append(sub)
            else:
                if fragment:
                    deps.append(fragment)
    return deps
    
def parse_builddeps(deps):
    packages = []
    for dep in deps:
        match = bd_re.match(dep)
        if match is None:
            raise RuntimeError, "no match for %s" % dep
        package = match.groupdict()['package']
        if package is None:
            raise RuntimeError, "No Package for %s" % dep
        archs = match.groupdict()['archs']
        if archs is not None:
            archs = get_archs(archs)
            append = False
            for arch in ARCHS:
                if arch in archs:
                    append = True
            if append:
                if pkgthere(package):
                    packages.append(package)
                else:
                    print "package", package, "not found"
        else:
            if pkgthere(package):
                packages.append(package)
            else:
                print "package", package, "not found"
    return packages

            
    

def get_packages():
    cmd = ['dpkg', '--get-selections']
    output = StringIO(getoutput(cmd))
    packages  = [line.split()[0] for line in output]
    return packages

def get_all_builddeps():
    packages = get_packages()
    all = Set()
    current = [line.strip() for line in file('builddeps')]
    for package in current:
        all.add(package)
    for package in packages:
        builddeps = get_builddeps(package)
        builddeps = parse_builddeps(builddeps)
        for dep in builddeps:
            if dep not in all:
                if dep not in packages:
                    all.add(dep)
                    print "In package", package, "added", dep, "total", len(all)
        pkgs = list(all)
        pkgs.sort()
        f = file('builddeps', 'w')
        for p in pkgs:
            f.write('%s\n' % p)
        f.close()
    all = list(all)
    all.sort()
    return all


if __name__ == '__main__':
    packages = get_packages()
    bd = get_builddeps('gcc-4.1')
    bp = parse_builddeps(bd)
    #all = get_all_builddeps()
    deps = get_all_builddeps()
    
    
        
    
