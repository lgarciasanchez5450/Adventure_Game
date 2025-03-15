from typing import Any, Protocol, Callable, Literal, TypeAlias,Final, Generic,TypeVar,ParamSpec, Iterable,Optional,MutableSequence, Hashable, TYPE_CHECKING
if TYPE_CHECKING:
  from pygame import Surface,Rect
  from .events import Event
  from .Input import Input


P = ParamSpec("P")
T = TypeVar("T")

BorderDirecton:TypeAlias = Literal['top','bottom','left','right']
ColorType:TypeAlias = tuple[int,int,int] | tuple[int,int,int,int]
EventHook = Callable[[],None]
EventHookAny = Callable[[],Any]
EventHookInt = Callable[[int],None]



class SupportsResize(Protocol):
  def onResize(self,size:tuple[int,int]): ...

class SupportsUpdate(Protocol):
  def update(self,input:'Input'): ...
  
class SupportsDraw(Protocol):
  order_in_layer:int
  def draw(self,surf:'Surface'): ...

class SupportsQuit(Protocol):
  def onQuit(self): ...

class HasRect(Protocol):
  @property
  def rect(self) -> 'Rect':...
  # rect:Rect
  order_in_layer:int
  def draw(self,surf:'Surface'): ...

class SelectionLike(Protocol):
  @property
  def fullHeight(self) -> int: ...
  size_change_event:'Event'
  max_y:int
  rect:'Rect'
  order_in_layer:int
  def getScrollPercent(self) -> float: ... 
  def setScrollPercent(self,percent:float): ...
  def setYScroll(self,y:int): ...
  def update(self,input:'Input'): ...
  def draw(self,surf:'Surface'): ...


class SelectionProtocol(Protocol):
  rect:'Rect'
  def setYOffset(self,y:int): ...
  def getYOffSet(self) -> int: ...
  def setToUp(self): ...
  def update(self,input:'Input'): ...
  def draw(self,surf:'Surface'): ...

class Runnable(Protocol):
  def run(self): ...
  def stop(self): ...

class WrapperObject(Protocol):
  def get(self): ...
  def set(self,value): ...

class ThumbnailURL:
  url:str
  width:int
  height:int

  @classmethod
  def new(cls,url:str,width:int,height:int) -> 'ThumbnailURL':
    out = cls()
    out.url = url
    out.width = width
    out.height = height
    return out
 
class YTVideoResult:
  title:str
  thumbnail:ThumbnailURL|Callable[[int],str]
  views:int
  duration_secs:int
  channel_name:str
  channel_url:str
  channel_thumnail:ThumbnailURL|Callable[[int],str]
  url:str

  def __repr__(self) -> str:
    return f'YTVideo[{self.__dict__.__repr__()}]'

  def __hash__(self):
    return self.url.__hash__()

class ItunesResults:
  title:str
  album:str
  artist:str
  album_thumbnail:ThumbnailURL|Callable[[int],str]
  duration_secs:int
  release_date:str
  track_count:int
  track_number:int
  explicit:bool
  genre:str
  def __repr__(self) -> str:
      return f'ItunesSong[{self.__dict__.__repr__()}]'


UIElement = TypeVar('UIElement',SupportsDraw,SupportsUpdate)