from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from route_app.models import Floor


def floor_plan_preview(request, pk):
    floor = get_object_or_404(Floor, pk=pk)

    base_view_width, base_view_height = 800, 600
    padding = 50

    all_x, all_y = [], []
    for loc in floor.locations.all():
        for corner in loc.corners.all():
            all_x.append(corner.x)
            all_y.append(corner.y)

    if not all_x or not all_y:
        min_x = min_y = 0
        max_x = max_y = 100
    else:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

    content_width = max_x - min_x if max_x > min_x else 1
    content_height = max_y - min_y if max_y > min_y else 1

    # Масштабируем с учётом базового окна и отступов
    scale_x = (base_view_width - 2 * padding) / content_width
    scale_y = (base_view_height - 2 * padding) / content_height
    initial_scale = min(scale_x, scale_y)

    # Размеры после масштабирования
    scaled_width = content_width * initial_scale
    scaled_height = content_height * initial_scale

    # Определяем размер view с запасом, чтобы вместить всё
    view_width = max(base_view_width, int(scaled_width + 2 * padding))
    view_height = max(base_view_height, int(scaled_height + 2 * padding))

    # Пересчёт масштаба уже для итогового окна
    scale_x = (view_width - 2 * padding) / content_width
    scale_y = (view_height - 2 * padding) / content_height
    initial_scale = min(scale_x, scale_y)

    scaled_width = content_width * initial_scale
    scaled_height = content_height * initial_scale

    # Сдвиг, чтобы план был по центру, с учётом минимальных координат (min_x, min_y)
    origin_x = (view_width - scaled_width) / 2 - min_x * initial_scale
    origin_y = (view_height - scaled_height) / 2 + min_y * initial_scale  # Обратите внимание на знак (поясню ниже)

    # Построение полигонов и подписей с поправкой координат (уже применяется масштаб и origin в SVG)
    polygons = []
    labels = []
    for location in floor.locations.all():
        corners = location.corners.all().order_by('order')
        if corners.count() < 3:
            continue

        points = " ".join(f"{c.x},{-c.y}" for c in corners)
        color = getattr(location.location_type, "color", "#cccccc") or "#cccccc"
        name = location.name

        polygons.append(f'''
            <polygon points="{points}" fill="{color}" stroke="#000000" stroke-width="1">
                <title>{name}</title>
            </polygon>
        ''')

        avg_x = sum(c.x for c in corners) / corners.count()
        avg_y = sum(c.y for c in corners) / corners.count()

        labels.append(f'''
            <text x="{avg_x}" y="{-avg_y}" font-size="12" fill="#000" text-anchor="middle" dominant-baseline="middle" pointer-events="none">
                {name}
            </text>
        ''')

    # Сетка — рисуем с шагом 50, но теперь от min_x и min_y, сдвигаем и подписываем реальные координаты
    grid_lines = []
    step = 50

    # Определим диапазоны для сетки по X и Y с запасом, округлим вниз и вверх до шагов сетки
    grid_min_x = (int(min_x) // step) * step
    grid_max_x = ((int(max_x) + step - 1) // step) * step
    grid_min_y = (int(min_y) // step) * step
    grid_max_y = ((int(max_y) + step - 1) // step) * step

    # Вертикальные линии (оси X)
    for x in range(grid_min_x, grid_max_x + step, step):
        # Координаты линии сдвинуты, масштабируется позже в <g>
        # Линия идет по SVG координате (x, от 0 до -view_height)
        # Поскольку у нас viewBox начинается с (0, -view_height), а трансформ смещает на origin
        # просто рисуем линии на координате x
        # Подписи показываем координаты x
        svg_x = x
        grid_lines.append(f'<line x1="{svg_x}" y1="0" x2="{svg_x}" y2="{-content_height}" stroke="#eee" stroke-width="1" />')
        grid_lines.append(f'<text x="{svg_x + 2}" y="12" font-size="10" fill="#999">{x}</text>')

    # Горизонтальные линии (оси Y)
    for y in range(grid_min_y, grid_max_y + step, step):
        svg_y = y
        grid_lines.append(f'<line x1="{grid_min_x}" y1="{-svg_y}" x2="{grid_max_x}" y2="{-svg_y}" stroke="#eee" stroke-width="1" />')
        grid_lines.append(f'<text x="{grid_min_x - 40}" y="{-svg_y + 4}" font-size="10" fill="#999">{y}</text>')

    # Оси
    axis_lines = f'''
        <line x1="0" y1="0" x2="{grid_max_x}" y2="0" stroke="black" stroke-width="2" marker-end="url(#arrow)" />
        <line x1="0" y1="0" x2="0" y2="{-grid_max_y}" stroke="black" stroke-width="2" marker-end="url(#arrow)" />
    '''

    svg = f'''
    <html>
    <head>
        <style>
            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f8f8f8;
            }}
            #floor-map {{
                border: 1px solid #ccc;
                background: #fff;
                cursor: grab;
            }}
        </style>
    </head>
    <body>
        <svg id="floor-map" width="{view_width}" height="{view_height}"
             xmlns="http://www.w3.org/2000/svg"
             viewBox="0 {-view_height} {view_width} {view_height}">
            <defs>
                <marker id="arrow" markerWidth="10" markerHeight="10" refX="6" refY="3"
                        orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L9,3 z" fill="#000"/>
                </marker>
            </defs>
            <g id="viewport" transform="translate({origin_x}, {origin_y}) scale({initial_scale})">
                {axis_lines}
                {''.join(grid_lines)}
                {''.join(polygons)}
                {''.join(labels)}
            </g>
        </svg>

        <script>
        (function() {{
            const svg = document.getElementById('floor-map');
            const viewport = document.getElementById('viewport');
            let scale = {initial_scale};
            let originX = {origin_x};
            let originY = {origin_y};
            let isPanning = false;
            let startX = 0;
            let startY = 0;

            function updateTransform() {{
                viewport.setAttribute('transform', `translate(${{originX}}, ${{originY}}) scale(${{scale}})`);
            }}

            svg.addEventListener('wheel', (e) => {{
                e.preventDefault();
                const rect = svg.getBoundingClientRect();
                const offsetX = e.clientX - rect.left;
                const offsetY = e.clientY - rect.top;
                const svgX = (offsetX - originX) / scale;
                const svgY = (offsetY - originY) / scale;

                const delta = e.deltaY > 0 ? 0.9 : 1.1;
                scale *= delta;
                originX = offsetX - svgX * scale;
                originY = offsetY - svgY * scale;
                updateTransform();
            }});

            svg.addEventListener('mousedown', (e) => {{
                isPanning = true;
                startX = e.clientX;
                startY = e.clientY;
                svg.style.cursor = 'grabbing';
            }});

            svg.addEventListener('mousemove', (e) => {{
                if (!isPanning) return;
                const dx = e.clientX - startX;
                const dy = e.clientY - startY;
                originX += dx;
                originY += dy;
                updateTransform();
                startX = e.clientX;
                startY = e.clientY;
            }});

            svg.addEventListener('mouseup', () => {{
                isPanning = false;
                svg.style.cursor = 'grab';
            }});
        }})();
        </script>
    </body>
    </html>
    '''

    return HttpResponse(svg)
