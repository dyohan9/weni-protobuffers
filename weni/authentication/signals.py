import logging

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from keycloak import exceptions

from weni.api.v1.keycloak import KeycloakControl
from weni.authentication.models import User

logger = logging.getLogger("weni.authentication.signals")


@receiver(models.signals.post_save, sender=User)
def signal_user(instance, created, **kwargs):
    if not settings.TESTING:
        try:
            keycloak_instance = KeycloakControl()

            user_id = keycloak_instance.get_user_id_by_email(email=instance.email)
            keycloak_instance.get_instance().update_user(
                user_id=user_id,
                payload={
                    "firstName": instance.first_name,
                    "lastName": instance.last_name,
                },
            )
        except exceptions.KeycloakGetError as e:
            logger.error(e)

    if created:
        from weni.common.models import RequestPermissionOrganization

        requests_perm = RequestPermissionOrganization.objects.filter(
            email=instance.email
        )
        for perm in requests_perm:
            permission = perm.organization.get_user_authorization(user=instance)
            permission.role = perm.role
            permission.save(update_fields=["role"])

        requests_perm.delete()
