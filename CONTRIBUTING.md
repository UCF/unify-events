# Contributing to UCF's Events System

Thank you for your interest in contributing to this project!  If you are a developer for UCF and want to contribute, we'd love to hear from you.

This document outlines the best ways to submit new ideas or inform us of bugs.  Please take a moment to review these guidelines before submitting new issues or pull requests in order to make the contribution process easy and effective for everyone involved.

## Quick links
* [Using the issue tracker](#using-the-issue-tracker)
* [Bug reports](#bug-reports)
* [Feature requests](#feature-requests)
* [Pull requests](#pull-requests)
* [Asking questions/getting help](#asking-questionsgetting-help)
* [Code standards and style guides](#code-standards-and-style-guides)

-----

## Using the issue tracker

The [issue tracker](https://github.com/UCF/unify-events/issues) in Github is the preferred channel for [bug reports](#bug-reports), [feature requests](#feature-requests) and [submitting pull requests](#pull-requests).

Please do not use the issue tracker for personal support requests.  See the section on [getting help](#asking-questionsgetting-help) for more information.


## Bug reports

A bug is a demonstrable problem that is caused by the code in the repository. Concise and thorough bug reports will help us fix reported problems more quickly and effectively.

### Before submitting a bug report
Before you submit a new bug report, please follow these steps:

1. **Use the GitHub issue search** &mdash; check if the issue has already been reported.  Feel free to comment in the existing issue if it is still open and you have new information to share.

2. **Check if the issue has been fixed** &mdash; make sure the problem isn't already resolved in an upcoming [milestone](https://github.com/UCF/unify-events/milestones).

### Submit a bug report
If you've followed the steps above and have a valid bug report to submit, you can submit it by [creating a new issue in Github](https://github.com/UCF/unify-events/issues/new?template=bug_report.md).

Add a descriptive, understandable title and details about the bug in the description field, following the template provided. Please try to be as detailed as possible in your report. What steps will reproduce the issue? What browser(s) and OS experience the problem? Do other browsers show the bug differently? What would you expect to be the outcome? All of the information you provide will help us quickly evaluate and fix the issue.

If you have a live example of the bug available somewhere public, please include a link in the bug report.


## Feature requests

We welcome new feature requests from developers across campus. Please provide as much detail and context as possible to justify the inclusion of your idea in the project. However, we reserve the right to deny feature requests when they don't align with the project's goals, or if said feature is already accomplishable with existing components/functionality.

You can submit a new feature request by [creating a new issue in Github](https://github.com/UCF/unify-events/issues/new?template=feature_request.md) and filling out the provided template.


## Pull requests

[**Please ask first**](#asking-questionsgetting-help) before embarking on any _significant_ pull request (e.g. implementing features, refactoring code); otherwise you risk spending a lot of time working on something that the project's maintainers might not want to merge into the project. Pull requests should be related to existing issues that have been acknowledged by UCF Web Communications.

All pull requests should remain focused in scope and avoid containing unrelated commits.

Your pull request will be reviewed by at least one maintainer of the project.  While your code should be complete enough to be understood by the person reviewing it, we don't want to spend an extensive amount of time reviewing code--try to keep your code sample brief enough to be reviewed within one hour.

Please adhere to the [coding guidelines](#code-standards-and-style-guides) used throughout the project (indentation, accurate comments, etc.)  Code that does not adhere to these standards will not be merged into the project.

### How to submit a pull request

Adhering to the following process is the best way to submit a pull request:

1. [Fork](https://help.github.com/articles/fork-a-repo/) the project.
2. Clone your fork, and configure the remotes:

   ```bash
   # Clone your fork of the repo into the current directory
   git clone https://github.com/<your-username>/unify-events.git

   # Navigate to the newly cloned directory
   cd unify-events

   # Assign the original repo to a remote called "upstream"
   git remote add upstream https://github.com/UCF/unify-events.git
   ```

3. If you cloned a while ago, get the latest changes from upstream:

   ```bash
   git checkout master
   git pull upstream master
   ```

4. Create a new topic branch to contain your feature, change, or fix.

   ```bash
   git checkout -b <topic-branch-name>
   ```

    New branches **must** be branched off of the most recent existing `rc-*` branch (typically there will only be one open at a time), or off of `master` directly if no `rc-*` branch exists.

    **Never create _any_ new branch from the `develop` branch**--`develop` exists solely for project maintainers' usage and is considered a "dirty" branch. **Branches created from `develop` will not be merged into the project.**

5. Commit your changes in logical chunks. Please provide [helpful, readable commit messages](https://chris.beams.io/posts/git-commit/) (avoid nondescriptive messages such as "bugfix" or "minor change").

    If you're making changes to scss or js files, make sure you're minifying **and committing** those minified file changes.  scss and js file processing should be performed using gulp commands provided in the repo (see [gulpfile.js](https://github.com/UCF/unify-events/blob/master/gulpfile.js))

6. Locally merge the upstream `rc-*` or `master` branch (whichever you branched off of initially) into your topic branch:

   ```bash
   git merge --no-ff upstream master
   ```

7. Push your topic branch up to your fork:

   ```bash
   git push origin <topic-branch-name>
   ```

8. [Open a Pull Request](https://help.github.com/articles/about-pull-requests/) against the `rc-*` or `master` branch (whichever you initially branched off of.) Pull request titles and descriptions should be as descriptive and clear as possible.

-----

## Asking questions/getting help

The events system has a [comprehensive help & documentation section](https://events.ucf.edu/help/) that explains how to use the system, create events, manage calendars, etc.  Please refer to this documentation first if you have a question about events system functionality.

If you have a personal support request or have a question about the events system's functionality that isn't already covered in the help docs, please use the "Contact" link at the bottom of any page on the events system to submit your request.

If you think you've encountered a bug or some other unintended behavior, use the issue tracker to [submit a bug](#bug-reports).

-----

## Code standards and style guides

Whenever you add or modify code in this repo, please follow the code style guides noted below, per language:

### Python

[Adhere to PEP 8 Standards](https://www.python.org/dev/peps/pep-0008/) for new or modified code.

### HTML

[Adhere to the mdo Code Guide.](http://codeguide.co/#html)

- Use tags and elements appropriate for an HTML5 doctype (e.g., self-closing tags).
- Use CDNs and HTTPS when referencing third-party JS.
- Use [WAI-ARIA](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA) attributes when appropriate to promote accessibility.

### CSS/Sass

Adhere to the [mdo Code Guide](http://codeguide.co/#css) for basic CSS formatting guidelines, except for what's noted below.

Use [CSS-Tricks' Sass Style Guide](https://css-tricks.com/sass-style-guide/) for Sass-specific features (e.g. order of extends, mixin inclusions, etc in a ruleset).

- Declaration order: declarations should be in alphabetical order.
- Selectors: all selectors in a ruleset should be on their own line.
- All generated color pallettes and font sizes/weights should comply with [WCAG 2.0 AA contrast guidelines](https://www.w3.org/TR/WCAG20/#visual-audio-contrast) in their default state.  Components and utilities with hover/focus/active states should try to comply with these contrast requirements whenever possible.
- Except in rare cases, don't remove default `:focus` styles (via e.g. `outline: none;`) without providing alternative styles. See [this A11Y Project post](http://a11yproject.com/posts/never-remove-css-outlines/) for more details.

New/modified Sass code should not throw any Sass-lint errors.  We recommend using a [Sass-lint integration with your IDE of choice](https://www.npmjs.com/package/sass-lint#ide-integration) to show linter warnings/errors as you code.  This repo includes a Sass-lint config file with the desired linter rulesets for this project.

### JS

[Adhere to the jQuery Coding Standards and Best Practices](http://lab.abhinayrathore.com/jquery-standards/).

- 2 spaces (no tabs)
- Don't use [jQuery event alias convenience methods](https://github.com/jquery/jquery/blob/master/src/event/alias.js) (such as `$().focus()`). Instead, use [`$().trigger(eventType, ...)`](https://api.jquery.com/trigger/) or [`$().on(eventType, ...)`](https://api.jquery.com/on/), depending on whether you're firing an event or listening for an event. (For example, `$().trigger('focus')` or `$().on('focus', function (event) { /* handle focus event */ })`) We do this to be compatible with custom builds of jQuery where the event aliases module has been excluded.

New/modified JavaScript code should not throw any eslint errors.  We recommend using a [eslint integration with your IDE of choice](https://eslint.org/docs/user-guide/integrations#editors) to show linter warnings/errors as you code.  This repo includes an eslint config file with the desired linter rulesets for this project.
