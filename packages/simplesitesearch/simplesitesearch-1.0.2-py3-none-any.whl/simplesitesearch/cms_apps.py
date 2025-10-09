# -*- coding: utf-8 -*-
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _


@apphook_pool.register
class SiteSearchApp(CMSApp):
    app_name = "site_search"
    name = _("Site Search")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["simplesitesearch.urls"]


