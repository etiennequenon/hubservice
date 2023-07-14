import database
import user
import commands
import worker
import handlers
import time


class FakeDatabase(database.AbstractDatabase):
    def __init__(self, obj):
        super().__init__()
        self._collection = set(obj)  # Type Set(object)

    def create(self, obj: object):
        self._collection.add(obj)

    def read(self, uuid: str) -> object:
        return next((a for a in self._collection if a.uuid == uuid), None)

    def delete(self, uuid: str):
        ad = next(a for a in self._collection if a.uuid == uuid)
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
    with w:
        provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, False, None)
        command = commands.PublishAdvertisement("TestAd", "This is a test Ad", None, None, None, "00000-0000-0000-00000000")
        w.db.create(provider)
        ad = handlers.publish_advertisement(command, w)

        assert w.db.read(ad.uuid) is not None
        assert w.commited


def test_unpublish_advertisement():
    w = FakeWorker()
    with w:
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
    with w:
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
    with w:
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
    with w:
        provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, False, None)
        command = commands.PublishAdvertisement("TestAd", "This is a test Ad", None, None, None, "00000-0000-0000-00000000")
        w.db.create(provider)
        ad = handlers.publish_advertisement(command, w)

        command = commands.DeleteAdvertisement(provider.uuid, ad.uuid)
        handlers.delete_ad(command, w)

        assert provider.get_ad(ad.uuid) is None
        assert w.db.read(ad.uuid) is None
        assert w.commited
