#  Copyright (c) 2025 The Eclipse Foundation
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
from datetime import datetime

from github import Auth, Github
from gitlab import Gitlab

from .. import ghub
from .. import glab
from ..common import eclipse_api
from ..dash import report

logger = logging.getLogger(__name__)


def write_gh_dep_locations(config, dependency_locations):
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


def write_gl_dep_locations(config, dependency_locations):
    if (config.has_section('DependencyLocations') and
            config.getboolean('DependencyLocations', 'Save', fallback=False)):
        # Write list of dependency locations to a file
        output_file = config.get('DependencyLocations', 'OutputFile', fallback='gitlab-dependencies.txt')
        line_count = 0
        with open(output_file, 'a') as fp:
            for proj in dependency_locations.keys():
                for lang in dependency_locations[proj].keys():
                    fp.write("\n".join(proj + ';' + depl + ';' + lang
                                       for depl in dependency_locations[proj][lang]))
                    line_count = line_count + 1
                    fp.write("\n")
        logger.info("Wrote " + str(line_count) + " dependency locations to " + output_file)


def write_output_report(config, output_report):
    if config.getboolean('EclipseDash', 'OutputReport', fallback=True):
        # Generate output report
        report_filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "-ip-report.html"
        if config.has_option('EclipseDash', 'ReviewProjectID'):
            report.render("", output_report, report_template='review_report', report_filename=report_filename)
        else:
            report.render("", output_report, report_template='default_report', report_filename=report_filename)

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


def execute(config):
    # Set logging
    log_level = logging.getLevelName(config.get('General', 'LogLevel', fallback='INFO'))
    log_file = config.get('General', 'LogFile', fallback='ip_analysis.log')
    logging.basicConfig(filename=log_file, encoding='utf-8',
                        format='%(asctime)s [%(levelname)s] %(message)s', level=log_level)

    print("Executing IP Analysis of Eclipse Project")
    logger.info("Starting IP Analysis of Eclipse Project")

    # Get repositories for Eclipse Project
    eclipse_project = config.get('General', 'EclipseProject', fallback='technology.dash')
    repositories = eclipse_api.get_repositories(eclipse_project, logger)

    logger.info('Found ' + str(len(repositories)) + ' repositories for ' + eclipse_project)

    if repositories is None:
        print("Error obtaining repositories for " + eclipse_project
              + ". Please check the logs for more information.")
        exit(1)

    output_report = []
    if 'github' in repositories:
        # Using an access token
        auth_token = config.get('General', 'GithubAuthToken', fallback=None)
        auth = Auth.Token(auth_token) if auth_token else None

        # Open GitHub connection
        gh = Github(auth=auth)

        # Get dependency locations
        dependency_locations = ghub.remote.get_dependency_locations(gh, config, repositories['github'])

        # Analyze dependencies
        results = ghub.remote.analyze_dependencies(gh, config, dependency_locations)
        for r in results:
            r['base_url'] = 'https://github.com/'
        output_report.extend(results)

        # Close GitHub connection
        gh.close()

        # Write dependency locations (if enabled)
        write_gh_dep_locations(config, dependency_locations)

    if 'gitlab' in repositories:
        # Gitlab instance
        gl = Gitlab(url=config.get('General', 'GitlabURL', fallback='https://gitlab.eclipse.org'),
                    private_token=config.get('General', 'GitlabAuthToken', fallback=None))

        # Get dependency locations
        dependency_locations = glab.remote.get_dependency_locations(gl, config, repositories['gitlab'])

        # Analyze dependencies
        results = glab.remote.analyze_dependencies(gl, config, dependency_locations)
        for r in results:
            r['base_url'] = config.get('General', 'GitlabURL', fallback='https://gitlab.eclipse.org') + "/"
        output_report.extend(results)

        # Write dependency locations (if enabled)
        write_gl_dep_locations(config, dependency_locations)

    # Write an output report
    write_output_report(config, output_report)

    print("IP Analysis of Eclipse Project is now complete. Goodbye!")
    logger.info("IP Analysis of Eclipse Project is now complete. Goodbye!")
