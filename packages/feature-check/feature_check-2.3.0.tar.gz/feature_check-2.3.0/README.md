<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

feature-check - query a program for supported features
======================================================

The `feature_check` library obtains the list of supported features from
a program via various methods and allows programs to check for the presence
and, possibly, versions of specific features.

The `feature_check` library is fully typed.

Obtaining the features supported by a program
---------------------------------------------

The `obtain_features()` function in the `feature_check` module runs
a program with the appropriate option to obtain its list of features;
the default is to pass the `--features` option, but this may be overridden.
The `obtain_features()` function then examines the output to find a line
that matches the specified prefix (or the default `Features: ` prefix) and
expects the rest of the line to be a whitespace-separated list of either
feature names or `name=version` pairs.  It returns a dictionary of
the features obtained with their versions (or `1.0` if only a feature name
was found in the program's output).

    import feature_check
    
    data = feature_check.obtain_features("timelimit")
    print(data.get("subsecond", "not supported"))
    
For programs that need a different command-line option to list features:

    import feature_check
    
    print("SSL" in feature_check.obtain_features("curl", option="--version"))

Testing for feature versions
----------------------------

The `feature_check` library also provides a simple expression evaluation
mechanism for examining feature versions - the `expr` module defines
several `Expr` and `Result` classes and also provides the `parse_simple()`
function (also exported by `feature_check()` itself) for creating simple
version comparisons:

    import feature_check
    
    data = feature_check.obtain_features("timelimit")
    expr = feature_check.parse_simple("subsecond >= 1")
    print(expr.evaluate(data).value)

Contact the author
------------------

For more information, please see the `feature_check` library's
[homepage][ringlet] or contact the author, [Peter Pentchev][roam].

[ringlet]: https://devel.ringlet.net/misc/feature-check/
[roam]: <mailto:roam@ringlet.net>
