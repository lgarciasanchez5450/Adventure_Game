from typing import Callable,Callable,ParamSpec,TypeVar
__all__ = [
	'njit',
	'prange',
	'cache',
	'literal_unroll'
]


try:
	from numba import njit,prange,literal_unroll
except ImportError:
	print('Numba module not found, this can affect performance greatly.')
	def njit (*args,**kwargs):
		def wrapper(func):
			return func
		return wrapper
	prange = range
	def literal_unroll(container): 
		return container

P = ParamSpec("P")
T = TypeVar("T")



def cache(func:Callable[P,T]) -> Callable[P,T]:
	inputs:dict[tuple,T] = {}
	def wrapper(*args: P.args,**kwargs:P.kwargs) -> T:
		if kwargs: raise ValueError("Functions that are being cached to no support key word arguments")
		if args not in inputs:
			inputs[tuple(args)] = func(*args,**kwargs)
		return inputs[tuple(args)]
	wrapper.__name__ = func.__name__
	wrapper.__annotations__ = func.__annotations__
	wrapper.__doc__ = func.__doc__
	return wrapper
