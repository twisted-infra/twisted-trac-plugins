from setuptools import setup, find_packages

setup(
    entry_points={'trac.plugins': "IRC REPORT TICKET MAN = ticket_reporter"},
    name='IRC REPORT TICKET MAN', version='ONE',
    description='REPORT TICKET CHANGE ON IRC CHANNEL',
    author="JEAN-PAUL CALDERONE", author_email="DO NOT SEND ME EMAIL I PROBABLY HATE YOU",
    license='YOU MAY NOT USE THIS SOFTWARE', url='THERE IS NO URL',
    packages=['ticket_reporter'])
