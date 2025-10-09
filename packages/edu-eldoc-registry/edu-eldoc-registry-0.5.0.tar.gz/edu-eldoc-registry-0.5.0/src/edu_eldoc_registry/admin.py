
from django.contrib import (
    admin,
)

from edu_eldoc_registry.models import (
    Certificate,
    Document,
    Sign,
)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'


@admin.register(Sign)
class SignAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
