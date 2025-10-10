from pathlib import Path
from tomllib import load
from ls_buildtools.protect import Protector
from ls_buildtools.protector_config import ProtectorConfig
try:
	from setuptools.command.sdist import sdist
	class ProtectionCommand(sdist):
		def make_release_tree(F,base_dir,files):
			B=base_dir;super().make_release_tree(B,files);print('Protecting files with LocalStack BuildTools protection...');B=Path(B);G=B/'setup.py';G.unlink()
			with Path(B/'..'/'ls_buildtools.toml').open(mode='rb')as H:I:ProtectorConfig=load(H)
			J=F.distribution.get_version();E=Protector();E.initialize(version=J,config=I)
			for K in B.rglob('*'):
				A=Path(K)
				if A.is_file():
					print(f"- Protecting file: {A}");C,D=E.protect_file(A,A)
					if D is not None:
						if C.absolute()!=A.absolute():A.unlink()
						if D.absolute()!=C.absolute():C.rename(D.absolute())
					else:A.unlink();C.unlink(missing_ok=True)
except ImportError:pass