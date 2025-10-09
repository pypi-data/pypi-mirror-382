# first line: 633
@cache.cache(ignore=['octa'])
def _build_octa_irrep(octa: Octahedral, l: int):
    
    if l == -1:
        
        # matrix coefficients from https://arxiv.org/pdf/1110.6376.pdf
        
        # the matrix coefficients there are expressed wrt a different set of generators
        # we fist build this set of generators
        
        r3 = octa.generators[0]
        r = r3 @ r3 @ r3
        
        k = octa.elements[0]
        s = octa.generators[1]
        t = ~s @ k @ s @ r
        
        # Representation of `t`
        rho_t = np.array([
            [1., 0., 0.],
            [0., 0., 1.],
            [0., 1., 0.],
        ])
        
        # Representation of `k`
        rho_k = np.array([
            [1., 0., 0.],
            [0., -1., 0.],
            [0., 0., -1.],
        ])
        
        # Representation of `s`
        rho_s = np.array([
            [0., 1., 0.],
            [0., 0., 1.],
            [1., 0., 0.],
        ])
        
        #  https://arxiv.org/pdf/1110.6376.pdf defines the irrep `l = 1` (denoted by 3 there) as our
        #  `standard_representation`, which is expressed on a different basis than the Wigner D matrix with l=1.
        # Since `l=-1` (their 3') is defined as the tensor product between `l=1` and `l=3` (their 1')
        # we apply the inverse change of basis used in `standard_representation` to ensure that
        # `-1 = 1 \tensor 3` for us as well
        
        change_of_basis = np.array([
            [0, 0, 1],
            [1, 0, 0],
            [0, 1, 0]
        ])
        
        rho_t = change_of_basis.T @ rho_t @ change_of_basis
        rho_k = change_of_basis.T @ rho_k @ change_of_basis
        rho_s = change_of_basis.T @ rho_s @ change_of_basis
        
        generators = [
            (t, rho_t),
            (k, rho_k),
            (s, rho_s),
        ]
        
        return generate_irrep_matrices_from_generators(octa, generators)

    elif l == 2:

        # matrix coefficients from https://arxiv.org/pdf/1110.6376.pdf

        # the matrix coefficients there are expressed wrt a different set of generators
        # we fist build this set of generators

        r3 = octa.generators[0]
        r = r3 @ r3 @ r3

        k = octa.elements[0]
        s = octa.generators[1]
        t = ~s @ k @ s @ r

        # Representation of `t`
        rho_t = np.array([
            [0., 1.],
            [1., 0.],
        ])

        # Representation of `k`
        rho_k = np.array([
            [1., 0.],
            [0., 1.],
        ])

        # Representation of `s`
        rho_s = 0.5 * np.array([
            [-1., -np.sqrt(3)],
            [np.sqrt(3), -1.],
        ])

        generators = [
            (t, rho_t),
            (k, rho_k),
            (s, rho_s),
        ]
        
        return generate_irrep_matrices_from_generators(octa, generators)

    elif l == 3:

        # matrix coefficients from https://arxiv.org/pdf/1110.6376.pdf

        # the matrix coefficients there are expressed wrt a different set of generators
        # we fist build this set of generators

        r3 = octa.generators[0]
        r = r3 @ r3 @ r3

        k = octa.elements[0]
        s = octa.generators[1]
        t = ~s @ k @ s @ r

        # Representation of `t`
        rho_t = np.array([[-1.]])

        # Representation of `k`
        rho_k = np.array([[1.]])

        # Representation of `s`
        rho_s = np.array([[1.]])

        generators = [
            (t, rho_t),
            (k, rho_k),
            (s, rho_s),
        ]

        return generate_irrep_matrices_from_generators(octa, generators)

    else:
        raise ValueError()
