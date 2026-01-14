def patch_source(app, docname, source):
    import os
    from pathlib import Path

    on_rtd = os.environ.get('READTHEDOCS') == 'True'
    if not on_rtd:
        print('not on RTD')
        return

    # Path(app.srcdir)) points to ../docs/
    auto_example_dir = Path(app.srcdir) / 'auto_examples'
    image_dir = Path(app.srcdir) / '_static' / 'auto_examples' / 'images'

    if docname.startswith("auto_examples/index"):
        # thumbnails
        

        content = source[0]
        lines = content.split('\n')

        for i, line in enumerate(lines):
            lines[i] = line.replace('/auto_examples/images/thumb/', 
                                '/_static/auto_examples/images/thumb/')

        source[0] = '\n'.join(lines)

    elif docname.startswith("auto_examples/plot_"):
        # example images

        # Find corresponding images
        dir_name, script_name = docname.split('/')
        images = sorted(image_dir.glob(f'*{script_name}_*.png'))

        if not images:
            print(f'No image found')
            return

        # Insert image directives after the main header
        image_rst = []
        for i, img in enumerate(images, 1):
            rel_path = f'/_static/auto_examples/images/{img.name}'
            image_rst.append(f"""

 .. image:: {rel_path}
   :alt: {script_name}
   :class: sphx-glr-single-img

""")

        # Insert after the first header/description
        content = source[0]
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '.. GENERATED FROM PYTHON' in line:
                insert_pos = i - 1
                break

        lines.insert(insert_pos, '\n'.join(image_rst))
        
        source[0] = '\n'.join(lines)

    else:
        pass

def setup(app):
    app.connect("source-read", patch_source)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
