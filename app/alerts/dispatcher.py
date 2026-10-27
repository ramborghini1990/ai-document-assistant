"""Dispatcher: aggregates pending alerts per recipient into a single digest and logs results."""
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import date
from app.config import ALERT_MAX_OVERDUE_DAYS
from app.alerts.store import (
    get_active_deadlines,
    get_active_recipients,
    is_alert_already_sent,
    log_alert_result
)
from app.alerts.scanner import scan_deadlines, Alert
from app.alerts.notifiers import SmtpEmailNotifier, TwilioSmsNotifier


@dataclass(frozen=True)
class DispatchReadiness:
    """Why a real dispatch would (not) send anything, in plain Italian. `blockers` empty <=> `can_send`."""
    can_send: bool
    blockers: Tuple[str, ...]
    warnings: Tuple[str, ...]
    n_deadlines: int
    n_alerts: int            # deadlines that crossed a threshold (or are recently overdue)
    n_email: int
    n_sms: int
    email_configured: bool
    sms_configured: bool
    pending: int             # (alert, recipient) pairs not sent yet on a configured channel


def check_dispatch_readiness(today: Optional[date] = None) -> DispatchReadiness:
    """
    Dry diagnosis of `dispatch_alerts(dry_run=False)`: no message is sent and nothing is written. Every reason that makes a
    dispatch a silent no-op is reported, so the UI can explain it instead of just disabling the button.
    """
    deadlines = get_active_deadlines()
    alerts = scan_deadlines(deadlines, today=today)
    rec_email = get_active_recipients(channel="email")
    rec_sms = get_active_recipients(channel="sms")
    email, sms = SmtpEmailNotifier(), TwilioSmsNotifier()

    blockers: List[str] = []
    warnings: List[str] = []
    if not deadlines:
        blockers.append("Nessuna scadenza attiva nel registro: esegui l'analisi dei documenti o usa "
                        "«Sincronizza scadenze dai record».")
    elif not alerts:
        blockers.append(f"Ci sono {len(deadlines)} scadenze attive, ma nessuna ha raggiunto una soglia di avviso o è scaduta "
                        f"da meno di {ALERT_MAX_OVERDUE_DAYS} giorni: oggi non c'è nulla da inviare.")

    def channel_problem(name: str, recipients: list, client) -> Optional[str]:
        if not recipients or client.configured:
            return None
        return (f"Canale {name} non configurato: {len(recipients)} destinatari non raggiungibili. "
                f"Imposta {', '.join(client.missing_settings())} nel file .env (o nei Secrets di Streamlit Cloud) "
                f"e riavvia l'applicazione.")

    problems = [p for p in (channel_problem("email", rec_email, email), channel_problem("SMS", rec_sms, sms)) if p]
    usable_email = rec_email if email.configured else []
    usable_sms = rec_sms if sms.configured else []
    pending = 0
    if not (rec_email or rec_sms):
        blockers.append("Nessun destinatario attivo: aggiungine almeno uno nella sezione «Destinatari».")
    elif not (usable_email or usable_sms):
        blockers.extend(problems)
    else:
        warnings.extend(problems)                                   # the other channel can still go out
        for a in alerts:
            pending += sum(1 for r in usable_email
                           if not is_alert_already_sent(a.deadline_id, a.due_date, a.threshold, "email", r["address"]))
            pending += sum(1 for r in usable_sms
                           if not is_alert_already_sent(a.deadline_id, a.due_date, a.threshold, "sms", r["address"]))
        if alerts and not pending:
            blockers.append("Tutti gli avvisi in soglia risultano già inviati a tutti i destinatari raggiungibili: "
                            "nessun nuovo invio necessario.")
    if usable_email and not email.has_credentials:
        warnings.append("SMTP_USER / SMTP_PASSWORD non impostati: l'invio email avverrà senza autenticazione "
                        "(molti provider, es. Gmail, la richiedono).")

    return DispatchReadiness(
        can_send=not blockers, blockers=tuple(blockers), warnings=tuple(warnings), n_deadlines=len(deadlines),
        n_alerts=len(alerts), n_email=len(rec_email), n_sms=len(rec_sms), email_configured=email.configured,
        sms_configured=sms.configured, pending=pending,
    )


def build_email_digest(alerts: List[Alert]) -> str:
    lines = [
        "AVVISO SCADENZE E CONFORMITÀ NORMATIVA",
        "=====================================",
        f"Totale scadenze in evidenza: {len(alerts)}\n"
    ]
    for a in alerts:
        if a.days_left < 0:
            status_txt = f"SCADUTO DA {-a.days_left} GIORNI"
        elif a.days_left == 0:
            status_txt = "SCADE OGGI!"
        else:
            status_txt = f"Scade tra {a.days_left} giorni"

        lines.append(f"• [{status_txt}] {a.description}")
        lines.append(f"  Data Scadenza: {a.due_date} | Fonte: {a.source} | Modulo: {a.module_id}\n")

    lines.append("Verificare gli adempimenti sulla piattaforma Document Intelligence.")
    return "\n".join(lines)


def dispatch_alerts(
    today: Optional[date] = None,
    dry_run: bool = False,
    errors: Optional[List[str]] = None,
) -> Dict[str, int]:
    """
    اجرای کامل فرآیند اسکن و توزیع هشدارها.
    خروجی: دیکشنری تعداد هشدارهای ارسال‌شده، شبیه‌سازی‌شده و رد شده.
    `errors` (optional list) receives one readable line per failed send, so a caller can show WHY something failed.
    """
    deadlines = get_active_deadlines()
    alerts = scan_deadlines(deadlines, today=today)

    recipients_email = get_active_recipients(channel="email")
    recipients_sms = get_active_recipients(channel="sms")

    email_client = SmtpEmailNotifier()
    sms_client = TwilioSmsNotifier()

    # اضافه شدن کلید simulated
    stats = {"sent_email": 0, "sent_sms": 0, "skipped": 0, "failed": 0, "simulated": 0}

    # ۱. پردازش ایمیل‌ها
    for rec in recipients_email:
        addr = rec["address"]
        pending_alerts = [
            a for a in alerts 
            if not is_alert_already_sent(a.deadline_id, a.due_date, a.threshold, "email", addr)
        ]

        if not pending_alerts:
            stats["skipped"] += len(alerts)
            continue

        subject = f"⚠️ Notifica Scadenze ({len(pending_alerts)} adempimenti in scadenza)"
        body = build_email_digest(pending_alerts)

        if dry_run:
            print(f"[DRY-RUN EMAIL to {addr}]\n{subject}\n{body}\n")
            stats["sent_email"] += len(pending_alerts)
            continue

        # اگر تنظیمات SMTP کانفیگ نشده باشد، فقط در آمار شبیه‌سازی حساب می‌شود و لاگ 'sent' ثبت نمی‌شود
        if not email_client.configured:
            stats["simulated"] += len(pending_alerts)
            continue

        try:
            email_client.send(addr, subject, body)
            for a in pending_alerts:
                log_alert_result(str(uuid.uuid4()), a.deadline_id, a.due_date, a.threshold, "email", addr, "sent")
            stats["sent_email"] += len(pending_alerts)
        except Exception as e:
            for a in pending_alerts:
                log_alert_result(str(uuid.uuid4()), a.deadline_id, a.due_date, a.threshold, "email", addr, "failed", str(e))
            stats["failed"] += len(pending_alerts)
            if errors is not None:
                errors.append(f"Email a {addr}: {e}")

    # ۲. پردازش پیامک‌ها
    for rec in recipients_sms:
        addr = rec["address"]
        for a in alerts:
            if is_alert_already_sent(a.deadline_id, a.due_date, a.threshold, "sms", addr):
                continue

            msg_txt = f"Avviso: {a.description} scade il {a.due_date} ({a.days_left} gg rimasti)."
            if dry_run:
                print(f"[DRY-RUN SMS to {addr}]: {msg_txt}")
                stats["sent_sms"] += 1
                continue

            # اگر تنظیمات توئیلیو کانفیگ نشده باشد، لاگ 'sent' ثبت نمی‌شود
            if not sms_client.configured:
                stats["simulated"] += 1
                continue

            try:
                sms_client.send(addr, "ALLERTA SCADENZA", msg_txt)
                log_alert_result(str(uuid.uuid4()), a.deadline_id, a.due_date, a.threshold, "sms", addr, "sent")
                stats["sent_sms"] += 1
            except Exception as e:
                log_alert_result(str(uuid.uuid4()), a.deadline_id, a.due_date, a.threshold, "sms", addr, "failed", str(e))
                stats["failed"] += 1
                if errors is not None:
                    errors.append(f"SMS a {addr}: {e}")

    return stats