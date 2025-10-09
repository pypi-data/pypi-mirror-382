from kitconcept.core import DEFAULT_PROFILE
from kitconcept.core import PACKAGE_NAME
from kitconcept.core.utils import gs
from plone import api
from Products.CMFPlone import setuphandlers
from Products.GenericSetup.tool import SetupTool
from zope.component.hooks import getSite


def purge_profile_versions():
    """Purge profile dependency versions."""
    st = gs.get_setup_tool()
    st._profile_upgrade_versions = {}


def set_profile_version(profile: str):
    """Set profile version."""
    mt = api.portal.get_tool("portal_migration")
    mt.setInstanceVersion(mt.getFileSystemVersion())
    st = gs.get_setup_tool()
    version = st.getVersionForProfile(profile)
    st.setLastVersionForProfile(profile, version)


def initialize_migration_tool(profile: str, package_name: str):
    """Set list of addons managed by this package."""
    mt = api.portal.get_tool("portal_migration")
    mt.initializeTool(profile, package_name)


def import_final_steps(context: SetupTool):
    """Final Plone import steps.

    This was an import step, but is now registered as post_handler
    specifically for our main 'plone' (profiles/default) profile.
    """
    site = getSite()
    profile = DEFAULT_PROFILE
    package_name = PACKAGE_NAME
    # Initialize Migration Tool
    initialize_migration_tool(profile, package_name)

    # Unset all profile upgrade versions in portal_setup.  Our default
    # profile should only be applied when creating a new site, so this
    # list of versions should be empty.  But some tests apply it too.
    # This should not be done as it should not be needed.  The profile
    # is a base profile, which means all import steps are run in purge
    # mode.  So for example an extra workflow added by
    # plone.app.discussion is purged.  When plone.app.discussion is
    # still in the list of profile upgrade versions, with the default
    # dependency strategy it will not be reapplied again, which leaves
    # you with a site that misses stuff.  So: when applying our
    # default profile, start with a clean slate in these versions.
    purge_profile_versions()

    # Set out default profile version.
    set_profile_version(profile)

    # Install cmf dependencies
    gs.install_package(package_name, "cmfdependencies")

    # Install our dependencies
    gs.install_package(package_name, "dependencies")

    setuphandlers.replace_local_role_manager(site)
    setuphandlers.addCacheHandlers(site)

    setuphandlers.first_weekday_setup(context)
    setuphandlers.timezone_setup(context)
