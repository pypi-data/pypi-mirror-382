from typing import Union, Dict, List
import uuid, subprocess

class Job:
    def __init__(self, engine: str, slurm_params : Dict[str, Union[str, int]], modules : List[str], exec: str = '!/bin/bash', location: str = ".") -> None:
        self.engine = engine
        self.slurm_params = slurm_params
        self.exec = exec
        self.inside_idx = uuid.uuid4()
        self.location = location
        self.cmd_to_execute = []
        self.modules = modules
        self._header_lines = []

    @property
    def header(self):
        header = self.exec + "\n\n"
        
       
        for param in self.slurm_params:
            if param not in corresponding_tags[self.engine]:
                raise UnavailableTag(f'{param} is not an available tag for {self.engine} engine')
        
            header += f'#{tag_prefix[self.engine]} {corresponding_tags[self.engine][param]} {self.slurm_params[param]}\n'

        header += "\n".join(self._header_lines) + "\n"
        header += "\n"

        for module in self.modules:
            header += f'module load {module}\n'

        header += "\n"

        return header
    
    def register_cmd_line(self, cmd_line: str):
        self.cmd_to_execute.append(cmd_line)

    def launch(self):
        where = f'{self.location}/{self.inside_idx}.slurm'
        with open(where, 'w') as o:
            o.write(self.header)
            for cmd in self.cmd_to_execute:
                o.write(f'{cmd}\n')
        
        print(f'slurm script written to {where}')
        exec_cmd = f'{self.engine} {where}'
        print(f'Execute : {exec_cmd}')
        process = subprocess.run([self.engine, where], capture_output = True)
        #print(process)

    def set_job_name(self, job_name: str):
        self.slurm_params['job_name'] = job_name

    def set_stderr(self, stderr: str):
        self.slurm_params['error'] = stderr

    def set_stdout(self, stdout: str):    
        self.slurm_params['output'] = stdout

    def set_wait(self, wait:bool):
        line = f'#{tag_prefix[self.engine]} -E "--wait"'
        if wait and line not in self._header_lines:
            self._header_lines.append(line)
        if not wait and line in self._header_lines:
            self._header_lines.remove(line)
    
corresponding_tags = { 
    "ccc_msub" : {
        "nodes" : "-N", 
        "ntasks" : "-n",
        "cpus_per_task" : "-c",
        "time" : "-T",
        "partition" : "-q",
        "account" : "-A", 
        "service" : "-Q",
        "multiple" : "-W",
        "file_system" : "-m",
        "job_name" : "-r",
        "error" : "-e", 
        "output" : "-o"
    } 
    
}

tag_prefix = {
    "ccc_msub" : "MSUB"
}

class UnavailableTag(Exception):
    pass