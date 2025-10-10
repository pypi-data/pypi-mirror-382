#  Copyright (c) 2024 The Eclipse Foundation
#
#  This program and the accompanying materials are made available under the
#  terms of the Eclipse Public License 2.0 which is available at
#  http://www.eclipse.org/legal/epl-2.0.
#
#  SPDX-License-Identifier: EPL-2.0
#
#  Contributors:
#      asgomes - Initial implementation

__version__ = "0.1.0"

from fnmatch import translate
from re import match

from requests import exceptions, get


def find_dependencies_gitlab(config, logger, lang, files, default_filenames):
    # Attempt to find dependency files
    filepaths = []
    for pattern in config.get(lang, 'DependencySearch', fallback=default_filenames).split(','):
        # Pattern to regex
        regex = translate(pattern.strip())
        for f in files:
            if match(regex, f['name']):
                filepaths.append(f['path'])
    # print(filepaths)
    logger.info("Dependency filepaths for " + lang + ": " + str(filepaths))
    return filepaths


def find_dependencies_github(config, logger, lang, files, default_filenames):
    # Attempt to find dependency files
    filepaths = []
    for pattern in config.get(lang, 'DependencySearch', fallback=default_filenames).split(','):
        # Pattern to regex
        regex = translate(pattern.strip())
        for f in files:
            if match(regex, f.name):
                filepaths.append(f.path)
    # print(filepaths)
    logger.info("Dependency filepaths for " + lang + ": " + str(filepaths))
    return filepaths


def add_gldep_locations(dependency_locations, proj, lang, paths):
    for path in paths:
        try:
            dependency_locations[proj.path_with_namespace][lang].append(str(proj.path_with_namespace) + '/' + path)
        except KeyError:
            dependency_locations[proj.path_with_namespace][lang] = []
            dependency_locations[proj.path_with_namespace][lang].append(str(proj.path_with_namespace) + '/' + path)


def add_ghdep_locations(dependency_locations, proj, lang, paths):
    for path in paths:
        try:
            dependency_locations[proj][lang].append(path)
        except KeyError:
            dependency_locations[proj][lang] = []
            dependency_locations[proj][lang].append(path)


def get_pypy_latest_version(package_name):
    pypi_url = "https://pypi.org/pypi"
    json_url = f"{pypi_url}/{package_name}/json"

    try:
        # Make the request to the PyPI API with a timeout
        response = get(json_url, timeout=30)

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        data = response.json()
    except exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Package '{package_name}' not found on PyPI.") from e
        raise ValueError(
            f"Failed to retrieve data from PyPI. Status: {e.response.status_code}"
        ) from e
    except exceptions.RequestException as e:
        # Handle network-related errors like timeouts or connection issues
        raise ValueError(f"Request to PyPI failed: {e}") from e

    # Extract the latest version
    try:
        latest_version = data["info"]["version"]
        return latest_version
    except KeyError:
        raise ValueError(f"Could not find 'info' or 'version' in PyPI response for {package_name}.")


def add_error_report(config, location, error):
    if config['output_report']:
        return {'location': location, 'name': error, 'license': '', 'status': 'error', 'authority': '-',
                'review': ''}
    return {}
