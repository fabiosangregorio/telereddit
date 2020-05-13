"""
Services are used to retrieve media contents from external sources.

Summary
-------
This module is comprised of a main entrypoint
(`services_wrapper.ServicesWrapper`) which is a facade for the services logic, a
base abstract class for all services (`service.Service`), which determines the
common logic of all services, and a class for each service provider, which
implements in practice the steps to retrieve the media information.

A `generic_service.Generic` service class is also present, which will be used if
no handler for a specific service is found.
"""
