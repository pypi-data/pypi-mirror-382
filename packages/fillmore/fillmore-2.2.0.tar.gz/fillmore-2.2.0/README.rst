========
Fillmore
========

**Status 2025-10-09: This project is deprecated.**

The Python sentry-sdk has a before_send hook that lets you scrub Sentry events
before they're sent. Fillmore makes it easier to set up a before_send scrubber
and test it.

:Code:          https://github.com/mozilla-services/fillmore
:Issues:        https://github.com/mozilla-services/fillmore/issues
:License:       MPL v2
:Documentation: https://fillmore.readthedocs.io/


Goals
=====

Goals of Fillmore:

1. make it easier to configure Sentry event scrubbing in a way that you can
   reason about
2. make it easier to test your scrubbing code so you know it's working over
   time
3. scrub in a resilient manner and default to emitting some signal when it
   kicks up errors so you know when your error handling code is kicking up
   errors

From that, Fillmore has the following features:

* lets you specify keys to scrub in a Sentry event
* resilient to errors--if it fails, it will emit a signal that you can see and
  alert on
* links to relevant Sentry documentation, projects, and other things
* testing infrastructure to use in your integration tests


Install
=======

Run::

    $ pip install fillmore


Quickstart
==========

.. [[[cog
    import cog

    cog.outl("")
    cog.outl("Example::\n")
    with open("examples/myapp/myapp/app.py", "r") as fp:
        for line in fp:
            cog.out(f"   {line}")
    cog.outl("")
    ]]]

Example::

   # examples/myapp/myapp/app.py
   import logging
   import logging.config
   
   from fillmore.libsentry import set_up_sentry
   from fillmore.scrubber import Scrubber, Rule, build_scrub_query_string
   
   
   # Set up logging to capture fillmore error messages
   logging.getLogger("fillmore").setLevel(logging.ERROR)
   
   # Create a scrubber
   scrubber = Scrubber(
       rules=[
           Rule(
               path="request.headers",
               keys=["Auth-Token", "Cookie"],
               scrub="scrub",
           ),
           Rule(
               path="request",
               keys=["query_string"],
               scrub=build_scrub_query_string(params=["code", "state"]),
           ),
           Rule(
               path="exception.values.[].stacktrace.frames.[].vars",
               keys=["username", "password"],
               scrub="scrub",
           ),
       ]
   )
   
   # Set up Sentry with the scrubber and the default integrations which
   # includes the LoggingIntegration which will capture messages with level
   # logging.ERROR.
   set_up_sentry(
       sentry_dsn="http://user@example.com/1",
       host_id="some host id",
       release="some release name",
       before_send=scrubber,
   )
   
   
   def kick_up_exception():
       username = "James"  # noqa
       try:
           raise Exception("internal exception")
       except Exception:
           logging.getLogger(__name__).exception("kick_up_exception exception")

.. [[[end]]]


Now you have a scrubber and you've set up the Sentry client to use it. How do
you know it's scrubbing the right stuff? How will you know if something changes
and it's no longer scrubbing the right stuff?

You can test it like this:

.. [[[cog
    import cog

    cog.out("\n::\n\n")

    with open("examples/myapp/myapp/test_app.py", "r") as fp:
        for line in fp:
            cog.out(f"   {line}")

    cog.outl("")
   ]]]

::

   # examples/myapp/myapp/test_app.py
   import unittest
   
   from fillmore.test import SentryTestHelper
   
   from myapp.app import kick_up_exception
   
   
   class TestApp(unittest.TestCase):
       def test_scrubber(self):
           # Reuse the existing Sentry configuration and set up the helper
           # to capture Sentry events
           sentry_test_helper = SentryTestHelper()
           with sentry_test_helper.reuse() as sentry_client:
               kick_up_exception()
   
               (payload,) = sentry_client.envelope_payloads
               error = payload["exception"]["values"][0]
               self.assertEqual(error["type"], "Exception")
               self.assertEqual(error["value"], "internal exception")
               self.assertEqual(
                   error["stacktrace"]["frames"][0]["vars"]["username"], "[Scrubbed]"
               )

.. [[[end]]]

This creates a Sentry client specific to this test and kicks up an exception in
the test and captures it with Sentry.

Note that this is a contrived context using a Sentry client created for this
test. You'll want to write tests that use the Sentry client configured for your
application and handling events kicked up from different points in your
application to make sure that Sentry events are getting scrubbed correctly.

See Fillmore documentation for explanation and examples.


Why this? Why not other libraries?
==================================

Other libraries:

* **Have an awkward API that is hard to reason about.**

  I'm not scrubbing Sentry events for fun. I need to be able to write scrubbing
  configuration that is exceptionally clear about what it is and isn't doing.

* **Don't covers large portions of the Sentry event structure.**

  I need scrubbers that cover the entire event structure as well as some
  of the curious cases like the fact that cookie information shows up twice
  and can be encoded as a string.

* **Aren't resilient.**

  The scrubber is running in the context of Sentry reporting an error. If it
  also errors out, then you can end up in situations where you never see errors
  and have no signal that something is horribly wrong. We need scrubbing code
  to be extremely resilient and default to emitting a signal that it's broken.

* **Don't include testing infrastructure.**

  I'm not scrubbing Sentry events for fun. I need to know that the scrubbing
  code is working correctly and that it continues to work as we upgrade
  Python, sentry_sdk, and other things.

  Having testing infrastructure for making this easier is really important.
