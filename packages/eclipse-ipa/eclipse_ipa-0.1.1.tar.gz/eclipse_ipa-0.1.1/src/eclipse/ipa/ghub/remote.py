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

import logging
import os
import re
import shutil
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from subprocess import PIPE, Popen
from time import sleep

from github import Auth, Github, GithubException

from ..common import utils
from ..dash import report, run

logger = logging.getLogger(__name__)


def get_dependency_locations(gh, config, repositories):
    # Data structure
    # dict -> dict -> list
    dependency_locations = defaultdict(dict)

    # If repositories are directly retrieved for an Eclipse Project
    if repositories is not None:
        line_count = 0
        for repo in repositories:
            dependency_locations[repo] = {}
            line_count = line_count + 1
        print("Read " + str(line_count) + " GitHub project(s) from " + config.get('General', 'EclipseProject',
                                                                                  fallback='technology.dash'))
        logger.info("Read " + str(line_count) + " GitHub project(s) from " + config.get('General', 'EclipseProject',
                                                                                        fallback='technology.dash'))
        return dependency_locations

    # If a list of dependency locations is given, work with that
    if config.getboolean('DependencyLocations', 'LoadFromFile', fallback=False):
        input_file = config.get('DependencyLocations', 'InputFile', fallback='github-dependencies.txt')
        line_count = 0
        try:
            with open(input_file, 'r') as fp:
                for line in fp:
                    # Ignore commented lines
                    if not line.startswith('#') and line != "":
                        line_count = line_count + 1
                        tokens = line.strip().split(';')
                        proj_id = tokens[0]
                        try:
                            dependency_locations[proj_id][tokens[2]].append(tokens[1])
                        except KeyError:
                            dependency_locations[proj_id][tokens[2]] = []
                            dependency_locations[proj_id][tokens[2]].append(tokens[1])
            print("Read " + str(line_count) + " dependency location(s) from " + input_file)
            logger.info("Read " + str(line_count) + " dependency location(s) from " + input_file)
        except FileNotFoundError:
            print("The provided dependency file (" + input_file + ") cannot be found. Exiting...")
            logger.error("The provided dependency file (" + input_file + ") cannot be found. Exiting...")
            exit(1)
    # If a list of projects is given, work with that
    elif config.getboolean('Projects', 'LoadFromFile', fallback=False):
        input_file = config.get('Projects', 'InputFile', fallback='github-projects.txt')
        line_count = 0
        try:
            with open(input_file, 'r') as fp:
                for line in fp:
                    # Ignore commented lines
                    if not line.startswith('#'):
                        line_count = line_count + 1
                        proj_id = line.strip()
                        dependency_locations[proj_id] = {}
            print("Read " + str(line_count) + " project(s) from " + input_file)
            logger.info("Read " + str(line_count) + " project(s) from " + input_file)
        except FileNotFoundError:
            print("The provided projects file (" + input_file + ") cannot be found. Exiting...")
            logger.error("The provided projects file (" + input_file + ") cannot be found. Exiting...")
            exit(1)
    # If an organization is given, get our own list of projects from it
    elif config.has_option('Groups', 'BaseGroupID'):
        # Set base organization to work
        organization = gh.get_organization(config.get('Groups', 'BaseGroupID'))

        # Get all projects
        projects = organization.get_repos()
        # print("Invalid BaseGroupID provided. Exiting...")
        # logger.warning("Invalid BaseGroupID specified. Exiting...")

        # Iterate over all projects (several API calls because of pagination)
        for proj in projects:
            dependency_locations[proj.full_name] = {}

        if config.getboolean('Projects', 'Save', fallback=False):
            # Write all projects to a file
            output_file = config.get('Projects', 'OutputFile', fallback='github-projects.txt')
            with open(output_file, 'w') as fp:
                fp.write("#PROJ_NAME\n")
                fp.write("\n".join(proj for proj in dependency_locations.keys()))
                logger.info("Wrote " + str(len(projects)) + " project(s) to " + output_file)
    # Work with a single project ID
    elif config.has_option('Projects', 'SingleProjectID'):
        dependency_locations[config.get('Projects', 'SingleProjectID')] = {}
    else:
        # No valid option provided, exit
        print("Insufficient parameters provided. Exiting...")
        logger.warning("Insufficient parameters provided. Exiting...")
        exit(0)

    return dependency_locations


def analyze_dependencies(gh, config, dependency_locations):
    # If dependency check with Eclipse Dash is enabled, proceed
    if config.getboolean('General', 'AnalyzeDependencies', fallback=True):
        # Initialize output with dependency locations
        if (config.has_section('DependencyLocations') and
                config.getboolean('DependencyLocations', 'Save', fallback=False)):
            # Write list of dependency files to a file
            output_file = config.get('DependencyLocations', 'OutputFile', fallback='github-dependencies.txt')
            with open(output_file, 'w') as fp:
                fp.write("#PROJ_NAME;PATH;P_LANGUAGE\n")
        output_report = []
        proj_count = 0
        print("Handling dependency location(s) for " + str(len(dependency_locations)) + " Github project(s)")
        logger.info("Handling dependency location(s) for " + str(len(dependency_locations)) + " Github project(s)")
        # For all projects to be processed
        for proj in dependency_locations.keys():
            proj_count = proj_count + 1
            print("Handling Github project " + str(proj_count) + "/" + str(len(dependency_locations)))
            logger.info("Handling Github project " + str(proj_count) + "/" + str(len(dependency_locations)))

            # Get project details
            max_attempts = int(config.get('General', 'APIConnectionAttempts', fallback=3)) + 1
            for i in range(max_attempts):
                try:
                    p_details = gh.get_repo(re.sub(r'https://github.com/', '', proj))
                except GithubException as e:
                    # Max attempts reached
                    if i == max_attempts - 1:
                        print('"' + e.message + '"' + " after " + str(
                            max_attempts - 1) + " attempts to fetch project with ID "
                              + str(proj) + ". Exiting...")
                        logger.error('"' + e.message + '"' + " after " + str(
                            max_attempts - 1) + " attempts to fetch project with ID "
                                     + str(proj) + ". Exiting...")
                        exit(1)
                    logger.warning(
                        '"' + e.message + '"' + " while attempting to fetch project with ID " + str(
                            proj) + ". Retrying in 30 seconds...")
                    sleep(30)

            logger.info("Project full path: " + str(p_details.full_name))

            # User did not provide dependencies for the project
            if len(dependency_locations[proj]) == 0:
                logger.info("No dependencies given for project. Attempting to find them.")

                # Get programming languages of the project
                p_langs = p_details.get_languages()
                logger.info("Project programming languages: " + str(p_langs))

                # Get a list of files in the project repository
                files = []
                repo_contents = p_details.get_contents("")
                while repo_contents:
                    file = repo_contents.pop(0)
                    if file.type == "dir":
                        repo_contents.extend(p_details.get_contents(file.path))
                    else:
                        files.append(file)
                # logger.warning("Project repository not found for: " + p_details.full_name)

                # Attempt to find dependency files for supported programming languages
                if 'Go' in p_langs and config.getboolean('Go', 'Enabled', fallback=True):
                    dependency_paths = utils.find_dependencies_github(config, logger, 'Go', files,
                                                                      default_filenames='go.sum')
                    utils.add_ghdep_locations(dependency_locations, proj, 'Go', dependency_paths)
                if 'Java' in p_langs and config.getboolean('Java', 'Enabled', fallback=True):
                    dependency_paths = utils.find_dependencies_github(config, logger, 'Java', files,
                                                                      default_filenames='pom.xml, build.gradle.kts')
                    utils.add_ghdep_locations(dependency_locations, proj, 'Java', dependency_paths)
                if 'JavaScript' in p_langs and config.getboolean('JavaScript', 'Enabled', fallback=True):
                    dependency_paths = utils.find_dependencies_github(config, logger, 'JavaScript', files,
                                                                      default_filenames='package-lock.json, '
                                                                                        'yarn.lock, pnpm-lock.yaml')
                    utils.add_ghdep_locations(dependency_locations, proj, 'JavaScript', dependency_paths)
                if 'TypeScript' in p_langs and config.getboolean('TypeScript', 'Enabled', fallback=True):
                    dependency_paths = utils.find_dependencies_github(config, logger, 'TypeScript', files,
                                                                      default_filenames='package-lock.json, '
                                                                                        'yarn.lock, pnpm-lock.yaml')
                    utils.add_ghdep_locations(dependency_locations, proj, 'TypeScript', dependency_paths)
                if 'Kotlin' in p_langs and config.getboolean('Kotlin', 'Enabled', fallback=True):
                    dependency_paths = utils.find_dependencies_github(config, logger, 'Kotlin', files,
                                                                      default_filenames='build.gradle.kts')
                    utils.add_ghdep_locations(dependency_locations, proj, 'Kotlin', dependency_paths)
                if 'Python' in p_langs and config.getboolean('Python', 'Enabled', fallback=True):
                    dependency_paths = utils.find_dependencies_github(config, logger, 'Python', files,
                                                                      default_filenames='requirements.txt, '
                                                                                        'pyproject.toml')
                    utils.add_ghdep_locations(dependency_locations, proj, 'Python', dependency_paths)

            # Dash Analysis
            for lang in dependency_locations[proj].keys():
                if config.getboolean(lang, 'Enabled', fallback=True):
                    print("Processing " + str(len(dependency_locations[proj][lang])) +
                          " dependency location(s) for " + lang + " in project " + p_details.full_name)
                    logger.info("Processing " + str(len(dependency_locations[proj][lang])) +
                                " dependency location(s) for " + lang + " in project" + p_details.full_name)
                    output_report.extend(dash_processing(config, p_details, dependency_locations[proj][lang], lang))

        return output_report
    return None


def dash_processing(config, project, filepaths, lang):
    effective_count = 0
    total_count = 0
    output_report = []
    dash_config = {
        'batch_size': config.get('EclipseDash', 'BatchSize', fallback='500'),
        'confidence_threshold': config.get('EclipseDash', 'ConfidenceThreshold', fallback='60'),
        'output_report': config.getboolean('EclipseDash', 'OutputReport', fallback=True),
    }

    # Set review options, when enabled
    review_opts = []
    if config.has_option('EclipseDash', 'ReviewProjectID'):
        review_opts.extend(['-review', '-token', config.get('General', 'GithubAuthToken', fallback=None),
                            '-repo', project.html_url, '-project',
                            config.get('EclipseDash', 'ReviewProjectID', fallback=None)])
    dash_config['review_opts'] = review_opts

    dash_runner = run.Dash(dash_config, logger)

    for fpath in filepaths:
        total_count = total_count + 1
        print("Processing " + lang + " dependency location " + str(total_count) + "/" + str(len(filepaths)))
        logger.info("Processing " + lang + " dependency location " + str(total_count) + "/" + str(len(filepaths)))

        # Set full location for reports
        location = project.full_name + "/blob/" + config.get('General', 'Branch',
                                                             fallback=project.default_branch) + "/" + fpath
        # Java (Maven Only)
        if lang == 'Java' and 'gradle' not in fpath:
            # Git clone repo for Maven
            with tempfile.TemporaryDirectory() as tmpdir:
                p_git = Popen([shutil.which('git'), 'clone', '-b',
                               config.get('General', 'Branch', fallback=project.default_branch), '--single-branch',
                               '--depth', '1', project.clone_url, tmpdir], stdout=PIPE, stderr=PIPE)
                stdout, stderr = p_git.communicate()
                # If errors from Git clone
                if p_git.returncode != 0:
                    logger.warning(
                        "Error Git cloning repository for dependency file (" + project.full_name + "/" + fpath
                        + "). Please check.")
                    error_log = stdout.decode().splitlines()
                    error_log.extend(stderr.decode().splitlines())
                    for line in error_log:
                        if line.strip() != '':
                            logger.warning(line)
                    output_report.append(
                        utils.add_error_report(dash_config, location,
                                               "Error Git cloning repository for the dependency file"))
                    continue
                # Create dependency list with Maven
                relative_path = tmpdir + os.pathsep + fpath.replace(project.full_name, "")

                dash_output = dash_runner.dash_java(relative_path)
                for line in dash_output:
                    if 'error' in line['status']:
                        logger.warning(
                            "Error running Maven for dependency file (" + project.full_name + "/" + fpath
                            + "). Please see debug information below.")
                        logger.warning(line['name'])
                        output_report.append(
                            utils.add_error_report(dash_config, location,
                                                   "Error running Maven for the dependency file"))
                        continue
                    else:
                        line['location'] = (project.full_name + "/blob/" +
                                            config.get('General', 'Branch', fallback=project.default_branch) +
                                            "/" + fpath)
                        output_report.append(line)
        # Java or Kotlin using Gradle
        elif 'gradle' in fpath:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Get raw version of build.gradle.kts
                if tmpfile := get_file_github(config, project, fpath, tmpdir):
                    dash_output = dash_runner.dash_java([str(tmpfile)])
                    for line in dash_output:
                        line['location'] = (project.full_name + "/blob/" +
                                            config.get('General', 'Branch', fallback=project.default_branch) +
                                            "/" + fpath)
                        output_report.append(line)
                else:
                    output_report.append(
                        utils.add_error_report(dash_config, location, "Error obtaining dependency file from GitHub"))
                    continue
        # Python
        elif lang == 'Python':
            with tempfile.TemporaryDirectory() as tmpdir:
                # Get raw version of requirements.txt
                if tmpfile := get_file_github(config, project, fpath, tmpdir):
                    dash_output = dash_runner.dash_python([str(tmpfile)])
                    for line in dash_output:
                        line['location'] = (project.full_name + "/blob/" +
                                            config.get('General', 'Branch', fallback=project.default_branch) +
                                            "/" + fpath)
                        output_report.append(line)
                else:
                    output_report.append(
                        utils.add_error_report(dash_config, location, "Error obtaining dependency file from GitHub"))
                    continue
        # Go, Javascript (or others directly supported)
        else:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Get raw version of file
                if tmpfile := get_file_github(config, project, fpath, tmpdir):
                    dash_output = dash_runner.dash_generic([str(tmpfile)])
                    for line in dash_output:
                        line['location'] = (project.full_name + "/blob/" +
                                            config.get('General', 'Branch', fallback=project.default_branch) +
                                            "/" + fpath)
                        output_report.append(line)
                else:
                    output_report.append(
                        utils.add_error_report(dash_config, location, "Error obtaining dependency file from GitHub"))
                    continue
        effective_count += 1

    return output_report


def get_file_github(config, project, fpath, tmpdir):
    wpath = Path(f'{os.path.join(tmpdir, os.path.basename(fpath))}')
    with open(wpath, 'w+b') as f:
        file_contents = project.get_contents(fpath, ref=config.get('General', 'Branch',
                                                                   fallback=project.default_branch)).decoded_content
        f.write(file_contents)
    return wpath
    # logger.warning("Error obtaining file (" + fpath + ") from Gitlab (" + str(e.response_code) + ")")


def write_output(config, dependency_locations, output_report):
    # Initialize output with dependency locations
    if (config.has_section('DependencyLocations') and
            config.getboolean('DependencyLocations', 'Save', fallback=False)):
        # Write list of dependency locations to a file
        output_file = config.get('DependencyLocations', 'OutputFile', fallback='github-dependencies.txt')
        line_count = 0
        with open(output_file, 'a') as fp:
            for proj in dependency_locations.keys():
                for lang in dependency_locations[proj].keys():
                    fp.write("\n".join(str(proj.id) + ';' + depl + ';' + lang
                                       for depl in dependency_locations[proj][lang]))
                    line_count = line_count + 1
                    fp.write("\n")
        logger.info("Wrote " + str(line_count) + " dependency locations to " + output_file)
    if config.getboolean('EclipseDash', 'OutputReport', fallback=True):
        base_url = 'https://github.com/'

        # Generate output report
        report_filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "-ip-report.html"
        if config.has_option('EclipseDash', 'ReviewProjectID'):
            report.render(base_url, output_report, report_template='review_report', report_filename=report_filename)
        else:
            report.render(base_url, output_report, report_template='default_report', report_filename=report_filename)

        print("IP Analysis Report written to " + os.path.join(os.getcwd(), report_filename))
        logger.info("IP Analysis Report written to " + os.path.join(os.getcwd(), report_filename))
    if config.getboolean('EclipseDash', 'OutputSummary', fallback=False):
        # Generate output summary
        summary_filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "-ip-summary.csv"
        summary_contents = ""
        for e in output_report:
            if e['status'] != 'error':
                summary_contents = (summary_contents + e['name'] + ", " + e['license'] + ", " + e['status'] + ", " +
                                    e['authority'] + "\n")
        with open(summary_filename, 'w') as fp:
            fp.write(summary_contents)

        print("IP Analysis Summary written to " + os.path.join(os.getcwd(), summary_filename))
        logger.info("IP Analysis Summary written to " + os.path.join(os.getcwd(), summary_filename))


def execute(config, repositories=None):
    # Set logging
    log_level = logging.getLevelName(config.get('General', 'LogLevel', fallback='INFO'))
    log_file = config.get('General', 'LogFile', fallback='ip_analysis.log')
    logging.basicConfig(filename=log_file, encoding='utf-8',
                        format='%(asctime)s [%(levelname)s] %(message)s', level=log_level)

    print("Executing IP Analysis of Github Projects")
    logger.info("Starting IP Analysis of Github Projects")

    # Using an access token
    auth_token = config.get('General', 'GithubAuthToken', fallback=None)
    auth = Auth.Token(auth_token) if auth_token else None

    # Open GitHub connection
    gh = Github(auth=auth)

    # Get dependency locations
    dependency_locations = get_dependency_locations(gh, config, repositories)

    # Analyze dependencies
    output_report = analyze_dependencies(gh, config, dependency_locations)

    # Close GitHub connection
    gh.close()

    # Write output
    write_output(config, dependency_locations, output_report)

    print("IP Analysis of Github Projects is now complete. Goodbye!")
    logger.info("IP Analysis of Github Projects is now complete. Goodbye!")
