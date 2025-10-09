from kitconcept.core import _
from kitconcept.core.interfaces import IBrowserLayer
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.registry.interfaces import IRegistry
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.restapi.interfaces import ISiteEndpointExpander
from zope import schema
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface


class IKitconceptSettings(Interface):
    """kitconcept core settings stored in the backend"""

    custom_css = schema.Text(
        title=_("Custom CSS"),
        description=_("Custom CSS for this site."),
        required=False,
    )


class KitconceptSettingsEditForm(RegistryEditForm):
    schema = IKitconceptSettings
    label = _("kitconcept Settings")
    schema_prefix = "kitconcept.core.settings"

    def updateFields(self):
        super().updateFields()

    def updateWidgets(self):
        super().updateWidgets()


class KitconceptSettingsControlPanel(ControlPanelFormWrapper):
    form = KitconceptSettingsEditForm


@adapter(Interface, Interface)
class KitconceptControlpanel(RegistryConfigletPanel):
    schema = IKitconceptSettings
    configlet_id = "kitconceptSettings"
    configlet_category_id = "plone-general"
    schema_prefix = "kitconcept.core.settings"


@adapter(Interface, IBrowserLayer)
@implementer(ISiteEndpointExpander)
class SiteEndpointExpander:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, data):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IKitconceptSettings, prefix="kitconcept.core.settings"
        )
        data["kitconcept.custom_css"] = settings.custom_css
