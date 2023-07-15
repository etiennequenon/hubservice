from collections import defaultdict

import database
import notifications
import user
import commands
import worker
import handlers
import time
from typing import Dict, List


class FakeDatabase(database.AbstractDatabase):
    def __init__(self, obj):
        super().__init__()
        self._collection = set(obj)  # Type Set(object)

    def create(self, obj: object):
        self._collection.add(obj)

    def read(self, uuid: str) -> object:
        return next((a for a in self._collection if a.uuid == uuid), None)

    def delete(self, uuid: str):
        ad = next((a for a in self._collection if a.uuid == uuid), None)
        self._collection.remove(ad)

    def update(self, obj: object):
        self._collection.add(obj)


class FakeWorker(worker.AbstractWorker):
    def __init__(self):
        self.db = FakeDatabase([])
        self.commited = False

    def _commit(self):
        self.commited = True

    def rollback(self):
        pass


def test_publish_advertisement():
    w = FakeWorker()
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    command = commands.PublishAdvertisement("TestAd", "This is a test Ad", None, None, None, "00000-0000-0000-00000000")
    w.db.create(provider)
    ad = handlers.publish_advertisement(command, w)

    assert w.db.read(ad.uuid) is not None
    assert w.commited


def test_unpublish_advertisement():
    w = FakeWorker()
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    command = commands.PublishAdvertisement("TestAd", "This is a test Ad", None, None, None, "00000-0000-0000-00000000")
    w.db.create(provider)
    ad = handlers.publish_advertisement(command, w)

    command = commands.UnPublishAdvertisement(provider.uuid, ad.uuid)
    updated_ad = handlers.un_publish_advertisement(command, w)

    assert w.db.read(updated_ad.uuid).published is False
    assert w.db.read(updated_ad.uuid).expiry_date is None
    assert w.db.read(updated_ad.uuid).date_published is None
    assert w.commited


def test_update_published_date_advertisement():
    w = FakeWorker()
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, True, None)
    command = commands.PublishAdvertisement("TestAd", "This is a test Ad", None, None, None, "00000-0000-0000-00000000")
    w.db.create(provider)
    ad = handlers.publish_advertisement(command, w)
    first_date = ad.date_published

    time.sleep(0.0001)

    command = commands.UpdateAdvertisementPublishedDate(provider.uuid, ad.uuid)
    updated_ad = handlers.update_ad_published_date(command, w)

    second_date = updated_ad.date_published

    assert first_date < second_date
    assert w.commited


def test_promote_ad_to_premium():
    w = FakeWorker()
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, True, None)
    command = commands.PublishAdvertisement("TestAd", "This is a test Ad", None, None, None, "00000-0000-0000-00000000")
    w.db.create(provider)
    ad = handlers.publish_advertisement(command, w)

    command = commands.PromoteAdvertisementToPremium(provider.uuid, ad.uuid)
    promoted_ad = handlers.promote_ad_to_premium(command, w)

    assert type(promoted_ad) == user.PremiumAdvertisement
    assert w.commited


def test_delete_ad():
    w = FakeWorker()
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    command = commands.PublishAdvertisement("TestAd", "This is a test Ad", None, None, None, "00000-0000-0000-00000000")
    w.db.create(provider)
    ad = handlers.publish_advertisement(command, w)

    command = commands.DeleteAdvertisement(provider.uuid, ad.uuid)
    handlers.delete_ad(command, w)

    assert provider.get_ad(ad.uuid) is None
    assert w.db.read(ad.uuid) is None
    assert w.commited


def test_add_comment():
    visitor = user.Visitor("testdude", "00000-0000-0000-00000000", "abcd1234", "test@test.com", "29-03-1998", "Rue des fleurs 27", bytes(), {}, True, [])
    provider = user.Provider("testdude", "00000-0000-0000-00000001", None, None, list(), False, False, None)
    command = commands.AddComment(provider.uuid, visitor.uuid, "C'est à chier putain.")
    w = FakeWorker()
    w.db.create(provider)
    w.db.create(visitor)

    comment: user.Comment = handlers.add_comment(command, w)

    assert comment.target_uuid == "00000-0000-0000-00000001"
    assert comment.content == "C'est à chier putain."
    assert comment.owner_uuid == "00000-0000-0000-00000000"
    assert w.db.read(comment.uuid)
    assert comment in visitor.comments


def test_modify_comment():
    visitor = user.Visitor("testdude", "00000-0000-0000-00000000", "abcd1234", "test@test.com", "29-03-1998", "Rue des fleurs 27", bytes(), {}, True, [])
    provider = user.Provider("testdude", "00000-0000-0000-00000001", None, None, list(), False, False, None)
    command = commands.AddComment(provider.uuid, visitor.uuid, "C'est à chier putain.")
    w = FakeWorker()
    w.db.create(provider)
    w.db.create(visitor)

    comment: user.Comment = handlers.add_comment(command, w)

    command = commands.ModifyComment(visitor.uuid, comment.uuid, "Correction, c'est ULTRA À CHIER")
    modified_comment = handlers.modify_comment(command, w)

    assert modified_comment.content == "Correction, c'est ULTRA À CHIER"


class FakeNotifications(notifications.AbstractNotifications):
    def __init__(self):
        self.sent = defaultdict(list)  # type: Dict[str, List[str]]

    def send(self, to: str, message: str):
        self.sent[to].append(message)


def test_send_sms_visitor():
    visitor = user.Visitor("testdude", "00000-0000-0000-00000000", "abcd1234", "test@test.com", "29-03-1998", "Rue des fleurs 27", bytes(), {}, True, [])
    command = commands.SendSms(visitor.uuid, "+320000000", "This is a test SMS")
    notification = FakeNotifications()
    w = FakeWorker()
    w.db.create(visitor)

    for i in range(50):
        handlers.send_sms_visitor(command, w, notification)

    assert visitor.sms_sent == 50
    assert len(notification.sent["+320000000"]) == 50

    try:
        handlers.send_sms_visitor(command, w, notification)
    except user.SmsLimitWasReached:
        pass
