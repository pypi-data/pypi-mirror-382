# Pyrarchical State Machine

Pyrarchical state machine is a framework for a responsive heirarchical state-machine. An HSM built with this framework provides callbacks to execute functionality as the HSM responds to dispatched events. The PHSM loosely follows a hybrid dynamic system model allowing for a persistant analog state held by the HSM in addition to discrete state (which may be heirarchical). Your HSM is constructed through inheritance of the base functionality.

The simplest two-state model with no heirarchy is shown here with more complete examples later on.

```python

from src.pyrarchical import hsm


class TwoState(hsm.HSM):
    top = hsm.State("top")
    s1 = hsm.State("s1")
    s2 = hsm.State("s2")

    def __init__(self):
        self.x.append(0)
        self.top.configure(parent=None,
                           init=self.s1,
                           transitions=(hsm.Transition(event=Events.RESET,
                                                       target=self.s1),))
        self.s1.configure(parent=self.top,
                          transitions=(hsm.Transition(event=Events.FLIP,
                                                      target=self.s2),))
        self.s2.configure(parent=self.top,
                          transitions=(hsm.Transition(event=Events.FLOP,
                                                      target=self.s1),))
        super().__init__(self.top)


class Events(hsm.Event):
    FLIP = "flip"
    FLOP = "flop"
    RESET = "reset"


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    flip_flop = TwoState()
    flip_flop.dispatch(Events.FLIP)
    flip_flop.dispatch(Events.FLOP)
    flip_flop.dispatch(Events.FLIP)
    flip_flop.dispatch(Events.RESET)
```

## Description

This module provides a framework for a responsive heirarchical state-machine.

For hybrid dynamical systems, the following update equations are commonly used.
```math
x[k+1] = f_s(x[k], u(k]))
```
```math
y[k] = g_s(x[k], u(k]))
```
where f and g are functions specific to each discrete state s, x is a
continuous state that exists in all discrete states, u is a set of inputs, and
y is the output of the system.

In a Python HSM implementation, only the during state will really obey the
discrete-time step, k. However, we may need to update states during other HSM
actions.
```
x = init_s(x, u)
x = entry_s(x, u)
x = during_s(x, u)
x = exit_s(x, u)
y = output_s(x, u)
```
The continuous state, x, is a member variable of the HSM. The output function
is a static method. The input, continuous state, and output each need an
object defined to describe them. At the simplest, this will just be a list.

## Getting Started

The only file needed to use the state-machine is hsm.py. There is currently no installation. Copy the file to your active project to use it.

### Prerequisites

hsm.py is only implemented in Python3 using standard Python libraries (enum and logging).

### Installing

```
git clone git@gitlab.com:roelle/pyrarchical-state-machine.git
cp pyrarchical-state-machine/hsm.py ../your-project/hsm.py
```

## Running the tests

Running `hsm.py` will run an example. Continupous integration tests are run by executing `hsm_test.py` in the `pyrarchical-state-machine` directory.

### Break down into end to end tests

To test, you need a heirarchincal state state-machine. The state machine shown in this figure is described in the following code. This particular implementation is based on an example offers a comprehensive set of tests of all types of transitions.

![Canonical heirarchical-state machine with all transitions](hsm.svg)

```python

from src.pyrarchical import hsm
from hashlib import md5


class S211(hsm.State):

    def default_exit_action(self, x, u):
        hsm._log.info(self._name + " : Exit")
        return x


class Events(hsm.Event):
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    F = "f"
    G = "g"
    H = "h"


class Example(hsm.HSM):
    s0 = hsm.State("s0")
    s1 = hsm.State("s1")
    s11 = hsm.State("s11")
    s2 = hsm.State("s2")
    s21 = hsm.State("s21")
    s211 = S211("s211")

    def __init__(self):
        self.x.append(md5())
        self.s0.configure(parent=None,
                          init=self.s1,
                          transitions=(hsm.Transition(event=Events.E,
                                                      target=self.s211),))
        self.s1.configure(parent=self.s0,
                          init=self.s11,
                          transitions=(hsm.Transition(event=Events.A,
                                                      target=self.s1),
                                       hsm.Transition(event=Events.B,
                                                      target=self.s11),
                                       hsm.Transition(event=Events.C,
                                                      target=self.s2),
                                       hsm.Transition(event=Events.D,
                                                      target=self.s0),
                                       hsm.Transition(event=Events.F,
                                                      target=self.s211)))
        self.s11.configure(parent=self.s1,
                           transitions=(hsm.Transition(event=Events.G,
                                                       target=self.s211),))
        self.s2.configure(parent=self.s0,
                          init=self.s21,
                          transitions=(hsm.Transition(event=Events.C,
                                                      target=self.s1),
                                       hsm.Transition(event=Events.F,
                                                      target=self.s11)))
        self.s21.configure(parent=self.s2,
                           init=self.s211,
                           transitions=(hsm.Transition(event=Events.B,
                                                       target=self.s211),
                                        hsm.Transition(event=Events.H,
                                                       target=self.s21)))
        self.s211.configure(parent=self.s21,
                            transitions=(hsm.Transition(event=Events.B,
                                                        target=self.s21),
                                         hsm.Transition(event=Events.D,
                                                        target=self.s21),
                                         hsm.Transition(event=Events.G,
                                                        target=self.s0),
                                         hsm.Transition(guard=self.s211_s11_guard,
                                                        target=self.s11)))

        self.s0.init_action = lambda x, u: self.update(self.x, b"s0_init")
        self.s0.entry_action = lambda x, u: self.update(self.x, b"s0_entry")
        self.s0.exit_action = lambda x, u: self.update(self.x, b"s0_exit")
        self.s0.during_action = lambda x, u: self.update(self.x, b"s0_during")

        self.s1.init_action = lambda x, u: self.update(self.x, b"s1_init")
        self.s1.entry_action = lambda x, u: self.update(self.x, b"s1_entry")
        self.s1.exit_action = lambda x, u: self.update(self.x, b"s1_exit")
        self.s1.during_action = lambda x, u: self.update(self.x, b"s1_during")

        self.s11.init_action = lambda x, u: self.update(self.x, b"s11_init")
        self.s11.entry_action = lambda x, u: self.update(self.x, b"s11_entry")
        self.s11.exit_action = lambda x, u: self.update(self.x, b"s11_exit")
        self.s11.during_action = lambda x, u: self.update(self.x, b"s11_during")

        self.s2.init_action = lambda x, u: self.update(self.x, b"s2_init")
        self.s2.entry_action = lambda x, u: self.update(self.x, b"s2_entry")
        self.s2.exit_action = lambda x, u: self.update(self.x, b"s2_exit")
        self.s2.during_action = lambda x, u: self.update(self.x, b"s2_during")

        self.s21.init_action = lambda x, u: self.update(self.x, b"s21_init")
        self.s21.entry_action = lambda x, u: self.update(self.x, b"s21_entry")
        self.s21.exit_action = lambda x, u: self.update(self.x, b"s21_exit")
        self.s21.during_action = lambda x, u: self.update(self.x, b"s21_during")

        self.s211.init_action = lambda x, u: self.update(self.x, b"s211_init")
        self.s211.entry_action = lambda x, u: self.update(self.x, b"s211_entry")
        self.s211.exit_action = lambda x, u: self.update(self.x, b"s211_exit")
        self.s211.during_action = lambda x, u: self.update(self.x, b"s211_during")

        super().__init__(self.s0)

    @staticmethod
    def s211_s11_guard(x, u):
        try:
            return u > 10.0
        except:
            return False

    @staticmethod
    def update(x, u):
        x[0].update(u)
        return x
```

This machine may be tested for any transition 
```python
test_hsm = Example()
test_hsm.x[0] = md5() # Reset the hsm continuous state
test_hsm.dispatch(Events.E)
x = [md5()]
x = Example.update(x, b"s11_exit")
x = Example.update(x, b"s1_exit")
x = Example.update(x, b"s2_entry")
x = Example.update(x, b"s21_entry")
x = Example.update(x, b"s211_entry")
x[0].digest == test_hsm.x[0].digest
```

<!---### And coding style tests
Explain what these tests test and why

```
Give an example
```

## Deployment

There is no deplpyment.Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.
-->

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://gitlab.com/roelle/pyrarchical-state-machine/tags). 

## Authors

* **Matt Roelle** - *Initial work* - [roelle](https://gitlab.com/roelle)

See also the list of [contributors](https://gitlab.com/roelle/pyrarchical-state-machine/graphs/develop) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* This README [template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) was copied from [PurpleBooth](https://github.com/PurpleBooth)
* Many discussions about heirarchical-state machines informed this work.
