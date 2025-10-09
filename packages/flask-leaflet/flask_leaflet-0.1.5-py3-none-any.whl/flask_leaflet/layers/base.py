from typing import Any, Optional, Protocol, Self, Union

from markupsafe import Markup

from ..mixins import Renderable, RendersArgsMixin, RendersVarNameMixin


class HasLayers(Protocol):
    layers: list[Union["Layer", "LayerGroup"]]

    @property
    def var_name(self) -> str: ...


class Layer(Renderable, RendersArgsMixin, RendersVarNameMixin):
    __not_render_options__ = ["id", "owner", "var_name"]

    attribution: Optional[str] = None
    pane: str = "overlayPane"
    owner: Optional[HasLayers] = None

    def __init__(
        self,
        attribution: Optional[str] = None,
        pane: str = "overlayPane",
        owner: Optional[HasLayers] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.attribution = attribution
        self.pane = pane
        self.owner = owner

    def __factory_str__(self) -> str:
        class_name = self.__class__.__name__
        return class_name[0].lower() + class_name[1:]

    def add_to(self, owner: HasLayers) -> Self:
        owner.layers.append(self)
        self.owner = owner
        return self

    def remove(self) -> Self:
        if self.owner:
            self.owner.layers.remove(self)
            self.owner = None
        return self

    def __render_html__(self, as_variable: bool = False) -> Markup:
        print(self)
        string = f"L.{self.__factory_str__()}({self.render_args()}{self.render_options()})"
        if self.owner:
            string += f".addTo({self.owner.var_name})"
        if as_variable:
            string = f"var {self.var_name} = {string};"
        return Markup(string)


class InteractiveLayer(Layer):
    interactive: bool = True
    bubbling_mouse_events: bool = True

    def __init__(self, interactive: bool = True, bubbling_mouse_events: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.interactive = interactive
        self.bubbling_mouse_events = bubbling_mouse_events


class LayerGroup(InteractiveLayer):
    __render_args__ = ["layers"]
    __not_render_options__ = InteractiveLayer.__not_render_options__ + __render_args__

    layers: list[Layer]

    def __init__(self, layers: Optional[list[Layer]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.layers = layers or []

    def add_layer(self, layer: Layer) -> Self:
        self.layers.append(layer)
        return self
