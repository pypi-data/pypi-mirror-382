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

import re
import tempfile
from collections import OrderedDict
from datetime import datetime
from importlib import resources
from os import path
from shutil import which
from subprocess import PIPE, Popen
from tomllib import loads, TOMLDecodeError

from chardet import detect

from ..common import utils


def read_file(fpath, decode=True):
    # Get file contents
    try:
        with open(fpath, 'rb') as fp:
            raw_contents = fp.read()
    except FileNotFoundError:
        return None

    # If contents need to be decoded
    if decode:
        # Detect charset and decode
        res = detect(raw_contents)
        if res['encoding'] is None:
            return None
        return raw_contents.decode(res['encoding'])

    return raw_contents


def write_file(fpath, raw_contents):
    # Write file contents
    with open(fpath, 'wb') as fp:
        fp.write(raw_contents)


def handle_gradle(contents):
    # Get only the dependencies
    filtered_contents = re.findall(r'(?s)(?<=^dependencies\s\{)(.+?)(?=})', contents,
                                   flags=re.MULTILINE)

    # Remove Kotlin internals
    filtered_contents = "\n".join(x for x in filtered_contents[0].splitlines() if 'kotlin(' not in x)

    # Expand variables with versions
    variables = re.findall(r'val(.*=.*)$', filtered_contents, flags=re.MULTILINE)
    for var in variables:
        var_declaration = var.split('=')
        filtered_contents = filtered_contents.replace('$' + var_declaration[0].strip(),
                                                      var_declaration[1].strip().replace('"', ''))

    # Sort dependencies
    sorted_contents = re.findall(r'"(.*?)"', filtered_contents, flags=re.MULTILINE)
    sorted_contents.sort()

    # Convert from list to text and ignore duplicates
    processed_contents = "\n".join(list(OrderedDict.fromkeys(sorted_contents)))

    # Encode as file
    raw_contents = processed_contents.encode('utf-8')

    return raw_contents


def handle_maven(fpath):
    # Run Maven
    p_maven = Popen([which('mvn'), '-f', fpath, 'verify', 'dependency:list', '-DskipTests',
                     '-Dmaven.javadoc.skip=true', '-DoutputFile=maven.deps'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = p_maven.communicate()

    # If no errors from Maven
    if p_maven.returncode == 0:
        with open(fpath.replace('pom.xml', 'maven.deps'), 'r') as fp:
            raw_contents = fp.read()

        # Retrieve only the right content
        processed_contents = [x.group(0) for x in re.finditer(r'\S+:(system|provided|compile)', raw_contents)]

        # Sort and remove duplicates
        processed_contents.sort()
        processed_contents = "\n".join(list(OrderedDict.fromkeys(processed_contents)))
        raw_contents = processed_contents.encode('utf-8')

        return raw_contents, None
    else:
        # Get Maven error
        maven_error = [x for x in stdout.decode('utf-8', errors='ignore').splitlines()
                       if '[ERROR]' in x][0].replace('[ERROR]', '').strip()
        return None, maven_error


class Dash:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def dash_execute(self, input_file, tmpdir):
        # Output summary full path
        summary_filepath = path.join(tmpdir, str(datetime.now().timestamp()) + '_analysis.txt')

        # Run Eclipse Dash
        with resources.as_file(resources.files(__package__).joinpath('assets/eclipse-dash.jar')) as exe:
            args = ['java', '-jar', str(exe), '-summary', summary_filepath,
                    '-batch', self.config['batch_size'], '-confidence',
                    self.config['confidence_threshold']]
            args.extend(self.config['review_opts'] + [input_file])
            p_dash = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p_dash.communicate()

            # Log Eclipse Dash Output
            error = False
            reviews = {}
            last = ''
            for line in stderr.decode().splitlines():
                if line.startswith('[main] INFO'):
                    line = line.replace('[main] INFO ', '')
                    self.logger.info('[DASH] ' + line)
                    # Report automatic IP team review requests
                    if line.startswith('A review is required for'):
                        line = line.replace('A review is required for ', '')
                        reviews[line.strip()[:-1].strip()] = ''
                        last = line.strip()[:-1].strip()
                    if line.startswith('A review request was created'):
                        line = line.replace('A review request was created ', '')
                        reviews[last] = line.strip()[:-1].strip()
                if line.startswith('[main] ERROR'):
                    line = line.replace('[main] ERROR ', '')
                    self.logger.error('[DASH] ' + line)
            if error:
                print("Eclipse Dash Execution Error. Please check the logs for more information.")

            return p_dash.returncode, summary_filepath, reviews

    def dash_report(self, input_file):
        report = []
        with tempfile.TemporaryDirectory() as tmpdir:
            return_code, summary_filepath, reviews = self.dash_execute(input_file, tmpdir)
            try:
                with open(summary_filepath, 'r') as fp:
                    for line in fp:
                        columns = [x.strip() for x in line.split(',')]
                        entry = {'name': columns[0], 'license': columns[1], 'status': columns[2],
                                 'authority': columns[3], 'review': reviews.get(columns[0], '')}
                        report.append(entry)
            except FileNotFoundError:
                return None
        return report

    def dash_generic(self, dependency_locations):
        report = []
        for dependency in dependency_locations:
            # Run Dash and get report
            rep = self.dash_report(dependency)
            if rep is not None:
                for line in rep:
                    line['location'] = dependency
                    report.append(line)
        return report

    def dash_python(self, dependency_locations):
        report = []
        for dependency in dependency_locations:
            # Get file contents
            contents = read_file(dependency)
            if contents is None:
                report.append(utils.add_error_report(self.config, dependency,
                                                     "Error detecting encoding for the dependency file"))
                continue

            # Handle pyproject.toml
            if 'pyproject.toml' in dependency:
                try:
                    toml = loads(contents)
                    # If no project table or dependencies within it, skip
                    if 'project' not in toml.keys() or 'dependencies' not in toml['project'].keys():
                        continue
                    contents = "\n".join(x for x in toml['project']['dependencies'])
                except KeyError:
                    report.append(utils.add_error_report(self.config, dependency,
                                                         "Error parsing pyproject.toml file"))
                    continue
                except TOMLDecodeError:
                    report.append(utils.add_error_report(self.config, dependency,
                                                         "Error decoding pyproject.toml file"))
                    continue

            # If using Conda
            if '$ conda' in contents:
                # Get build platform
                line = next(line for line in contents.splitlines() if 'platform:' in line)
                platform = line.split(": ", 1)[1].strip()
                # Remove commented lines
                contents = re.sub(r'(?m)#.*', '', contents, flags=re.MULTILINE)
                # Remove empty lines
                contents = re.sub(r'^\s*\n', '', contents, flags=re.MULTILINE)
                contents = contents.rstrip()
                # Sort content
                sorted_contents = contents.splitlines()
                sorted_contents.sort()
                # Convert from list to text and ignore duplicates
                contents = "\n".join(list(OrderedDict.fromkeys(sorted_contents)))
                # Change format to be compatible with Eclipse Dash
                contents = re.sub(r'^([^=]+)=([^=]+)=(.+)$', rf'conda/conda-forge/{platform}/\1/\2-\3',
                                  contents, flags=re.MULTILINE)
            else:
                # Remove commented lines
                contents = re.sub(r'(?m)#.*', '', contents, flags=re.MULTILINE)

                # If multiple version conditions given, only consider the base one
                contents = re.sub(r'(?m),.*', '', contents, flags=re.MULTILINE)

                # If there are any additional requirements for a package, ignore them for this purpose
                contents = re.sub(r'(?m);.*', '', contents, flags=re.MULTILINE)

                # Sort content
                sorted_contents = contents.splitlines()
                sorted_contents.sort()

                # Handle versions
                contents = []
                for line in sorted_contents:
                    # Remove any whitespaces
                    line = re.sub(r'\s+', '', line)
                    if line == "":
                        continue
                    # If a range of versions is given assume the base version
                    elif "<" in line:
                        tmp = line.split('<')
                        contents.append(tmp[0] + "==" + tmp[1].replace("=", "").strip())
                    elif ">" in line:
                        tmp = line.split('>')
                        contents.append(tmp[0] + "==" + tmp[1].replace("=", "").strip())
                    elif "=" not in line:
                        # When no version is specified, assume the latest
                        try:
                            contents.append(line + "==" + utils.get_pypy_latest_version(line))
                        except ValueError:
                            self.logger.warning(
                                "Error obtaining latest PyPi version for " + line + ". Attempting with " +
                                line.capitalize())
                            try:
                                contents.append(line.capitalize() + "==" +
                                                utils.get_pypy_latest_version(line.capitalize()))
                            except ValueError:
                                self.logger.warning(
                                    "Error obtaining latest PyPi version for " + line.capitalize() + ". Gave up...")
                                continue
                        except BaseException:
                            self.logger.warning(
                                "Error obtaining latest PyPi version for " + line + ". Gave up...")
                            continue
                    else:
                        contents.append(line)

                # Convert from list to text and ignore duplicates
                contents = "\n".join(list(OrderedDict.fromkeys(contents)))

                # Change format to be compatible with Eclipse Dash
                contents = re.sub(r'^([^=~ ]+)[=|~]=([^= ]+)$', r'pypi/pypi/-/\1/\2', contents,
                                  flags=re.MULTILINE)
                contents = re.sub(r'\[.*]', '', contents, flags=re.MULTILINE)

            # Encode as file
            raw_contents = contents.encode('utf-8')
            write_file(dependency, raw_contents)

            # Run Dash and get report
            rep = self.dash_report(dependency)
            if rep is not None:
                for line in rep:
                    line['location'] = dependency
                    report.append(line)
        return report

    def dash_java(self, dependency_locations):
        report = []
        for dependency in dependency_locations:
            if 'gradle' in dependency:
                # Get file contents
                contents = read_file(dependency)
                if contents is None:
                    report.append(utils.add_error_report(self.config, dependency,
                                                         "Error detecting encoding for the dependency file"))
                    continue

                # Process contents for Gradle analysis
                raw_contents = handle_gradle(contents)
                write_file(dependency, raw_contents)

                # Run Dash and get report
                rep = self.dash_report(dependency)
                if rep is not None:
                    for line in rep:
                        line['location'] = dependency
                        report.append(line)
            elif 'pom.xml' in dependency:
                # Process contents for Maven analysis
                raw_contents, error = handle_maven(dependency)
                if raw_contents is None:
                    report.append(utils.add_error_report(self.config, dependency, error))
                    continue
                new_dependency = dependency.replace('pom.xml', 'maven.deps')
                write_file(new_dependency, raw_contents)

                # Run Dash and get report
                rep = self.dash_report(new_dependency)
                if rep is not None:
                    for line in rep:
                        line['location'] = dependency
                        report.append(line)
        return report

    def dash_kotlin(self, dependency_locations):
        report = []
        for dependency in dependency_locations:
            if 'gradle' in dependency:
                # Get file contents
                contents = read_file(dependency)
                if contents is None:
                    report.append(utils.add_error_report(self.config, dependency,
                                                         "Error detecting encoding for the dependency file"))
                    continue

                # Process contents for Gradle analysis
                raw_contents = handle_gradle(contents)
                write_file(dependency, raw_contents)

                # Run Dash and get report
                rep = self.dash_report(dependency)
                if rep is not None:
                    for line in rep:
                        line['location'] = dependency
                        report.append(line)
        return report
