_D='Patch'
_C=False
_B=True
_A=None
import os,shutil
from pathlib import Path
import re,functools,inspect,types
from collections.abc import Callable
from tempfile import mkdtemp,tempdir
from typing import Any,Tuple
from python_minifier import minify
from.import Protection
from..protector_config import ObfuscationConfig
from ls_buildtools.utilities import load_file,save_file
class Obfuscation(Protection):
	def __init__(A,config:ObfuscationConfig|_A=_A):
		A.config=config or ObfuscationConfig(custom_patches=_C,remove_annotations=_B,remove_literal_statements=_B);A.exclude=[re.compile(A)for A in A.config.get('exclude_regexes',[])];A.minified_directory=Path(mkdtemp(dir=tempdir))
		if A.config['custom_patches']:A._apply_python_minifier_patches()
	def should_protect(A,source_path:Path,distribution_path:Path)->bool:
		B=source_path
		if os.environ.get('LS_SKIP_OBFUSCATION','0')=='1':print(f"--- ! OBFUSCATION HAS EXPLICITLY BEEN DISABLED: {distribution_path} is NOT being obfuscated! ! ---");return _C
		if A.exclude and any(A.search(str(B))for A in A.exclude):return _C
		if B.suffix!='.py':return _C
		return _B
	def protect_file(A,source_path:Path,distribution_path:Path)->Tuple[Path,Path]:C=distribution_path;B=Path(A.minified_directory)/C;B.parent.mkdir(parents=_B,exist_ok=_B);D=A.config['remove_annotations'];E=A.config['remove_literal_statements'];F=minify(load_file(source_path),remove_annotations=D,remove_literal_statements=E);save_file(B,F);return B,C
	def finalize(A):shutil.rmtree(A.minified_directory)
	def _apply_python_minifier_patches(D)->_A:
		import ast as A;from python_minifier.ast_annotation import get_parent as C;from python_minifier.transforms.remove_annotations import RemoveAnnotations as B
		if not hasattr(B.visit_AnnAssign,'_ls_patched'):
			def F(node:A.AST):
				D=node
				if not isinstance(C(D),A.ClassDef):return _C
				if len(C(D).bases)==0:return _C
				E=['NamedTuple','TypedDict','BaseModel']
				for B in C(D).bases:
					if isinstance(B,A.Name)and B.id in E:return _B
					elif isinstance(B,A.Attribute)and B.attr in E:return _B
				return _C
			@patch(B.visit_AnnAssign)
			def E(fn,self,node):
				E='annotation';B=node
				if F(B):return B
				if isinstance(B,A.AnnAssign):
					D=getattr(B,E,_A);C=fn(self,B);G=getattr(C,E,_A)
					if isinstance(G,A.Constant)and isinstance(D,A.Subscript|A.Name|A.BinOp):C.annotation=D
					return C
				return fn(self,B)
			B.visit_AnnAssign._ls_patched=_B
def get_defining_object(method:Callable)->type[Any]|Any:
	A=method
	if inspect.ismethod(A):return A.__self__
	if inspect.isfunction(A):
		C=A.__qualname__.split('.<locals>',1)[0].rsplit('.',1)[0]
		try:B=getattr(inspect.getmodule(A),C)
		except AttributeError:B=A.__globals__.get(C)
		if isinstance(B,type):return B
	return inspect.getmodule(A)
def create_patch_proxy(target:Callable,new:Callable)->Callable:
	A=target
	@functools.wraps(A)
	def B(*B,**D):
		if C:B=B[1:]
		return new(A,*B,**D)
	C=inspect.ismethod(A)
	if C:B=types.MethodType(B,A.__self__)
	return B
class Patch:
	obj:Any;name:str;new:Any;old:Any;is_applied:bool
	def __init__(A,obj:Any,name:str,new:Any)->_A:super().__init__();A.obj=obj;A.name=name;A.old=getattr(A.obj,name);A.new=new;A.is_applied=_C
	def apply(A)->_A:setattr(A.obj,A.name,A.new);A.is_applied=_B
	def undo(A)->_A:setattr(A.obj,A.name,A.old);A.is_applied=_C
	def __enter__(A)->_D:A.apply();return A
	def __exit__(A,exc_type:type|_A,exc_val:BaseException|_A,exc_tb:Any|_A)->_D:A.undo();return A
	@staticmethod
	def function(target:Callable,fn:Callable,pass_target:bool=_B)->_D:
		C=target;A=fn;B=get_defining_object(C);D=C.__name__;F=not inspect.isclass(B)and not inspect.ismodule(B)
		if F:A.__name__=D;A=types.MethodType(A,B)
		if pass_target:E=create_patch_proxy(C,A)
		else:E=A
		return Patch(B,D,E)
def patch(target:Callable,pass_target:bool=_B)->Callable[[Callable],Callable]:
	def A(fn:Callable)->Callable:fn.patch=Patch.function(target,fn,pass_target=pass_target);fn.patch.apply();return fn
	return A