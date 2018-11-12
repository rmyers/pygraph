from july.models import Commit
from july.models import Game


class CommitCalendar:
    # start: datetime
    # end: datetime
    # commits: [Commit]

    def __init__(self, username=None):
        # TODO: check info.context for the correct user permissions?
        self.game = Game.active_or_latest()
        self.filters = {}
        if username is not None:
            self.filters['user__username'] = username

        self.start = self.game.start
        self.end = self.game.end

    @property
    def commits(self):
        # None -> [Commit]
        # Allow for lazy loading
        calendar = Commit.calendar(game=self.game, **self.filters)
        return calendar['objects']


def getCommitCalendar(source, info, username=None):
    return CommitCalendar(username=username)
