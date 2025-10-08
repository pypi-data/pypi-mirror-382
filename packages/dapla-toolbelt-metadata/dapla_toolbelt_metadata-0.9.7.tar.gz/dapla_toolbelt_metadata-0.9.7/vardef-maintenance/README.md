# Vardef maintenance

This directory pertains to a service deployed on Dapla Lab. The purpose of the service is to allow users to maintain variable definitions. The service is based on the existing Jupyter IDE service.

## Init script

On startup of the service, the [init script](./vardef_client_init.sh) is run, which among other things:

- Retrieves the [user interface Notebooks](../demo/variable_definitions/) from this repo.
- Retrieves the [toml project config](./vardef-maintenance.toml) from this repo and installs the specified dependencies and creates a kernel.
- Modifies the metadata of the user interface Notebooks such that the created kernel is pre-selected.

## Service configuration

The service vardef-forvaltning is a copy of the existing Jupyter service, with the difference that we specify the `personalInit` configuration value to point to the init script discussed above. This prepares the Notebooks and environment for maintenance of variable definitions.

It is also possible to supply arguments to the init script with `personalInitArgs`, for example to specify the branch from which to retrieve files with `"--branch=dpmeta-837-vardef-init-script"`

In the future we may wish to make further changes, such as reducing the options available to the user.

## Dependency specification

In [./vardef-maintenance.toml](./vardef-maintenance.toml) we use a Poetry compatible configuration. This is becayse we use the `ssb-project` tool to install the dependencies and a kernel and that supports Poetry. It is desirable to change to using `uv` for installation and configuration once this is supported.
