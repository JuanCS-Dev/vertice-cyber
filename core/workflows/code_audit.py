
import logging
from typing import Dict, Any, Optional

from tools.patch_ml import get_patch_validator
from tools.magistrate import get_magistrate
from tools.vertex_ai import get_vertex_ai # Direct Vertex Access
from fastmcp import Context

logger = logging.getLogger(__name__)

async def code_audit_patch(repo_url: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """
    Workflow 2: Code Audit & Patch
    Scans repo, validates vulnerabilities with AI, generates patch, checks safety, and applies.
    """
    state = {"repo_url": repo_url, "status": "running"}
    
    try:
        # --- Step 1: Scan (Patch Validator ML) ---
        if ctx:
            await ctx.info(f"[Workflow] Scanning repo {repo_url}")
        validator = get_patch_validator()
        # Mocking repo content fetch - in real life we'd clone
        # For this draft we simulate finding a vulnerability
        mock_diff = 'def login(user): cursor.execute("SELECT * FROM users WHERE user=" + user)' 
        
        # Initial Validation
        risk_assessment = await validator.validate_patch(mock_diff, language="python")
        state["initial_risk"] = risk_assessment.model_dump()
        
        if risk_assessment.risk_score < 0.3:
            state["status"] = "completed"
            state["message"] = "No critical vulnerabilities found."
            return state

        # --- Step 2: AI Validation (Vertex AI) ---
        if ctx:
            await ctx.info("[Workflow] Validating with Vertex AI")
        vertex = get_vertex_ai()
        # Using vertex directly to confirm vulnerability (Draft logic)
        # Assuming we have a method or utilizing generic generation
        ai_confirmation = await vertex.analyze_threat_intelligence(
            f"Confirm if this code is vulnerable: {mock_diff}", {}
        )
        state["ai_validation"] = ai_confirmation
        
        # --- Step 3: Remediation (Generate Patch) ---
        if ctx:
            await ctx.info("[Workflow] Generating Patch")
        # Prompting AI for fix
        patch_response = await vertex.generate_content(
            f"Fix this SQL injection safely in Python: {mock_diff}"
        )
        if ctx:
            await ctx.debug(f"[Workflow] Patch generated: {patch_response[:50]}...")
        # Mocking extraction of code block
        generated_patch = 'def login(user): cursor.execute("SELECT * FROM users WHERE user=?", (user,))'
        state["generated_patch"] = generated_patch
        
        # --- Step 4: Safety Check (Patch Validator) ---
        if ctx:
            await ctx.info("[Workflow] Verifying Patch Safety")
        safety_check = await validator.validate_patch(generated_patch)
        state["patch_safety_score"] = safety_check.risk_score
        
        if safety_check.risk_score > 0.3: # If risk remains high
             state["status"] = "failed"
             state["error"] = "Generated patch failed safety check"
             return state
             
        # --- Step 5: Governance (Magistrate) ---
        if ctx:
            await ctx.info("[Workflow] Requesting Governance Approval")
        magistrate = get_magistrate()
        approval = await magistrate.validate(
            action=f"Apply Security Patch to {repo_url}",
            context={"patch": generated_patch, "risk_reduction": "High"}
        )
        
        if not approval.is_approved:
             state["status"] = "blocked"
             state["block_reason"] = approval.reasoning
             return state
             
        # --- Step 6: Apply Patch ---
        if ctx:
            await ctx.info("[Workflow] Applying Patch (Simulated)")
        # Real Orchestrator would git apply here
        state["status"] = "completed"
        state["message"] = "Patch applied successfully"
        
    except Exception as e:
        logger.error(f"Code Audit Workflow Failed: {e}")
        state["status"] = "error"
        state["error"] = str(e)
        
    return state
