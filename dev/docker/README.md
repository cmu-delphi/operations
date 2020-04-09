# Docker images

This subtree contains assets for Docker images. A Docker images is based on
exactly one parent image, where the special image "scratch" represents an empty
parent. Delphi's images are organized as follows:

- There is one directory per image, and each directory contains both a
  `Dockerfile` and a `README.md`.
- Any supporting files for a given image are located in an `assets`
  subdirectory.
- Top-level images are generally based on a Docker Hub image and are located in
  the current directory.
- Nested images are based on a Delphi image and are located within the
  directory of the image on which they are based.
  - Alternatively, if an image is of use _only to a particular repo_, then that
    image may be defined in the relevant repo rather than here. In that case,
    an analogous directory structure applies.

To summarize, the image hierarchy is directly reflected by the directory
hierarchy. A consequence of this tree structure is that images become
increasingly more specialized with depth. This allows convenient sharing of
common infrastructure (e.g. python packages) among related child images (e.g.
forecasting and nowcasting utilities).

Best practice is to document the image in the corresponding `README.md` file.
Even just a short note will go a long way to helping other developers
understand the context around each image.
