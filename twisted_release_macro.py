"""
Trac macros for Twisted.
"""

from StringIO import StringIO
from urlparse import urlparse

from trac.core import TracError
from trac.util.html import Markup
from trac.wiki.formatter import OneLinerFormatter
from trac.wiki.macros import WikiMacroBase

from twisted.python.versions import Version
from twisted.python.filepath import FilePath


RELEASES = FilePath('/srv/www-data/twisted/Releases/')



class ProjectVersionMacro(WikiMacroBase):
    """
    Macro that knows the current [http://twistedmatrix.com Twisted] version number.

    The version information is loaded from a folder containing text files with
    md5sums for each released package/installer. Also see the
    [http://twistedmatrix.com/trac/wiki/Downloads#SignedMD5Sums Twisted downloads]
    page.

    '''Standalone'''
    {{{
    [[ProjectVersion]]
    }}}

    produces:

    [[ProjectVersion]]

    '''URL'''

    {{{
    [[ProjectVersion(http://twistedmatrix.com/Releases/Twisted/%(major)s.%(minor)s/Twisted-%(base)s.win32-py2.7.msi Twisted %(base)s for Python 2.7)]]
    }}}

    produces:

    [[ProjectVersion(http://twistedmatrix.com/Releases/Twisted/%(major)s.%(minor)s/Twisted-%(base)s.win32-py2.7.msi Twisted %(base)s for Python 2.7)]]

    Including the MD5 hash (eg. `b568b504524fda2440c62aa1616b3fe5`):

    {{{
     - [[ProjectVersion(http://pypi.python.org/packages/source/T/Twisted/Twisted-%(base)s.tar.bz2#md5=%(md5)s Twisted %(base)s tar)]]
     - [[ProjectVersion(http://pypi.python.org/packages/2.7/T/Twisted/Twisted-%(base)s.win32-py2.7.msi#md5=%(md5)s Twisted %(base)s for Python 2.7)]]
    }}}

    produces:

     - [[ProjectVersion(http://pypi.python.org/packages/source/T/Twisted/Twisted-%(base)s.tar.bz2#md5=%(md5)s Twisted %(base)s tar)]]
     - [[ProjectVersion(http://pypi.python.org/packages/2.7/T/Twisted/Twisted-%(base)s.win32-py2.7.msi#md5=%(md5)s Twisted %(base)s for Python 2.7)]]

    '''Source browser'''

    {{{
    [[ProjectVersion(source:/tags/releases/twisted-%(base)s/ Tag for Twisted %(base)s)]]
    }}}

    produces:

    [[ProjectVersion(source:/tags/releases/twisted-%(base)s/ Tag for Twisted %(base)s)]]
    """


    revision = "$Rev$"
    url = "$URL$"

    def getVersion(self):
        versions = []
        pattern = 'twisted-%s-md5sums.txt'
        for md5sums in RELEASES.globChildren(pattern % '*'):
            try:
                components = map(int, md5sums.basename().split('-')[1].split('.'))
            except ValueError:
                pass
            else:
                versions.append(components)

        version = Version('Twisted', *max(versions))
        md5sums_file = RELEASES.child(pattern % version.base())
        return version, md5sums_file


    def expand_macro(self, formatter, name, args):
        """
        Return output that will be displayed in the Wiki content.

        @param name: the actual name of the macro
        @param args: the text enclosed in parenthesis at the call of the macro.
          Note that if there are ''no'' parenthesis (like in, e.g.
          [[ProjectVersion]]), then `args` is `None`.
        """
        if not RELEASES.exists():
            self.log.error("The specified RELEASES directory does not exist at %s" % RELEASES.path)
            raise TracError("Error loading Twisted version information")

        v, md5sums = self.getVersion()        
        md5sum = ''

        if args is None:
            text = v.base()
        else:
            uc = unicode(args).replace('%28', '(').replace('%29', ')')
            if uc.find('%(md5)s') > -1:
                sep = '-----BEGIN PGP SIGNATURE-----\n'
                lines = md5sums.open().readlines()
                path = urlparse(uc).path % dict(base=v.base())
                filename = path.split('/')[-1]
                for entry in lines[3:lines.index(sep)]:
                    entry = entry.rstrip('\n').split('  ')
                    if entry[1] == filename:
                        md5sum = entry[0]
                        break

            url = urlparse(uc).netloc
            text = uc % dict(major=v.major, minor=v.minor, micro=v.micro, base=v.base(),
                             md5=md5sum)

            # handle links
            if args.startswith('source:') or url != '':
                text = "[%s]" % text

        out = StringIO()
        OneLinerFormatter(self.env, formatter.context).format(text, out)

        return Markup(out.getvalue())
