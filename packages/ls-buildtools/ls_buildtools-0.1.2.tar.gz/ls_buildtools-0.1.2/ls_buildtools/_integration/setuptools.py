import shutil
from pathlib import Path
from ls_buildtools.protect import Protector
from ls_buildtools.protector_config import ProtectorConfig
from ls_buildtools.utilities import read_protector_config
try:
	from setuptools.command.sdist import sdist
	class ProtectionCommand(sdist):
		def make_release_tree(F,base_dir,files):
			B=base_dir;super().make_release_tree(B,files);print('Protecting files with LocalStack BuildTools protection...');B=Path(B);G=B/'setup.py';G.unlink();H:ProtectorConfig=read_protector_config(B/'..'/'ls_buildtools.toml');I=F.distribution.get_version();E=Protector();E.initialize(version=I,config=H)
			for J in B.rglob('*'):
				A=Path(J)
				if A.is_file():
					print(f"- Protecting file: {A}");C,D=E.protect_file(A,A)
					if D is not None:
						if C.absolute()!=A.absolute():A.unlink()
						if D.absolute()!=C.absolute():shutil.move(C.absolute(),D.absolute())
					else:A.unlink();C.unlink(missing_ok=True)
except ImportError:pass