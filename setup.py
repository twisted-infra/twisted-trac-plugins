# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from setuptools import setup

setup(
    entry_points={
        'trac.plugins': [
            "release-macro = twisted_trac_plugins.release_macro",
            "ticket-reporter = twisted_trac_plugins.ticket_reporter",
            ],
        },
    name='Twisted Trac Plugins',
    version='0.1',
    description="Plugins for twisted's trac instance",
    author="Tom Prince",
    author_email="tomprince@twistedmatrix.com",
    license='MIT',
    url='https://github.com/twisted-infra/twisted-trac-plugins',
    packages=['twisted_trac_plugins'],
)
