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

__version__ = "0.1.1"

import argparse
import configparser
from shutil import which

from . import generic
from . import ghub
from . import glab

config = configparser.ConfigParser()


def main():
    # Handle parameters and defaults
    parser = argparse.ArgumentParser()
    parser.add_argument('-ci', '--ci_mode', action='store_true', help='execute in CI mode')
    parser.add_argument('-gh', '--github', action='store_true', help='execute for GitHub')
    parser.add_argument('--gh-token', help='Github access token for API')
    parser.add_argument('-gl', '--gitlab', default='gitlab.eclipse.org', help='execute for GitLab URL')
    parser.add_argument('--gl-token', help='Gitlab access token for API/IP review')
    parser.add_argument('-b', '--branch', help='branch to analyze')
    parser.add_argument('-c', '--config', default='config.ini', help='config file to use')
    parser.add_argument('-df', '--dependencies_file', help='file with dependency locations to analyze')
    parser.add_argument('-e', '--eclipse_project', help='execute for Eclipse Project')
    parser.add_argument('-g', '--group', help='Github Organization/Gitlab Group to analyze')
    parser.add_argument('-p', '--project', help='Github/Gitlab project to analyze')
    parser.add_argument('-pf', '--projects_file', help='file with projects to analyze')
    parser.add_argument('-r', '--review', nargs='?', const='_AUTO_', help='Eclipse Project ID for IP review')
    parser.add_argument('-s', '--summary', action='store_true', help='output is an Eclipse Dash summary file')
    parser.add_argument('-v', '--version', action='version', version=f'Eclipse IP Analysis {__version__}',
                        help='Show the version and exit')

    try:
        args = parser.parse_args()
        config.read(args.config)

        if args.branch is not None:
            if not config.has_section('General'):
                config.add_section('General')
            config.set('General', 'Branch', str(args.branch))
        if args.group is not None:
            if not config.has_section('Groups'):
                config.add_section('Groups')
            config.set('Groups', 'BaseGroupID', str(args.group))
        if args.project is not None:
            if not config.has_section('Projects'):
                config.add_section('Projects')
            config.set('Projects', 'SingleProjectID', str(args.project))
        if args.projects_file is not None:
            if not config.has_section('Projects'):
                config.add_section('Projects')
            config.set('Projects', 'LoadFromFile', 'Yes')
            config.set('Projects', 'InputFile', str(args.projects_file))
        if args.dependencies_file is not None:
            if not config.has_section('DependencyLocations'):
                config.add_section('DependencyLocations')
            config.set('DependencyLocations', 'LoadFromFile', 'Yes')
            config.set('DependencyLocations', 'InputFile', str(args.dependencies_file))
        if args.summary:
            if not config.has_section('EclipseDash'):
                config.add_section('EclipseDash')
            config.set('EclipseDash', 'OutputReport', 'No')
            config.set('EclipseDash', 'OutputSummary', 'Yes')
        if args.review is not None:
            if args.review == '_AUTO_':
                # Executing for an Eclipse Project, the user only needs -r and the ID for review = Eclipse Project ID
                if args.eclipse_project is not None:
                    args.review = args.eclipse_project
                else:
                    print('You must provide an Eclipse Project ID for Automatic IP Team Review Requests')
                    print('Exiting...')
                    exit(0)
            if not config.has_section('EclipseDash'):
                config.add_section('EclipseDash')
            config.set('EclipseDash', 'ReviewProjectID', str(args.review))
            if args.gl_token is None:
                print('You must provide a GitLab token for Automatic IP Team Review Requests')
                print('Exiting...')
                exit(0)

        # Check for pre-requisites
        if which('git') is None:
            print('Git CLI not found. Please check the official installation instructions:')
            print('https://git-scm.com/book/en/v2/Getting-Started-Installing-Git')
            print('Exiting...')
            exit(0)
        if which('java') is None:
            print('Java CLI not found. Please check the official installation instructions:')
            print('https://adoptium.net/installation/')
            print('Exiting...')
            exit(0)
        if which('mvn') is None:
            print('Maven CLI not found. Please check the official installation instructions:')
            print('https://maven.apache.org/install.html')
            print('Exiting...')
            exit(0)

        # If in CI mode
        if args.ci_mode:
            glab.ci.execute()
        elif args.eclipse_project is not None:
            if not config.has_section('General'):
                config.add_section('General')
            config.set('General', 'EclipseProject', str(args.eclipse_project))
            if args.gh_token is not None:
                config.set('General', 'GithubAuthToken', str(args.gh_token))
            if args.gl_token is not None:
                config.set('General', 'GitlabAuthToken', str(args.gl_token))
            generic.remote.execute(config)
        elif args.github:
            if not config.has_section('General'):
                config.add_section('General')
            if args.gh_token is not None:
                config.set('General', 'GithubAuthToken', str(args.gh_token))
            # Only for Automatic IP Team Review Requests
            if args.gl_token is not None:
                config.set('General', 'GitlabAuthToken', str(args.gl_token))
            ghub.remote.execute(config)
        elif args.gitlab is not None:
            if not config.has_section('General'):
                config.add_section('General')
            config.set('General', 'GitlabURL', 'https://' + str(args.gitlab))
            if args.gl_token is not None:
                config.set('General', 'GitlabAuthToken', str(args.gl_token))
            glab.remote.execute(config)
        else:
            print('Not yet supported. Exiting...')
            exit(0)

    except argparse.ArgumentError as e:
        print(e)


if __name__ == '__main__':
    main()
