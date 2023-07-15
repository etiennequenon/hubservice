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

