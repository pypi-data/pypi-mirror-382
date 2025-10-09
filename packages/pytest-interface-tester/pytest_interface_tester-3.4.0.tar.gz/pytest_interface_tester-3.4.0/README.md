# pytest-interface-tester

This repository contains a library meant to facilitate compliance testing of charm relation interfaces.
The problem is best stated as follows:
- there is a repository containing relation interface specifications and tests (henceforth 'the **spec** repo'), such as [charm-relation-interfaces](https://github.com/canonical/charm-relation-interfaces).
- there is a charm repository such as [traefik-k8s](https://github.com/canonical/traefik-k8s-operator) that implements the provider side of the `ingress` relation interface (henceforth 'the **charm** repo').
- The maintainers of the spec repo want to be able to automatically verify if all the registered charms that claim to implement a relation interface do in fact comply with its specification.
- The maintainers of the charm repo want to be able to automatically verify that their implementation of the standardized relation interfaces are in fact compliant.

The interface tester package facilitates both these verification flows.

# How to use the interface_tester in the spec repo

Follow the instructions [here](https://github.com/canonical/charm-relation-interfaces/blob/main/README_INTERFACE_TESTS.md).

# How to use the interface_tester in the charm repo

1) Ensure that [charm-relation-interfaces](https://github.com/canonical/charm-relation-interfaces) has one or more interface tests and a schema for the interface you want to test. If that is not the case, ask the maintainers of the interface (or its 'official' implementation) to add some.
2) Install this package.
3) Add a `...charm-root/tests/interface_tests/conftest.py` file containing at least:
   ```python
   import pytest
   from charm import MyCharm  # your charm class
   from interface_tester.plugin import InterfaceTester
   
   @pytest.fixture
   def interface_tester(interface_tester: InterfaceTester):
       interface_tester.configure(charm_type=MyCharm)
       yield interface_tester
   ```
   `interface_tester` is a pytest fixture exposed by this plugin. You are expected to override it with your own. The idea is that in doing this you:
   1) configure this fixture so that the spec repo will be able to find your charm location and name (it will default to whatever CharmBase subclass it can find in `...charm-root/src/charm.py`, but it will give up soon if that is nonstandard or there are multiple charm classes).
   2) the test runner can be made aware of any special configuration that your charm needs in order to function. For example if your charm will do nothing unless it is configured in a certain way, a given file is present, a network is active, a container can connect, etc... then this is your chance to set your charm up so that it is ready for handling the necessary relation events. 
   3) the runtime can be patched with anything necessary for your charm to function. For example, you can mock out any `Popen` calls, HTTP requests,  

At this stage, if you commit this to your `main` branch, the spec repo will already be able to find your charm and run the interface tests against it.

The flow is (from the POV of the spec repo): 
- gather all tests, schemas and charms for an interface
- for each charm:
  - clone the charm repo
  - fetch the `interface_tester` fixture from the charm's own tests, if any, otherwise assume no config is needed and try to grab the charm type off of `src/charm.py`
  - use the interface tester (configured or not) to run each test case:
    1) check that the scenario completes without uncaught charm errors, get the output state
    2) check whether the test case's own validator determines that the output state is valid
    3) check whether the relations in the output state are valid according to the schema

What if you want to run the tests yourself, charm-side, in CI, to catch potential issues before they trigger failures in the spec repo?

## How to run the tests in the charm repo
A minimal example of a test is:

```python
from interface_tester import InterfaceTester
from charm import MyCharm

def test_ingress_interface(interface_tester: InterfaceTester):
    interface_tester.configure(
      # you can skip this if your interface_tester fixture is already configured with the charm_type in conftest.py  
      charm_type=MyCharm, 
      # put here the interface that you wish to test. Omitting it will test for all interfaces that your charm supports.
      interface_name='ingress'
    )
    interface_tester.run()
```

If you have a conftest.py where you configured an `interface_tester` fixture and did all necessary mocking/patching already, then in principle you are good to go.

The flow is (from the POV of the spec repo): 
- clone the spec repo (or another)
- gather all tests, schemas and charms for the interface you want to test
- use the interface_tester fixture from the plugin (or one you override) to run the test cases
  - same 3 steps as above


## Customizing the fixture's address
You can customize name and location of the fixture, but you will need to include that data when registering your charm with the interface. In `interface.yaml`, you can then specify:
```yaml
  - name: my-charm-name  # required
    url: https://github.com/foo/my-charm-name  # required
    test_setup:  # optional
      location: path/to/file.py  # optional; default = tests/interface/conftest.py
      identifier: my_fixture_name # optional; default = interface_tester
```

## Upgrading from v1
`pytest-interface-tester` supports both pydantic v1 and v2, but using v2 is recommended.
You might need to adjust your tested charm to also support v2. See [migration guide](https://docs.pydantic.dev/latest/migration/) for more information.