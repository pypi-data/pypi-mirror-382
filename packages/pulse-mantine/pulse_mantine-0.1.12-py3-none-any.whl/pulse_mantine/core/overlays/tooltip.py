from typing import Optional
import pulse as ps


@ps.react_component("Tooltip", "@mantine/core")
def Tooltip(*children: ps.Child, key: Optional[str] = None, **props): ...


@ps.react_component("Tooltip", "@mantine/core", prop="Floating")
def TooltipFloating(*children: ps.Child, key: Optional[str] = None, **props): ...


@ps.react_component("Tooltip", "@mantine/core", prop="Group")
def TooltipGroup(*children: ps.Child, key: Optional[str] = None, **props): ...

