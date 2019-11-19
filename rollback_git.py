#    Copyright 2019 Google LLC
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse
import re

try:
    import git
except ImportError as e:
    raise SystemExit('Failed to import GitPython. Install GitPython using the '
                     'following command:\n\n\tpip install gitpython\n')

REVERT_PATTERN = re.compile('Revert ".*"[\s\n]*This reverts commit '
                            '([\da-f]{40}).')
REVERT_MERGE_PATTERN = re.compile('Revert ".*"[\s\n]*This reverts commit '
                                  '([\da-f]{40}), reversing[\s\n]*changes made '
                                  'to [\da-f]{40}.')


def parse_args():
    parser = argparse.ArgumentParser(description='Reverts commits in a git '
                                                 'branch from HEAD to an '
                                                 'arbitrary tag')
    parser.add_argument('-b',
                        '--branch',
                        default='master',
                        help='Branch on which to add reverts. Default: master')
    parser.add_argument('-t',
                        '--tag',
                        default='prod',
                        help='Tag at which to stop reverting. Default: prod')
    return parser.parse_args()


def main():
    args = parse_args()

    repo = git.Repo()
    commits = repo.iter_commits(args.branch)
    tag_ref = 'refs/tags/%s' % args.tag

    try:
        stop_ref = repo.commit(tag_ref)
    except Exception as e:
        raise SystemExit(e)

    next_revert = None
    reverted = set()

    print('Beginning reverts on branch %s to tag %s.' % (args.branch, args.tag))

    for commit in commits:
        abbrev = commit.hexsha[:7]

        if commit == stop_ref:
            print('At tag %s, SHA %s.' % (args.tag, stop_ref.hexsha[:7]))
            break
        elif commit.hexsha in reverted:
            print('Commit %s has already been reverted; continuing...' % abbrev)
            continue
        elif next_revert is not None and next_revert != commit:
            # We're either at HEAD and there is no next_revert, or...
            # this means the current commit came from a merged branch and should
            # have been reverted when the merge commit was reverted, so iterate
            # commits in this branch until we find next_revert
            continue

        try:
            # merge commit
            this_branch, merge_branch = commit.parents
        except ValueError:
            # regular commit
            this_branch, merge_branch = commit.parents[0], None

        next_revert = this_branch

        merge_revert = re.match(REVERT_MERGE_PATTERN, commit.message)
        regular_revert = re.match(REVERT_PATTERN, commit.message)

        if merge_revert or regular_revert:
            if merge_revert:
                hexsha = merge_revert.groups()[0]
            elif regular_revert:
                hexsha = regular_revert.groups()[0]

            reverted.add(hexsha)
            print('Commit %s is a revert commit; continuing...' % abbrev)
            continue

        elif merge_branch is not None:
            # merge commit
            repo.git.revert('-m', '1', commit, no_edit=True)
        else:
            # not a merge commit
            repo.git.revert(commit, no_edit=True)

        print('Reverted %s, message: %s' % (abbrev, commit.message.strip()))

    else:
        print('No commits to revert.')

    print('Done.')


if __name__ == '__main__':
    main()
