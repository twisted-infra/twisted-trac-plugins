# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for the C{twisted_release_macro}.
"""

from twisted.python.filepath import FilePath
from twisted.trial.unittest import TestCase

from trac.core import ComponentManager, TracError

from twisted_release_macro import ProjectVersionMacro



class ProjectVersionMacroTests(TestCase):
    md5sums = """\
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

93fc2756a09ffd1350c046cc940e4311  Twisted-12.2.3.tar.bz2
13e9132589a6f4f4545fc208effd4b16  TwistedConch-12.2.3.tar.bz2
bd1fd44a73916f050b6d96f098f3c532  TwistedCore-12.2.3.tar.bz2
0c054504da9c986af7a28a25ed130ea0  TwistedLore-12.2.3.tar.bz2
2f226725928552f2abb2ff9b22b781d4  TwistedMail-12.2.3.tar.bz2
b0f27585dc50a7288762c7efa44897be  TwistedNames-12.2.3.tar.bz2
24609c1c4f48347e6ef95950f0d7d797  TwistedNews-12.2.3.tar.bz2
edc067b540f78b1b0f479b4e12f8e3f6  TwistedPair-12.2.3.tar.bz2
717be087cf0aef1d72767c9d9c7e4600  TwistedRunner-12.2.3.tar.bz2
40b1a2f158b615b2fcfe288c341beac7  TwistedWeb-12.2.3.tar.bz2
5fb53c7c9ba53cfa6f2c1915dcb4460a  TwistedWords-12.2.3.tar.bz2
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1.4.9 (GNU/Linux)

iEYEARECAAYFAksUKiEACgkQzG3xEdDSIIg3nwCfb7bvRAvVGOYIByzfvSpRK4iS
ES8An3MrYOSXnI6bTqO0moiVGNl8SEim
=qP/7
-----END PGP SIGNATURE-----
"""

    def setUp(self):
        """
        Create a directory full of pseudo-releases to be inspected by
        L{ProjectVersionMacro} in its expansion.
        """
        self.releases = FilePath(self.mktemp())
        self.releases.makedirs()
        self.releases.child('twisted-9.0.0-md5sums.txt').touch()
        self.releases.child('twisted-10.0.0-md5sums.txt').touch()
        self.releases.child('twisted-11.1.0-md5sums.txt').touch()
        self.releases.child('twisted-12.2.3-md5sums.txt').setContent(
            self.md5sums)

        self.macro = ProjectVersionMacro(ComponentManager())
        self.macro.log = lambda *args: None
        self.macro.log.error = lambda *args: None
        self.macro.log.warn = lambda *args: None
        self.macro.RELEASES = self.releases


    def _test(self, format, expected):
        result = self.macro._expandText(format)
        self.assertEqual(expected, result)


    def test_nonexistingReleasesDirectory(self):
        """
        L{ProjectVersionMacro._expandText} raises L{TracError} when
        L{ProjectVersionMacro.RELEASES} does not exist.
        """
        self.macro.RELEASES = FilePath("foo")
        self.assertRaises(TracError, self.macro._expandText, [])


    def test_missingReleaseFiles(self):
        """
        L{ProjectVersionMacro.getVersion} raises L{TracError} when
        L{ProjectVersionMacro.RELEASES} doesn't contain any valid md5sums.txt files.
        """
        tmp_releases = FilePath(self.mktemp())
        tmp_releases.makedirs()
        self.macro.RELEASES = tmp_releases
        self.assertRaises(TracError, self.macro.getVersion)


    def test_noArguments(self):
        """
        Using L{ProjectVersionMacro} without any arguments (eg.
        C{[[ProjectVersion]]}) returns the latest detected version.
        """
        self._test(None, "12.2.3")


    def test_noSubstitions(self):
        """
        Using L{ProjectVersionMacro} with a string that doesn't contain
        a substitution format returns the string without any modifications.
        """
        self._test("Hello World", "Hello World")


    def test_major(self):
        """
        The major version number of the current release is substituted for
        C{"%(major)s"} in the format string.
        """
        self._test("%(major)s", "12")


    def test_minor(self):
        """
        The minor version number of the current release is substituted for
        C{"%(minor)s"} in the format string.
        """
        self._test("%(minor)s", "2")


    def test_micro(self):
        """
        The micro version number of the current release is substituted for
        C{"%(micro)s"} in the format string.
        """
        self._test("%(micro)s", "3")


    def test_base(self):
        """
        The base version string of the current release is substituted for
        C{"%(base)s"} in the format string.
        """
        self._test("%(base)s", "12.2.3")


    def test_baseMultipleSubstitution(self):
        """
        Using C{"%(base)s"} in the format string multiple times results in
        multiple substitutions.
        """
        self._test("1: %(base)s, 2: %(base)s", "1: 12.2.3, 2: 12.2.3")


    def test_regularLink(self):
        """
        Normal links without substitution strings should only prepend and append
        brackets. 
        """
        self._test("http://twistedmatrix.com", "[http://twistedmatrix.com]")


    def test_sourceLink(self):
        """
        L{ProjectVersionMacro._expandText} also works with regular Trac
        C{source:} links.
        """
        self._test("source:/tags/releases/twisted-%(base)s/ Tag for Twisted %(base)s",
                   "[source:/tags/releases/twisted-12.2.3/ Tag for Twisted 12.2.3]")
        self._test("source:",
                   "[source:]")


    def test_md5(self):
        """
        The hexdigest of the md5 hash of the current release is substituted for
        C{"%(md5)s"} in the format string.
        """
        self._test("http://pypi.python.org/packages/source/T/Twisted/Twisted-%(base)s.tar.bz2#md5=%(md5)s Twisted %(base)s tar.bz2",
                   "[http://pypi.python.org/packages/source/T/Twisted/Twisted-12.2.3.tar.bz2#md5=93fc2756a09ffd1350c046cc940e4311 Twisted 12.2.3 tar.bz2]")
        self._test("file:///home/thijs/TwistedConch-%(base)s.tar.bz2#md5=%(md5)s Conch %(base)s",
                   "file:///home/thijs/TwistedConch-12.2.3.tar.bz2#md5=13e9132589a6f4f4545fc208effd4b16 Conch 12.2.3")


    def test_md5MissingArguments(self):
        """
        L{ProjectVersionMacro._expandText} raises L{TracError} when there is not
        a filename specified that can be used for the md5 match.
        """
        self.assertRaises(TracError, self.macro._expandText, ["%(md5)s"])
        self.assertRaises(TracError, self.macro._expandText, ["source:trunk#md5=%(md5)s"])
        self.assertRaises(TracError, self.macro._expandText, ["Twisted-%(base)s.tar.bz2#md5=%(md5)s Twisted-12.2.3.tar.bz2"])
        self.assertRaises(TracError, self.macro._expandText,
            ["http://pypi.python.org/packages/source/T/Twisted/Twisted.tar.bz2#md5=%(md5)s Twisted tar"])

