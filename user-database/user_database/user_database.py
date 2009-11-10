
import os, pkg_resources

from trac import util
from trac.env import IEnvironmentSetupParticipant
from trac.core import Component, implements
from trac.web import IRequestHandler
from trac.web.chrome import INavigationContributor, ITemplateProvider

class UserConfigurationPlugin(Component):
    implements(IRequestHandler, INavigationContributor, ITemplateProvider, IEnvironmentSetupParticipant)

    # IEnvironmentSetupParticipant
    def environment_created(self):
        self.upgrade_environment()

    def environment_needs_upgrade(self, db):
        cursor = db.cursor()
        try:
            cursor.execute("SELECT * FROM user_database LIMIT 1")
        except:
            return True
        return False

    def upgrade_environment(self, db):
        cursor = db.cursor()
        cursor.execute("CREATE TABLE user_database ( username varchar, email varchar )")


    # INavigationContributor
    def get_active_navigation_item(self, req):
        return 'user_configuration'

    def get_navigation_items(self, req):
        if req.authname != 'anonymous':
            yield ('mainnav',
                   'user_configuration',
                   util.Markup('<a href="%s">User Configuration</a>' % (self.env.href.user_configuration(),)))

    # IRequestHandler
    def match_request(self, req):
        return req.path_info == '/user_configuration'

    def process_request(self, req):
        db = self.env.get_db_cnx()
        cursor = db.cursor()

        if 'email' in req.args:
            email = req.args['email']
            cursor.execute(
                "DELETE FROM user_database WHERE username = %s",
                (req.authname,))
            cursor.execute(
                "INSERT INTO user_database (username, email) VALUES (%s, %s)",
                (req.authname, email))
            db.commit()
        else:
            cursor.execute(
                "SELECT email FROM user_database WHERE username = %s LIMIT 1",
                (req.authname,))
            for (email,) in cursor:
                break
            else:
                email = ''

        req.hdf['user_database.email'] = email
        return 'user_config.cs', None

    # ITemplateProvider
    def get_templates_dirs(self):
        return [pkg_resources.resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []

