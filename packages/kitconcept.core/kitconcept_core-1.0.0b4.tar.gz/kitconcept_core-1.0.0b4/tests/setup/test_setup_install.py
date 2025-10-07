from kitconcept.core import PACKAGE_NAME
from Products.CMFPlone.TypesTool import TypesTool
from Products.GenericSetup.tool import SetupTool

import pytest


class TestSetupInstall:
    @pytest.fixture(autouse=True)
    def _setup(self, current_versions):
        self.profile_version: str = current_versions.base
        self.dependencies_profile_version: str = current_versions.dependencies

    def test_browserlayer(self, browser_layers):
        """Test that IBrowserLayer is registered."""
        from kitconcept.core.interfaces import IBrowserLayer

        assert IBrowserLayer in browser_layers

    def test_latest_version(self, profile_last_version):
        """Test latest version of default profile."""
        assert profile_last_version(f"{PACKAGE_NAME}:base") == self.profile_version

    def test_base_profile(self, setup_tool):
        """Test if we have the base profile."""
        assert setup_tool.getBaselineContextID() == f"profile-{PACKAGE_NAME}:base"

    def test_dependencies_version(self, profile_last_version):
        """Test latest version of dependencies profile."""
        assert (
            profile_last_version(f"{PACKAGE_NAME}:dependencies")
            == self.dependencies_profile_version
        )


class TestSetupDependencies:
    @pytest.fixture(autouse=True)
    def _setup(self, portal_class):
        self.portal = portal_class
        self.setup_tool: SetupTool = portal_class.portal_setup
        self.types_tool: TypesTool = portal_class.portal_types

    @pytest.mark.parametrize(
        "profile",
        [
            "Products.MimetypesRegistry:MimetypesRegistry",
            "Products.PortalTransforms:PortalTransforms",
            "Products.CMFEditions:CMFEditions",
            "Products.PlonePAS:PlonePAS",
            "plone.app.linkintegrity:default",
            "plone.app.registry:default",
            "plone.app.theming:default",
            "plone.app.users:default",
            "plone.outputfilters:default",
            "plone.protect:default",
            "plone.staticresources:default",
            "plone.app.contenttypes:default",
            "plone.restapi:default",
            "plone.volto:default",
            "plonetheme.barceloneta:default",
            "kitconcept.voltolighttheme:default",
            "collective.volto.formsupport:default",
            "plonegovbr.socialmedia:default",
        ],
    )
    def test_installed(self, profile: str):
        """Test if a profile is installed."""
        assert self.setup_tool.getLastVersionForProfile(profile) is not None

    @pytest.mark.parametrize(
        "portal_type,title,klass",
        [
            ("Plone Site", "Plone Site", "Products.CMFPlone.Portal.PloneSite"),
            ("Document", "Page", "plone.volto.content.FolderishDocument"),
            ("News Item", "News Item", "plone.volto.content.FolderishNewsItem"),
            ("Event", "Event", "plone.volto.content.FolderishEvent"),
            ("Image", "Image", "plone.app.contenttypes.content.Image"),
        ],
    )
    def test_portal_type(self, portal_type: str, title: str, klass: str):
        """Test if a portal_type is installed."""
        from plone.dexterity.fti import DexterityFTI

        fti = self.types_tool.getTypeInfo(portal_type)
        assert isinstance(fti, DexterityFTI)
        assert fti.title == title
        assert fti.klass == klass
