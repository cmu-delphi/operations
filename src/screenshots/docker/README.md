# `delphi_screenshot`

This image is based on a standard [selenium](https://www.selenium.dev/) chrome
image. Currently there is nothing else added on top of that base image. In
other words, `delphi_screenshot` is essentially just an alias for that base
image. Although this is a bit redundant, it allows us to easily add additional
things to `delphi_screenshot` in the future without having to update image
names in dependent code.

This image is used by the [../covidcast](COVIDcast screenshot utility), which
produces specially tailored screenshots of the COVIDcast website.

The recommend build command for this image, from automation's `driver`
directory is:

```
docker build -t delphi_screenshot delphi/operations/screenshots/docker
```
