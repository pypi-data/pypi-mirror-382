""" cd_player.py

A simple example that uses the states-are-classes approach

"""
import unittest
import enum
import logging
import sys
# setting path
sys.path.append('..')
import hsm

logger = logging.getLogger(__name__)


class CdEvent(enum.Enum):
    PLAY = enum.auto()
    OPEN_CLOSE = enum.auto()
    STOP = enum.auto()
    CD_DETECTED = enum.auto()
    PAUSE = enum.auto()
    END_PAUSE = enum.auto()
    HAMMER = enum.auto()


class CdPlayer(hsm.HSM):
    """ The one-and-only top-level state (machine) """

    def __init__(self, controller):
        super().__init__(controller=controller)
        self._controller = controller

        # TODO: remove top state now that the HSM is the top state
        self.add_state(Top())
        self.set_initial('Top')

        # Final step
        self._initialize()


class Top(hsm.State):

    def __init__(self):
        super().__init__()

        self.add_state(NotBroken())
        self.add_state(Broken())
        self.set_initial('NotBroken')

        self.add_transition(event=CdEvent.HAMMER, target='Broken')


class Broken(hsm.State):
    """ Example showing the minimal amount of code required to define a state with this pattern """
    pass


class NotBroken(hsm.State):

    def __init__(self):
        super().__init__()
        self.add_state(Stopped())
        self.add_state(Open())
        self.add_state(Empty())
        self.add_state(Playing())
        self.add_state(Paused())
        self.set_initial('Empty')


class Stopped(hsm.State):

    def __init__(self):
        super().__init__()
        self.add_transition(event=CdEvent.PLAY, target='Playing')
        self.add_transition(event=CdEvent.OPEN_CLOSE, target='Open')
        self.add_transition(event=CdEvent.STOP, target=None, action=self._on_stop)

    def _on_stop(self):
        """ Just an example of how a state can handle an event without a transition """
        logger.info('Received redundant STOP event')

    def entry_action(self):
        """ Example showing how to create custom entry/exit actions """
        super().entry_action()
        logger.info('Displacy CD title screen')


class Open(hsm.State):

    def __init__(self):
        super().__init__()
        self.add_transition(event=CdEvent.OPEN_CLOSE, target='Empty')

    def entry_action(self):
        """ Example showing how to create custom entry/exit actions """
        super().entry_action()
        logger.info('Blank screen and display brand logo')


class Empty(hsm.State):

    def __init__(self):
        super().__init__()
        self.add_transition(event=CdEvent.OPEN_CLOSE, target='Open')
        self.add_transition(event=CdEvent.CD_DETECTED, target='Stopped')


class Playing(hsm.State):

    def __init__(self):
        super().__init__()
        self.add_transition(event=CdEvent.STOP, target='Stopped')
        self.add_transition(event=CdEvent.PAUSE, target='Paused')
        self.add_transition(event=CdEvent.OPEN_CLOSE, target='Open')


class Paused(hsm.State):

    def __init__(self):
        super().__init__()

        self.add_transition(event=CdEvent.STOP, target='Stopped')
        self.add_transition(event=CdEvent.HAMMER, target='Broken', guard=self._returns_true)
        self.add_transition(event=CdEvent.PLAY, target='Playing')
        self.add_transition(event=CdEvent.OPEN_CLOSE, target='Open')

    def _returns_true(self):
        return True


class DummyController:
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    controller = DummyController()
    cd_player = CdPlayer(controller)
    assert cd_player.state.name == 'Empty'

    cd_player.dispatch(CdEvent.OPEN_CLOSE)
    cd_player.execute_during_action()
    assert cd_player.state.name == 'Open'

    cd_player.dispatch(CdEvent.OPEN_CLOSE)
    cd_player.execute_during_action()
    assert cd_player.state.name == 'Empty'

    cd_player.dispatch(CdEvent.CD_DETECTED)
    cd_player.execute_during_action()
    assert cd_player.state.name == 'Stopped'

    cd_player.dispatch(CdEvent.STOP)
    cd_player.execute_during_action()
    assert cd_player.state.name == 'Stopped'

    cd_player.dispatch(CdEvent.PLAY)
    cd_player.execute_during_action()
    assert cd_player.state.name == 'Playing'

    cd_player.dispatch(CdEvent.PAUSE)
    cd_player.execute_during_action()
    assert cd_player.state.name == 'Paused'

    cd_player.dispatch(CdEvent.PLAY)
    cd_player.execute_during_action()
    assert cd_player.state.name == 'Playing'

    cd_player.dispatch(CdEvent.HAMMER)
    cd_player.execute_during_action()
    assert cd_player.state.name == 'Broken'
