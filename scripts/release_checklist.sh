#!/usr/bin/env bash
set -e

# ---------- helpers ----------

pause() {
    echo
    read -rp "Press ENTER when done, or Ctrl+C to abort..."
}

fail() {
    echo
    echo "❌ $1"
    exit 1
}

header() {
    echo
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

# ---------- step 1: git sanity ----------

header "Step 1: Git sanity checks"

branch=$(git rev-parse --abbrev-ref HEAD)
status=$(git status --porcelain)

echo "Current branch: $branch"

if [[ "$branch" == "master" || "$branch" == "main" ]]; then
    fail "You are on '$branch'. Releases must be done from a dev branch."
fi

if [[ -n "$status" ]]; then
    echo "Working tree is not clean. Commit or stash changes before releasing."
    read -p "type y/yes to skip this check for now: " skip
    if [[ "${skip}" == 'y' ]] || [[ "${skip}" == 'yes' ]] ; then
      echo "continuing..."
    else
      fail "Stoping here"
    fi
else
    echo "✔ The working tree on dev branch is clean"
fi


# ---------- step 1b: Check if a conda environment is activated --------
header "Step 1b: Development environment"
echo "Make sure you are in a development environment with all the dependencies"
echo ""
echo "To create such a conda environment, run:"
echo "  make env"
pause



# ---------- step 2: run local tests ----------

header "Step 2: Run unit tests"

echo "Please run:"
echo "  make test"
echo
echo "This should run ~150 tests and exit cleanly."
echo 
pause

# ---------- step 3: docs + doctests ----------

header "Step 3: Doctests and documentation"

echo "Please run:"
echo "  make docs"
echo
echo "Verify:"
echo "  - doctests pass"
echo "  - HTML builds successfully"
pause

# ---------- step 4: tox matrix ----------

header "Step 4: tox compatibility testing"

echo "Please run:"
echo "  make tox"
echo
echo "Ensure all Python / matplotlib / cartopy combinations pass."
pause

# ---------- step 5: test data / Zenodo ----------

header "Step 5: Test data / Zenodo (ONLY if needed)"

echo "If this release changes:"
echo "  - reference figures"
echo "  - example figures"
echo "  - test datasets"
echo
echo "Then you MUST:"
echo " 1. Go in the directory containing test datasets:"
echo "    cd /home/dja001/shared_stuff/files/test_data_for_domutils_on_zenodo/"
echo 
echo " 2. Copy the modified test_data directory into its own versionned directory"
echo "    cp -r  ~/python/packages/domutils_package/test_data v1.0.10"
echo 
echo " 3. List differences with previous version and build .tgz for archive"
echo "    cd v?.?.? (or most recent version being worked on)"
echo "    chmod 755 prepare_tgz_for_zenodo.sh"
echo "    ./prepare_tgz_for_zenodo.sh v?.?.? (previous version) "
echo 
echo " 4. Login on zenodo with @gmail.com account"
echo "    - go on domutils repo, click update"
echo "    - delete files that are modified"
echo "    - upload new and modified files"
echo "      - don't forget to add new files and .tgz if needed"
echo "    - change publication date"
echo "    - change version"
echo "    - publish"
echo 
echo " 5. Get record number by clicking on new version"
echo "    eg  5497958"
echo 
echo " 6. Adjust version and record number in scripts/download_test_data.sh"
echo 
echo " 7. Re-download test_data and re-run tests"
echo
echo "If NOT needed, you may skip this step."
pause

# ---------- step 6: versioning ----------

header "Step 6: Version bump and changelog"

echo "Please update:"
echo "  - VERSION"
echo "  - CHANGELOG"
echo
echo "Ensure version matches intended release."
pause


# ---------- step 6b: ensure version + changelog are committed ----------

header "Step 6b: Verify VERSION and CHANGELOG.md are committed"

# Ensure files exist
[[ -f VERSION ]] || fail "VERSION file not found"
[[ -f CHANGELOG.md ]] || fail "CHANGELOG.md file not found"

# Check if either file is modified or untracked
while true; do
    dirty_files=$(git status --porcelain VERSION CHANGELOG.md)
    
    if [[ -n "$dirty_files" ]]; then
        echo
        echo "The following release files are not committed:"
        echo
        echo "$dirty_files"
        echo
        echo "Commit VERSION and CHANGELOG before continuing."
        pause
    else
        echo "✔ VERSION and CHANGELOG are committed"
        break
    fi
done


# -------------  beyond this point, everything must be commited --------------------
status=$(git status --porcelain)
if [[ -n "$status" ]]; then
    echo "Working tree is not clean. Commit before releasing."
      fail "Stoping here"
fi



# ---------- step 7: build + upload ----------

header "Step 7: Build and upload to PyPI"

echo "Please run:"
echo "  make release"
echo
echo "This will:"
echo "  - clean dist/"
echo "  - build package"
echo "  - upload via twine"
pause

# ---------- step 8: merge + tag ----------

header "Step 8: Merge and tag release"

echo "Please perform:"
echo "  - Push dev branch"
echo "  - Open and merge PR on GitHub"
echo
echo "Then tag and push:"
echo "  git checkout master"
echo "  git pull github master"
echo "  git tag -a vX.Y.Z -m 'Release vX.Y.Z'"
echo "  git push github --tags"
pause

# ---------- step 9: RTD ----------

header "Step 9: ReadTheDocs verification"

echo "Verify on RTD:"
echo "  - Build succeeded"
echo "  - 'stable' points to new tag"
pause

# ---------- done ----------

header "Release checklist complete"

echo "If all steps were completed successfully,"
echo "the release is DONE."

