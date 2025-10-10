import subprocess
import os

class NSYSInterface():

    def __init__(self, types, filter_nvtx, range_nvtx, force_sqlite):
        self.use_path = True
        self.nsys_binary = ("nsys",)
        
        if 'NSYS_HOME' in os.environ:
            self.NSYS_HOME = os.path.abspath(os.getenv('NSYS_HOME'))
            self.use_path = False
        
        if self.use_path:
            self.nsys_binary = ("nsys",)
        else:
            self.nsys_binary = (os.path.join(self.NSYS_HOME, "bin/nsys"),)

        self.types  = types
        self.filter = filter_nvtx
        self.range_nvtx = range_nvtx
        self.force = force_sqlite

    def check_export_report(self, rf):
        if not os.path.exists(self.sqlite_cwd_file(rf)) or self.force:
            #Try exporting first
            export_call = self.nsys_binary + ("export", "-t", "sqlite", "--force-overwrite=true", "--include-json=true", rf)
            try:
                with subprocess.Popen(export_call, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
                    for line in p.stdout:
                        print(line.decode(), end='')
                
                if p.returncode != 0:
                    raise ChildProcessError(p.returncode, p.args)        
            except FileNotFoundError:
                print("You don't have an Nsight Systems installation in your PATH. Please install, Nsight Systems, or locate your installation using PATH or setting NSYS_HOME environment variable.")
                exit(1)
            except ChildProcessError:
                print("Could not export SQLite database. Exiting.")
                exit(1)

    def call_stats(self, report):
        nsys_call = self.nsys_binary + ("stats", "-r", ",".join(self.types), 
            "--timeunit", "nsec", "-f", "csv", 
            "-o", self.build_nsys_stats_basename(report))
        if self.filter:
            nsys_call += ("--filter-nvtx="+self.range_nvtx,)

        nsys_call += (self.sqlite_cwd_file(report),)

        try:
            with subprocess.Popen(nsys_call, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
                for line in p.stdout:
                    print(line.decode(), end='')

            if p.returncode != 0:
                raise ChildProcessError(p.returncode, p.args)
        except FileNotFoundError:
            print("You don't have an Nsight Systems installation in your PATH. Please install, Nsight Systems, or locate your installation using PATH or setting NSYS_HOME environment variable.")
            exit(1)

    def build_nsys_stats_basename(self, rf):
        return f"{os.path.join(os.getcwd(), os.path.splitext(os.path.basename(rf))[0])}"

    def build_nsys_stats_name(self, rf, rd, report_name):
        base_name = self.build_nsys_stats_basename(rf)
        if self.filter:
            return os.path.join(rd, base_name+"_{}_nvtx={}.csv".format(report_name, self.range_nvtx))
        else:
            return os.path.join(rd, base_name+"_{}.csv".format(report_name))
        
    def sqlite_cwd_file(self, rf):
        return f"{os.path.join(os.getcwd(), os.path.splitext(os.path.basename(rf))[0])}.sqlite"