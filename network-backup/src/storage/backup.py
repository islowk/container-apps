import json
from pathlib import Path
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from src.helper.utils import safe_name


BACKUP_BASE_DIR = Path("azure_network_backups")


def backup_network_resources(credential, sub_id: str, sub_name: str, datestamp: str) -> Path:
    """Backup all networking resources for one subscription."""
    print(f"\n{'='*70}")
    print(f"Processing Subscription: {sub_name} ({sub_id})")
    print(f"{'='*70}")

    net_client = NetworkManagementClient(credential, sub_id)
    rg_client = ResourceManagementClient(credential, sub_id)

    # Use the datestamp passed from the main function for consistency
    backup_dir = BACKUP_BASE_DIR / datestamp / safe_name(sub_name)
    backup_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for rg in rg_client.resource_groups.list():
        rg_dir = backup_dir / rg.name / "network"
        rg_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n Resource Group: {rg.name}")

        resources = {
            "vnet": ("Virtual Networks", net_client.virtual_networks.list(rg.name)),
            "nsg": ("Network Security Groups", net_client.network_security_groups.list(rg.name)),
            "route_table": ("Route Tables", net_client.route_tables.list(rg.name)),
            "load_balancer": ("Load Balancers", net_client.load_balancers.list(rg.name)),
            "public_ip": ("Public IPs", net_client.public_ip_addresses.list(rg.name)),
        }

        rg_count = 0
        for rtype, (label, items) in resources.items():
            for res in items:
                file_path = rg_dir / f"{safe_name(res.name)}_{rtype}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(res.as_dict(), f, indent=2, default=str)
                print(f"{label}: {res.name}")
                rg_count += 1
                total += 1

        if rg_count == 0:
            print(f"(No network resources found)")

    print(f"\n Total resources backed up: {total}")
    print(f"Backup location: {backup_dir}")
    return backup_dir
