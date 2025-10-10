
import torch
import torch.nn as nn

from typing import List, Optional, Set,Type

#code adapted from https://github.com/cloneofsimo/lora.git 

class LoraInjectedLinear(nn.Module):
    def __init__(
        self, in_features, out_features, bias=False, r=4, dropout_p=0.1, scale=1.0
    ):
        super().__init__()

        if r > min(in_features, out_features):
            raise ValueError(
                f"LoRA rank {r} must be less or equal than {min(in_features, out_features)}"
            )
        self.r = r
        self.linear = nn.Linear(in_features, out_features, bias)
        self.lora_down = nn.Linear(in_features, r, bias=False)
        self.dropout = nn.Dropout(dropout_p)
        self.lora_up = nn.Linear(r, out_features, bias=False)
        self.scale = scale
        self.selector = nn.Identity()

        nn.init.normal_(self.lora_down.weight, std=1 / r)
        nn.init.zeros_(self.lora_up.weight)

    def forward(self, input):
        return (
            self.linear(input)
            + self.dropout(self.lora_up(self.selector(self.lora_down(input))))
            * self.scale
        )

    def realize_as_lora(self):
        return self.lora_up.weight.data * self.scale, self.lora_down.weight.data

    def set_selector_from_diag(self, diag: torch.Tensor):
        # diag is a 1D tensor of size (r,)
        assert diag.shape == (self.r,)
        self.selector = nn.Linear(self.r, self.r, bias=False)
        self.selector.weight.data = torch.diag(diag)
        self.selector.weight.data = self.selector.weight.data.to(
            self.lora_up.weight.device
        ).to(self.lora_up.weight.dtype)


def _find_modules(
    model,
    ancestor_class: Optional[Set[str]] = None,
    search_class: List[Type[nn.Module]] = [nn.Linear],
    exclude_children_of: List[Type[nn.Module]] = [],
    layer_number: List[int] = [],
):
    found = []

    def _traverse(module, prefix="", current_layer_idx=None, parent=None):
        for name, child in module.named_children():
            full_name = f"{prefix}.{name}" if prefix else name

            if isinstance(child, nn.ModuleList):
                for idx, block in enumerate(child):
                    block_name = f"{full_name}.{idx}"
                    _traverse(block, prefix=block_name, current_layer_idx=idx, parent=module)
            else:
                if ancestor_class is None or module.__class__.__name__ in ancestor_class:
                    if any(isinstance(child, cls) for cls in search_class):
                        if not layer_number or (current_layer_idx in layer_number):
                            excluded = False
                            for excl in exclude_children_of:
                                for parent_mod in child.modules():
                                    if isinstance(parent_mod, excl):
                                        print(
                                            f"❌ Excluded: {full_name} ({type(child).__name__}) "
                                            f"— child of {excl.__name__}"
                                        )
                                        excluded = True
                                        break
                                if excluded:
                                    break
                            if not excluded:
                                # Use 'module' as parent here (the immediate parent)
                                found.append((module, name, child, current_layer_idx))

                _traverse(child, prefix=full_name, current_layer_idx=current_layer_idx, parent=module)

    _traverse(model)
    return found


def inject_trainable_lora(
    model: nn.Module,
    target_replace_module: Set[str] = None,
    r: int = 4,
    loras=None,  # path to lora .pt
    verbose: bool = False,
    dropout_p: float = 0.0,
    scale: float = 1.0,
    inject_layers: List[int] = [0],
):
    """
    inject lora into model, and returns lora parameter groups with added inject_layers list
    """

    require_grad_params = []
    names = []

    if loras != None:
        loras = torch.load(loras)
    

    for _module, name, _child_module, index in _find_modules(
        model, target_replace_module, search_class=[nn.Linear], layer_number=inject_layers,
        exclude_children_of=[LoraInjectedLinear]):


        weight = _child_module.weight
        bias = _child_module.bias                          
        if verbose:
            print("LoRA Injection : injecting lora into ", name)
            print("LoRA Injection : weight shape", weight.shape)
        
        #based on the type determine which linear model to use

        _tmp = LoraInjectedLinear(
            _child_module.in_features,
            _child_module.out_features,
            _child_module.bias is not None,
            r=r,
            dropout_p=dropout_p,
            scale=scale,
        )
        _tmp.linear.weight = weight
        if bias is not None:
            _tmp.linear.bias = bias

        # switch the module
        _tmp.to(_child_module.weight.device).to(_child_module.weight.dtype)
        _module._modules[name] = _tmp

        require_grad_params.append(_module._modules[name].lora_up.parameters())
        require_grad_params.append(_module._modules[name].lora_down.parameters())

        if loras != None:
            _module._modules[name].lora_up.weight = loras.pop(0)
            _module._modules[name].lora_down.weight = loras.pop(0)

        _module._modules[name].lora_up.weight.requires_grad = True
        _module._modules[name].lora_down.weight.requires_grad = True
        names.append(name)

    return require_grad_params, names
