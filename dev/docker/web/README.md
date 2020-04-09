# `delphi_web`

This image contains a standard
[Apache+PHP web server](https://hub.docker.com/_/php). It's configured with
`mysqli` available and enabled. Serving is done out of `/var/www/html`.

Several Delphi web frontends require credentials (e.g. for database access). To
satisfy this need, this image comes with a burned-in
[`secrets.php`](secrets.php). That file is a special development-only version
that doesn't contain any _actual_ secrets.

This image is intended to be extended by other images, not run directly.
