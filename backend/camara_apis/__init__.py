"""
Mock clients for the CAMARA APIs used by SafeRemit, shaped to mirror the
real Nokia Network-as-Code (NaC) responses as closely as possible so that
swapping a mock for a live call is a one-file change (see PROTOTYPE_NOTES.md).

Each mock is deliberately scenario-aware: pass a `scenario` key and it
returns the canned response for that demo case. Pass no scenario and it
falls back to a generic "clean" response, so the same orchestrator code
works whether you're driving it from the demo UI or from a real request.
"""
