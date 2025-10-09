import argparse
import yaml
import os 
import socket


def get_cloud_domain(target_pve):
  with open(os.path.expanduser("~/.pve-cloud-dyn-inv.yaml"), "r") as f:
    pve_inventory = yaml.safe_load(f)

  for pve_cloud in pve_inventory:
    for pve_cluster in pve_inventory[pve_cloud]:
      if pve_cluster + "." + pve_cloud == target_pve:
        return pve_cloud
  
  raise Exception(f"Could not identify cloud domain for {target_pve}")


def get_cld_domain_prsr(args):
  print(f"export PVE_CLOUD_DOMAIN='{get_cloud_domain(args.target_pve)}'")


def get_online_pve_host(target_pve):
  with open(os.path.expanduser("~/.pve-cloud-dyn-inv.yaml"), "r") as f:
    pve_inventory = yaml.safe_load(f)

  for pve_cloud in pve_inventory:
    for pve_cluster in pve_inventory[pve_cloud]:
      if pve_cluster + "." + pve_cloud == target_pve:
        for pve_host in pve_inventory[pve_cloud][pve_cluster]:
          # check if host is available
          pve_host_ip = pve_inventory[pve_cloud][pve_cluster][pve_host]["ansible_host"]
          try:
              with socket.create_connection((pve_host_ip, 22), timeout=3):
                  return pve_host_ip
          except Exception as e:
              # debug
              print(e, type(e))
              pass
  
  raise Exception(f"Could not find online pve host for {target_pve}")


def get_online_pve_host_prsr(args):
  print(f"export PVE_ANSIBLE_HOST='{get_online_pve_host(args.target_pve)}'")

  
def main():
  parser = argparse.ArgumentParser(description="PVE Cloud utility cli. Should be called with bash eval.")

  base_parser = argparse.ArgumentParser(add_help=False)

  subparsers = parser.add_subparsers(dest="command", required=True)

  get_cld_domain_parser = subparsers.add_parser("get-cloud-domain", help="Get the cloud domain of a pve cluster.", parents=[base_parser])
  get_cld_domain_parser.add_argument("--target-pve", type=str, help="The target pve cluster to get the cloud domain of.", required=True)
  get_cld_domain_parser .set_defaults(func=get_cld_domain_prsr)

  get_online_pve_host_parser = subparsers.add_parser("get-online-host", help="Gets the ip for the first online proxmox host in the cluster.", parents=[base_parser])
  get_online_pve_host_parser.add_argument("--target-pve", type=str, help="The target pve cluster to get the first online ip of.", required=True)
  get_online_pve_host_parser.set_defaults(func=get_online_pve_host_prsr)

  args = parser.parse_args()
  args.func(args)


if __name__ == "__main__":
  main()