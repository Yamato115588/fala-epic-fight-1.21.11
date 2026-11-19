"""Upgrade the pinned port's crafting and smithing ingredient encodings."""
import json
from pathlib import Path


def ingredient(value):
    if isinstance(value, list):
        return [ingredient(item) for item in value]
    if isinstance(value, dict):
        if set(value) == {'item'}:
            return value['item']
        if set(value) == {'tag'}:
            return '#' + value['tag']
        raise ValueError(f'Unknown recipe ingredient: {value}')
    return value


def migrate_recipes(source: Path):
    for path in sorted(source.glob('src/generated/resources/data/*/recipe/*.json')):
        recipe = json.loads(path.read_text())
        if recipe['type'] == 'minecraft:crafting_shaped':
            recipe['key'] = {key: ingredient(item) for key, item in recipe['key'].items()}
        elif recipe['type'] == 'minecraft:smithing_transform':
            for name in ('base', 'template', 'addition'):
                recipe[name] = ingredient(recipe[name])
        else:
            continue
        path.write_text(json.dumps(recipe, indent=2) + '\n')
