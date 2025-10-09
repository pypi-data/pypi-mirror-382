import jinja2

import itertools
import json
import os
import pathlib
import types

def intersect(l0, l1):
  return sorted(frozenset(l0) & frozenset(l1))

def filterout(l0, l1):
  return sorted(frozenset(l1) - frozenset(l0))

def out_of_date(target, source, verbose=False):
  if not os.path.exists(target):
    if verbose:
      print("njinja: not found:", target)
    return True
  if not os.path.exists(source):
    return True
  ttime = os.path.getmtime(target)
  if ttime < os.path.getmtime(source):
    if verbose:
      print("njinja: out-of-date:", target, "vs", source)
    return True
  if os.path.isdir(source):
    # if target is a directory, check all subdir modtimes too
    for p, dd, _ in os.walk(source):
      for d in dd:
        if ttime < os.path.getmtime(os.path.join(p, d)):
          return True
  return False

class BuildConfig(object):
  """Tracks which files and directories we scanned to configure the build.

  You should use the methods in this class and not `open()` or `os.walk()`
  directly, when configuring the build. Then, use `collect_config()` to
  generate a context dict for your build.ninja.j2.
  """
  def __init__(self):
    self.used_files = {}
    self.used_dirs = {}

  def used(self):
    return itertools.chain(self.used_files.keys(), self.used_dirs.keys())

  def open(self, file, *args, **kwargs):
    """Tracked version of `open()`."""
    self.used_files[file] = None
    return open(file, *args, **kwargs)

  def walk_files(self, base):
    """Tracked version of `os.walk()` that returns only files."""
    self.used_dirs[base] = None
    for p, _, ff in os.walk(base):
      for f in ff:
        yield os.path.join(p, f)

  def walk_dirs(self, base):
    """Tracked version of `os.walk()` that returns only directories."""
    self.used_dirs[base] = None
    if os.path.isdir(base):
      yield base
    for p, dd, _ in os.walk(base):
      for d in dd:
        yield os.path.join(p, d)

  def rel_vars(self, bases, path):
    p = pathlib.Path(path)
    for n, d in bases.items():
      dp = pathlib.Path(d)
      if dp == p or dp in p.parents:
        rp = os.path.relpath(p, d)
        return "$"+n if rp == "." else os.path.join("$"+n, rp)
    return path

  def examine_deps(self, ctx, extra_dirs=[]):
    bases = {}
    # figure out which variables correspond to which used directories
    for u in list(self.used_dirs.keys()) + extra_dirs:
      for k, v in ctx.items():
        if u == v:
          bases[k] = v
    # to depend on a directory means to depend on the list of files of that directory (and its subdirs)
    # ninja doesn't apply recursion logic to directory dependencies, so we do it here
    return [self.rel_vars(bases, d)
      for x in self.used()
      for d in (self.walk_dirs(x) if os.path.isdir(x) else [x])]

  def collect_config(self, local_, global_, global_filter=lambda _: True, extra_dirs=[]):
    """Collect a context dict for your build.ninja.j2 template.

    The files and directories that were opened or scanned, are added into the
    dict under the CONFIGURE_DEPS key. When used with something similar to our
    example build.ninja.j2, this helps the meta-build avoid performing these
    filesystem operations and/or regenerating build.ninja unless absolutely
    necessary i.e. something changed.

    The natural thing is to pass the result of this to `mk_ninja()`.
    """
    ctx = {
      k: v
      for k, v in global_.items()
      if k.isupper() and global_filter(k)
    } | {
      k: v
      for k, v in local_.items()
      if k.isupper() and not callable(v)
    }
    ctx["CONFIGURE_DEPS"] = self.examine_deps(ctx, extra_dirs=extra_dirs)
    return ctx

def nj_q(f, var=True):
  """Quote function for the body of a ninja rule.

  # https://ninja-build.org/manual.html#ref_lexer
  """
  if var and f[0] == "$":
    # don't escape values that start with a ninja variable
    return "$" + f[1:].replace("$", "$$").replace("\n", "$\n")
  else:
    return f.replace("$", "$$").replace("\n", "$\n")

def nj_qi(f):
  """Quote function for the inputs of a ninja rule.

  # https://ninja-build.org/manual.html#ref_lexer
  """
  return nj_q(f).replace(" ", "$ ")

def nj_qo(f):
  """Quote function for the outputs of a ninja rule.

  # https://ninja-build.org/manual.html#ref_lexer
  """
  return nj_qi(f).replace(":", "$:")

def mk_qio(f):
  """Quote function for depfiles.

  Syntax check:
  $ gcc -M 'test lol%#*$\#*$[|: wtf.c'
  test\ lol%\#*$$\\#*$$[|:\ wtf.o: test\ lol%\#*$$\\#*$$[|:\ wtf.c
  # Same result with clang

  Note that this output cannot actually parsed by GNU make because their whole
  ecosystem is a piece of inconsistent shit and that's why we're ditching it
  for ninja-build. (To be precise, GNU make expects that \|: are also escaped.)

  https://github.com/ninja-build/ninja/issues/168 does something slightly
  different but that is their problem and in the source code they say they will
  fix things on their side if the problem becomes apparent with real examples.
  https://github.com/ninja-build/ninja/blob/master/src/depfile_parser.cc#L48
  """
  return f.replace(" ", r"\ ").replace("#", r"\#").replace("$", "$$")

def njinjify(j2env, depfile=None):
  j2env.filters |= {
    "nj_q": nj_q,
    "nj_qi": nj_qi,
    "nj_qo": nj_qo,
  }
  j2env.globals |= {
    "path_exists": os.path.exists,
    "path_join": os.path.join,
    "relpath": os.path.relpath,
    "map": map,
    "zip": zip,
  }

  if depfile:
    # monkeypatch j2env to track dependencies on other files
    # TODO: drop after https://github.com/pallets/jinja/pull/1776
    j2env._parsed_names = []
    old_parse = j2env._parse
    def _parse(self, source, name, filename):
      if name is not None:
          self._parsed_names.append(name)
      return old_parse(source, name, filename)
    j2env._parse = types.MethodType(_parse, j2env)
  return j2env

class FileLoader(jinja2.BaseLoader):
  def get_source(self, env, tpl):
    mtime = os.path.getmtime(tpl)
    with open(tpl) as fp:
      return (fp.read(), tpl, lambda: mtime == os.path.getmtime(tpl))

def run_j2(infile, ctx, outfile, depfile=None, outjson=None, j2env=None, headers=None):
  j2env = j2env or jinja2.Environment()
  njinjify(j2env, depfile=depfile)

  if outjson:
    with open(outjson, "w") as fp:
      json.dump(ctx, fp, indent=2)

  result = j2env.overlay(loader=FileLoader()).get_template(infile).render(ctx)

  with open(outfile, 'w') as fp:
    if headers:
      for h in headers.format(**ctx).splitlines():
        fp.writelines(["# ", h, "\n"])
      fp.write("\n")
    # jinja templates strip trailing newline by default so we need print
    print(result, file=fp)

  if depfile:
    deps = j2env._parsed_names
    assert deps[0] == infile
    with open(depfile, 'w') as fp:
      print("%s: %s" % (mk_qio(outfile), " ".join(mk_qio(d) for d in deps)), file=fp)

def mk_ninja(infile, mk_config, builddir, outfile=None, depfile=None, cfgfile=None, headers=None, force=False):
  """Top-level API function for building build.ninja from your Jinja template

  infile
    Path to your build.ninja.j2 template
  mk_config
    Function that generates the context dictionary, e.g. by calling
    `BuildConfig.collect_config()`.
  builddir
    Build directory to place build.ninja
  outfile
    Optional output file, if not $builddir/${infile-stem}

    ${infile-stem} is $infile minus any final extension e.g. .j2
  depfile
    Optional dependency output file, if not $builddir/${infile-stem}.d
  cfgfile
    Optional context output file to write cfg into as a JSON object.
  headers
    List of comment lines to add at the start of the output
  returns
    Command-line to run; could be ninja or a null command. Caller should append
    any suitable ninja arguments to this list, e.g. build commands or targets.
  """
  basename = os.path.splitext(os.path.basename(infile))[0]
  outfile = outfile or os.path.join(builddir, basename)
  depfile = depfile or os.path.join(builddir, basename+".d")
  cfgfile = cfgfile or os.path.join(builddir, basename+".json")
  headers = headers or """This file was automatically generated. ANY EDITS WILL BE LOST.

input: %s
context: %s
""" % tuple(os.path.relpath(f, builddir) for f in (infile, cfgfile))
  if force or any(out_of_date(o, infile, verbose=True) for o in [outfile, depfile]):
    os.makedirs(builddir, exist_ok=True)
    print("njinja: configure:", cfgfile, depfile, outfile)
    cfg = mk_config()
    run_j2(
      infile, cfg, outfile,
      outjson=cfgfile,
      depfile=depfile,
      headers=headers)
    if force:
      # we are (likely) being called from ninja, so don't invoke it again
      return ["true"]
  return ["ninja", "-f", outfile]
