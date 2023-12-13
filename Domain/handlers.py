"""
    By Etienne Quenon
"""


import commands
import worker
import user
import uuid
import notifications


def publish_advertisement(command: commands.PublishAdvertisement, w: worker.AbstractWorker):
    with w:
        publisher: user.Provider = w.db.read(command.owner)
        advertisement = publisher.publish_ad(command.title, command.description, command.prices, command.localisation, command.service, str(uuid.uuid4()))
        w.db.create(advertisement)
        w.commit()
    return advertisement


def un_publish_advertisement(command: commands.UnPublishAdvertisement, w: worker.AbstractWorker):
    with w:
        publisher: user.Provider = w.db.read(command.owner)
        advertisement = publisher.un_publish_ad(command.uuid)
        w.db.update(advertisement)
        w.commit()
    return advertisement


def update_ad_published_date(command: commands.UpdateAdvertisementPublishedDate, w: worker.AbstractWorker):
    with w:
        publisher: user.Provider = w.db.read(command.owner)
        advertisement = publisher.update_ad_published_date(command.uuid)
        w.db.update(advertisement)
        w.commit()
    return advertisement


def promote_ad_to_premium(command: commands.PromoteAdvertisementToPremium, w: worker.AbstractWorker):
    with w:
        publisher: user.Provider = w.db.read(command.owner)
        advertisement = publisher.promote_ad_to_premium(command.uuid)
        w.db.update(advertisement)
        w.commit()
    return advertisement


def delete_ad(command: commands.DeleteAdvertisement, w: worker.AbstractWorker):
    with w:
        publisher: user.Provider = w.db.read(command.owner)
        publisher.delete_ad(command.uuid)
        w.db.delete(command.uuid)
        w.commit()


def add_comment(command: commands.AddComment, w: worker.AbstractWorker):
    with w:
        visitor: user.Visitor = w.db.read(command.owner)
        comment = visitor.add_comment(command.target_uuid, command.content, str(uuid.uuid4()))
        w.db.create(comment)
        w.commit()
    return comment


def modify_comment(command: commands.ModifyComment, w: worker.AbstractWorker):
    with w:
        visitor: user.Visitor = w.db.read(command.owner)
        comment = visitor.modify_comment(command.uuid, command.content)
        w.db.update(comment)
        w.commit()
    return comment


def delete_comment(command: commands.DeleteComment, w: worker.AbstractWorker):
    with w:
        visitor: user.Visitor = w.db.read(command.owner)
        visitor.delete_comment(command.uuid)
        w.db.delete(command.uuid)
        w.commit()


def send_sms_visitor(command: commands.SendSms, w: worker.AbstractWorker, notification: notifications.AbstractNotifications):
    with w:
        visitor: user.Visitor = w.db.read(command.user_uuid)
        notification.send(command.to, command.message)
        visitor.send_sms()
        w.db.update(visitor)
        w.commit()


def report(command: commands.Report, w: worker.AbstractWorker):
    with w:
        reporting_user: user.User = w.db.read(command.owner)
        reports = reporting_user.report(command.target_uuid, command.content, str(uuid.uuid4()))
        w.db.create(reports)
        w.commit()
    return reports


def comment_report(command: commands.CommentReport, w: worker.AbstractWorker):
    with w:
        commenting_user: user.User = w.db.read(command.owner)
        target_report: user.Report = w.db.read(command.target_uuid)
        commenting_user.comment_report(target_report, command.content, str(uuid.uuid4()))
        w.db.update(target_report)
        w.commit()
    return target_report


def open_report(command: commands.OpenReport, w: worker.AbstractWorker):
    with w:
        moderator: user.Moderator = w.db.read(command.moderator_uuid)
        target_report: user.Report = w.db.read(command.report_uuid)
        moderator.open_report(target_report, str(uuid.uuid4()))
        w.db.update(target_report)
        w.commit()


def close_report(command: commands.CloseReport, w: worker.AbstractWorker):
    with w:
        moderator: user.Moderator = w.db.read(command.moderator_uuid)
        target_report: user.Report = w.db.read(command.report_uuid)
        moderator.close_report(target_report, str(uuid.uuid4()))
        w.db.update(target_report)
        w.commit()


def activate_user(command: commands.ActivateUser, w: worker.AbstractWorker):
    with w:
        admin: user.Admin = w.db.read(command.admin_uuid)
        target_user = w.db.read(command.user_uuid)
        admin.activate_user(target_user)
        w.db.update(target_user)
        w.commit()


def disable_user(command: commands.ActivateUser, w: worker.AbstractWorker):
    with w:
        admin: user.Admin = w.db.read(command.admin_uuid)
        target_user = w.db.read(command.user_uuid)
        admin.disable_user(target_user)
        w.db.update(target_user)
        w.commit()


def set_private_pics(command: commands.SetPrivatePics, w: worker.AbstractWorker):
    with w:
        provider: user.Provider = w.db.read(command.user_uuid)
        provider.private_pics(command.pictures)
        w.db.update(provider)
        w.commit()


def update_billing(command: commands.UpdateBilling, w: worker.AbstractWorker):
    with w:
        provider: user.Provider = w.db.read(command.user_uuid)
        provider.update_billing(command.card_number, command.expiry_date, command.secret_code, command.fullname)
        w.db.update(provider)
        w.commit()
