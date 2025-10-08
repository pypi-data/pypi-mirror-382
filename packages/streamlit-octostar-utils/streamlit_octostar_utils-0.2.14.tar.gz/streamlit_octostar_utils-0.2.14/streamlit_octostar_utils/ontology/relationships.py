from .inheritance import is_child_concept


def get_relationships_between_concepts(source, target, ontology):
    ontology_rels = {k["relationship_name"]: k for k in ontology["relationships"]}
    from_rels = ontology["concepts"][source]["relationships"]
    from_rels = [ontology_rels[r] for r in from_rels]
    from_rels = [
        r
        for r in from_rels
        if is_child_concept(
            target,
            r["target_concept"],
            {
                "concepts": ontology["concepts"],
                "relationships": list(ontology_rels.values()),
            },
        )
    ]
    return from_rels


def invert_relationships(rels, ontology):
    ontology_rels = {k["relationship_name"]: k for k in ontology["relationships"]}
    inverses = []
    for rel in rels:
        inverses.append(ontology_rels[rel]["inverse_name"])
    return inverses
