import pydantic as _p

from parcelforce_expresslink.shared import CollectionNotificationType, NotificationType, PFBaseModel


class CollectionNotifications(PFBaseModel):
    notification_type: list[CollectionNotificationType] = _p.Field(default_factory=list)

    @classmethod
    def standard_coll(cls):
        return cls(
            notification_type=[
                CollectionNotificationType.EMAIL,
                # CollectionNotificationType.SMS_RECIEVED,
                # CollectionNotificationType.EMAIL_RECIEVED,
            ]
        )


class RecipientNotifications(PFBaseModel):
    notification_type: list[NotificationType] = _p.Field(default_factory=list)

    @classmethod
    def standard_recip(cls):
        return cls(
            notification_type=[
                NotificationType.EMAIL,
                NotificationType.SMS_DOD,
                NotificationType.DELIVERY,
            ]
        )
