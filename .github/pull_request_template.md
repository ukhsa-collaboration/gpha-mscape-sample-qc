# Pull request template for mSCAPE code
How to use this pull request template:
1. Choose EITHER:
   'Writing a new component' if your code has not yet been reviewed and is the first PR to main,
   OR
   'Updating an existing component' if the PR is to make an update to an existing component.
   Delete the section you do not need.
2. Complete all actions in the relevant checklist and tick off as they are completed by putting an "x" inside the square brackets (or ticking the box after opening the PR).
3. Add an explanation for any tasks that have not been completed to explain why they have been omitted. For example, if only documentation was updated, then you would not need to add or update unit tests.
4. Update the list of tasks for the reviewer, deleting ones that are not needed for this PR.
5. Delete any lines starting with >> to keep the PR neat.
6. Assign the PR to a reviewer (this can also be done once the PR is created).

## Writing a new component
- [ ] I have read the SOP for creating or updating code to be integrated into mSCAPE
- [ ] The repository contains all required files as set out in the template/SOP
- [ ] The code base contains no CLIMB IDs or other sensitive information
- [ ] All functions involving calls to Onyx have appropriate error handling
- [ ] If writing to Onyx, the code includes a "dry run" option
- [ ] The code has passed linting checks in ruff with no errors raised
- [ ] I have written unit tests for all functions
- [ ] I have successfully run the code and unit tests on devscape

## Updating an existing component
- [ ] I have read the SOP for creating or updating code to be integrated into mSCAPE
- [ ] The updated code base contains no CLIMB IDs or other sensitive information
- [ ] Version number bumped in pyproject.toml
- [ ] Changes documented in the component CHANGELOG.md
- [ ] Documentation has been updated if required
- [ ] I have added or updated unit tests to cover the changes made
- [ ] New and existing unit tests have passed
- [ ] The updated code has passed linting checks in ruff with no errors raised
- [ ] I have successfully run the code and unit tests on devscape

## Tasks skipped
>> (Any exceptions/skipped tasks from the checklist above)

## Pull request description

>> Please include a short description of the aim of the pull request and changes made. Highlight
>> any particular areas of code you would like a reviewer to focus on during the review.
>> You may paste the changelog in here if useful.

## Reviewers Tasks
>> (Below are some examples, delete the ones that are not relevant to this PR)
- [ ] Read all files
- [ ] Read all changed files
- [ ] Add comments for major (must be corrected), minor (should be corrected unless justified), nitpick (typos, formatting, stylistic choices etc)
- [ ] Install and run unit tests/end-to-end test/test command
- [ ] Check for spelling/grammar
