from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from froide.helper.utils import get_redirect_url

from froide.foirequest.models import FoiRequest

from .models import (
    PageAnnotationCMSPlugin, DocumentPagesCMSPlugin, DocumentEmbedCMSPlugin,
    PrimaryLinkCMSPlugin, FoiRequestListCMSPlugin, OneClickFoiRequestCMSPlugin
)
from .contact import ContactForm


@plugin_pool.register_plugin
class PageAnnotationPlugin(CMSPluginBase):
    model = PageAnnotationCMSPlugin
    module = _("Document")
    name = _("Page Annotation")
    text_enabled = True
    render_template = "document/cms_plugins/page_annotation.html"
    raw_id_fields = ('page_annotation',)

    def render(self, context, instance, placeholder):
        context = super(PageAnnotationPlugin, self)\
            .render(context, instance, placeholder)

        context['object'] = instance.page_annotation

        return context


@plugin_pool.register_plugin
class DocumentPagesPlugin(CMSPluginBase):
    model = DocumentPagesCMSPlugin
    module = _("Document")
    name = _("Document pages")
    text_enabled = True
    render_template = "document/cms_plugins/document_pages.html"
    raw_id_fields = ('doc',)

    def render(self, context, instance, placeholder):
        context = super(DocumentPagesPlugin, self)\
            .render(context, instance, placeholder)

        context['object'] = instance
        context['pages'] = instance.get_pages()

        return context


@plugin_pool.register_plugin
class DocumentEmbedPlugin(CMSPluginBase):
    model = DocumentEmbedCMSPlugin
    module = _("Document")
    name = _("Document embed")
    text_enabled = True
    render_template = "document/cms_plugins/document_embed.html"
    raw_id_fields = ('doc',)

    def render(self, context, instance, placeholder):
        context = super(DocumentEmbedPlugin, self)\
            .render(context, instance, placeholder)

        context['object'] = instance.doc
        context['instance'] = instance
        return context


@plugin_pool.register_plugin
class PrimaryLinkPlugin(CMSPluginBase):
    module = _("Elements")
    name = _('Primary Link')
    default_template = "cms/plugins/primarylink/default.html"
    model = PrimaryLinkCMSPlugin

    def get_render_template(self, context, instance, placeholder):
        if instance.template:
            return instance.template
        return self.default_template

    def render(self, context, instance, placeholder):
        context = super(PrimaryLinkPlugin, self)\
            .render(context, instance, placeholder)
        context['object'] = instance
        return context


@plugin_pool.register_plugin
class ContinueLinkPlugin(CMSPluginBase):
    module = _("Elements")
    name = _('Continue Link')
    text_enabled = True
    cache = False
    render_template = "cms/plugins/continue_link.html"

    def render(self, context, instance, placeholder):
        context = super(ContinueLinkPlugin, self)\
            .render(context, instance, placeholder)
        request = context['request']
        context['title'] = request.GET.get('next_title', 'Zurück zu Ihrer Anfrage')
        next_url = get_redirect_url(request)
        context['next_url'] = next_url
        return context


@plugin_pool.register_plugin
class DropdownBannerPlugin(CMSPluginBase):
    module = _("Ads")
    name = _('Dropdown Banner')
    allow_children = True
    cache = True
    render_template = "cms/plugins/dropdown_banner.html"


@plugin_pool.register_plugin
class FoiRequestListPlugin(CMSPluginBase):
    """
    Plugin for including the latest entries filtered
    """
    model = FoiRequestListCMSPlugin
    name = _('Latest FOI requests')
    default_template = 'foirequest/cms_plugins/list.html'
    filter_horizontal = ['tags']
    text_enabled = True
    raw_id_fields = ['user', 'jurisdiction', 'category', 'project',
                     'classification', 'publicbody']

    def get_render_template(self, context, instance, placeholder):
        if instance.template:
            return instance.template
        return self.default_template

    def render(self, context, instance, placeholder):
        """
        Update the context with plugin's data
        """
        foirequests = FoiRequest.published.all()

        FILTER_KEYS = (
            'user', 'jurisdiction_id', 'category_id',
            'classification_id', 'status', 'resolution'
        )
        filters = {}

        tag_list = instance.tags.all().values_list('id', flat=True)
        if tag_list:
            filters['tags__in'] = tag_list

        for key in FILTER_KEYS:
            if getattr(instance, key, None):
                filters[key] = getattr(instance, key)

        if instance.publicbody_id:
            filters['public_body_id'] = instance.publicbody_id

        foirequests = foirequests.filter(**filters)

        if instance.offset:
            foirequests = foirequests[instance.offset:]
        if instance.number_of_entries:
            foirequests = foirequests[:instance.number_of_entries]

        context = super().render(context, instance, placeholder)
        context['object_list'] = foirequests
        return context


@plugin_pool.register_plugin
class OneClickFoiRequestPlugin(CMSPluginBase):
    """
    Plugin for including the latest entries filtered
    """
    model = OneClickFoiRequestCMSPlugin
    name = _('One click FoiRequest form')
    default_template = 'foirequest/cms_plugins/one_click.html'
    text_enabled = True
    cache = False
    raw_id_fields = ['foirequest']

    def get_render_template(self, context, instance, placeholder):
        if instance.template:
            return instance.template
        return self.default_template

    def render(self, context, instance, placeholder):
        """
        Update the context with plugin's data
        """

        context = super().render(context, instance, placeholder)
        context['object'] = instance.foirequest
        context['redirect_url'] = instance.redirect_url
        context['reference'] = instance.reference
        return context


@plugin_pool.register_plugin
class SetPasswordFormPlugin(CMSPluginBase):
    module = _("Account")
    name = _('Set Password Form')
    text_enabled = True
    render_template = "account/cms_plugins/set_password.html"


@plugin_pool.register_plugin
class PublicBodyFeedbackPlugin(CMSPluginBase):
    module = _("Contact")
    name = _('Contact Form')
    text_enabled = True
    render_template = "fds_cms/feedback.html"

    def render(self, context, instance, placeholder):
        """
        Update the context with plugin's data
        """

        context = super().render(context, instance, placeholder)
        context['form'] = ContactForm()
        return context
