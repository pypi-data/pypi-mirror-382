from typing import Optional
import pulse as ps


@ps.react_component("VisuallyHidden", "@mantine/core")
def VisuallyHidden(*children: ps.Child, key: Optional[str] = None, **props): ...

