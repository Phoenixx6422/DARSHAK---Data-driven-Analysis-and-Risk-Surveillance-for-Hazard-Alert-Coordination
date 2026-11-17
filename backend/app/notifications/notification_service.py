"""
PDEWS Automated Notification Gateway
Architectural Role: Member 2 (Himanshu Shukla) - Database and Monitoring
Master Context Rule: Automated dispatch on High / Critical risk with ZERO authority approval.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PDEWS-NotificationGateway")

class NotificationService:
    def __init__(self):
        self.dispatched_history: List[Dict[str, Any]] = []

    def evaluate_and_dispatch(
        self,
        region_name: str,
        risk_level: str,
        safety_score: float,
        advisory: str,
        recipients: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates risk level and triggers automated emergency notifications.
        - High / Critical: Dispatches automated multi-channel emergency alerts.
        - Low / Moderate: Logs advisory only, suppresses emergency sirens/broadcasts.
        """
        normalized_risk = risk_level.strip().title()
        is_emergency = normalized_risk in ["High", "Critical"]

        if recipients is None:
            # Default recipient pool (e.g. registered citizens in target region)
            recipients = [
                {"name": "Himanshu Shukla", "phone": "+91-9876543210", "email": "cs25b1017@iiitraichur.ac.in"},
                {"name": "Emergency Response Hub", "phone": "+91-9123456789", "email": "emergency@iiitraichur.ac.in"}
            ]

        dispatches = []
        if is_emergency:
            for rec in recipients:
                sms_payload = {
                    "channel": "SMS",
                    "recipient": rec["phone"],
                    "recipient_name": rec["name"],
                    "risk_level": normalized_risk,
                    "region": region_name,
                    "safety_score": safety_score,
                    "message": f"EMERGENCY WARNING [{normalized_risk}]: High disaster threat detected in {region_name}. SafetyScore: {safety_score}. {advisory}",
                    "authority_approval_required": False,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "DELIVERED"
                }
                email_payload = {
                    "channel": "EMAIL",
                    "recipient": rec["email"],
                    "recipient_name": rec["name"],
                    "risk_level": normalized_risk,
                    "region": region_name,
                    "safety_score": safety_score,
                    "subject": f"PDEWS Urgent Warning - {normalized_risk} Disaster Alert for {region_name}",
                    "message": f"Automated Alert: Immediate safety measures advised for {region_name}.\nDetails: {advisory}",
                    "authority_approval_required": False,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "DELIVERED"
                }
                dispatches.extend([sms_payload, email_payload])
                self.dispatched_history.extend([sms_payload, email_payload])

            logger.warning(
                f"[AUTOMATED ALERT DISPATCHED] Region: {region_name} | Level: {normalized_risk} | "
                f"Recipients: {len(recipients)} | Authority Approval: BYPASSED (Automated)"
            )
        else:
            logger.info(
                f"[ADVISORY LOGGED] Region: {region_name} | Level: {normalized_risk} | No emergency sirens dispatched."
            )

        return {
            "region_name": region_name,
            "risk_level": normalized_risk,
            "safety_score": safety_score,
            "emergency_triggered": is_emergency,
            "dispatches_count": len(dispatches),
            "dispatches": dispatches,
            "authority_intervention": False
        }

    def get_history(self) -> List[Dict[str, Any]]:
        return self.dispatched_history

notification_service = NotificationService()
