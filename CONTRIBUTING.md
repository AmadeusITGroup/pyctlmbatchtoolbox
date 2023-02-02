## Project philosphy
The goal of this project is to provide an _user centric_ tool. Before everything, we want to provide to the user a good experience. 

The second aspect of the project is its code simplicity and maintenance. We want to keep a _low entry barrier_ for contributions.

The project structure is very simple:
* Each command available is defined on the `setup.py` as `console_scripts`.
* Each entry in `console_scripts` corresponds to a `command_*` python file in `src` directory.
* Each command inherits from the `Command` class.
* The functions that are generic are defined in `common.py`.

## Testing
Try to write _testeable_ code (static functions when possible, simple types or structures as input parameters). Add `doctests` when possible.

We dont have integration tests. We ask the contributors to test their code locally. Proof of testing (copy paste of the output or screenshots) are welcome.

## Pull requests
* Add a proper description to your PR.
* Try to provide a single commit with a meaningful commit message.
* We are very welcoming to code contributions. Please ensure they follow project philosopy.


## Code conventions
Please follow the standard python rules if possible:
  * existing conventions
  * [PEP8](https://www.python.org/dev/peps/pep-0008/)
  * [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

There is always room for opportunistic refactoring, but be careful and ensure the cosmetic changes have no adverse impact on performance or readability.

