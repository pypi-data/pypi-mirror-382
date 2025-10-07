from src.sputnikqa.boosters.restapi.utils.openapi_gen.parser import OpenApiParser
from pathlib import Path

EXAMPLES = Path(__file__).parent.parent.joinpath('openapi_examples')

a_internal = EXAMPLES.joinpath('adverts_internal.json')
a_public = EXAMPLES.joinpath('adverts_public.json')
atomverse = EXAMPLES.joinpath('atomverse.json')
p_internal = EXAMPLES.joinpath('payments_internal.json')
petstore = EXAMPLES.joinpath('petstore.json')

list_files = [
    a_internal,
    a_public,
    atomverse,
    p_internal,
    #petstore
]

if __name__ == '__main__':
    for f in list_files:
        parser = OpenApiParser()
        # parser.load_openapi_from_file(atomverse)
        parser.load_openapi_from_file(f)
        a = parser.parse_openapi()
        pass


    # тут файлы генерю
    # p_bodies = []
    # for f in list_files:
    #     parser = OpenApiParser()
    #     parser.load_openapi_from_file(f)
    #
    #     aaa = parser.openapi_dict
    #     for path, methods in aaa.get("paths", {}).items():
    #         for method, op in methods.items():
    #             tags = op.get("tags", ["_untagged"])
    #             for section_name in tags:
    #                 parameters = op.get('parameters')
    #                 p_bodies.append(str(parameters))
    #
    # p_bodies = list(set(p_bodies))
    # with open('parameters.txt', 'w', encoding='utf-8') as f:
    #     for r in p_bodies:
    #         f.write(r + '\n')