# sz-sdk-json-type-definition development

The following instructions are useful during development.

**Note:** This has been tested on Linux and Darwin/macOS.
It has not been tested on Windows.

## Prerequisites for development

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. The following software programs need to be installed:
    1. [git]
    1. [make]
    1. [docker]
    1. [go]
    1. [jtg-codegen]

## Install Git repository

1. Identify git repository.

    ```console
    export GIT_ACCOUNT=senzing-garage
    export GIT_REPOSITORY=sz-sdk-json-type-definition
    export GIT_ACCOUNT_DIR=~/${GIT_ACCOUNT}.git
    export GIT_REPOSITORY_DIR="${GIT_ACCOUNT_DIR}/${GIT_REPOSITORY}"

    ```

1. Using the environment variables values just set, follow
   steps in [clone-repository] to install the Git repository.

## Dependencies

1. A one-time command to install dependencies needed for `make` targets.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make dependencies-for-development

    ```

1. Install dependencies needed for [Go] code.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make dependencies

    ```

## Update senzingsdk-RFC8927.json

1. Make changes to [senzingsdk-RFC8927.json]

## Version

1. Create artifacts for a version.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make version

    ```

## Lint

1. Run linting.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make lint

    ```

1. Review analysis:
    1. **TEST 1:** Make sure JSON keys are in sorted order.
    1. **TEST 2:**
    1. **TEST 3:** Report how many times a JSON key has been specified.
    1. **TEST 4:** Report JSON keys that have more than one datatype.
    1. **TEST 5:** Report any `ref` keys that have a bad value.
    1. **TEST 6:** Report JSON keys that are not used.

1. Address any issues in the `diff` between `senzingsdk-RFC8927.json` and the temporary `senzingsdk-RFC8927-pretty.json`.

## Test

1. Run tests.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make test

    ```

## Package

1. Build the `wheel` file for distribution.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make package

    ```

1. Activate virtual environment.

    ```console
    cd ${GIT_REPOSITORY_DIR}
    source .venv/bin/activate

    ```

1. Verify that `senzing-core` is not installed.
   Example:

    ```console
    python3 -m pip freeze | grep -e senzing-typedef

    ```

   Nothing is returned.

1. Install directly from `wheel` file.
   Example:

    ```console
    python3 -m pip install ${GIT_REPOSITORY_DIR}/dist/*.whl

    ```

1. Verify that `senzing-core` is installed.
   Example:

    ```console
    python3 -m pip freeze | grep -e senzing-typedef

    ```

   Example return:

    > senzing-typedef @ file:///home/senzing/senzing-garage.git/sz-sdk-json-type-definition/dist/senzing_typedef-0.2.0-py3-none-any.whl#sha256=ff40b60c764d867c0450f0370673b53b44cf8161e61cab012f2aa21c9db24e3e

1. Uninstall the `senzing-core` python package.
   Example:

    ```console
    python3 -m pip uninstall senzing-typedef

    ```

1. Deactivate virtual environment.

    ```console
    deactivate

    ```

## References

1. [JSON TypeDef]
1. [JSON TypeDef on Github]

[clone-repository]: https://github.com/senzing-garage/knowledge-base/blob/main/HOWTO/clone-repository.md
[docker]: https://github.com/senzing-garage/knowledge-base/blob/main/WHATIS/docker.md
[git]: https://github.com/senzing-garage/knowledge-base/blob/main/WHATIS/git.md
[go]: https://github.com/senzing-garage/knowledge-base/blob/main/WHATIS/go.md
[JSON TypeDef on Github]: https://github.com/jsontypedef
[JSON TypeDef]: https://jsontypedef.com/
[jtg-codegen]: https://github.com/senzing-garage/knowledge-base/blob/main/WHATIS/jtd-codegen.md
[make]: https://github.com/senzing-garage/knowledge-base/blob/main/WHATIS/make.md
[senzingsdk-RFC8927.json]: ../senzingsdk-RFC8927.json
