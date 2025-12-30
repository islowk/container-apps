import re, os
from azure.mgmt.resource import SubscriptionClient

def safe_name(name: str) -> str:
    """Sanitize names for safe folder/file paths."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", name.strip())

def get_subscriptions(credential, target_sub: str | None = None):
    response = SubscriptionClient(credential)
    all_subs = list(response.subscriptions.list())

    if target_sub == "all" or target_sub == None:
      return all_subs

    for sub in all_subs:
        if target_sub.lower() in (sub.subscription_id.lower(), sub.display_name.lower()):
            return [sub]

    raise ValueError(
        f"Subscription '{target_sub}' not found. Available: {[s.display_name for s in all_subs]}"
    )

