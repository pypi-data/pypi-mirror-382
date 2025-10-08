# from cs_dynamicpages import _
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface


# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IDynamicView(Interface):
    """Marker Interface for IDynamicView"""


@implementer(IDynamicView)
class DynamicView(BrowserView):
    def rows(self):
        dynamic_page_folder = self.dynamic_page_folder_element()
        if dynamic_page_folder:
            return api.content.find(
                portal_type="DynamicPageRow",
                sort_on="getObjPositionInParent",
                context=dynamic_page_folder[0].getObject(),
            )
        return []

    def dynamic_page_folder_element(self):
        page_folders = api.content.find(
            portal_type="DynamicPageFolder",
            context=self.context,
            depth=1,
            sort_on="getObjPositionInParent",
        )
        if page_folders:
            return page_folders
        else:
            if self.can_edit():
                alsoProvides(self.request, IDisableCSRFProtection)
                api.content.create(
                    container=self.context,
                    type="DynamicPageFolder",
                    title="Rows",
                )
                return api.content.find(
                    portal_type="DynamicPageFolder",
                    context=self.context,
                    depth=1,
                    sort_on="getObjPositionInParent",
                )

    def dynamic_page_folder_element_url(self):
        dynamic_page_folder = self.dynamic_page_folder_element()
        if dynamic_page_folder:
            return dynamic_page_folder[0].getObject().absolute_url()
        return ""

    def can_edit(self):
        return api.user.has_permission("Modify portal content", obj=self.context)
