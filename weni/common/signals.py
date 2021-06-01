import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from weni.authentication.models import User
from weni.common.models import (
    Project,
    Service,
    Organization,
    OrganizationAuthorization,
    RequestPermissionOrganization,
)
from weni.celery import app as celery_app

logger = logging.getLogger("weni.common.signals")


@receiver(post_save, sender=Project)
def create_service_status(sender, instance, created, **kwargs):
    if created:
        for service in Service.objects.filter(default=True):
            instance.service_status.create(service=service)


@receiver(post_save, sender=Service)
def create_service_default_in_all_user(sender, instance, created, **kwargs):
    if created and instance.default:
        for project in Project.objects.all():
            project.service_status.create(service=instance)


@receiver(post_save, sender=Organization)
def update_organization(sender, instance, **kwargs):
    for authentication in instance.authorizations.all():
        instance.send_email_delete_organization(
            first_name=authentication.user.first_name, email=authentication.user.email
        )


@receiver(post_delete, sender=Organization)
def delete_organization(instance, **kwargs):
    instance.send_email_remove_permission_organization(
        first_name=instance.user.first_name, email=instance.user.email
    )


@receiver(post_save, sender=OrganizationAuthorization)
def org_authorizations(sender, instance, **kwargs):
    celery_app.send_task(
        "update_user_permission_organization",
        args=[
            instance.organization.inteligence_organization,
            instance.user.email,
            instance.role,
        ],
    )
    for project in instance.organization.project.all():
        celery_app.send_task(
            "update_user_permission_project",
            args=[
                project.flow_organization,
                instance.user.email,
                instance.role,
            ],
        )


@receiver(post_delete, sender=OrganizationAuthorization)
def delete_authorizations(instance, **kwargs):
    instance.organization.send_email_remove_permission_organization(
        first_name=instance.user.first_name, email=instance.user.email
    )


@receiver(post_save, sender=RequestPermissionOrganization)
def request_permission_organization(sender, instance, created, **kwargs):
    if created:
        user = User.objects.filter(email=instance.email)
        if user.exists():
            perm = instance.organization.get_user_authorization(user=user.first())
            perm.role = instance.role
            perm.save(update_fields=["role"])
            instance.delete()
        instance.organization.send_email_invite_organization(email=instance.email)