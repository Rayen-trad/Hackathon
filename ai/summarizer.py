from typing import Dict

def summarize_hate_report(report: Dict) -> Dict:
    """
    Takes a hate detector report and produces a manager-friendly interpretation.
    No new analysis, only interpretation.
    """

    incident_count = report.get("incident_count", 0)
    severity = report.get("overall_severity", 0)
    hate_events = report.get("hate_events", [])

    if incident_count == 0:
        summary_text = (
            "No abusive or hateful language was detected during this conversation. "
            "The interaction appears compliant with communication standards."
        )
        risk_level = "None"
        recommendation = "No action required."

    else:
        # Who initiated abuse?
        speakers = {event["speaker"] for event in hate_events}
        initiator = (
            "customer" if "customer" in speakers and "agent" not in speakers
            else "agent" if "agent" in speakers and "customer" not in speakers
            else "both parties"
        )

        # Severity interpretation
        if severity >= 0.7:
            risk_level = "High"
            recommendation = (
                "Flag this conversation for supervisor review and consider "
                "post-incident support for the agent."
            )
        elif severity >= 0.4:
            risk_level = "Medium"
            recommendation = (
                "Monitor similar interactions and remind agents of de-escalation protocols."
            )
        else:
            risk_level = "Low"
            recommendation = "No immediate action required, log for record."

        summary_text = (
            f"The conversation contains {incident_count} abusive or insulting "
            f"incident(s), primarily initiated by the {initiator}. "
            f"The overall severity of the interaction is rated as {risk_level.lower()}."
        )

    return {
        "conversation_id": report.get("conversation_id"),
        "agent_id": report.get("agent_id"),
        "incident_count": incident_count,
        "overall_severity": severity,
        "risk_level": risk_level,
        "summary": summary_text,
        "recommendation": recommendation
    }
