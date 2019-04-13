# pylint: disable=line-too-long
"""
The tool to check the availability or syntax of domains, IPv4 or URL.

::


    ██████╗ ██╗   ██╗███████╗██╗   ██╗███╗   ██╗ ██████╗███████╗██████╗ ██╗     ███████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██║     ██╔════╝
    ██████╔╝ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║██║     █████╗  ██████╔╝██║     █████╗
    ██╔═══╝   ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗██║     ██╔══╝
    ██║        ██║   ██║     ╚██████╔╝██║ ╚████║╚██████╗███████╗██████╔╝███████╗███████╗
    ╚═╝        ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═════╝ ╚══════╝╚══════╝

Provide the logic and interface for a test with the API.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Special thanks:
    https://pyfunceble.readthedocs.io/en/dev/special-thanks.html

Contributors:
    http://pyfunceble.readthedocs.io/en/dev/contributors.html

Project link:
    https://github.com/funilrys/PyFunceble

Project documentation:
    https://pyfunceble.readthedocs.io/en/dev/

Project homepage:
    https://funilrys.github.io/PyFunceble/

License:
::


    MIT License

    Copyright (c) 2017, 2018, 2019 Nissar Chababy

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
# pylint: enable=line-too-long

import PyFunceble
from PyFunceble.check import Check
from PyFunceble.status import Status, URLStatus
from PyFunceble.whois_db import WhoisDB


class APICore:
    """
    Provide the logic and interface for the tests from the API.

    :param str subject: The element we are testing.
    :param bool complete:
        Activate the return of a dictionnary with signigicant - if not all -
        data about the test.

    :param dict configuration:
        The configuration to
    """

    # The subject we are working with.
    subject = None
    # Tell us if we have to return all possible data.
    complete = False
    # Saves the configuration.
    configuration = None

    def __init__(self, subject, complete=False, configuration=None):
        # We share the subject.
        self.subject = subject

        # We share the complete option.
        self.complete = complete
        # We share the configuration.
        self.configuration = configuration

        # We load the global configuration
        # if it was not alreay done.
        PyFunceble.load_config(
            generate_directory_structure=False, custom=self.configuration
        )

        # We update the configuration with the given
        # configuration.
        PyFunceble.Preset().api()

        # We create an instance of the whois database.
        self.whois_db = WhoisDB()

    def domain_and_ip(self):
        """
        Run a domain/IP avaibility check over the given subject.
        """

        if isinstance(self.subject, list):
            # The given subject is a list of subjects.

            # We initiate a variable which save our result.
            result = {}

            for subject in self.subject:
                # We loop through the list of subject.

                # We get the complete data related to the status
                # of the subject.
                data = Status(
                    subject, subject_type="domain", whois_db=self.whois_db
                ).get()

                if self.complete:
                    # The user want a copy of the complete data.

                    # We set it.
                    result[subject] = data
                else:
                    # The user do not want a copy of the complete data.

                    # We only set the status.
                    result[subject] = data["status"]

            # We return our local result.
            return result

        # We get the status of the given subject.
        data = Status(self.subject, subject_type="domain", whois_db=self.whois_db).get()

        if self.complete:
            # The user want a copy of the compelte data.

            # We return them
            return data

        # We only return the status.
        return data["status"]

    def domain_syntax(self):
        """
        Run a domain syntax check over the given subject.
        """

        if isinstance(self.subject, list):
            # The given subject is a list of subject.

            # We return the validity of each subjects.
            return {subject: Check(subject).is_domain() for subject in self.subject}

        # We return the validity of the the given subject.
        return Check(self.subject).is_domain()

    def subdomain_syntax(self):
        """
        Run a subdomain syntax check over the given subject.
        """

        if isinstance(self.subject, list):
            # The given subjet is a list of subject.

            # We return the validity of each subjects.
            return {subject: Check(subject).is_subdomain() for subject in self.subject}

        # We return the validity of the given subject.
        return Check(self.subject).is_subdomain()

    def ipv4_syntax(self):
        """
        Run an IPv4 syntax check over the given subject.
        """

        if isinstance(self.subject, list):
            # The given subjet is a list of subject.

            # We return the validity of each subjects.
            return {subject: Check(subject).is_ipv4() for subject in self.subject}

        # We return the validity of the given subject.
        return Check(self.subject).is_ipv4()

    def ipv4_range_syntax(self):
        """
        Run an IPv4 range syntax check over the given subject.
        """

        if isinstance(self.subject, list):
            # The given subjet is a list of subject.

            # We return the validity of each subjects.
            return {subject: Check(subject).is_ipv4_range() for subject in self.subject}

        # We return the validity of the given subject.
        return Check(self.subject).is_ipv4_range()

    def url(self):
        """
        Run an URL avaibility check over the given subject.
        """

        if isinstance(self.subject, list):
            # The given subjet is a list of subject.

            # We initiate a local variable which will save
            # what we are going to return.
            result = {}

            for subject in self.subject:
                # We loop through the list of subjects.

                # We get the complete data about the status.
                data = URLStatus(subject, subject_type="url").get()

                if self.complete:
                    # The user want a complete copy of the data.

                    # We set it.
                    result[subject] = data
                else:
                    # The user does not want a complete copy of the data.

                    # We only set the status.
                    result[subject] = data["status"]

            # We return the result of each subjects.
            return result

        # We get the complete data about the status of the subject.
        data = URLStatus(self.subject, subject_type="url").get()

        if self.complete:
            # The user want a complete copy of the data.

            # We return them.
            return data

        # We return the result of each subjects.
        return data["status"]

    def url_syntax(self):
        """
        Run an IPv4 syntax check over the given subject.
        """

        if isinstance(self.subject, list):
            # The given subjet is a list of subject.

            # We return the validity of each subjects.
            return {subject: Check(subject).is_url() for subject in self.subject}

        # We return the validity of the subject.
        return Check(self.subject).is_url()