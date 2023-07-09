# pydomotic

[![PyPI version](https://badge.fury.io/py/pydomotic.svg)](https://badge.fury.io/py/pydomotic)

A Python library for home automation execution, enabling seamless control and
management of your IoT devices.

_"Domotics": The automatic control of home appliances by electronic systems.
Contraction of domestic robotics, from the Latin domus ("home"), and robotics._

## Getting Started

1. Install `pydomotic` in your environment.

    ```bash
    $ pip install pydomotic
    ```

1. Create your `pydomotic.yml` configuration file where you will define your
devices and automations.

    ```yaml
    # pydomotic.yml

    devices:
      fan:
        description: fan switch
        provider: noop
        id: '012'
      thermometer:
        description: temperature sensor
        provider: noop
        id: '345'

    automations:
      fan:
        enabled: true
        components:
          - if:
              thermometer:
                temp: '>75'
            then:
              turn-on: fan
            else:
              turn-off: fan
    ```

1. Running the following will check each trigger and execute any actions.

    ```bash
    $ python -m pydomotic
    ```

Note that each configured provider will require separate installation of its specific dependencies. For installing these dependencies and full configuration documentation, see [CONFIGURATION.md](https://github.com/purple4reina/pydomotic/blob/main/docs/CONFIGURATION.md)

For more details on deployment options, see [DEPLOYING.md](https://github.com/purple4reina/pydomotic/blob/main/docs/DEPLOYING.md)

## Glossary

**trigger:** A small piece of code which evaluates to either true or false.
Usually it calls on devices or 3rd party APIs to make this determination.

**action:** A small piece of code which is run when a trigger fires. Usually
this is managing device state like turning a lightbulb on or off. When
configured, it can be designated as a "then" action or an "else" action.

**provider:** The third party which owns the API for a set of devices. The
manufacturer of a device will usually provide this API.

**device:** Any IoT device which can be controled with a 3rd party API managed
by a provider.

**sensor:** A device or 3rd party API which senses information about the
physical world around it. For example, a smart lightbulb or REST based current
weather API.

**component:** A grouping of triggers and actions. When all triggers evaluate
to true, its "then" actions will be run. When any trigger evaluates to false,
its "else" actions will be run.

**handler:** The code used to run a set of components. This is the main
entrypoint to the `pydomotic` system.

**parser:** The code used to read the configuration yaml and transform it into
a list of components.
