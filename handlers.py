"""
    By Etienne Quenon
"""
import commands
import worker
import user
import uuid


def publish_advertisement(command: commands.PublishAdvertisement, w: worker.AbstractWorker):
    with w:
        publisher = w.db.read(command.owner)
        advertisement = publisher.publish_ad(command.title, command.description, command.prices, command.localisation, command.service, str(uuid.uuid4()))
        w.db.create(advertisement)
        w.commit()
        return advertisement


def un_publish_advertisement(command: commands.UnPublishAdvertisement, w: worker.AbstractWorker):
    with w:
        publisher = w.db.read(command.owner)
        advertisement = publisher.un_publish_ad(command.uuid)
        w.db.update(advertisement)
        w.commit()
        return advertisement


