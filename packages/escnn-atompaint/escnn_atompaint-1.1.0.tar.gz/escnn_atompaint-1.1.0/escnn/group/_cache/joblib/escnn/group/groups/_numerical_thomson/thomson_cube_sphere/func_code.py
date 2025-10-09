# first line: 482
@cache.cache
def thomson_cube_sphere(N: int) -> np.ndarray:
    attempts = 20
    verbose = 0

    # to ensure a determinist behaviour of this method
    rng = np.random.RandomState(42)

    best_U = (24*N) ** 2
    best_X = None
    for i in range(attempts):
        X = _thomson_cube_sphere(N, lr=1e-1, optimizer='Adam', rng=rng, verbose=verbose - 1)
        U = _potential_sphere(X).item()

        if U < best_U:
            best_U = U
            best_X = X

    if verbose > 0:
        print(f'Best Potential: {best_U}')

    return best_X.numpy()
