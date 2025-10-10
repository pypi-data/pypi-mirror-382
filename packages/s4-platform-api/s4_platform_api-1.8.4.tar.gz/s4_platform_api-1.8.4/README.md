# S4 Platform API

## Requirements

`s4-platform-api` requires Python 3.9+.

## PyPi

The SDK is available to third party developers.

The SDK PyPi project is here: https://pypi.org/project/s4-platform-api/#description

## How to Release

For a Major/Minor Release:
- Create a `release-x.y` branch if one doesn't exist yet: `git checkout -b release-1.8`
- Ensure the log looks as expected: `git log --oneline -15`

For a Patch Release:
- cherry pick commits from main to release branch
- Ensure the log looks as expected: `git log --oneline -15`
- create PR aganst the release branch

Finally:
- create a tag: `git tag 1.8.3`
- push tag: `git push origin tag 1.8.3`
- git hub action will launch
- ensure the github release is set to latest
- ensure the github release notes are correct
