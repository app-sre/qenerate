# Architecture

## Preprocessor

To properly support fragments we must in a first step generate a dependency graph.
A definition can reference multiple other fragments.
I.e., for every gql definition we must collect the following information:

- definition type: `query`, `fragment`, `mutation`
- fragment dependencies
- feature flags

The preprocessor parses every defintion and collects the above information.
Inferring concrete types happens in a later step.
The preprocessor is in the core package, i.e., it is common to all plugins.

## Generator

Every plugin has its own generator. A generator is responsible for inferring
concrete types and converting them to `.py` files.

In a first step, it generates all given fragments found by the preprocessor.
Fragments must be generated first in order to know how to properly import them
in queries (What is the proper Python name of the generated class?).
In a second step, it generates all given queries found by the preprocessor.
