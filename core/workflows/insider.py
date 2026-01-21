
import logging
import re
from typing import Dict, Any, Optional

from tools.osint import get_osint_hunter
from tools.magistrate import get_magistrate
from tools.threat import get_threat_prophet
from fastmcp import Context

logger = logging.getLogger(__name__)

async def insider_threat_hunter(employee_email: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """
    Workflow 3: Insider Threat Hunter
    Investigates anomaly behavior with Privacy-First approach (PII Masking).
    """
    state = {"target": employee_email, "status": "running"}
    
    try:
        # --- Step 1: Breach Check (OSINT) ---
        if ctx:
            await ctx.info(f"[Workflow] Checking Breaches for {employee_email}")
        hunter = get_osint_hunter()
        breaches = await hunter.check_breach(employee_email)
        state["breach_count"] = len(breaches)
        
        # --- Step 2: Privacy Shield (Magistrate) ---
        if ctx:
            await ctx.info("[Workflow] Requesting Privacy Access")
        magistrate = get_magistrate()
        approval = await magistrate.validate(
            action="Access Internal Logs for Behavior Analysis",
            context={"target": employee_email, "has_pii": True}
        )
        
        if not approval.is_approved:
            state["status"] = "blocked"
            state["block_reason"] = "Privacy Check Failed"
            return state
            
        # PII Masking Logic (Internal helper)
        def mask_pii(text: str) -> str:
            # Mask emails (basic regex)
            text = re.sub(r'[\w\.-]+@[\w\.-]+', '[MASKED_EMAIL]', text)
            # Mask IPs
            text = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[MASKED_IP]', text)
            return text
            
        # Simulating Log Retrieval & Masking
        raw_logs = f"User {employee_email} logged in from 192.168.1.5 at 3AM"
        masked_logs = mask_pii(raw_logs)
        state["masked_data_sample"] = masked_logs
        
        # --- Step 3: Behavior Analysis (Threat Prophet) ---
        # Note: ThreatProphet usually analyzes external threats. 
        # We adapt it here to analyze the 'risk' of the user based on breach data + anomaly context.
        prophet = get_threat_prophet()
        # We use analyzing the email as a 'target' to get risk score derived from breaches/indicators
        analysis = await prophet.analyze_threats(target=employee_email)
        
        # Mocking behavioral anomaly score addition since ThreatProphet doesn't natively do behavioral log analysis yet
        behavioral_score = 0.0
        if state["breach_count"] > 5:
             behavioral_score += 40
        
        final_risk = analysis.overall_risk_score + behavioral_score
        state["anomaly_score"] = min(final_risk, 100.0)
        
        if final_risk > 50:
            if ctx:
                await ctx.warning(f"[Workflow] High Insider Risk Detected: {final_risk}")
        
        state["status"] = "completed"
    
    except Exception as e:
        logger.error(f"Insider Threat Workflow Failed: {e}")
        state["status"] = "error"
        state["error"] = str(e)
        
    return state
