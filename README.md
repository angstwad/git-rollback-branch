# git-rollback-branch

Reverts commits in a Git branch from HEAD to an arbitrary tag.

## Requirements

* Python 3.5+
* gitpython

## Installation

1. Clone the repo
2. `cd git-rollback-branch`
3. `pip3 install .`

## Use

```
$ rollback_git --help
usage: rollback_git [-h] [-b BRANCH] [-t TAG]

Reverts commits in a git branch from HEAD to an arbitrary tag

optional arguments:
  -h, --help            show this help message and exit
  -b BRANCH, --branch BRANCH
                        Branch on which to add reverts. Default: master
  -t TAG, --tag TAG     Tag at which to stop reverting. Default: prod
```

## Disclaimer

This is not an officially supported Google product.