# first line: 172
@cache.cache
def _find_tensor_decomposition(J: Tuple, l: Tuple, group_class: str, **group_keys) -> List[Tuple[Tuple, int]]:
    G = escnn.group.groups_dict[group_class]._generator(**group_keys)
    
    psi_J = G.irrep(*J)
    psi_l = G.irrep(*l)
    
    irreps = []
    
    size = 0
    for psi_j in G.irreps():
        CG = G._clebsh_gordan_coeff(psi_J, psi_l, psi_j)
        
        S = CG.shape[-2]
        
        if S > 0:
            irreps.append((psi_j.id, S))
        
        size += psi_j.size * S

    # check that size == psi_J.size * psi_l.size
    
    if size < psi_J.size * psi_l.size:
        from textwrap import dedent
        message = dedent(f"""
            Error! Did not find sufficient irreps to complete the decomposition of the tensor product of '{psi_J.name}' and '{psi_l.name}'.
            It is likely this happened because not sufficiently many irreps in '{G}' have been instantiated.
            Try instantiating more irreps and then repeat this call.
            The sum of the sizes of the irreps found is {size}, but the representation has size {psi_J.size * psi_l.size}.
        """)
        raise InsufficientIrrepsException(G, message)

    assert size <= psi_J.size * psi_l.size, f"""
        Error! Found too many irreps in the the decomposition of the tensor product of '{psi_J.name}' and '{psi_l.name}'.
        This should never happen!
    """

    return irreps
