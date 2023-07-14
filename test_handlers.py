import database
import user
import commands
import worker
import handlers


class FakeDatabase(database.AbstractDatabase):
    def __init__(self, obj):
        super().__init__()
        self._collection = set(obj)  # Type Set(object)

    def create(self, obj: object):
        self._collection.add(obj)

    def read(self, uuid: str) -> object:
        return next(a for a in self._collection if a.uuid == uuid)

    def delete(self, uuid: str):
        ads = (a for a in self._collection if a.uuid == uuid)
        for ad in ads:
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
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    command = commands.PublishAdvertisement("TestAd", "This is a test Ad", None, None, None, "00000-0000-0000-00000000")
    w = FakeWorker()
    with w:
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

