""" diagram.py

Injest a pyrarchical-state-machine and draw diagrams of it with plant UML.

This code shamelessly borrowed from https://github.com/MainspringEnergy/eta-hsm

I originally thought that the functionality to spit out plant UML code would just be build directly
into hsm.py, but to keep that code lightweight, I am going to start off with using this as an external
translation module.
"""
try:
    from pyrarchical import hsm
except ImportError:
    import hsm


class Transition:
    """An event that causes a transition to another state.

    possibly subject to a guard.
    """

    def __init__(self, source, events, target, guard=None, action=None):
        """Give up and just making these public for now."""
        self.source = source
        self.events = events  # could be a string or a list/tuple
        self.target = target
        self.guard = guard
        self.action = action

    def events_as_string(self, wrap=None):
        """Get the one or several events as a printable string."""
        if isinstance(self.events, str):
            return self.events
        elif len(self.events) == 1:
            return self.events[0]
        else:
            event_string = "("
            for idx, event in enumerate(self.events):
                event_string += event
                if idx < (len(self.events) - 1):  # there are more to come
                    if wrap and len(self.events) > wrap:  # there are too many for a single line
                        event_string += "\\n| "
                    else:
                        event_string += " | "
            event_string += ")"
            return event_string

    def euml_string(self):
        """Describe the transition in eUML syntax."""
        return "{} + {} [{}] / {} == {}".format(
            self.source,
            self.events_as_string(),
            self.guard,
            self.action,
            self.target,
        )


class State:
    """Container to represent a state in the state machine."""

    def __init__(self, name, parent=None):
        """Initialize a new state."""
        self._name = name
        self._parent = parent
        self._children = []
        self._initial_state = None
        self._transitions = []
        self._entry = []
        self._exit = []
        # children are responsible for registering themselves
        # with their parents
        if self._parent:
            self._parent.register_child(self)

    @property
    def name(self):
        """Read-only access to name."""
        return self._name

    @property
    def parent(self):
        """Read-only access to parent."""
        return self._parent

    @property
    def children(self):
        """Read-only access to children."""
        return self._children

    @property
    def entry(self):
        """Entry property."""
        return self._entry

    @property
    def exit(self):
        """Exit property."""
        return self._exit

    @property
    def initial_state(self):
        """Initialize property."""
        return self._initial_state

    @property
    def transitions(self):
        """Transitions property."""
        return self._transitions

    def is_substate_of(self, name):
        """Is substrate of.

        Is this state a substate of some other named state?
        """
        if self.parent == None or self.parent.name == None:
            return False
        elif self.parent.name == name:
            return True
        else:
            # recurse our way up the state hierarchy
            return self.parent.is_substate_of(name)

    def levels_of_nesting_below(self, name):
        """Level of nesting below name.

        How many levels deep is this state nested below the named super-state?
        """
        # print('{}.levels_of_nesting_below({})'.format(self.name, name))
        if self.name == "Top":
            return 0
        elif self.name == name:
            return 0
        elif self.parent.name == name:
            return 1
        elif self.parent.name == "Top":
            return None  # to signify failure
        else:
            # recurse our way up the state hierarchy
            return self.parent.levels_of_nesting_below(name) + 1

    def ancestor_at_most_n_levels_of_nesting_below(self, name, max_depth):
        """Ancestor at most n levels of nesting below.

        Find ancestor that is at most N levels of nesting below named
        super-state.
        """
        assert self.is_substate_of(name)
        if self.levels_of_nesting_below(name) <= max_depth:
            return self
        else:
            return self.parent.ancestor_at_most_n_levels_of_nesting_below(
                name, max_depth
            )

    def register_child(self, child):
        """Register child.

        Children are responsible for registering themselves with the parent
        """
        assert child.parent == self
        self._children.append(child)

    def add_initial_state(self, initial_state):
        """Add initial state.

        Initial state transition for a composite state is represented by
        a dot on the diagram.
        """
        assert initial_state in self._children
        self._initial_state = initial_state

    def add_transition(self, transition):
        """Add transition.

        Transitions are defined by an event, target_state, and guard_condition.
        """
        assert transition.source == self._name
        self._transitions.append(transition)

    def add_entry(self, statement):
        """Add entry.

        For now, we're just going to keep the full block of code
        we found in hsmEntry().
        """
        stripped_statement = statement.strip()
        if stripped_statement[:2] == "//":
            # ignore commented out lines
            return
        if stripped_statement == "":
            # ignore empty lines
            return
        self._entry.append(stripped_statement)

    def add_exit(self, statement):
        """Add exit.

        For now, we're just going to keep the full block of code
        we found in hsmExit().
        """
        stripped_statement = statement.strip()
        if stripped_statement[:2] == "//":
            # ignore commented out lines
            return
        if stripped_statement == "":
            # ignore empty lines
            return
        self._exit.append(stripped_statement)

    def print_state_hierarchy(self, indentation=0):
        """Print state hierarchy."""
        description_of_self = " " * indentation + self._name
        if isinstance(self, Region):
            description_of_self += " (region)"
        if self._initial_state:
            description_of_self += " ( --> {})".format(self._initial_state.name)
        print(description_of_self)
        for child in self._children:
            child.print_state_hierarchy(indentation=indentation + 4)

    def print_transition_table(self, indentation=0):
        """Print transition table."""
        for transition in self._transitions:
            print(" " * indentation + transition.euml_string())
        for child in self._children:
            child.print_transition_table(indentation=indentation + 4)


class Region(State):
    pass


class StateMachine:
    """A collection of states makes a state machine."""

    def __init__(self, hsm):
        """Initialize a new state machine."""
        self._hsm = hsm
        self._basename = hsm.name
        self._states = {}
        self._plant_uml_legend = []
        self._plant_uml_out_of_scope_transition = False

    def state(self, name):
        """Get a reference to an individual state by name."""
        return self._states[name]

    def add_state(self, state):
        """Add state."""
        self._states[state.name] = state
        # TODO: is there any additional linking we need to do here?
        # TODO: Maybe populate children?

    def _add_legend_entry(self, entry):
        """Add legend entry.

        Legend entries to appear at the bottom of the plantUML diagram.
        """
        if entry in self._plant_uml_legend:
            # already have this one, do not repeat
            return
        else:
            self._plant_uml_legend.append(entry)

    def print_state_hierarchy(self, top=None):
        """Print state hierarchy."""
        if top is None:
            if self._basename in self._states:
                top = self._basename
            else:
                top = 'Top'  # Hope that we have a top state called 'Top'
        print("State hierarchy for {} state machine".format(self._basename))
        self.state(top).print_state_hierarchy()

    def print_transition_table(self, top=None):
        """Print transition table."""
        if top is None:
            if self._basename in self._states:
                top = self._basename
            else:
                top = 'Top'  # Hope that we have a top state called 'Top'
        print("Transition table for {} state machine".format(self._basename))
        self.state(top).print_transition_table()

    def extract_everything(self):
        """Extract everything.

        Scan files in standard locations for all of the things
        we know how to scrape.
        """
        self.extract_state_tree()
        self.extract_initial_states()
        self.extract_transitions()
        self.extract_entry_exit_actions()

    def extract_state_tree(self, hsm_state=None):
        """ Extract state tree from a pyrarchical-state-machine """
        if hsm_state is None:
            hsm_state = self._hsm
        print(f'extract_state_tree({hsm_state.name})')

        if isinstance(hsm_state, hsm.Region):
            if hsm_state.parent:
                self.add_state(Region(name=hsm_state.name, parent=self.state(hsm_state.parent.name)))
            else:
                self.add_state(Region(name=hsm_state.name))
        else:
            if hsm_state.parent:
                self.add_state(State(name=hsm_state.name, parent=self.state(hsm_state.parent.name)))
            else:
                self.add_state(State(name=hsm_state.name))

        # recurse down into substates
        for substate_name, substate in hsm_state._states.items():
            self.extract_state_tree(hsm_state=substate)

        for region_name, region in hsm_state._regions.items():
            self.extract_state_tree(hsm_state=region)

    def extract_initial_states(self, hsm_state=None):
        """ Extract initial states.

        Performed as a separate recursion to ensure states exist already.
        """
        if hsm_state is None:
            hsm_state = self._hsm
        print(f'extract_initial_states({hsm_state.name})')

        if hsm_state.initial:
            self.state(hsm_state.name).add_initial_state(self.state(hsm_state.initial.name))

        # recurse down into substates
        for substate_name, substate in hsm_state._states.items():
            self.extract_initial_states(hsm_state=substate)

        for region_name, region in hsm_state._regions.items():
            self.extract_initial_states(hsm_state=region)

    def extract_transitions(self, hsm_state=None):
        """ Extract transitions """
        if hsm_state is None:
            hsm_state = self._hsm
        print(f'extract_transitions({hsm_state.name})')

        for hsm_transition in hsm_state.transitions:
            if hsm_transition.event:
                event = hsm_transition.event.name
            else:
                event = None
            transition = Transition(source=hsm_state.name,
                                    events=[event],
                                    guard=hsm_transition.guard.__name__ if hsm_transition.guard else None,
                                    action=hsm_transition.action.__name__ if hsm_transition.action else None,
                                    target=hsm_transition.target.name if hsm_transition.target else None)
            # print(transition.euml_string())
            self.state(hsm_state.name).add_transition(transition)

        # recurse down into substates
        for substate_name, substate in hsm_state._states.items():
            self.extract_transitions(hsm_state=substate)

        for region_name, region in hsm_state._regions.items():
            self.extract_transitions(hsm_state=region)

    def extract_entry_exit_actions(self, hsm_state=None):
        """ Extract entry exit actions. """

        raise NotImplementedError

        # self.state(state_name).add_entry(line)
        # self.state(state_name).add_exit(line)

    def generate_event_set(self):
        """Generate a set of all events that are USED by the state machine.

        This conceptually could be different than the list of events that are
        DEFINED in the enum.
        """
        events = set()  # unordered and unique
        for name, state in self._states.items():
            for transition in state.transitions:
                events.update(transition.events)
        return events

    def generate_plant_uml(self, top=None, max_depth=None, do_not_expand=None,
                           include_actions=True, include_guards=True,
                           filename=None):
        """Generate plant uml.

        Generate the text input expected by PlantUML for automatically drawing a UML state diagram.

        `top` specifies the top of **this** diagram, effectively defining the scope
        `do_not_expand` is a LIST of states to not expand into substates
        """
        if top is None:
            top = self._basename

        # Clear members that will be populated by the recursive calls
        # to _generate_plant_uml_for_state below
        self._plant_uml_legend = []
        self._plant_uml_out_of_scope_transition = False

        with open(filename, "w") as fid:
            # header
            fid.write("@startuml\n")

            # First pass:  Just declare states
            self._generate_plant_uml_states_for_state(fid, state=self.state(top), top=top,
                                               max_depth=max_depth, do_not_expand=do_not_expand)

            # If any transition **targets** are out of the current diagram scope, we create a single explicitly named
            # fake-state at the top level for these transitions to point to.
            if self._plant_uml_out_of_scope_transition:
                fid.write("state OutOfScope {\n}\n")

            # Second pass: Declare transitions
            self._generate_plant_uml_transitions_for_state(fid, state=self.state(top), top=top,
                                               max_depth=max_depth, do_not_expand=do_not_expand,
                                               include_actions=include_actions, include_guards=include_guards)

            if self._plant_uml_legend:
                fid.write("legend\n")
                for entry in self._plant_uml_legend:
                    fid.write("  {}\n".format(entry))
                fid.write("end legend\n")

            # footer
            fid.write("@enduml\n")

    def _generate_plant_uml_states_for_state(self, fid, state, top, max_depth, do_not_expand,
                                             include_actions=False, include_guards=False,
                                             indentation=0):
        """ declare sub-states (but do not decend into them yet)

        plant-uml seems to be creating local substates for any transition terminations that are not yet defined,
        which seems wrong.  this is an attempt to work around that by declaring states earlier in the sequence.
        it is likely a band-aid at best.
        """
        initial_indent = " " * indentation
        internal_indent = " " * (indentation + 2)

        # declare ourselves as a state
        if isinstance(state, Region) and state.parent is not None:
            # exclude top-level hsm, which is technically a region
            # I tried valiantly to diagram regions as actual regions (which actually worked, see git history),
            # but plantUML does not seem to allow defining transitions to target states outside the region.
            # As an unsatisfying but functional alternative, we can simply draw regions as states with extra labels.
            fid.write(initial_indent + f'state REGION_{state.name} {{\n')
        else:
            fid.write(initial_indent + f'state {state.name} {{\n')

        # describe transition to initial state, if any
        if do_not_expand is not None and state.name in do_not_expand:
            # regardless of how deep we are, we will not descend into our sub-states
            pass
        elif max_depth is None or state.levels_of_nesting_below(top) < max_depth:
            if state.initial_state:
                fid.write(internal_indent + "[*] --> {}\n".format(state.initial_state.name))

        # entry/exit actions
        if include_actions:  # even if at max_depth
            for entry in state.entry:
                fid.write(internal_indent + "{} : entry / {}\n".format(state.name, entry))
            for exit in state.exit:
                fid.write(internal_indent + "{} : exit / {}\n".format(state.name, exit))

        # descend into sub-states
        if do_not_expand is not None and state.name in do_not_expand:
            # regardless of how deep we are, we will not descend into our sub-states
            pass
        elif max_depth is None or state.levels_of_nesting_below(top) < max_depth:
            for child in state.children:
                self._generate_plant_uml_states_for_state(fid, state=child, top=top,
                                                          max_depth=max_depth, do_not_expand=do_not_expand,
                                                          include_actions=include_actions, include_guards=include_guards,
                                                          indentation=indentation + 2)
        # close our block
        fid.write(initial_indent + "}\n")

    def _generate_plant_uml_transitions_for_state(self, fid, state, top, max_depth,
                                      do_not_expand, include_actions, include_guards,
                                      indentation=0):
        """Generate plant uml for state.

        Generate the text input expected by PlantUML for automatically drawing a UML state diagram

        `top` specifies the top of **this** diagram, effectively defining the scope.

        Transitions to states outside of this scope will be directed to UML's "final" state.

        Transitions from states outside of this scope are (for now) simply omitted.

        This functionality original resided within the State class, but I was having to pass in a reference
        to the state machine in order to look up "scope" of target states, so I decided to move it here to the
        StateMachine class.  The downside is that now I had to make more of the details of the State class public.
        """
        initial_indent = " " * indentation

        # list transitions
        for transition in state.transitions:
            arrow = "-->"

            # figure out if the target state is hidden by do_not_expand list
            do_not_expand_state_hiding_target = None
            if do_not_expand is not None:
                for name in do_not_expand:
                    if transition.target is not None:
                        if self.state(transition.target).is_substate_of(name):
                            do_not_expand_state_hiding_target = name

            # catch transitions to states that are out of scope for the
            # current diagram
            if transition.target is None:  # INTERNAL transition (different from a self-transition)
                arrow = ''
                diagram_target = ''
            elif not self.state(transition.target).is_substate_of(top):
                # Previously useed UML's "Final" state icon to represent that we have left the current diagram.
                # The problem with this was that it generated a "Final" icon locally in every state that
                # had an out-of-scope transition, which often bloated the diagram.  Instead, we're going to
                # create a single explicit "OutOfScope" state for all of these transitions to point to.
                diagram_target = "OutOfScope"  # '[*]'
                # Flag that this occurred so that generate_plant_uml can create the state at the top level
                self._plant_uml_out_of_scope_transition = True
            elif (max_depth is not None
                  and state.levels_of_nesting_below(top) == max_depth
                  and self.state(transition.target).is_substate_of(state.name)):
                # If the current state is already the max depth, then drop
                # transitions to our own substates (instead of letting the
                # next elif redirect them to ourselves)
                break
            elif do_not_expand is not None and state.name in do_not_expand:
                # If the current state is explicitly not going to be expanded,
                # then drop transitions to our own substates so that they do
                # not get auto-drawn.
                break
            elif max_depth is not None and self.state(transition.target).levels_of_nesting_below(top) > max_depth:
                # redirect transitions to deeply nested states to their parent state
                diagram_target = self.state(transition.target).ancestor_at_most_n_levels_of_nesting_below(top, max_depth).name
                # use a different style arrow to explicitly show that this has
                # been modified/approximated
                arrow = "-[dotted]->"
                self._add_legend_entry("dotted arrow = transition to hidden substate")
            elif do_not_expand_state_hiding_target:
                # redirect transitions to states hidden by do_no_expand list
                diagram_target = do_not_expand_state_hiding_target
                # use a different style arrow to explicitly show that this has
                # been modified/approximated
                arrow = "-[dotted]->"
                self._add_legend_entry("dotted arrow = transition to hidden substate")
            else:  # target in scope
                diagram_target = transition.target

            # start generating the actual plantUML string to represent a transition
            transition_string = f'{transition.source} {arrow} {diagram_target} : {transition.events_as_string(wrap=3)}'
            if transition.guard:
                if include_guards:
                    transition_string += " [{}]".format(transition.guard)
                else:
                    # explicitly show that a guard condition has been omitted
                    transition_string += " [*]"
                    self._add_legend_entry("[*] = guard condition omitted")

            if transition.action is not None:
                if include_actions or transition.target is None:  # always include actions on INTERNAL transitions
                    transition_string += " / {}".format(transition.action)
                else:
                    # explicitly show that a transition action has been omitted
                    transition_string += " /*"
                    self._add_legend_entry("/* = transition action omitted")

            fid.write(initial_indent + transition_string + "\n")

        # descend into sub-states
        if do_not_expand is not None and state.name in do_not_expand:
            # regardless of how deep we are, we will not descend into our sub-states
            pass
        elif max_depth is None or state.levels_of_nesting_below(top) < max_depth:
            for child in state.children:
                self._generate_plant_uml_transitions_for_state(fid, state=child, top=top,
                                                   max_depth=max_depth, do_not_expand=do_not_expand,
                                                   include_actions=include_actions, include_guards=include_guards,
                                                   indentation=indentation + 2)


if __name__ == "__main__":
    import argparse
    import examples.canonical
    import examples.cd_player
    import examples.orthogonal

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default='examples')
    args = parser.parse_args()

    # -------- CdPlayer -----------
    controller = examples.cd_player.DummyController()
    cd_player_hsm = examples.cd_player.CdPlayer(controller)
    state_machine = StateMachine(hsm=cd_player_hsm)
    state_machine.extract_state_tree()
    state_machine.extract_initial_states()
    state_machine.extract_transitions()

    print()
    state_machine.print_state_hierarchy()
    print()
    state_machine.print_transition_table()

    # default plantUML output
    state_machine.generate_plant_uml(filename=args.path + "/cd_player.txt")

    # -------- Canonical -----------
    canonical_hsm = examples.canonical.CanonicalHsm()
    state_machine = StateMachine(hsm=canonical_hsm)
    state_machine.extract_state_tree()
    state_machine.extract_initial_states()
    state_machine.extract_transitions()

    print()
    state_machine.print_state_hierarchy()
    print()
    state_machine.print_transition_table()

    # default plantUML output
    state_machine.generate_plant_uml(filename=args.path + "/canonical.txt")

    # -------- Orthogonal -----------
    print('\n\n\n Orthogonal Example \n\n\n')
    orthogonal_hsm = examples.orthogonal.OrthogonalHsm()
    state_machine = StateMachine(hsm=orthogonal_hsm)
    state_machine.extract_state_tree()
    state_machine.extract_initial_states()
    state_machine.extract_transitions()

    print()
    state_machine.print_state_hierarchy()
    print()
    state_machine.print_transition_table()

    # default plantUML output
    state_machine.generate_plant_uml(filename=args.path + "/orthogonal.txt")
