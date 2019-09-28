# pylint:disable=line-too-long
"""
The tool to check the availability or syntax of domains, IPv4, IPv6 or URL.

::


    ██████╗ ██╗   ██╗███████╗██╗   ██╗███╗   ██╗ ██████╗███████╗██████╗ ██╗     ███████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██║     ██╔════╝
    ██████╔╝ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║██║     █████╗  ██████╔╝██║     █████╗
    ██╔═══╝   ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗██║     ██╔══╝
    ██║        ██║   ██║     ╚██████╔╝██║ ╚████║╚██████╗███████╗██████╔╝███████╗███████╗
    ╚═╝        ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═════╝ ╚══════╝╚══════╝

This submodule will create the autosave logic.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Special thanks:
    https://pyfunceble.github.io/special-thanks.html

Contributors:
    https://pyfunceble.github.io/contributors.html

Project link:
    https://github.com/funilrys/PyFunceble

Project documentation:
    https://pyfunceble.readthedocs.io/en/dev/

Project homepage:
    https://pyfunceble.github.io/

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

from sys import stdout as sys_stdout

import PyFunceble
from PyFunceble.helpers import Command, Regex
from PyFunceble.percentage import Percentage


class AutoSave:  # pragma: no cover  pylint: disable=too-few-public-methods
    """
    Provide the autosave logic.

    :param bool is_last_domain:
        Tell this subsystem if we are at the very end of the file testing.

    :param bool is_bypass:
        Tell this subsystem if we are in bypassing mode.
    """

    # We set the varible which will save the global authorization to operate.
    authorized = None
    # We set the variable which will save the travis instance.
    travis = None
    # We set the variable which will save the starting time.
    start_time = None
    # We set the variable which will save the end time.
    endtime = None
    # We set the variable which will process as a chache for the
    # time exceeed value.
    time_exceed = False

    def __init__(self, start_time=None):
        self.travis = Travis()
        self.authorized = self.authorization()

        PyFunceble.Logger().info(f"Authorized: {self.authorized}")

        if self.authorized:
            self.travis.init()
            self.travis.bypass()

            self.start_time = PyFunceble.datetime.fromtimestamp(int(start_time))
            self.end_time = self.start_time + PyFunceble.timedelta(
                minutes=int(PyFunceble.CONFIGURATION.travis_autosave_minutes)
            )

            PyFunceble.Logger().debug(f"Start Time: {self.start_time}")
            PyFunceble.Logger().debug(f"End Time:  {self.end_time}")

    def authorization(self):
        """
        Provide the authorization to operate.
        """

        return self.travis.authorized

    def is_time_exceed(self):
        """
        Check if the end time is exceed.
        """

        if self.authorized:
            # We are authorized to operate.

            if not self.time_exceed and PyFunceble.datetime.now() >= self.end_time:
                # * We did not tested previously if the time exceed.
                # and
                # * The time exceed.

                # We update the time exceed marker.
                self.time_exceed = True

        PyFunceble.Logger().debug(f"Time exceed: {self.time_exceed}")

        return self.time_exceed

    def process(self, test_completed=False):
        """
        Process the autosave base on the current state of the test.

        :param bool test_completed: Tell us if we finished the test.
        """

        if self.authorized:
            # We are authorized to operate with Travis.

            if test_completed:
                # The test was completed.

                # We run the end commit.
                self.travis.end_commit()
            elif self.is_time_exceed():
                # The current time excessed the minimal time for autosaving.

                # We run the not end commit.
                self.travis.not_end_commit()


class Travis:
    """
    Provide the autosaving for under travis CI.
    """

    # Save the authorization to process.
    authorized = False

    # We set the regex to match in order to bypass the execution of
    # PyFunceble.
    regex_bypass = r"\[PyFunceble\sskip\]"

    def __init__(self):
        self.authorized = self.authorization()

    @classmethod
    def authorization(cls):
        """
        Provide the operation authorization.
        """

        try:
            _ = PyFunceble.environ["TRAVIS_BUILD_DIR"]

            return PyFunceble.CONFIGURATION.travis
        except KeyError:
            return False

    @classmethod
    def __get_remote_destination(cls):
        """
        Return the remote destination we are going to use.
        """

        regex = r"(?:[a-z]+(?:\s+|\t+))(.*)(?:(?:\s+|\t+)\([a-z]+\))"
        remote_of_interest = [
            x for x in Command("git remote -v").execute().splitlines() if "(push)" in x
        ][0]

        filtered = Regex(remote_of_interest, regex, return_data=True, group=1).match()

        if filtered and "@" in filtered:
            return filtered[filtered.find("@") + 1 :]
        raise ValueError("Could not find remote.")

    def init(self):
        """
        Init the TravisCI virtual machine.
        """

        if self.authorized:
            remote = self.__get_remote_destination()

            commands = [
                ("git remote rm origin", True),
                (
                    "git remote add origin "
                    f'https://{PyFunceble.environ["GH_TOKEN"]}@{remote}',  # pylint: disable=line-too-long
                    False,
                ),
                (
                    f'git config --global user.email "{PyFunceble.environ["GIT_EMAIL"]}"',
                    True,
                ),
                (
                    f'git config --global user.name "{PyFunceble.environ["GIT_NAME"]}"',
                    True,
                ),
                ("git config --global push.default simple", True),
                (f'git checkout "{PyFunceble.CONFIGURATION.travis_branch}"', True),
            ]

            for command, allow_stdout in commands:
                if allow_stdout:
                    PyFunceble.Logger().debug(f"Executing: {repr(command)}")
                    for line in Command(command).run():
                        sys_stdout.write("{}\n".format(line))
                else:
                    Command(command).execute()

    def permissions(self):
        """
        Set permissions in order to avoid issues before commiting.
        """

        if self.authorized:
            build_dir = PyFunceble.environ["TRAVIS_BUILD_DIR"]
            commands = [
                "sudo chown -R travis:travis %s" % (build_dir),
                "sudo chgrp -R travis %s" % (build_dir),
                "sudo chmod -R g+rwX %s" % (build_dir),
                "sudo chmod 777 -Rf %s.git"
                % (build_dir + PyFunceble.directory_separator),
                r"sudo find %s -type d -exec chmod g+x '{}' \;" % (build_dir),
            ]

            for command in commands:
                Command(command).execute()
                PyFunceble.Logger().debug(f"Executed: {command}")

            if Command("git config core.sharedRepository").execute() == "":
                Command("git config core.sharedRepository group").execute()

    def bypass(self):
        """
        Stop everything if :code:`[PyFunceble skip]` is matched into
        the latest commit message.
        """

        if (
            self.authorized
            and Regex(
                Command("git log -1").execute(), self.regex_bypass, return_data=False
            ).match()
        ):

            PyFunceble.Logger().info(f"Bypass given. Ending process.")

            self.end_commit()

    def push(self):
        """
        Push.
        """

        if self.authorized:

            command = "git push origin {0}".format(
                PyFunceble.CONFIGURATION.travis_branch
            )

            Command(command).execute()
            PyFunceble.Logger().info(f"Executed: {command}")

            PyFunceble.sys.exit(0)

    def end_commit(self):
        """
        Commit and push at the very end of the test.
        """

        if self.authorized:
            Percentage().log()
            self.permissions()

            command = 'git add --all && git commit -a -m "{0}"'.format(
                PyFunceble.CONFIGURATION.travis_autosave_final_commit + " [ci skip]"
            )

            if PyFunceble.CONFIGURATION.command_before_end:
                PyFunceble.Logger().info(
                    f"Executing: {PyFunceble.CONFIGURATION.command_before_end}"
                )

                for line in Command(PyFunceble.CONFIGURATION.command_before_end).run():
                    sys_stdout.write("{}\n".format(line))

                self.permissions()

            PyFunceble.Logger().info(f"Executing: {command}")

            for line in Command(command).run():
                sys_stdout.write("{}\n".format(line))
            self.push()

    def not_end_commit(self):
        """
        Commit and push at on the middle of the test.
        """

        if self.authorized:
            Percentage().log()
            self.permissions()

            command = 'git add --all && git commit -a -m "{0}"'.format(
                PyFunceble.CONFIGURATION.travis_autosave_commit
            )

            if PyFunceble.CONFIGURATION.command:
                PyFunceble.Logger().info(
                    f"Executing: {PyFunceble.CONFIGURATION.command}"
                )

                for line in Command(PyFunceble.CONFIGURATION.command).run():
                    sys_stdout.write("{}\n".format(line))

                self.permissions()

            PyFunceble.Logger().info(f"Executing: {command}")

            for line in Command(command).run():
                sys_stdout.write("{}\n".format(line))

            self.push()
