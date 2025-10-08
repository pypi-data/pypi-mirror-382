.. Copyright NTESS. See COPYRIGHT file for details.

   SPDX-License-Identifier: MIT

A first test
============

The test file
-------------

Consider the test file ``first.pyt`` that defines a function to add two numbers and verifies it for correctness:

.. literalinclude:: /examples/basic/first/first.pyt
   :language: python

In addition to the test body, this test contains a :ref:`"directive" <test-directives>`: :func:`canary.directives.keywords`.  Directives are the method for a test file to communicate back to ``canary``.  The ``keywords`` directive applies "keywords" (labels) to the test which can be used to peform certain filtering actions.

.. note::

   This test file is an example of a ``.pyt`` test file - a Python file with ``canary`` directives.

Running the test
----------------

To run the test, navigate to ``examples/basic/first`` and execute ``canary run .``:

.. command-output:: canary run .
   :cwd: /examples/basic/first
   :nocache:
   :setup: rm -rf TestResults

A test is considered to have successfully completed if its exit code is ``0``.  See :ref:`basics-status` for more details on test statuses.

Inspecting the results
----------------------

Test execution was conducted within a "test session" - a folder created to run the tests "out of source".  The default name of the test session is ``TestResults``.  The test session tree mirrors the layout of the source tree used to generate the test session:

.. command-output:: canary tree examples/basic/first/TestResults
   :nocache:

Details of the session can be obtained by navigating to the test session directory and executing :ref:`canary status<canary-status>`:

.. command-output:: canary status
   :nocache:
   :cwd: /examples/basic/first/TestResults

By default, only details of the failed tests appear in the output.  To see the results of each test in the session, including passed tests, pass ``-rA``:

.. command-output:: canary status -rA
   :nocache:
   :cwd: /examples/basic/first/TestResults
