import boto3
from datetime import datetime, timedelta, UTC

class SentinelXAuditor:
    # Defining the cost table as a class attribute
    COST_TABLE = {
        't3.nano': 0.0052,
        't3.micro': 0.0104,
        't3.small': 0.0208,
        't3.medium': 0.0416,
        'default': 0.0100 
    }
    
    def __init__(self, target_regions=None):
        """
        Initialize with a specific list of regions, 
        or it will fetch all available regions by default.
        """
        self.session = boto3.Session()
        if target_regions:
            self.regions = target_regions
        else:
            # Dynamic discovery of all enabled regions
            ec2_client = self.session.client('ec2', region_name='us-east-1')
            self.regions = [r['RegionName'] for r in ec2_client.describe_regions()['Regions']]

    def scan_region(self, region):
        """Perform a deep scan for 'Ghost Resources' in a specific region."""
        print(f"🔍 [REGION: {region}] Scanning for Investment Drag...")
        
        ec2 = self.session.client('ec2', region_name=region)
        cw = self.session.client('cloudwatch', region_name=region)
        
        # 1. ORPHANED VOLUMES (Zero Utility Drag)
        volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
        orphan_vols = [v['VolumeId'] for v in volumes['Volumes']]
        
        # 2. IDLE INSTANCES (Zombie Capacity)
        instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        idle_instances = []

        for reservation in instances['Reservations']:
            for inst in reservation['Instances']:
                instance_id = inst['InstanceId']

                now = datetime.now(UTC)
                start_time = now - timedelta(hours=1)

                # Fetching CPU Metrics from CloudWatch
                stats = cw.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                    StartTime=start_time,
                    EndTime=now,
                    Period=3600,
                    Statistics=['Average']
                )
                
                if stats['Datapoints']:
                    avg_cpu = stats['Datapoints'][0]['Average']
                    if avg_cpu < 1.0: # 1% Threshold for 'Ghost' status
                        idle_instances.append({
                            'id': instance_id,
                            'cpu': f"{avg_cpu:.2f}%"
                        })
        
        return orphan_vols, idle_instances

    def run_full_audit(self):
        """Executes the audit across all selected regions and aggregates data."""
        report = {}
        print("🛡️ SENTINEL-X: GLOBAL GHOST RESOURCE AUDIT INITIATED\n")

        for region in self.regions:
            try:
                vols, idles = self.scan_region(region)
                if vols or idles:
                    report[region] = {'vols': vols, 'idles': idles}
            except Exception:
                print(f"⚠️ [REGION: {region}] Access denied or service unavailable. Skipping...")

        self.display_gauge(report)

    def display_gauge(self, report):
        print("\n" + "="*55)
        print("📈 GAUGE 1: INVESTMENT DRAG (EXECUTIVE SUMMARY)")
        print("="*55)
    
        total_drag_hourly = 0.0

        if not report:
            print("✅ SOVEREIGN ARROW: UP (No Ghost Resources Detected)")
        else:
            for region, data in report.items():
                print(f"\n📍 Region: {region}")
                
                # Reporting Orphan Volumes (EBS)
                if data['vols']:
                    for vol in data['vols']:
                        # EBS cost estimate (gp3 average is ~$0.08 per GB/month)
                        # Here we use a flat hourly fee just for the gauge logic
                        vol_drag = 0.002 
                        total_drag_hourly += vol_drag
                        print(f"  - Orphan Volume: {vol} | Drag: ${vol_drag}/hr")

                # Reporting Idle Instances
                for inst in data['idles']:
                    # Correct access using self.COST_TABLE
                    cost = self.COST_TABLE.get('t3.micro') 
                    total_drag_hourly += cost
                    print(f"  - Zombie Instance: {inst['id']} | CPU: {inst['cpu']} | Est. Drag: ${cost}/hr")

        print("\n" + "="*55)
        print(f"💰 TOTAL HOURLY INVESTMENT DRAG: ${total_drag_hourly:.4f}")
        print(f"📉 PROJECTED MONTHLY WASTED CAPITAL: ${total_drag_hourly * 720:.2f}")
        print("="*55)

# --- EXECUTION ---
if __name__ == "__main__":
    # Passing an empty list or None will trigger global scan
    auditor = SentinelXAuditor(target_regions=None) 
    auditor.run_full_audit()