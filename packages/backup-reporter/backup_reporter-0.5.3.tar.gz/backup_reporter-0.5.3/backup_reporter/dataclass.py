import json
import datetime

from dataclasses import dataclass, asdict, field


@dataclass
class BackupFileInfo:
    size: str = None
    backup_date: str = None
    backup_name: str = None
    sha1sum: str = None
    def __str__(self):
        '''String representation of that DataClass is valid json string'''
        return json.dumps(asdict(self), default=str)


@dataclass
class BackupMetadata:
    '''Class contain fields with info about backup'''
    type: str = None
    format: str = "json"
    size: str = None
    time: str = None
    customer: str = None
    placement: str = None
    backup_name: str = None
    description: str = None
    last_backup_date: str = None
    count_of_backups: str = None
    supposed_backups_count: str = None
    sha1sum: str = None
    backups: list[BackupFileInfo] = field(default_factory=list)
    
    def __str__(self):
        '''String representation of that DataClass is valid json string'''
        if self.format == "json":
            return json.dumps(asdict(self), default=str)
        elif self.format == "prom":
            return self.__get_prom_format()
        else:
            print(f"Got {self.format}, need json or prom")
    
    def __get_prom_format(self):
        prom_lines = []

        # ----- info метрика со строками -----
        labels = [f'customer="{self.customer}"']
        if self.type:
            labels.append(f'type="{self.type}"')
        if self.placement:
            labels.append(f'placement="{self.placement}"')
        if self.backup_name:
            labels.append(f'backup_name="{self.backup_name}"')
        if self.description:
            labels.append(f'description="{self.description}"')
        if self.sha1sum:
            labels.append(f'sha1sum="{self.sha1sum}"')

        prom_lines.append("# HELP backup_info Static labels about backup")
        prom_lines.append("# TYPE backup_info info")
        prom_lines.append(f'backup_info{{{",".join(labels)}}} 1')

        prom_lines.append("# HELP backup_size_mb Size of last backup in MB")
        prom_lines.append("# TYPE backup_size_mb gauge")
        prom_lines.append(f"backup_size_mb{{customer='{self.customer}'}} {float(self.size)}")
            
        prom_lines.append("# HELP backup_time Time when backup upload")
        prom_lines.append(f"backup_time{{customer='{self.customer}'}} {self.time}")

        if self.last_backup_date:
            # если строка формата ISO8601
            dt = datetime.datetime.fromisoformat(str(self.last_backup_date).replace("Z","+00:00"))
            prom_lines.append("# HELP last_backup_timestamp Unix timestamp of last backup")
            prom_lines.append("# TYPE last_backup_timestamp gauge")
            prom_lines.append(f'last_backup_timestamp{{customer="{self.customer}"}} {int(dt.timestamp())}')

        if self.count_of_backups:
            prom_lines.append("# HELP backup_count Number of backups found")
            prom_lines.append("# TYPE backup_count gauge")
            prom_lines.append(f'backup_count{{customer="{self.customer}"}} {int(self.count_of_backups)}')

        if self.supposed_backups_count:
            prom_lines.append("# HELP supposed_backups_count Expected number of backups")
            prom_lines.append("# TYPE supposed_backups_count gauge")
            prom_lines.append(f'supposed_backups_count{{customer="{self.customer}"}} {int(self.supposed_backups_count)}')

        return "\n".join(prom_lines) + "\n"
    