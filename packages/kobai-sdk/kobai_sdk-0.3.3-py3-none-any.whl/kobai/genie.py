
def get_genie_descriptions(solution_id, structure, schema):
    for di, dom in enumerate(structure["domains"]):
        structure["domains"][di]["label"] = dom["name"]

    add_episteme_metadata(structure)
    download_inherited_props(structure)
    add_map_count(structure)
    add_semantic_sentences(structure)
    add_schema_sentences(structure, schema, solution_id)

    #add map count

    return structure

#def get_genie_questions(solution_id, structure):

#    graph_uri = structure["uri"]

#    question_config = get_tenant_question_config(solution_id, structure)

#    questions = []
#    for q in question_config:
#        q_name = q["description"]
#        q_def = json.loads(q["definition"])

#        if q["published"]:
#            result = get_question_sql(q_def, graph_uri)
#            if result is not None:
#                questions.append({"name": q_name, "sql": result})

#    return questions

############################
# Config Building
############################

def add_episteme_metadata(structure):
    for dom in structure["domains"]:
        dom["e_id"] = dom["label"]
        for con in dom["concepts"]:
            con["e_id"] = dom["label"] + "_" + con["label"]
            
            for prop in con["properties"]:
                prop["e_id"] = dom["label"] + "_" + con["label"] + "_" + prop["label"]

            for rel in con["relations"]:
                rel["e_id"] = dom["label"] + "_" + con["label"] + "_" + rel["label"]
                rel["e_target_id"] = rel["relationTypeUri"].split("/")[-1].replace("#", "_")

def download_inherited_props(structure):
    for dom in structure["domains"]:
        if "concepts" in dom:
            for con in dom["concepts"]:
                recurse_parent_props(con["uri"], structure, con["properties"], con["relations"], visited=[])

def recurse_parent_props(uri, structure, props, rels, visited=None):
    visited.append(uri)
    for dom in structure["domains"]:
        for con in dom["concepts"]:
            if con["uri"] == uri:
                for icon in con["inheritedConcepts"]:
                    for pdom in structure["domains"]:
                        for pcon in pdom["concepts"]:
                            if pcon["uri"] == icon:
                                for pprop in pcon["properties"]:
                                    prop_found = False
                                    for pf in props:
                                        if pf["uri"] == pprop["uri"]:
                                            prop_found = True
                                    if not prop_found:
                                        props.append(pprop)
                                for prel in pcon["relations"]:
                                    rel_found = False
                                    for rf in rels:
                                        if rf["uri"] == prel["uri"]:
                                            rel_found = True
                                    if not rel_found:
                                        rels.append(prel)
                    if icon not in visited:
                        recurse_parent_props(icon, structure, props, rels, visited)

def add_map_count(structure):

    for dom in structure["domains"]:
        for con in dom["concepts"]:
            map_count = 0
            #for md in mapping_defs:
            for md in structure["mappingDefs"]:
                if con["uri"] == md["conceptTypeUri"]:
                    map_count = map_count + 1
            con["map_count"] = map_count

############################
# Question Config
############################

def get_tenant_question_config(solution_id, structure):

    question_defs = []
    for row in structure["queries"]:
        print(row)
        is_published = False
        if row[4] is not None and row[4] != "":
            is_published = True
        question_def = {"question_id": row[1], "description": row[2], "definition": row[3], "published": is_published}
        question_defs.append(question_def)
    return question_defs

############################
# Sentences
############################

def add_semantic_sentences(structure):
    for dom in structure["domains"]:
        concept_list = []

        for con in dom["concepts"]:
            concept_sentence = ""
            property_list = []
            relation_list = []
            concept_list.append(con["label"])

            for prop in con["properties"]:
                property_list.append(prop["label"])
                property_sentence = "The " + prop["label"] + " for the " + dom["label"] + " " + con["label"] + "."
                prop["sementic_sentence"] = property_sentence

            for rel in con["relations"]:
                relation_list.append(rel["label"])

            concept_sentence = "The " + con["label"] + " concept contains details about " + smart_comma_formatting(property_list) + "."
            con["semantic_sentence"] = concept_sentence

        domain_sentence = "The " + dom["label"] + " domain contains concepts called " + smart_comma_formatting(concept_list) + "."
        dom["semantic_sentence"] = domain_sentence

def add_schema_sentences(structure, schema, tenant_id):
    for dom in structure["domains"]:

        for con in dom["concepts"]:
            neighbours_list = []
            concept_sentence = "The " + schema + ".data_" + tenant_id + "_" + dom["label"] + "_" + con["label"] + "_w table contains information about " + dom["label"] + " " + con["label"] + "s. "
            concept_sentence += "This refers to a class " + con["label"] + " in a domain of similar classes called " + dom["label"] + ". "
            concept_sentence += "It includes details such as "
            property_list = []

            if len(con["properties"]) > 0:
                for prop in con["properties"]:
                    property_list.append(prop["label"])
                    property_sentence = "The " + prop["label"] + " for the " + dom["label"] + " " + con["label"] + "."
                    prop["schema_sentence"] = property_sentence
                concept_sentence += smart_comma_formatting(property_list) + ". "

            if len(con["relations"]) > 0:
                for rel in con["relations"]:
                    rel_dom = rel["relationTypeUri"].split("/")[-1].split("#")[0]
                    rel_con = rel["relationTypeUri"].split("/")[-1].split("#")[1]
                    rel_table = schema + ".data_" + tenant_id + "_" + rel_dom + "_" + rel_con + "_w"
                    relation_sentence = "A relationship called " + rel["label"] + " connecting " + dom["label"] + " " + con["label"] + "s to " + rel_dom + " " + rel_con + "s. "
                    relation_sentence += "A key connecting this table to the unique identifier of the " + rel_table + " table. "
                    rel["schema_sentence"] = relation_sentence
                    neighbours_list.append(rel_dom + " " + rel_con)
                    #structure["domains"][idom]["concepts"][icon]["relations"][irel].pop("target", None)
            if len(neighbours_list) > 0:
                concept_sentence += "For context, it is connected to neighbor classes like " + smart_comma_formatting(neighbours_list)

            con["schema_sentence"] = concept_sentence
            con["schema_id_sentence"] = "The unique identifier for each " + dom["label"] + " " + con["label"] + ". "
            con["schema_table"] = schema + ".data_" + tenant_id + "_" + dom["label"] + "_" + con["label"] + "_np"

def smart_comma_formatting(items):
    if items is None:
        return ""
    match len(items):
        case 0:
            return ""
        case 1:
            return items[0]
        case 2:
            return items[0] + " and " + items[1]
        case _:
            return ", ".join(items[0: -1]) + " and " + items[-1]
        
def label_from_url(inpt):
    try:
        return inpt.split("#")[1].replace("_", " ")
    except IndexError:
        return inpt
    
############################
# Mapping
############################

