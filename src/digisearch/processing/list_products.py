from os import walk
import json
from digisearch.paths import RAW_DIR, PROCESSED_DIR


products = []
category = ''
catwalk = walk(RAW_DIR)
for cw in catwalk:
    dirpath = cw[0]
    splitted_dirpath = dirpath.split('/')

    if 'category' in splitted_dirpath[-1]:
        categories = cw[1]
        for cat in categories:    
            category = cat
            CAT_DIR = RAW_DIR / 'category' / category
            PRO_DIR = CAT_DIR / 'product'        
            prowalk = walk(PRO_DIR)
            for pw in prowalk:
                dirpath = pw[0]
                splitted_dirpath = dirpath.split('/')
                if 'product' in splitted_dirpath:
                    product_id = splitted_dirpath[-1]
                    SUB_PRO_DIR = PRO_DIR / str(product_id)
                    try:
                        questions_path = SUB_PRO_DIR / f'{pw[2][0]}'
                        details_path = SUB_PRO_DIR / f'{pw[2][1]}'
                        comments_path = SUB_PRO_DIR / f'{pw[2][2]}'

                        products.append({
                            product_id: {
                            'questions_path' : str(questions_path),
                            'details_path': str(details_path),
                            'comments_path': str(comments_path),
                        },
                        'category': cat,
                        })
                    except:
                        continue

with open(PROCESSED_DIR / 'product_list.json', 'w', encoding='utf-8') as file:
    json.dump(products, file,  indent=4)
