# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import subprocess

from trac.core import Component, implements
from trac.ticket.api import ITicketChangeListener

class IRCTicketObserver(Component):
    implements(ITicketChangeListener)

    def ticket_created(self, ticket):
        subprocess.call([
            self.config.get('ticket-reporter', 'ticket_executable'),
            self.config.get('ticket-reporter', 'tracker_location'),
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
                messages.append('%(author)s reviewed <https://tm.tl/#%(ticket)d> - %(summary)s (%(assignee)s)')
            elif 'review' in new and 'review' not in old:
                # It is up for review, and it wasn't before
                messages.append('%(author)s submitted <https://tm.tl/#%(ticket)d> - %(summary)s (%(assignee)s) for review')
        old = old_values.get('status', None)
        if old is not None:
            new = ticket.values['status']
            if old != 'closed' and new == 'closed':
                # It wasn't closed, now it is.
                messages.append('%(author)s closed <https://tm.tl/#%(ticket)d> - %(summary)s')
            elif old == 'closed' and new != 'closed':
                # It was closed, now it isn't.
                messages.append('%(author)s re-opened <https://tm.tl/#%(ticket)d> - %(summary)s')
        if messages is not None:
            assignee = 'unassigned'
            if ticket.values['owner']:
                assignee = 'assigned to ' + ticket.values['owner']
            executable = self.config.get('ticket-reporter', 'message_executable')
            channels = self.config.get('ticket-reporter', 'report_channels').split(',')
            message = '.  '.join([
                    m % {'author': author,
                         'ticket': ticket.id,
                         'assignee': assignee,
                         'summary': ticket.values['summary']}
                    for m in messages])
            for channel in channels:
                subprocess.call([executable, channel, message])



    def ticket_deleted(self, ticket):
        pass
