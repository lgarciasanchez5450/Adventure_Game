import typing
import difflib

def sortBySimilarity(s:str,l:typing.Iterable[str]):
    m = difflib.SequenceMatcher(False,'',s)
    def rank(other:str):
        m.set_seq1(other)
        return m.ratio()
    return sorted(l,key=rank,reverse=True)

