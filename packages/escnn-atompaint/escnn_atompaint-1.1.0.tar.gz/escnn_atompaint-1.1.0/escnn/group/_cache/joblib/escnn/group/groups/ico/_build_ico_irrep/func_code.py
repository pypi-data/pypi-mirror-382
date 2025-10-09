# first line: 671
@cache.cache(ignore=['ico'])
def _build_ico_irrep(ico: Icosahedral, l: int):
    
    if l == 3:
        
        # Representation of the generator of the cyclic subgroup of order 5
        rho_p = np.zeros((3, 3))
        
        rho_p[0, 0] = rho_p[1, 1] = np.cos(144 / 180. * np.pi)
        rho_p[1, 0] = np.sin(144 / 180. * np.pi)
        rho_p[0, 1] = -np.sin(144 / 180. * np.pi)
        rho_p[2, 2] = 1.
        
        # Representation of the generator of the cyclic subgroup of order 2
        rho_q = np.zeros((3, 3))
        rho_q[0, 0] = 1. / np.sqrt(5)
        rho_q[0, 2] = - 2. / np.sqrt(5)
        rho_q[1, 1] = - 1
        rho_q[2, 0] = - 2. / np.sqrt(5)
        rho_q[2, 2] = - 1. / np.sqrt(5)
        
        generators = [
            (ico._generators[0], rho_p),
            (ico._generators[1], rho_q),
        ]
        
        return generate_irrep_matrices_from_generators(ico, generators)

    elif l == 4:

        # Representation of the generator of the cyclic subgroup of order 5
        rho_p = np.zeros((4, 4))

        rho_p[0, 0] = rho_p[1, 1] = np.cos(72 / 180. * np.pi)
        rho_p[1, 0] = np.sin(72 / 180. * np.pi)
        rho_p[0, 1] = -np.sin(72 / 180. * np.pi)

        rho_p[2, 2] = rho_p[3, 3] = np.cos(144 / 180. * np.pi)
        rho_p[3, 2] = np.sin(144 / 180. * np.pi)
        rho_p[2, 3] = -np.sin(144 / 180. * np.pi)

        # Representation of the generator of the cyclic subgroup of order 2
        rho_q = np.zeros((4, 4))
        rho_q[0, 2] = -1
        rho_q[1, 1] = 2. / np.sqrt(5)
        rho_q[1, 3] = 1. / np.sqrt(5)
        rho_q[2, 0] = -1
        rho_q[3, 1] = 1. / np.sqrt(5)
        rho_q[3, 3] = -2. / np.sqrt(5)

        generators = [
            (ico._generators[0], rho_p),
            (ico._generators[1], rho_q),
        ]

        return generate_irrep_matrices_from_generators(ico, generators)
    else:
        raise ValueError()
