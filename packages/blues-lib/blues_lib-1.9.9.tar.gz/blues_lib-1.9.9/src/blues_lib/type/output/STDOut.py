from dataclasses import dataclass, asdict

@dataclass
class STDOut:
  code: int = 200
  message: str = 'success'
  data: any = None
  detail: any = None

  def to_dict(self)->dict:
    return asdict(self)

  def to_status(self)->tuple:
    return (self.code,self.message)