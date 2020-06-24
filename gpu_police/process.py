import os
import pwd
import attr


@attr.s(auto_attribs=True, frozen=True)
class Process:
    gpu: int = attr.ib(converter=int)
    pid: int = attr.ib(converter=int)
    type: int = attr.ib(eq=False)
    sm: int = attr.ib(converter=int, eq=False)
    mem: int = attr.ib(converter=int, eq=False)
    enc: int = attr.ib(repr=False, eq=False)
    dec: int = attr.ib(repr=False, eq=False)
    fb: int = attr.ib(converter=int, eq=False)
    command: str
    user: str = attr.ib(init=False)
        
    def __attrs_post_init__(self):
        object.__setattr__(self, "user", self._user_from_pid(self.pid))
    
    @classmethod
    def from_str(cls, s):
        return cls(*s.split())
    
    def kill(self):
        os.system(f"kill -9 {self.pid}")
        
    @property
    def is_special(self):
        return (self.user is None) or self.command.startswith('X') or self.command.startswith('gnome-shell')

    @property
    def is_active(self):
        return (self.sm + self.mem) > 0    
    
    @property
    def memory_consumption(self):
        return self.fb
        
    @staticmethod
    def _user_from_pid(pid):
        uid = int(open(f"/proc/{pid}/loginuid").read().strip())
        try:
            return pwd.getpwuid(uid).pw_name
        except:
            return None