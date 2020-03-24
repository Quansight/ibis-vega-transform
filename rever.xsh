# Standard library imports
import ast
import os

# Third party imports
from rever.activity import activity
from rever.tools import replace_in_file


$ACTIVITIES = [
    'checkout',
    'clean_repo',
    'update_repo',
    'install_deps',
    'format_code',
    'update_release_version',
    'create_python_distributions',
    'create_npm_distributions',
    'upload_test_distributions',
    'install_test_distributions',
    'run_tests',
    'authors',
    'commit_release_version',
    'add_tag',
    'upload_python_distributions',
    'upload_npm_distributions',
    'update_dev_version',
    'commit_dev_version',
    'push',
]


$PROJECT = "ibis-vega-transform"
$MODULE = "ibis_vega_transform"
$GITHUB_ORG = 'Quansight'
$GITHUB_REPO = $PROJECT
$VERSION_BUMP_PATTERNS = [
    # These note where/how to find the version numbers
    ($MODULE + '/__init__.py', r'__version__\s*=.*', '__version__ = "$VERSION"'),
    ('package.json', r'"version":\s.*', '"version": "$VERSION",'),
]
$AUTHORS_FILENAME = "AUTHORS.md"
$AUTHORS_TEMPLATE = """
The $PROJECT project has some great contributors! They are:

{authors}

These have been sorted {sorting_text}.
"""
$AUTHORS_FORMAT= "- [{name}](https://github.com/{github})\n"
$AUTHORS_SORTBY = "alpha"
$TEMP_ENV = 'tmp-' + $PROJECT
$CONDA_ACTIVATE_SCRIPT = 'activate.xsh'
$HERE = os.path.abspath(os.path.dirname(__file__))


# --- Helpers
# ----------------------------------------------------------------------------
def get_version(version_type, module=$MODULE):
    """
    Get version info. Tuple with three items, major.minor.patch
    """
    with open(os.path.join($HERE, module, "__init__.py")) as fh:
        data = fh.read()

    major, minor, patch = 'MAJOR', 'MINOR', 'PATCH'
    lines = data.split("\n")
    for line in lines:
        if line.startswith("__version__"):
            version = ast.literal_eval(line.split("=")[-1].strip())
            major, minor, patch = [int(v) for v in version.split('.')[:3]]

    version_type = version_type.lower()
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    elif version_type == 'patch':
        patch += 1
    elif version_type in ['check', 'setup']:
        pass
    elif len(version_type.split('.')) == 3:
        major, minor, patch = version_type.split('.')
    else:
        raise Exception('Invalid option! Must provide version type: [major|minor|patch]')

    major = str(major)
    minor = str(minor)
    patch = str(patch)
    version = '.'.join([major, minor, patch])

    if version_type not in ['check', 'setup']:
        print('\n\nReleasing version {}\n\n'.format(version))

    return version


# Actual versions to use
$NEW_VERSION = get_version($VERSION)
$DEV_VERSION = $NEW_VERSION + '.dev0'
$DEV_NPM_VERSION = $NEW_VERSION + '-dev.0'


def activate(env_name):
    """
    Activate a conda environment.
    """
    if not os.path.isfile($CONDA_ACTIVATE_SCRIPT):
        with open('activate.xsh', 'w') as fh:
            fh.write($(conda shell.xonsh hook))

    # Activate environment
    source activate.xsh
    conda activate @(env_name)
    $[conda info]


def update_version(python_version, npm_version=None):
    """
    Update version patterns.
    """
    if npm_version is None:
        npm_version = python_version

    for fpath, pattern, new_pattern in $VERSION_BUMP_PATTERNS:
        if 'package.json' in fpath:
            new_pattern = new_pattern.replace('$VERSION', npm_version)
        elif '__init__.py' in fpath:
            new_pattern = new_pattern.replace('$VERSION', python_version)

        replace_in_file(pattern, new_pattern, fpath)


# --- Activities
# ----------------------------------------------------------------------------
@activity
def checkout(branch='master'):
    """
    Checkout master branch.
    """
    git checkout @(branch)


@activity
def clean_repo():
    """
    Clean the repo from build/dist and other files.
    """
    import pathlib

    # Remove python files
    for p in pathlib.Path('.').rglob('*.py[co]'):
        p.unlink()

    for p in pathlib.Path('.').rglob('__pycache__'):
        p.rmdir()

    rm -rf .pytest_cache/
    rm -rf build/
    rm -rf dist/
    rm -rf examples/.ipynb_checkpoints/
    rm -rf examples/population.db
    rm -rf activate.xsh
    rm -rf out.tgz
    rm -rf $MODULE.egg-info

    rm -rf lib/
    rm -rf node_modules/
    rm -rf tsconfig.tsbuildinfo
    rm -rf yarn.lock

    # Delete files not tracked by git?
    # git clean -xfd


@activity
def update_repo(branch='master'):
    """
    Stash any current changes and ensure you have the latest version from origin.
    """
    git stash
    git pull origin @(branch)


@activity
def install_deps():
    """
    Install release and test dependencies.
    """
    try:
        conda env remove --name $TEMP_ENV --yes
    except:
        pass

    conda env create --file binder/environment.yml --name $TEMP_ENV
    conda install --name $TEMP_ENV black twine yarn wheel --channel conda-forge --yes --quiet
    activate($TEMP_ENV)
    jlpm


@activity
def format_code():
    """
    Create distributions.
    """
    activate($TEMP_ENV)
    black ibis_vega_transform
    jlpm run prettier


@activity
def update_release_version():
    """
    Update version in `__init__.py` (set release version, remove 'dev0').
    and on the package.json file.
    """
    update_version($NEW_VERSION)


@activity
def create_python_distributions():
    """
    Create distributions.
    """
    activate($TEMP_ENV)
    python setup.py sdist bdist_wheel


@activity
def create_npm_distributions():
    """
    Create npm distributions.
    """
    activate($TEMP_ENV)
    yarn run build
    yarn pack --filename out.tgz


@activity
def upload_test_distributions():
    """
    Upload test distributions.
    """
    activate($TEMP_ENV)

    # The file might be already there
    try:
        python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    except Exception as err:
        print(err)


@activity
def install_test_distributions():
    """
    Upload test distributions.
    """
    activate($TEMP_ENV)

    # Python package
    pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple $PROJECT==$NEW_VERSION

    # Npm package
    jupyter labextension install out.tgz


@activity
def run_tests():
    """
    Run tests before cleaning repository.    
    """
    # Python tests
    # pytest $MODULE

    # Npm tests
    npm test

    while True:
        result = input(
            '\n\nPlease open a new console and type:\n\n'
            '  conda activate ' + $TEMP_ENV + '\n'
            '  cd "' + os.path.join($HERE, 'examples') + '"\n'
            '  jupyter lab\n\n'
            'And test that all notebooks work as expected.\n\n'
            'Once finished write "ok" and <enter>.\nIf notebooks are not '
            'working as expected write "cancel" and <enter>:\n\n'
        )

        if result == 'ok':
            git stash
            break
        elif result == 'cancel':
            git stash
            clean_repo()
            rm -rf rever/
            raise Exception('The package cannot be released yet!')


@activity
def commit_release_version():
    """
    Commit release version.
    """
    git add .
    git commit -m @('Set release version to ' + $NEW_VERSION + ' [ci skip]') --no-verify


@activity
def add_tag():
    """
    Add release tag.
    """
    # TODO: Add check to see if tag already exists?
    git tag -a @('v' + $NEW_VERSION) -m @('Tag version ' + $NEW_VERSION + ' [ci skip]')


@activity
def upload_python_distributions():
    """
    Upload the distributions to pypi production environment.
    """
    activate($TEMP_ENV)

    # The file might be already there
    try:
        twine upload dist/*
    except Exception as err:
        print(err)


@activity
def upload_npm_distributions():
    """
    Upload the distributions to npm.
    """
    activate($TEMP_ENV)

    # Ask for credentials
    npm login

    # The file might be already there
    try:
        npm publish out.tgz
    except Exception as err:
        print(err)


@activity
def update_dev_version():
    """
    Update `__init__.py` (add 'dev0' and increment minor).
    """
    update_version(python_version=$DEV_VERSION, npm_version=$DEV_NPM_VERSION)


@activity
def commit_dev_version():
    """"
    Commit dev changes.
    """
    git add .
    git commit -m "Restore dev version [ci skip]" --no-verify


@activity
def push(branch='master'):
    """
    Push changes.
    """
    git push origin @(branch)
    git push --tags
