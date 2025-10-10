from pathlib import Path
from typing import Any
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl
from..protect import Protector
from..protector_config import ProtectorConfig
from..utilities import read_protector_config
@hookimpl
def hatch_register_build_hook():return HatchlingProtectionHook
class HatchlingProtectionHook(BuildHookInterface):
	PLUGIN_NAME='ls_buildtools'
	def __init__(A,*B:Any,**C:Any)->None:super().__init__(*B,**C);A.builder_config=A.build_config;A.builder=A.builder_config.builder;A.protector=Protector();A.rename={}
	def initialize(A,version:str,build_data:dict[str,Any])->None:
		A.app.display_info('Protecting files with LocalStack BuildTools protection...');D:ProtectorConfig=read_protector_config(Path(A.builder_config.root)/'ls_buildtools.toml');print(D);A.protector.initialize(version,D)
		for B in A.builder.recurse_included_files():
			if not B.distribution_path:continue
			E=Path(B.path);C=Path(B.distribution_path);A.app.display_info(f"- Protecting file: {E}");G,F=A.protector.protect_file(E,C);build_data['force_include'][G]=F
			if C!=F:A.builder.build_config['exclude'].append(f"**/{str(C)}")
			del A.builder_config.exclude_spec
	def finalize(A,version:str,build_data:dict[str,Any],artifact_path:str)->None:A.protector.finalize()