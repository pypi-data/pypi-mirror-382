# first line: 52
@cache.cache
def _clebsh_gordan_tensor(J: Tuple, l: Tuple, j: Tuple, group_class: str, **group_keys) -> np.ndarray:
    
    G = escnn.group.groups_dict[group_class]._generator(**group_keys)
    
    psi_J = G.irrep(*J)
    psi_l = G.irrep(*l)
    psi_j = G.irrep(*j)
    
    D = psi_J.size * psi_l.size * psi_j.size
    
    def build_matrices(samples):
        D_Jl = []
        D_j = []
        for g in samples:
            D_J_g = psi_J(g)
            D_l_g = psi_l(g)
            D_j_g = psi_j(g)
        
            D_Jl_g = np.kron(D_J_g, D_l_g)
            
            D_j.append(D_j_g)
            D_Jl.append(D_Jl_g)
        return D_Jl, D_j
    
    try:
        generators = G.generators
        S = len(generators)
    except ValueError:
        generators = []
        # number of samples to use to approximate the solutions
        # usually 3 are sufficient
        S = 3

    _S = S
    
    while True:
        # sometimes it might not converge, so we need to try a few times
        attepts = 5
        while True:
            try:
                samples = generators + [G.sample() for _ in range(S - len(generators))]
                if len(samples) == 0:
                    basis = np.eye(D)
                else:
                    D_Jl, D_j = build_matrices(samples)
                    basis = find_intertwiner_basis_sylvester(D_Jl, D_j)
                
            except np.linalg.LinAlgError:
                if attepts > 0:
                    attepts -= 1
                    continue
                else:
                    raise
            else:
                break
                
        # check that the solutions found are also in the kernel of the constraint matrix built with other random samples
        D_Jl, D_j = build_matrices(generators + [G.sample() for _ in range(20)])
        tensor = build_sylvester_constraint(D_Jl, D_j).todense().reshape(-1, D)
        
        if np.allclose(tensor @ basis, 0.):
            break
        elif S < MAX_SAMPLES:
            # if this not the case, try again using more samples to build the constraint matrix
            S += 1
        else:
            raise UnderconstrainedCGSystem(G, psi_J.id, psi_l.id, psi_j.id, S)
    
    if S > _S:
        print(G.name, psi_J.id, psi_l.id, psi_j.id, S)

    # the dimensionality of this basis corresponds to the multiplicity of `j` in the tensor-product `J x l`
    s = basis.shape[1]
    assert s % psi_j.sum_of_squares_constituents == 0

    jJl = s // psi_j.sum_of_squares_constituents

    CG = basis.reshape((psi_j.size, psi_J.size, psi_l.size, s)).transpose(1, 2, 3, 0)
    # CG indexed as [J, l, s, j]

    if s == 0:
        return CG

    norm = np.sqrt((CG**2).mean(2, keepdims=True).sum(1, keepdims=True).sum(0, keepdims=True))
    CG /= norm
    
    ortho = np.einsum(
        'Jlsj,Jlti,kji->stk',
        CG, CG, psi_j.endomorphism_basis()
    )
    
    ortho = (ortho**2).sum(2) > 1e-9
    assert ortho.astype(np.uint).sum() == s * psi_j.sum_of_squares_constituents, (ortho, s, jJl, psi_j.sum_of_squares_constituents)

    n, dependencies = connected_components(csgraph=csr_matrix(ortho), directed=False, return_labels=True)
    assert n * psi_j.sum_of_squares_constituents == s, (ortho, n, s, psi_j.sum_of_squares_constituents)

    mask = np.zeros((ortho.shape[0]), dtype=bool)
    for i in range(n):
        columns = np.nonzero(dependencies == i)[0]
        assert len(columns) == psi_j.sum_of_squares_constituents
        selected_column = columns[0]
        mask[selected_column] = 1

    assert mask.sum() == n

    CG = CG[..., mask, :]

    assert CG.shape[-2] == jJl

    B = CG.reshape(-1, psi_j.size * jJl)
    assert np.allclose(B.T@B, np.eye(psi_j.size * jJl))
    
    return CG
