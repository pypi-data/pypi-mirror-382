# detdevlib
Library containing functions and classes that can be used across all det repositories.

## Contributing
Any branch that creates a merge requests into master will be checked for:
- style (black, isort and pydocstyle)
- passing pytest
It is recommended to run these checks locally before pushing. 

Commits merged into `master` must follow the **Conventional Commits** specification, as this is crucial for the automated release process.

## Releasing a New Version
This repository uses **release-please** to automate package and documentation publishing.

1.  **Use Conventional Commits**: When you merge a pull request, ensure your commit messages have a specific prefix. The most common are:
    * `fix:` for bug fixes (triggers a **patch** release, e.g., 1.2.3 → 1.2.4).
    * `feat:` for new features (triggers a **minor** release, e.g., 1.2.3 → 1.3.0).
    * Add a `!` after the type for breaking changes (e.g., `feat!: ...`) to trigger a **major** release (e.g., 1.2.3 → 2.0.0).

2.  **Automatic Release PR**: After a valid commit is merged into `master`, the `release-please` workflow runs. It automatically creates or updates a special "Release PR". This PR contains the new version number and an updated `CHANGELOG.md`.

3.  **Create the Release**: To publish a new version, simply **merge the Release PR**. Merging this PR will:
    * Create a new GitHub Release with a git tag.
    * Trigger the workflow to publish the package to PyPI.
    * Trigger the workflow to deploy the latest documentation to GitHub Pages.

## Documentation
Documentation is published to GitHub pages at https://dynamic-energy-trading.github.io/detdevlib/. 

The source code for the site is on the `gh-pages` branch.
