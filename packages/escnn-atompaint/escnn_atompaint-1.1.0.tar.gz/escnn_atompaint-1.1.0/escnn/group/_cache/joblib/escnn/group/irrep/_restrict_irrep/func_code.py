# first line: 233
@cache.cache
def _restrict_irrep(irrep_id: Tuple, id, group_class: str, **group_keys) -> Tuple[np.matrix, List[Tuple[Tuple, int]]]:
    
    group = escnn.group.groups_dict[group_class]._generator(**group_keys)
    
    irrep = group.irrep(*irrep_id)

    id = irrep.group._decode_subgroup_id_pickleable(id)

    subgroup, parent, child = group.subgroup(id)
    
    if subgroup.order() == 1:
        # if the subgroup is the trivial group, just return the identity cob and the list of trivial reprs
        return np.eye(irrep.size), [subgroup.trivial_representation.id]*irrep.size
    
    if subgroup.order() > 1:
        # if it is a finite group, we can sample all the element and use the precise method based on Character theory

        representation = {
            g: irrep(parent(g)) for g in subgroup.elements
        }

        # to solve the Sylvester equation and find the change of basis matrix, it is sufficient to sample
        # the generators of the subgroup
        change_of_basis, multiplicities = decompose_representation_finitegroup(
            representation,
            subgroup,
        )

    else:
        # if the group is not finite, we rely on the numerical method which is based on some samples of the group

        representation = lambda g: irrep(parent(g))

        change_of_basis, multiplicities = decompose_representation_general(
            representation,
            subgroup,
        )

    irreps = []
    
    for irr, m in multiplicities:
        irreps += [irr]*m
    
    return change_of_basis, irreps
