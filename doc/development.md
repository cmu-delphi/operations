# Delphi Developer Guide

Welcome! This guide is written to help you develop for Delphi. For first-time
setup, see [the setup section](#setup). Otherwise, for an overview of a typical
workflow, skip ahead to [the workflow section](#workflow).

_This guide is focused on python development under linux._

## setup

### install docker

Using [Docker](https://www.docker.com/), we'll make a local environment that
closely resembles the Delphi server and is totally isolated from everything
else on your local system. This has a number of benefits, including:

- You don't have to install packages on your personal machine that you might
not want or need (except for docker, of course).
- You don't have to worry about conflicts between what's installed on your
personal machine and what's installed on the server.
- Because everyone uses the same environment, bugs are easier to reproduce and
fix.
- Using a standardized development environment makes it faster and easier for
new developers to join the effort.

Visit [the site](https://www.docker.com/) and follow the instructions there to
get docker installed on your system. Once done, you should be able to check
that it's installed like this:

```bash
docker --version
```

#### some docker concepts

In docker terminology, an "image" is to an executable as a "container" is to a
process. That is, to _use_ an image, you instantiate a container based on that
image. The executable/process analogy is apt, as docker containers _are_
processes. It's tempting to think of a container as a virtual machine, but it's
much simpler than that. **A container is just a process.** It's a process which
is isolated from the rest of your machine by the kernel.

### create a workspace

Pick a nice home for Delphi work on your local filesystem (e.g. a fresh
directory named something like `my-delphi-project`).

Clone the various Delphi and supporting repos, including this one. Not all
repos are required in all cases, but since the dependency graph is
undocumented, it's safest to grab them all unless you know specifically which
subset of repos you need. (If you get a different set of repos, you'll have to
make corresponding changes to the `Dockerfile`.)

#### everyone

Note that the commands below pull everything directly from `cmu-delphi`. This
is fine for the repos you _don't_ need to modify. However, for the particular
repo that you _do_ need to modify, best practice is to:

1. On GitHub: fork the repo you need to work on
2. Locally: `git clone` _your fork_ of the repo
3. Locally: write, test, commit, and `git push` to _your fork_ of the repo
4. On GitHub: submit a pull request to merge your modified fork back into the
original `cmu-delphi` repo

#### delphi members only

Alternatively, if you have push access to Delphi repos, you can skip forking
and clone directly from `cmu-delphi`. However you should do all development in
your own branch. After pushing your branch, you should then submit a pull
request to merge your branch into the master branch. This will allow the rest
of the team to participate in code review. **You should not push to master as
this will bypass code review.** It is perfectly acceptable to use the fork
approach even if you have push access in `cmu-delphi`.

#### cloning repositories

```bash
# collect everything in a directory called "repos"
mkdir repos && cd repos

# NOTE: Fork the repo you want to work on, and clone it from there instead of
# cloning it from `cmu-delphi`.

# delphi python (sub)packages
mkdir delphi && cd delphi
git clone https://github.com/cmu-delphi/operations
git clone https://github.com/cmu-delphi/utils
git clone https://github.com/cmu-delphi/github-deploy-repo
git clone https://github.com/cmu-delphi/delphi-epidata
git clone https://github.com/cmu-delphi/flu-contest
git clone https://github.com/cmu-delphi/nowcast
cd ..

# third-party (sub)packages
mkdir undefx && cd undefx
git clone https://github.com/undefx/py3tester
git clone https://github.com/undefx/undef-analysis
cd ..

# go back up to the workspace root
cd ..
```

Link the docker build files into the root of the workspace.

```bash
ln -s repos/delphi/operations/dev/docker/delphi_img/* .
```

Your workspace should now look like this:

```bash
tree -L 3 .
```

```
.
├── assets -> repos/delphi/operations/dev/docker/delphi_img/assets
├── Dockerfile -> repos/delphi/operations/dev/docker/delphi_img/Dockerfile
└── repos
    ├── delphi
    │   ├── delphi-epidata
    │   ├── flu-contest
    │   ├── github-deploy-repo
    │   ├── nowcast
    │   ├── operations
    │   └── utils
    └── undefx
        ├── py3tester
        └── undef-analysis

12 directories, 1 file
```

## workflow

### overview

The development process is generally outlined as follows:

1. Write code and tests!
2. Create a docker image containing your latest changes.
3. Run unit tests in a docker container. Loop back to step 1 as needed.
4. Send a pull request for code review. Loop back to step 1 to address reviewer
feedback.
5. Merged code is automatically deployed to the Delphi server.

The remainder of this section focuses on the docker-specific steps,
particularly for testing.

### about testing

While unit testing in general is outside the scope of this document, here are
some highlights:

- For the general pattern to follow, see existing unit tests in other delphi
repos. In a nutshell:
  - there is one test file per source file, named like "test_[name].py"
  - test files live in a directory structure under `tests/` that exactly
  mirrors the sources in `src/`
  - the fully-qualified module name of the file to be tested is given in the
  unit test, as this is required to assess code coverage
  - unit test classes must extend python's built-in unit test class
  - individual test functions must be named with a leading "test_" and should
  contain a descriptive phrase (e.g. "test_fetch_data_handles_http404")
- In terms of line coverage, a commonly quoted rule of thumb is to aim for
80% coverage.
- Tests should be reasonably well documented. This aids in debugging failing
tests and helps curb the urge under pressure to simply delete failing tests.
- Tests should be deterministic. One of the most obvious sources of
nondeterminism is a random number generator. More subtle (and insidious)
sources of nondeterminism include conversion of unordered collections to
ordered collections and operations involving timing.
- Tests should be lightweight, not involving I/O. Best practice is to avoid
network and database operations, instead replacing those things with stand-in
fakes that are under direct control of the test. This helps tests remain
deterministic and fast.

**For new code and modifications to existing code, unit tests are considered
required by default, unless deemed otherwise during code review.** For untested
legacy code, it is recommended to add tests opportunistically. All tests must
pass in the master git branch, otherwise automatic deployment to the Delphi
server will (intentionally) fail.

### creating an image

To create the image, simply run the `docker build` command in the root of your
workspace:

```bash
docker build -t delphi_img .
```

It may take a few minutes to build the image for the first time as a large
number of packages need to be installed. This installation happens in an
intermediate image, which is cached and reused. Subsequent builds (e.g. when
iterating on coding and testing) should be very fast.

In addition to a success message at the end of the command output, you can
verify that the image was built by using the `docker images` command:

```bash
docker images
```

```
REPOSITORY             TAG                 IMAGE ID            CREATED             SIZE
delphi_img             latest              764f9ebf827d        4 minutes ago       1.28GB
```

### running a container

Tests, and the code they invoke, are confined within a docker container that is
instantiated from the image you created above. This ensures that code runs in
an environment that's very similar to the Delphi server, and it prevents
unwanted side-effects (e.g. filesystem modifications) on your personal machine.

Finally, a quick note on container lifecycles. By default, the docker engine
will persist container state to disk when execution ends. This is helpful in
some contexts, like when you want to "resume" a container without starting from
a blank slate. For testing, we actually _want_ to start from a blank slate each
time. To tell the docker engine that the container's state (e.g. any files it
may have written, etc.) should be discarded, use the `--rm` flag.

A container can be launched with the `docker run` command. For example, here's
how to show the usage information for the test driver:

```bash
docker run --rm delphi_img python3 -m undefx.py3tester.py3tester --help
```

For clarity, here's the anatomy of the above command:

- `docker run [options] delphi_img` means we're instantiating a container from
the latest version of the `delphi_img` image
  - `--rm` tells the docker engine to _not_ persist container state, as
discussed above
- `python3 [options]` runs the executable `python3` that's located _inside the
image_ (i.e. not your personal version in e.g. `/usr/bin`)
  - `-m undefx.py3tester.py3tester` is a flag that tells the python interpreter
  where _in the image_ to find the main entry point of our program
  - `--help` is a flag that our program knows how to handle, which it does by
  printing usage information

Unit tests are run by passing options and a path to the `py3tester` script in
the container. For example, here's how to run all unit tests recursively in the
`nowcast` repo:

```bash
docker run --rm delphi_img python3 -m undefx.py3tester.py3tester --color repos/delphi/nowcast/tests
```

```
[lots of output omitted for brevity]

✔ All tests passed! 59% (795/1334) coverage.
```

The following command shows how to run tests in just a single file, and it also
generates a full line-by-line coverage report (flag `--full`):

```bash
docker run --rm delphi_img python3 -m undefx.py3tester.py3tester --color --full repos/delphi/nowcast/tests/fusion/test_fusion.py
```

```
[some output omitted for brevity]

Test results for:
 delphi.nowcast.fusion.fusion (delphi/nowcast/fusion/fusion.py)
Unit:
 nowcast.tests.fusion.test_fusion.UnitTests.test_determine_statespace: pass
 nowcast.tests.fusion.test_fusion.UnitTests.test_eliminate: pass
 nowcast.tests.fusion.test_fusion.UnitTests.test_extract: pass
 nowcast.tests.fusion.test_fusion.UnitTests.test_fuse: pass
 nowcast.tests.fusion.test_fusion.UnitTests.test_matmul: pass
 error: 0
  fail: 0
  skip: 0
  pass: 5

[coverage map omitted for brevity]

✔ All tests passed! 100% (14/14) coverage.
```

Finally, you can run _all_ Delphi tests by not specifying any particular repo.
This make take some time (which is one reason why tests should be lightweight).

```bash
docker run --rm delphi_img python3 -m undefx.py3tester.py3tester --color repos/delphi
```

```
[tons of output omitted for brevity]

✔ All tests passed! 56% (1346/2395) coverage.
```

One last aside: the coverage figure quoted above is a bit optimistic. While the
numerator accurately indicates that 1346 lines are covered by tests, the
denominator only accounts for the 2395 total lines _in files that are tested_.
There are unfortunately many files that aren't tested at all, and those lines
don't show up in the coverage denominator.
