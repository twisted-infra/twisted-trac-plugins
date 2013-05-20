
import subprocess, StringIO, email.Message, email.MIMEText, email.Generator, email.Utils

from trac.core import Component, implements
from trac.ticket.api import ITicketChangeListener

LIST_ADDRESS = "twisted-bugs@twistedmatrix.com"
AGENT_ADDRESS = "trac@twistedmatrix.com"
REPLY_ADDRESS = "twisted-python@twistedmatrix.com"

TICKET_TRAILER = """\
http://twistedmatrix.com/trac/ticket/%(ticket_number)s
"""

NEW_TICKET = u"""\
New submission from %(creator_name)s <%(creator_email)s>:

%(ticket_description)s

----------
Type     : %(ticket_type)s
Component: %(ticket_component)s
Keywords : %(ticket_keywords)s
Priority : %(ticket_priority)s
Nosy     : %(ticket_cc)s
----------
""" + TICKET_TRAILER


CHANGE_TICKET = u"""\
Ticket %(ticket_summary)r changed by %(changer_name)s <%(changer_email)s>:

%(changer_comment)s

---------
%(change_information)s
---------
""" + TICKET_TRAILER


class EmailTicketObserver(Component):
    implements(ITicketChangeListener)

    requireEmail = False

    def ticketVars(self, ticket):
        c = self.env.get_db_cnx().cursor()
        c.execute("SELECT email FROM user_database WHERE username = %s", (ticket.values['reporter'],))
        for email, in c:
            break
        else:
            if self.requireEmail:
                raise RuntimeError("Visit the 'User Configuration' page and enter an email address before you create a ticket.")
            else:
                email = None

        return {
            'ticket_number': ticket.id,
            'ticket_type': ticket.values['type'],
            'ticket_component': ticket.values['component'],
            'ticket_keywords': ticket.values['keywords'],
            'ticket_priority': ticket.values['priority'],
            'ticket_cc': [s.strip() for s in ticket.values['cc'].split(',')],
            'ticket_summary': ticket.values['summary'],
            'ticket_description': ticket.values['description'],
            'ticket_owner': ticket.values['owner'],

            'creator_name': ticket.values['reporter'],
            'creator_email': email,
        }


    def flattenMessage(self, msg):
        s = StringIO.StringIO()
        g = email.Generator.Generator(s)
        g.flatten(msg)
        return s.getvalue()


    def sendmail(self, to, msg):
        cmd = ["/usr/sbin/sendmail"] + list(to)
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        # RFC 821, section 4.5.2.
        proc.stdin.write(msg.replace('\n.\n', '\n..\n'))
        proc.stdin.close()
        proc.wait()


    def baseMessage(self, ticket):
        info = self.ticketVars(ticket)
        mm = email.Message.Message()
        mm['From'] = AGENT_ADDRESS
        mm['Reply-To'] = REPLY_ADDRESS
        mm['Date'] = email.Utils.formatdate()
        return info, mm


    def ticketAddedMessage(self, ticket):
        info, mm = self.baseMessage(ticket)
        mm.set_payload((NEW_TICKET % info).encode('utf-8'))
        mm['To'] = LIST_ADDRESS
        mm['Subject'] = info['ticket_summary']
        return mm


    def ticketChangeMessage(self, cc, ticket, author, comment, oldValues):
        cursor = self.env.get_db_cnx().cursor()
        cursor.execute("SELECT email FROM user_database WHERE username = %s", (author,))
        try:
            [email] = iter(cursor).next()
        except StopIteration:
            email = author
        info, mm = self.baseMessage(ticket)
        mm['To'] = ', '.join(cc)
        mm['Subject'] = author + ' changed ' + repr(info['ticket_summary'])
        info['changer_comment'] = '\n'.join(comment.splitlines()) # Normalize newline convention
        info['changer_name'] = author
        info['changer_email'] = email

        changeInfo = []
        for (oldKey, oldValue) in oldValues.iteritems():
            changeInfo.append('%-9s: %s -> %s' % (oldKey, oldValue, ticket.values[oldKey]))
        info['change_information'] = '\n'.join(changeInfo)

        mm.set_payload((CHANGE_TICKET % info).encode('utf-8'))
        return mm


    def interestedParties(self, ticket):
        """
        Return a list of usernames interested in a change to the given ticket.
        """
        info = self.ticketVars(ticket)
        usernames = []

        # The creator of the ticket is interested
        usernames.append(info['creator_name'])

        # Everyone in the cc list is interested
        usernames.extend(info['ticket_cc'])

        # The owner of the ticket is interested
        usernames.append(info['ticket_owner'])

        # Unique it
        usernames = dict.fromkeys(usernames).keys()

        return usernames


    def emailForUsername(self, cursor, username):
        """
        Return the email address for the given username, as present in the
        user_database table.

        @param cursor: An open DB-API 2.0 cursor into the trac database

        @param username: A string giving the username for which to find an
        email address.
        
        @return: The email address for the given user as a string, or
        C{None} if they do not have one.
        """
        cursor.execute('SELECT email FROM user_database WHERE username = %s', (username,))
        results = list(cursor)
        if len(results) == 0:
            return None
        if results[0][0]:
            return results[0][0]
        return None


    # ITicketObserver
    def ticket_created(self, ticket):
        self.sendmail(
            [LIST_ADDRESS],
            self.flattenMessage(self.ticketAddedMessage(ticket)))


    def ticket_changed(self, ticket, comment, author, old_values):
        usernames = self.interestedParties(ticket)

        db = self.env.get_db_cnx()
        cursor = db.cursor()

        emails = filter(None, [self.emailForUsername(cursor, u) for u in usernames])

        if emails:
            self.sendmail(
                emails,
                self.flattenMessage(self.ticketChangeMessage(emails, ticket, author, comment, old_values)))
