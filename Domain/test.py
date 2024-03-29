"""
    By Etienne Quenon
"""

import user
import time
import datetime
import gc


def test_publish_advertisement():
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    ad = provider.publish_ad("TestAd", "This is a test Ad", {"service1": 123}, None, None, "00000-0000-0000-00000000")
    assert ad.published
    assert ad.date_published
    assert ad.expiry_date

    try:  # Test if the same ad can't be published twice.
        provider.publish_ad("TestAd", "This is a test Ad", {"service1": 123}, None, None, "00000-0000-0000-00000000")
    except user.AdAlreadyExist:
        pass


def test_unpublish_advertisement():
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    provider.publish_ad("TestAd", "This is a test Ad", {"service1": 123}, None, None, "00000-0000-0000-00000000")
    ad = provider.un_publish_ad("00000-0000-0000-00000000")
    assert not ad.published
    assert not ad.date_published
    assert not ad.expiry_date


def test_update_publish_vip_and_not_vip():
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    ad = provider.publish_ad("TestAd", "This is a test Ad", {"service1": 123}, None, None, "00000-0000-0000-00000000")
    try:
        provider.update_ad_published_date(ad.uuid)
    except user.NotVip:
        pass

    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, True, None)
    ad = provider.publish_ad("TestAd", "This is a test Ad", {"service1": 123}, None, None, "00000-0000-0000-00000000")
    date_published = ad.date_published
    expiry_date = ad.expiry_date
    time.sleep(0.001)
    ad_returned = provider.update_ad_published_date(ad.uuid)

    assert ad_returned
    assert ad_returned.date_published != date_published
    assert ad_returned.expiry_date != expiry_date


def test_update_billing():
    billing = user.Billing("7987846548498", "29-04-2027", "999", "VC AC")
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, False, billing)

    assert provider._billing.card_number == "7987846548498"
    assert provider._billing.expiry_date == "29-04-2027"
    assert provider._billing.secret_code == "999"
    assert provider._billing.fullname == "VC AC"

    provider.update_billing("789548112558", "30-01-2030", "000", "EQ EB")

    assert provider._billing.card_number == "789548112558"
    assert provider._billing.expiry_date == "30-01-2030"
    assert provider._billing.secret_code == "000"
    assert provider._billing.fullname == "EQ EB"


def test_update_ad_location():
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, True, None)
    location = user.Location("Avenue Pas Paul Des Fleurs", 27, "Mont-pas-Marchienne", 6142, "Brabant", "Belgium")
    ad = provider.publish_ad("TestAd", "This is a test Ad", {"service1": 123}, location, {}, "00000-0000-0000-00000001")

    assert ad.localisation.street == "Avenue Pas Paul Des Fleurs"
    assert ad.localisation.number == 27
    assert ad.localisation.city == "Mont-pas-Marchienne"
    assert ad.localisation.zip_code == 6142
    assert ad.localisation.state == "Brabant"
    assert ad.localisation.country == "Belgium"

    ad = provider.update_ad_location("00000-0000-0000-00000001", "Avenue Paul Des Fleurs", 42, "Mont-Marchienne", 6000, "Brabant Flamoush", "Belgique")

    assert ad.localisation.street == "Avenue Paul Des Fleurs"
    assert ad.localisation.number == 42
    assert ad.localisation.city == "Mont-Marchienne"
    assert ad.localisation.zip_code == 6000
    assert ad.localisation.state == "Brabant Flamoush"
    assert ad.localisation.country == "Belgique"


def test_update_ad_services():
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, True, None)
    ad = provider.publish_ad("TestAd", "This is a test Ad", {}, None, {"service1": "Je suis"}, "00000-0000-0000-00000001")

    assert ad.service["service1"] == "Je suis"

    provider.update_ad_services("00000-0000-0000-00000001", {"service2": "Je prends"})

    assert ad.service["service2"] == "Je prends"


def test_update_ad_prices():
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, True, None)
    ad = provider.publish_ad("TestAd", "This is a test Ad", {"service1": 132}, None, {}, "00000-0000-0000-00000001")

    assert ad.prices["service1"] == 132

    provider.update_ad_prices("00000-0000-0000-00000001", {"service1": 220})

    assert ad.prices["service1"] == 220


def test_promote_ad_to_premium():
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, True, None)
    ad = provider.publish_ad("TestAd", "This is a test Ad", None, None, {}, "00000-0000-0000-00000001")

    ad_promoted = provider.promote_ad_to_premium(ad.uuid)

    assert ad_promoted

    try:
        provider.promote_ad_to_premium(ad.uuid)
    except user.AdvertisementAlreadyPromoted:
        pass

    provider.vip = False  # Test if user is not VIP, so it returns an error.

    try:
        provider.promote_ad_to_premium(ad.uuid)
    except user.NotVip:
        pass


def test_assign_private_pics():
    provider = user.Provider("testdude", "00000-0000-0000-00000000", None, None, list(), False, True, None)
    timestamp = datetime.datetime.now()
    pics = [user.PrivatePicture(bytes(), timestamp), user.PrivatePicture(bytes(), timestamp), user.PrivatePicture(bytes(), timestamp)]

    provider.private_pics = pics

    assert len(provider.private_pics) == 3
    assert provider.private_pics[0].date_published == timestamp


def test_sms_sent():
    visitor = user.Visitor("testdude", "00000-0000-0000-00000000", "abcd1234", "test@test.com", "29-03-1998", "Rue des fleurs 27", bytes(), {}, True, [])
    for i in range(50):
        visitor.send_sms()

    assert visitor.sms_sent == 50

    try:
        visitor.send_sms()
    except user.SmsLimitWasReached:
        pass


def test_report_user():
    provider = user.Provider("testdudeprovider", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    visitor = user.Visitor("testdude", "00000-0000-0000-00000001", "abcd1234", "test@test.com", "29-03-1998", "Rue des fleurs 27", bytes(), {}, False, [])
    report = visitor.report(provider, "This is fake", "00000-0000-0000-00000002")

    assert report.status == "NEW"

    moderator = user.Moderator("testdudemodo", "00000-0000-0000-00000001", "abcd1234", "test@test.com")
    report2 = moderator.open_report(report, "00000-0000-0000-00000003")

    assert report2.status == "PENDING"
    assert report2.comment[0].target_uuid == report.uuid
    assert report2.comment[0].owner_uuid == visitor.uuid
    assert report2.comment[0].content == f"Moderator {moderator.username} has opened your ticket !"


def test_add_comment_to_report():
    provider = user.Provider("testdudeprovider", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    visitor = user.Visitor("testdude", "00000-0000-0000-00000020", "abcd1234", "test@test.com", "29-03-1998", "Rue des fleurs 27", bytes(), {}, False, [])
    report = visitor.report(provider, "This is fake", "00000-0000-0000-00000010")
    moderator = user.Moderator("testdudemodo2", "00000-0000-0000-00000001", "abcd1234", "test@test.com")

    exception_occured = 0

    try:
        moderator.comment_report(report, "This should fail", "00000-0000-0000-00000003")
    except user.ReportNotOpened:
        exception_occured += 1
    
    assert exception_occured == 1
    assert len(report.comment) == 0

    moderator.open_report(report, "00000-0000-0000-00000017")
    moderator.comment_report(report, "This should work", "00000-0000-0000-00000018")

    assert report.comment[1].content == "This should work"


def test_close_report():
    provider = user.Provider("testdudeprovider", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    visitor = user.Visitor("testdude", "00000-0000-0000-00000001", "abcd1234", "test@test.com", "29-03-1998", "Rue des fleurs 27", bytes(), {}, False, [])
    report = visitor.report(provider, "This is fake", "00000-0000-0000-00000002")
    moderator = user.Moderator("testdudemodo2", "00000-0000-0000-00000001", "abcd1234", "test@test.com")

    exception_occurred = 0

    try:
        moderator.close_report(report, "00000-0000-0000-00000003")
    except user.ReportNotOpened:
        exception_occurred += 1

    assert exception_occurred == 1
    assert len(report.comment) == 0

    moderator.open_report(report, "00000-0000-0000-00000003")
    moderator.close_report(report, "00000-0000-0000-00000004")

    assert report.status == "CLOSED"
    assert report.comment[1].content == f"Moderator {moderator.username} has closed your ticket !"


def test_enable_disable_user():
    provider = user.Provider("testdudeprovider", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    visitor = user.Visitor("testdude", "00000-0000-0000-00000001", "abcd1234", "test@test.com", "29-03-1998", "Rue des fleurs 27", bytes(), {}, False, [])
    moderator = user.Moderator("testdudemodo2", "00000-0000-0000-00000001", "abcd1234", "test@test.com")
    admin = user.Admin("testdudeadmin", "00000-0000-0000-00000001", "abcd1234", "test@test.com")

    admin.disable_user(provider)
    admin.disable_user(visitor)
    admin.disable_user(moderator)

    assert provider._active is False
    assert visitor._active is False
    assert moderator._active is False


def test_protection_disabled_user():
    provider = user.Provider("testdudeprovider", "00000-0000-0000-00000000", None, None, list(), False, False, None)
    visitor = user.Visitor("testdude", "00000-0000-0000-00000001", "abcd1234", "test@test.com", "29-03-1998", "Rue des fleurs 27", bytes(), {}, False, [])
    report = visitor.report(provider, "This is fake", "00000-0000-0000-00000002")
    moderator = user.Moderator("testdudemodo2", "00000-0000-0000-00000001", "abcd1234", "test@test.com")
    admin = user.Admin("testdudeadmin", "00000-0000-0000-00000001", "abcd1234", "test@test.com")

    admin.disable_user(provider)
    admin.disable_user(visitor)
    admin.disable_user(moderator)

    exception_occurred = 0

    try:
        provider.publish_ad("TestAd", "This is a test Ad", {"service1": 123}, None, None, "00000-0000-0000-00000000")
    except user.UserNotActive:
        exception_occurred += 1

    try:
        visitor.add_comment("00000-0000-0000-00000000", "test", "00000-0000-0000-00000001")
    except user.UserNotActive:
        exception_occurred += 1

    try:
        moderator.open_report(report, "00000-0000-0000-00000003")
    except user.UserNotActive:
        exception_occurred += 1

    assert exception_occurred == 3
