from .handler import Handler, handlers
from .renderer import renderers

import fnmatch
import shutil
import jinja2

import json
from pathlib import Path
from typing import Any


PATH_PROPERTY = 'path'
SOURCE_PROPERTY = 'source'
BODY_PROPERTY = 'body'
RENDERER_PROPERTY = 'renderer'
TEMPLATE_PROPERTY = 'template'
OUTPUT_PROPERTY = 'output'


def process_dir(input_dir: Path, output_dir: Path, templates_path: Path = Path('templates')):
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))
    process_dir_helper(input_dir, input_dir, output_dir, template_env)


def process_dir_helper(root_dir: Path, input_dir: Path, output_dir: Path,
                       template_env: jinja2.Environment) -> dict[Path, dict[str, Any]]:
    dirs = []
    files = []

    for p in input_dir.iterdir():
        r = p.relative_to(input_dir)
        if p.is_dir():
            dirs.append(r)
        else:
            files.append(r)

    file_metadata: dict[Path, dict[str, Any]] = {}

    for d in sorted(dirs):
        new_files_metadata = process_dir_helper(root_dir, input_dir / d, output_dir / d, template_env)
        file_metadata.update(new_files_metadata)

    for f in sorted(files):
        new_file_metadata = process_file(root_dir, input_dir, output_dir, f, file_metadata, template_env)
        path = (input_dir / f).relative_to(root_dir)
        file_metadata[path] = new_file_metadata

    return file_metadata


def glob(files: dict[Path, dict[str, Any]], pattern: str) -> list[dict[str, Any]]:
    matching_files = []
    for path in sorted(files.keys()):
        if fnmatch.fnmatch(str(path), pattern):
            matching_files.append(files[path])
    return matching_files


def process_file(root_dir: Path, input_dir: Path, output_dir: Path, source_path: Path,
                 file_metadata, template_env: jinja2.Environment) -> dict[str, Any]:
    print(f'processing {input_dir / source_path}')

    handler = get_handler(source_path)

    if handler is None:
        output_path = output_dir / source_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(input_dir / source_path, output_dir / source_path)
        return {}

    metadata, source = parse_file(input_dir / source_path)
    metadata[PATH_PROPERTY] = (input_dir / source_path).relative_to(root_dir)
    metadata[SOURCE_PROPERTY] = source

    renderer = handler.renderer
    if RENDERER_PROPERTY in metadata:
        renderer = metadata[RENDERER_PROPERTY]

    body = renderers[renderer](source) if renderer else source
    metadata[BODY_PROPERTY] = body

    template_name = handler.template
    if TEMPLATE_PROPERTY in metadata:
        template_name = metadata[TEMPLATE_PROPERTY]

    template = template_env.get_template(template_name + '.jinja') if template_name else None
    output = template.render(metadata, glob=lambda p: glob(file_metadata, p)) if template else body

    output_path = output_dir / (source_path.with_suffix(handler.suffix) if handler.suffix else source_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(output)

    return metadata


def parse_file(source_path: Path) -> tuple[dict[str, Any], str]:
    with open(source_path, 'r', encoding='utf-8') as f:
        source = f.read()

    parameters, idx = json.JSONDecoder().raw_decode(source)
    source = source[idx:].lstrip('\n')

    return parameters, source


def get_handler(source_path: Path) -> Handler | None:
    for handler in reversed(handlers):
        if handler.detect(source_path):
            return handler

    return None
