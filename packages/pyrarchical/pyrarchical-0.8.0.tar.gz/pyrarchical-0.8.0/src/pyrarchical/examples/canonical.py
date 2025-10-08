""" canonical.py

Re-implement Miro Samek's classic HSM example.

The purpose here is to explore different syntaxes for using this library.
"""
import unittest
import time
import enum
import sys
# setting path
sys.path.append('..')
import hsm


class CanonicalController:
    """ Example controller to manage continous state for the canonical example """

    def __init__(self):
        self.action_history = []
        self.temperature = 0.0
        self.input = None

    def clear_action_history(self):
        self.action_history = []

    def record_action_history(self, action):
        self.action_history.append(action)

    def set_input(self, input):
        self.input = input


class CanonicalState(hsm.State):
    """ Define some basic behavior that is shared across all states

    Additional specific states could further derive from CanonicalState
    """

    def init_action(self):
        super().init_action()
        self._controller.action_history.append(f'{self.name}_init')

    def entry_action(self):
        super().entry_action()
        self._controller.action_history.append(f'{self.name}_entry')

    def exit_action(self):
        super().exit_action()
        self._controller.action_history.append(f'{self.name}_exit')

    def during_action(self):
        super().during_action()
        self._controller.action_history.append(f'{self.name}_during')


class Events(enum.Enum):
    A = enum.auto()
    B = enum.auto()
    C = enum.auto()
    D = enum.auto()
    E = enum.auto()
    E2 = enum.auto()
    F = enum.auto()
    G = enum.auto()
    H = enum.auto()


class CanonicalHsm(hsm.HSM):

    def __init__(self):
        # TODO: clean this up
        super().__init__()

        # First thing to do is to instantiate the controller for managing continuous state
        self._controller = CanonicalController()

        # Add states by name
        self.add_state(CanonicalState("s0"), initial=True)
        self.add_state(CanonicalState("s1"), parent='s0', initial=True)
        self.add_state(CanonicalState("s11"), parent='s1', initial=True)
        self.add_state(CanonicalState("s2"), parent='s0')
        self.add_state(CanonicalState("s21"), parent='s2', initial=True)
        self.add_state(CanonicalState("s211"), parent='s21', initial=True)
        self.add_state(CanonicalState("s212"), parent='s21')

        self.add_transition(source='s0', event=Events.E, target='s211')
        self.add_transition(source='s0', event=Events.E2, target='s212')

        self.add_transition(source='s1', event=Events.A, target='s1')
        self.add_transition(source='s1', event=Events.B, target='s11')
        self.add_transition(source='s1', event=Events.C, target='s2')
        self.add_transition(source='s1', event=Events.D, target='s0')
        self.add_transition(source='s1', event=Events.F, target='s211')

        self.add_transition(source='s11', event=Events.G, target='s211')

        self.add_transition(source='s2', event=Events.C, target='s1')
        self.add_transition(source='s2', event=Events.F, target='s11')

        self.add_transition(source='s21', event=Events.B, target='s211')
        self.add_transition(source='s21', event=Events.H, target='s21')

        self.add_transition(source='s211', event=Events.B, target='s21')
        self.add_transition(source='s211', event=Events.G, target='s0')
        self.add_transition(source='s211', event=None, target='s11', guard=self.s211_s11_guard)

        # TODO: clean this up
        self._initialize()

    def s211_s11_guard(self):
        try:
            return self._controller.input > 10.0
        except:
            return False


class HSMTest(unittest.TestCase):

    def test_events_states(self):
        """Test that a sequence of events go to the correct states."""

        # Check the start-up init and entry sequence to end in the right state
        # and having gone through the right sequence
        canonical_hsm = CanonicalHsm()
        u = ["s0_entry", "s0_init", "s1_entry", "s1_init", "s11_entry"]
        self.assertIs(canonical_hsm.state.name, 's11')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event a in state s11
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.A)
        # u = ["s11_exit", "s1_exit", "s1_entry", "s1_init", "s11_entry"]  # exteranl semantics
        u = ["s11_exit", "s1_init", "s11_entry"]  # internal semantics
        self.assertIs(canonical_hsm.state.name, 's11')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event e in state s11
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.E)
        u = ["s11_exit", "s1_exit", "s2_entry", "s21_entry", "s211_entry"]
        self.assertIs(canonical_hsm.state.name, 's211')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event e in state s211
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.E)
        u = ["s211_exit", "s21_exit", "s2_exit", "s2_entry", "s21_entry", "s211_entry"]  # internal path
        # u = []  # minimal path
        self.assertIs(canonical_hsm.state.name, 's211')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event a in state s211
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.A)
        u = []
        self.assertIs(canonical_hsm.state.name, 's211')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event h in state s211
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.H)
        # u = ["s211_exit", "s21_exit", "s21_entry", "s21_init", "s211_entry"]  # external semantics
        u = ["s211_exit", "s21_init", "s211_entry"]  # internal semantics
        self.assertIs(canonical_hsm.state.name, 's211')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event g in state s211
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.G)
        u = ["s211_exit", "s21_exit", "s2_exit", "s0_init", "s1_entry", "s1_init", "s11_entry"]  # local
        # external semantics
        # u = ["s211_exit", "s21_exit", "s2_exit", "s0_exit", "s0_entry", "s0_init", "s1_entry", "s1_init", "s11_entry"]
        self.assertIs(canonical_hsm.state.name, 's11')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event b in state s11
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.B)
        # u = ['s11_exit', 's1_exit', 's1_entry', 's11_entry']  # external
        u = ['s11_exit', 's11_entry']  # local
        # u = []  # minimal
        self.assertIs(canonical_hsm.state.name, 's11')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event g in state s11
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.G)
        u = ["s11_exit", "s1_exit", "s2_entry", "s21_entry", "s211_entry"]
        self.assertIs(canonical_hsm.state.name, 's211')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event b in state s211
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.B)
        u = ["s211_exit", "s21_init", "s211_entry"]
        self.assertIs(canonical_hsm.state.name, 's211')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event None in state s211, with input under 10.0
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(event=None, input=0.0)
        u = []
        self.assertIs(canonical_hsm.state.name, 's211')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event None in state s211, with input over 10.0
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(event=None, input=20.0)
        u = ["s211_exit", "s21_exit", "s2_exit", "s1_entry", "s11_entry"]
        self.assertIs(canonical_hsm.state.name, 's11')
        self.assertEqual(canonical_hsm._controller.action_history, u)

    def test_unknown_event(self):
        """An unknown event should fail somehow."""
        canonical_hsm = CanonicalHsm()
        with self.assertRaises(Exception, msg='Attempt use unknown event'):
            canonical_hsm.dispatch(Events.Z)

    def test_exit_only_to_least_common_ancestor(self):
        canonical_hsm = CanonicalHsm()

        # Event e in state s11
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.E)
        u = ["s11_exit", "s1_exit", "s2_entry", "s21_entry", "s211_entry"]
        self.assertIs(canonical_hsm.state.name, 's211')
        self.assertEqual(canonical_hsm._controller.action_history, u)

        # Event e2 in state s211
        canonical_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        canonical_hsm.dispatch(Events.E2)
        u = ['s211_exit', 's21_exit', 's2_exit', 's2_entry', 's21_entry', 's212_entry']  # internal
        # u = ["s211_exit", "s212_entry"]  # minimal
        self.assertIs(canonical_hsm.state.name, 's212')
        self.assertEqual(canonical_hsm._controller.action_history, u)

    def test_events_entry_counter_simple(self):
        pass

    def test_events_entry_exit_init(self):
        pass

    def test_speed(self):
        hsm = CanonicalHsm()
        assert hsm.state.name == 's11'
        num_cycles = 1E3
        num_transitions = 2
        start_time = time.time()
        for idx in range(int(num_cycles)):
            hsm._controller.clear_action_history()  # Reset the hsm continuous state
            hsm.dispatch(Events.E)
            assert hsm.state.name == 's211'
            hsm.dispatch(Events.F)
            assert hsm.state.name == 's11'
        stop_time = time.time()
        duration_ms = (stop_time - start_time) * 1E3
        print(f'Executed {int(num_cycles)} cycles of {num_transitions} in {duration_ms:.2f} ms')
        print(f'Average transition time = {duration_ms / num_cycles / num_transitions * 1E3:.2f} us')


##############################
#  Module Level Test Harness #
##############################
if __name__ == "__main__":
    # Kick off all unit tests contained in the file
    unittest.main()
