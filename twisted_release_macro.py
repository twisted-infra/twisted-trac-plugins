"""
Trac macros for Twisted.
"""

from glob import glob
from StringIO import StringIO
from urlparse import urlparse, ParseResult

from genshi.builder import tag

from trac.util.html import Markup
from trac.wiki.formatter import OneLinerFormatter
from trac.wiki.macros import WikiMacroBase

from twisted.python.versions import Version
from twisted.python.filepath import FilePath

RELEASES = FilePath('/srv/www-data/twisted/Releases/')

class ProjectVersionMacro(WikiMacroBase):
    """
    Macro that returns the Twisted version.

    '''Standalone'''
    {{{
    [[ProjectVersion]]
    }}}

    produces:

    [[ProjectVersion]]

    '''URL'''

    {{{
    [[ProjectVersion(http://tmrc.mit.edu/mirror/twisted/Twisted/%(major)s.%(minor)s/Twisted-%(base)s.win32-py2.6.msi Twisted %s for Python 2.6)]]
    }}}

    produces:

    [[ProjectVersion(http://tmrc.mit.edu/mirror/twisted/Twisted/%(major)s.%(minor)s/Twisted-%(base)s.win32-py2.6.msi Twisted %s for Python 2.6)]]


    '''Source browser'''

    {{{
    [[ProjectVersion(source:/tags/releases/twisted-%(base)s/ SVN)]]
    }}}

    produces:

    [[ProjectVersion(source:/tags/releases/twisted-%(base)s/ SVN)]]
    """


    revision = "$Rev$"
    url = "$URL$"

    def getVersion(self):
        versions = []
        for path in RELEASES.globChildren('twisted-*-md5sums.txt'):
            try:
                components = map(int, path.basename().split('-')[1].split('.'))
            except ValueError:
                pass
            else:
                versions.append(components)
        return Version('Twisted', *max(versions))


    def expand_macro(self, formatter, name, args):
        """
        Return output that will be displayed in the Wiki content.

        @param name: the actual name of the macro
        @param args: the text enclosed in parenthesis at the call of the macro.
          Note that if there are ''no'' parenthesis (like in, e.g.
          [[ProjectVersion]]), then `args` is `None`.
        """
        v = self.getVersion()

        if args is None:
            text = v.base()
        else:
            uc = unicode(args).replace('%28', '(').replace('%29', ')')
            url = urlparse(uc).netloc
            text = uc % dict(major=v.major, minor=v.minor, micro=v.micro, base=v.base())

            # handle links
            if args.startswith('source:') or url != '':
                text = "[%s]" % text

        out = StringIO()
        OneLinerFormatter(self.env, formatter.context).format(text, out)

        return Markup(out.getvalue())
