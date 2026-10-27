"""Offline checks for the dispatch diagnosis: every reason for a silent no-op must be reported in plain Italian."""
from datetime import date

import pytest

from app.alerts.dispatcher import check_dispatch_readiness, dispatch_alerts
from app.alerts.notifiers import SmtpEmailNotifier, TwilioSmsNotifier
from app.alerts.store import add_recipient, log_alert_result, upsert_deadline

TODAY = date(2026, 10, 10)


@pytest.fixture(autouse=True)
def clean_channels(monkeypatch):
    for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM"):
        monkeypatch.delenv(key, raising=False)


def smtp(monkeypatch, host="smtp.example.org", user="", password=""):
    monkeypatch.setenv("SMTP_HOST", host)
    monkeypatch.setenv("SMTP_USER", user)
    monkeypatch.setenv("SMTP_PASSWORD", password)


def deadline(due="2026-10-15", did="d1"):
    upsert_deadline(did, "m", "s", "f", "Rinnovo test", due, [30, 15, 7], "a.pdf", 1)


@pytest.mark.offline
def test_nothing_to_send_explains_every_missing_piece_in_turn(monkeypatch):
    r = check_dispatch_readiness(TODAY)
    assert not r.can_send and "Nessuna scadenza attiva" in r.blockers[0] and r.n_deadlines == 0

    deadline(due="2027-12-31")                                   # far in the future: no threshold crossed yet
    r = check_dispatch_readiness(TODAY)
    assert not r.can_send and "nessuna ha raggiunto una soglia" in r.blockers[0] and r.n_deadlines == 1

    deadline()                                                   # now one deadline is inside its thresholds
    r = check_dispatch_readiness(TODAY)
    assert r.n_alerts == 1 and any("Nessun destinatario" in b for b in r.blockers)


@pytest.mark.offline
def test_recipients_on_unconfigured_channels_name_the_missing_settings():
    deadline()
    add_recipient("r1", "email", "a@b.it")
    r = check_dispatch_readiness(TODAY)
    assert not r.can_send and not r.email_configured
    assert any("SMTP_HOST" in b and "Secrets" in b for b in r.blockers)

    add_recipient("r2", "sms", "+393331234567")
    r = check_dispatch_readiness(TODAY)
    text = " ".join(r.blockers)
    assert "SMTP_HOST" in text and "TWILIO_ACCOUNT_SID" in text and "TWILIO_AUTH_TOKEN" in text and "TWILIO_FROM" in text


@pytest.mark.offline
def test_a_configured_channel_makes_dispatch_possible_and_the_other_one_only_a_warning(monkeypatch):
    deadline()
    add_recipient("r1", "email", "a@b.it")
    add_recipient("r2", "sms", "+393331234567")
    smtp(monkeypatch, user="u", password="p")
    r = check_dispatch_readiness(TODAY)
    assert r.can_send and r.blockers == () and r.pending == 1 and r.email_configured and not r.sms_configured
    assert any("Canale SMS non configurato" in w for w in r.warnings)
    assert not any("autenticazione" in w for w in r.warnings)


@pytest.mark.offline
def test_missing_smtp_credentials_are_a_warning_not_a_block(monkeypatch):
    deadline()
    add_recipient("r1", "email", "a@b.it")
    smtp(monkeypatch)
    r = check_dispatch_readiness(TODAY)
    assert r.can_send and any("SMTP_USER / SMTP_PASSWORD" in w for w in r.warnings)


@pytest.mark.offline
def test_everything_already_sent_is_reported_instead_of_a_silent_no_op(monkeypatch):
    deadline()
    add_recipient("r1", "email", "a@b.it")
    smtp(monkeypatch, user="u", password="p")
    log_alert_result("l1", "d1", "2026-10-15", 7, "email", "a@b.it", "sent")   # 5 days left -> threshold 7
    r = check_dispatch_readiness(TODAY)
    assert not r.can_send and r.pending == 0 and "già inviati" in r.blockers[0]


@pytest.mark.offline
def test_the_diagnosis_sends_and_writes_nothing(monkeypatch):
    deadline()
    add_recipient("r1", "email", "a@b.it")
    smtp(monkeypatch, user="u", password="p")
    sent = []
    monkeypatch.setattr(SmtpEmailNotifier, "send", lambda self, to, sub, body: sent.append(to))
    check_dispatch_readiness(TODAY)
    check_dispatch_readiness(TODAY)
    assert sent == [] and check_dispatch_readiness(TODAY).pending == 1       # still pending: nothing was logged


@pytest.mark.offline
def test_dispatch_collects_readable_errors_for_failed_sends(monkeypatch):
    deadline()
    add_recipient("r1", "email", "a@b.it")
    add_recipient("r2", "sms", "+393331234567")
    smtp(monkeypatch, user="u", password="bad")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC1")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "t")
    monkeypatch.setenv("TWILIO_FROM", "+390000000")

    def boom(self, *args, **kwargs):
        raise RuntimeError("535 Authentication failed")

    monkeypatch.setattr(SmtpEmailNotifier, "send", boom)
    monkeypatch.setattr(TwilioSmsNotifier, "send", boom)
    errors = []
    stats = dispatch_alerts(today=TODAY, dry_run=False, errors=errors)
    assert stats["failed"] == 2 and stats["sent_email"] == 0
    assert errors == ["Email a a@b.it: 535 Authentication failed", "SMS a +393331234567: 535 Authentication failed"]
    assert dispatch_alerts(today=TODAY, dry_run=True)["failed"] == 0         # `errors` stays optional
