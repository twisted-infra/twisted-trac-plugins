
import subprocess

from trac.core import Component, implements
from trac.ticket.api import ITicketChangeListener

TICKET = '/home/trac/Projects/Divmod/sandbox/exarkun/commit-bot/ticket'
MESSAGE = '/home/trac/Projects/Divmod/sandbox/exarkun/commit-bot/message'
TRACKER = 'http://twistedmatrix.com/trac/'
CHANNEL = '#twisted'

class IRCTicketObserver(Component):
    implements(ITicketChangeListener)

    def ticket_created(self, ticket):
        subprocess.call([
            TICKET,
            TRACKER,
            str(ticket.id),
            ticket.values['reporter'],
            ticket.values['type'],
            ticket.values['component'],
            ticket.values['summary']])


    def ticket_changed(self, ticket, comment, author, old_values):
        messages = []
        old = old_values.get('keywords', None)
        if old is not None:
            new = ticket.values['keywords']
            if 'review' in old and 'review' not in new:
                # It was up for review, now it isn't
                messages.append('%(author)s reviewed [#%(ticket)d] - %(summary)s (%(assignee)s)')
            elif 'review' in new and 'review' not in old:
                # It is up for review, and it wasn't before
                messages.append('%(author)s submitted [#%(ticket)d] - %(summary)s (%(assignee)s) for review')
        old = old_values.get('status', None)
        if old is not None:
            new = ticket.values['status']
            if old != 'closed' and new == 'closed':
                # It wasn't closed, now it is.
                messages.append('%(author)s closed [#%(ticket)d] - %(summary)s')
            elif old == 'closed' and new != 'closed':
                # It was closed, now it isn't.
                messages.append('%(author)s re-opened [#%(ticket)d] - %(summary)s')
        if messages is not None:
            assignee = 'unassigned'
            if ticket.values['owner']:
                assignee = 'assigned to ' + ticket.values['owner']
            subprocess.call([
                    MESSAGE,
                    CHANNEL,
                    '.  '.join([
                            m % {'author': author,
                                 'ticket': ticket.id,
                                 'assignee': assignee,
                                 'summary': ticket.values['summary']}
                            for m in messages])])

