def mock_lead_capture(name, email, platform):
    """
    Mock API to simulate lead capture.
    In production, this would POST to a CRM like HubSpot or Salesforce.
    """
    print(f"\n[LEAD CAPTURED]")
    print(f"  Name:     {name}")
    print(f"  Email:    {email}")
    print(f"  Platform: {platform}")
    print(f"[END LEAD]\n")
    return {
        "success": True,
        "message": f"Lead captured: {name} ({email}) on {platform}"
    }
