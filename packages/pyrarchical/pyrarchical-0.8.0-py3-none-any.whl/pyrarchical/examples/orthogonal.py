""" orthogonal.py

An example of orthogonal regions
"""
import unittest
import logging
import time
import enum
import sys
# setting path
sys.path.append('..')
import hsm


class OrthogonalController:
    """ Example controller to manage continuous state for the orthogonal regions example """

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


class TrackedState(hsm.State):
    """ States that record their actions in the controller for debugging and testing purposes """

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
    F = enum.auto()
    G = enum.auto()
    H = enum.auto()
    J = enum.auto()
    K = enum.auto()
    L = enum.auto()
    M = enum.auto()

class OrthogonalHsm(hsm.HSM):

    def __init__(self):
        # TODO: clean this up
        super().__init__(log_level=logging.DEBUG)

        # First thing to do is to instantiate the controller for managing continuous state
        self._controller = OrthogonalController()

        # Add states by name
        # Explicitly have a layer of states ABOVE the first regions to test for proper reactivation
        # of the 'default' region when we exit the highest-defined regions.
        self.add_state(TrackedState("s", log_level=self._log_level), initial=True)
        self.add_state(TrackedState("t", log_level=self._log_level))
        self.add_region('left', parent='s')
        self.add_region('right', parent='s')
        self.add_state(TrackedState("s1", log_level=self._log_level), parent='left', initial=True)
        self.add_state(TrackedState("s2", log_level=self._log_level), parent='left')
        self.add_state(TrackedState("sA", log_level=self._log_level), parent='right', initial=True)
        self.add_state(TrackedState("sB", log_level=self._log_level), parent='right')
        self.add_region('fred', parent='s1')
        self.add_region('george', parent='s1')
        self.add_state(TrackedState("s11", log_level=self._log_level), parent='fred', initial=True)
        self.add_state(TrackedState("s12", log_level=self._log_level), parent='fred')
        self.add_state(TrackedState("s1X", log_level=self._log_level), parent='george', initial=True)
        self.add_state(TrackedState("s1Y", log_level=self._log_level), parent='george')

        # self.add_transition(source='s1', event=Events.E, target='sA') INVALID
        self.add_transition(source='sB', event=Events.A, target='sA')
        self.add_transition(source='sA', event=Events.B, target='sB')
        self.add_transition(source='s1X', event=Events.C, target='s2')
        self.add_transition(source='s1', event=Events.F, target='s2')  # same effect as above, but defined in superstate
        self.add_transition(source='s1X', event=Events.D, target='s1')
        self.add_transition(source='s2', event=Events.E, target='s1')
        self.add_transition(source='s1X', event=Events.G, target='t')
        # Transitioning from the "shallow" side of the top-level regions is especially tricky
        # to handle exiting the "deep" side of the region (that has already been subdivided into more regions)
        self.add_transition(source='sA', event=Events.H, target='t')
        # need to be able to get out of state t
        self.add_transition(source='t', event=Events.J, target='s')

        # In order to test the order in which subregions get dispatched, create some local transitions
        # (they do not change state) that have some observable action
        self._chalkboard = None
        # sA is in the lower-priority 'right' region
        self.add_transition(source='sA', event=Events.K, target='sA',
                            action=lambda: self.write('sA self transition'))
        # s11 is in the 'fred' region which is nested under the higher-priority 'left' region
        self.add_transition(source='s11', event=Events.K, target='s11',
                            action=lambda: self.write('s11 self transition'))
        self.add_transition(source='s1X', event=Events.L, target='s1Y')
        # s1X is in the 'george' region which is nested under the higher-priority 'left' region
        self.add_transition(source='s1X', event=Events.K, target='s1X',
                            action=lambda: self.write('s1X self transition'))
        self.add_transition(source='s11', event=Events.L, target='s12')
        self.add_transition(source='s1X', event=Events.M, target='s1Y')

        # TODO: clean this up
        self._initialize()

    def write(self, message):
        self._chalkboard = message

class OrthogonalTest(unittest.TestCase):

    def test_initial_conditions(self):
        orthogonal_hsm = OrthogonalHsm()

        # Active states by region
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')
        self.assertEqual(orthogonal_hsm.region_state('right').name, 'sA')

        expected_actions = ['s_entry','s_init','s1_entry', 's1_init', 's11_entry', 's1X_entry', 'sA_entry']
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

    def test_region_priorities(self):
        orthogonal_hsm = OrthogonalHsm()

        left_priority = orthogonal_hsm.find_region_by_name('left').region_priority
        right_priority = orthogonal_hsm.find_region_by_name('right').region_priority
        fred_priority = orthogonal_hsm.find_region_by_name('fred').region_priority
        george_priority = orthogonal_hsm.find_region_by_name('george').region_priority

        self.assertTrue(left_priority < fred_priority < george_priority < right_priority)

        # confirm initial states
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')
        self.assertEqual(orthogonal_hsm.region_state('right').name, 'sA')
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state

        # regions should be dispatched fred -> george -> right
        orthogonal_hsm.dispatch(Events.K)
        # No states changed
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')
        # fred should have caught the event since K transitions defined in S11 (and s1X and sA)
        self.assertEqual(orthogonal_hsm._chalkboard, 's11 self transition')

        # transition fred region to s12 which does NOT handle the K event
        orthogonal_hsm.dispatch(Events.L)
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's12')
        # regions should still be dispatched fred -> george -> right, but K now caught by s1X in george
        orthogonal_hsm.dispatch(Events.K)
        # No states changed
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')
        # george should have caught the event since K transitions defined in S1X and sA
        self.assertEqual(orthogonal_hsm._chalkboard, 's1X self transition')

        # transition george region to s1Y which does NOT handle the K event
        orthogonal_hsm.dispatch(Events.M)
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1Y')
        # regions should still be dispatched fred -> george -> right, but K now caught by sA in right
        orthogonal_hsm.dispatch(Events.K)
        # No states changed
        self.assertEqual(orthogonal_hsm.region_state('right').name, 'sA')
        # right should have caught the event since K transitions defined in sA but NOT s1Y
        self.assertEqual(orthogonal_hsm._chalkboard, 'sA self transition')

    def test_transitions(self):
        """Test that a sequence of events go to the correct states."""
        orthogonal_hsm = OrthogonalHsm()
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')

        # Event B in state sA
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.B)
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')
        expected_actions = ['sA_exit', 'sB_entry']
        self.assertIs(orthogonal_hsm.region_state('right').name, 'sB')
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')  # unaffected
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event A in state sB
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.A)
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')
        expected_actions = ['sB_exit', 'sA_entry']
        self.assertIs(orthogonal_hsm.region_state('right').name, 'sA')
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')  # unaffected
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event C state s1X
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.C)
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')
        expected_actions = ['s1X_exit', 's11_exit', 's1_exit', 's2_entry']
        self.assertEqual(orthogonal_hsm.region_state('left').name, 's2')
        self.assertIs(orthogonal_hsm.region_state('right').name, 'sA')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event E in state s2
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.E)
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')
        expected_actions = ['s2_exit', 's1_entry', 's1_init', 's11_entry', 's1X_entry']
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')
        self.assertIs(orthogonal_hsm.region_state('right').name, 'sA')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event F in state s1X should have the same net effect as Event C, but state exit order may be different
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.F)
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')
        expected_actions = ['s1X_exit', 's11_exit', 's1_exit', 's2_entry']
        self.assertEqual(orthogonal_hsm.region_state('left').name, 's2')
        self.assertIs(orthogonal_hsm.region_state('right').name, 'sA')  # unaffected
        # can't actually guarantee order in which we exit states because we don't know which order the regions
        # will be dispatched, and either fred or george will find Event F
        for action in expected_actions:
            self.assertIn(action, orthogonal_hsm._controller.action_history)

        # Event E in state s2
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.E)
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')
        expected_actions = ['s2_exit', 's1_entry', 's1_init', 's11_entry', 's1X_entry']
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')
        self.assertIs(orthogonal_hsm.region_state('right').name, 'sA')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event D in state s1X
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.D)
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')
        # expected_actions = ['s1X_exit', 's11_exit', 's1_exit', 's1_entry', 's1_init', 's11_entry', 's1X_entry']  # external
        expected_actions = ['s1X_exit', 's11_exit', 's1_init', 's11_entry', 's1X_entry']  # local
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')
        self.assertIs(orthogonal_hsm.region_state('right').name, 'sA')  # unaffected
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event G in state s1X / S11 / sA
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.G)
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')
        expected_actions = ['s1X_exit', 's11_exit', 's1_exit', 'sA_exit', 's_exit', 't_entry']
        self.assertEqual(orthogonal_hsm.state.name, 't')
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event J in state t (to reset to s1X / S11 / sA)
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.J)
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')
        expected_actions = ['t_exit', 's_entry', 's_init', 's1_entry', 's1_init', 's11_entry', 's1X_entry', 'sA_entry']
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')
        self.assertIs(orthogonal_hsm.region_state('right').name, 'sA')
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

        # Event G in state s1X / S11 / sA
        # Transitioning from the "shallow" side of the top-level regions is especially tricky
        # to handle exiting the "deep" side of the region (that has already been subdivided into more regions)
        orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
        orthogonal_hsm.dispatch(Events.H)
        print(f'current state vector = {orthogonal_hsm.print_state_vector()}')
        expected_actions = ['sA_exit', 's11_exit', 's1X_exit', 's1_exit', 's_exit', 't_entry']
        self.assertEqual(orthogonal_hsm.region_state().name, 't')
        # make sure that we properly exited the deeply nested regions
        self.assertIsNone(orthogonal_hsm.region_state('fred'))
        self.assertIsNone(orthogonal_hsm.region_state('george'))
        self.assertIsNone(orthogonal_hsm.region_state('left'))
        self.assertIsNone(orthogonal_hsm.region_state('right'))
        self.assertEqual(orthogonal_hsm._controller.action_history, expected_actions)

    def test_speed(self):
        orthogonal_hsm = OrthogonalHsm()
        self.assertIs(orthogonal_hsm.region_state('right').name, 'sA')
        self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')
        self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')

        num_cycles = 1E3
        num_transitions = 4
        start_time = time.time()
        for idx in range(int(num_cycles)):

            # Event B in state sA
            orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
            orthogonal_hsm.dispatch(Events.B)
            self.assertIs(orthogonal_hsm.region_state('right').name, 'sB')

            # Event C in state s1X
            orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
            orthogonal_hsm.dispatch(Events.C)
            self.assertEqual(orthogonal_hsm.region_state('left').name, 's2')

            # Event A in state sB
            orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
            orthogonal_hsm.dispatch(Events.A)
            self.assertIs(orthogonal_hsm.region_state('right').name, 'sA')

            # Event E in state s2
            orthogonal_hsm._controller.clear_action_history()  # Reset the hsm continuous state
            orthogonal_hsm.dispatch(Events.E)
            self.assertEqual(orthogonal_hsm.region_state('fred').name, 's11')
            self.assertEqual(orthogonal_hsm.region_state('george').name, 's1X')

        stop_time = time.time()
        duration_ms = (stop_time - start_time) * 1E3
        print(f'Executed {int(num_cycles)} cycles of {num_transitions} in {duration_ms:.2f} ms')
        print(f'Average transition time = {duration_ms / num_cycles / num_transitions * 1E3:.2f} us')


##############################
#  Module Level Test Harness #
##############################
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Kick off all unit tests contained in the file
    unittest.main()
