# Frontend Development Guide

**Prerequisite:** this guide assumes that you have read the
[backend development guide](backend_development.md).

Frontend development for Delphi can be more challenging than backend
development for a number of reasons:

- Dynamic content is implemented with a combination of PHP and JavaScript,
  neither of which currently has unit test support at Delphi (unlike python,
  for example). This means we rely on integration tests, which provide more
  sparse coverage and are generally more complex.
- The serving stack consists of bulky and tightly-coupled components, like
  databases and web servers.
- Serving code is driven asynchronously by external requests.
- In the case of scripting and rendering, results are often device- and
  browser-dependent.

This guide provides an alternative to the perhaps tempting approach of
committing untested code accompanied by testing in production. Here, you'll
learn the basics of how to spin up a local instance of Delphi's serving stack
and run integration tests against that stack.

After reading this guide, much more in-depth guides to frontend development are
available for the
[Epidata API](https://github.com/cmu-delphi/delphi-epidata/blob/master/docs/epidata_development.md)
and for
[Crowdcast (aka Epicast)](https://github.com/cmu-delphi/www-epicast/blob/master/docs/epicast_development.md).

# setup

## docker

Install Docker and select an empty directory as your workspace per the
[backend development guide](backend_development.md#install-docker).

## networking

Frontend development involves the use of multiple coordinating containers (e.g.
apache and mysql), but by default containers can't see any other services
running on the host machine. To allow the containers to communicate with each
other, we need to use a virtual network. To separate Delphi instances from
other instances you may happen to be running, and to allow for resolution of
container instances by name (rather than by IP address), we'll create a new
"bridge" network. This is done using the `docker network` command.

```bash
docker network create --driver bridge delphi-net
```

You can verify that the network was created like this:

```bash
# show all networks
docker network ls

# show details for the `delphi-net` network
docker network inspect delphi-net
```

If you'd like to remove this network later, run:

```bash
docker network remove delphi-net
```

## repositories

For working on just about any frontend, you'll need at least two Delphi
repositories:

- [operations](https://github.com/cmu-delphi/operations), which contains
  `Dockerfile`s and assets for generic Delphi images
- the particular repo for the frontend that you want to work on, which contains
  `Dockerfile`s, assets, and integration tests specific to that frontend

# build images

For frontend development, you'll always need a web server, and usually a
database.

- The [`delphi_web` image](../dev/docker/web/README.md) builds a web server
  configured for Delphi frontends.
- The [`delphi_database` image](../dev/docker/database/README.md) builds a
  database server configured for Delphi front- and back-ends.

From the root of your workspace, the images can be built as follows:

```bash
docker build -t delphi_web \
  -f repos/delphi/operations/dev/docker/web/Dockerfile .

docker build -t delphi_database \
  -f repos/delphi/operations/dev/docker/database/Dockerfile .
```

Note that these images aren't very useful at this point. Each frontend will
extend and customize these images as necessary to replicate the server's
environment for that frontend.

To work with the new Python server, you will need the new image specified
[here](https://github.com/cmu-delphi/delphi-epidata/blob/76cc4c513fe1fa64eede08a6a9202aaa25e0dc1b/dev/docker/python/Dockerfile). See the [CI recipe](https://github.com/cmu-delphi/delphi-epidata/blob/76cc4c513fe1fa64eede08a6a9202aaa25e0dc1b/.github/workflows/ci.yaml#L54) for the latest instructions
on how to build, test, and run locally.

# test

After the images specific to your frontend have been built, you're ready to
bring the stack online.

Here's a basic example of how to launch a serving container. Note the `-p`
flag, which makes the containers visible for manual testing (e.g. in a web
browser). The external, or host, port is given first, and the internal, or
container, port is given second. For automated integration testing, the `-p`
flag can optionally be omitted.

```bash
# launch an empty database
docker run --rm -p 13306:3306 \
  --network delphi-net --name delphi_database \
  delphi_database
```

Note that web servers and databases are heavy processes and startup can take a
little while. For example, the database can take on the order of ~15 seconds to
become ready.

To stop servers in containers, a simple `ctrl+c` may suffice, depending on how
the container handles the signal. A more canonical (and guaranteed to succeed)
way to stop a container is to use the `docker stop` command. The command takes
either a container name or ID. You can find these details using the `docker ps`
command. For example:

```bash
# show running containers
docker ps

# stop the database which was started above
docker stop delphi_database
```

As you implement your changes, you'll periodically want to test things out. To
apply your code changes to the local stack, any affected containers have to be
stopped, the corresponding images have to be rebuilt, and the containers have
to be started again.

## manual

Manual testing is a good way to confirm during development that new changes are
working as intended. However, it can be very tedious. After development is
finished, integration tests should be written and added to the project. This
ensures that future developers can quickly and easily repeat your tests without
having to follow a detailed step-by-step guide, which is both wasteful of time
and error-prone.

Manual testing is ad hoc by nature. The integration tests for the particular
piece of code you're working on often don't yet exist, and so the only way to
test your changes is through one-off manual testing. For this reason, this
guide doesn't prescribe any particular sequence of steps for manual testing.

In the most general terms, manual testing begins with launching the appropriate
containers and is followed by assessing the behavior of the code under test.
The latter could involve, for example, observing the output of `curl` or using
a web browser to interactively exercise particular code paths.

## integration

Automated integration testing can help to validate (short-term) and protect
(long-term) complex execution paths that span multiple coordinating components,
as are frequent in frontend code.

For Delphi, integration tests are something of a hybrid between unit testing
and manual testing. The test procedure typically goes something like this:

1. Write a python _unit test_ which interacts with the frontend and makes
  assertions on the results. Interaction can happen, for example, using the
  `requests` module, the `epidata` client, or the `selenium` web driver.

  Note that such tests use python's built-in unit testing machinery for
  convenience, even though they're not truly unit tests. To reflect this, and
  to prevent unintentionally running integration tests at the same time as unit
  tests, integration tests are stored under a repo's `integrations/` directory,
  which is a sibling to the `tests/` directory for unit tests.

2. Build images containing both the tests (i.e. the `delphi_python` image) and
  the frontend under test (i.e. some image like `delphi_web_<name>` and
  probably also an image like `delphi_database_<name>`).

3. Launch containers to bring a local instance of the frontend online. (e.g.
  `docker run ... delphi_web_<name>`)

4. Run a container that executes tests against the local frontend instance.
  (e.g. `docker run ... delphi_python`)

5. Cleanup by bringing the stack down and removing any unused containers and
  images. (e.g. `docker stop`, `docker rmi`, etc.)

Integration testing is much more involved than unit testing, and so it is
therefore not performed as frequently. Still, best practice is to run all
integration tests for a given repo _at minimum_ prior to code review. New
integration tests should accompany all nontrivial frontend code changes.
