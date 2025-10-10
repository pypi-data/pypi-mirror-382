# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from collections import OrderedDict
from datetime import datetime


def _normalize(label):
    return label.strip().lower()




def _utc_timestamp():
    try:
        from datetime import timezone
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    except ImportError:  # pragma: no cover - Python 2 fallback
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

DEFAULT_IGNORED_LABELS = set([
    'migration',
    'custom',
    '(local run) to be merged',
    'to be merged',
    'blocked',
    'cancelled',
    'wip',
    'stale',
    'tmp patch :skull:',
    'force bypass',
    'local management',
    'rama de integración (base)',
    'rama de integración (sub)'
])


DEFAULT_LABEL_GROUPS = [
    {
        'title': 'Destacados',
        'subgroups': [
            {
                'title': 'Funciones destacadas',
                'labels': [
                    ':fire: Top feature',
                    'Top feature',
                    'feature',
                    'improvement'
                ]
            },
            {
                'title': 'Correcciones criticas e incidencias',
                'labels': [
                    'critical',
                    'High Priority',
                    'bug',
                    'bug prevention',
                    'BOE :sob:'
                ]
            },
            {
                'title': 'Calidad y pruebas',
                'labels': [
                    'Quality of Life',
                    'Performance',
                    'CI'
                ]
            }
        ]
    },
    {
        'title': 'Enfoque sectorial',
        'subgroups': [
            {'title': 'Gas', 'labels': ['Gas']},
            {'title': 'Electricidad', 'labels': ['Eléctrico']},
            {'title': 'Comercial', 'labels': ['comer', 'Comercial']},
            {'title': 'Distribucion', 'labels': ['distri']},
            {
                'title': 'Canales cliente',
                'labels': ['oficinavirtual', 'webclient', 'UX', 'CRM', 'Digitalización']
            },
            {
                'title': 'Plataformas energeticas',
                'labels': ['Bateria virtual', 'Serveis generacio (PPA)', 'Bessó Digital', 'AutoCAD']
            }
        ]
    },
    {
        'title': 'Normativa y finanzas',
        'subgroups': [
            {
                'title': 'Regulacion',
                'labels': ['Circular', 'SII', 'SICER', 'RECORE', 'Adaptación', 'CCH']
            },
            {
                'title': 'Facturacion y contabilidad',
                'labels': [
                    'factura-e',
                    'facturacio',
                    'contabilidad',
                    'rendibilitat',
                    'liquidacions',
                    'Suplemento Territorial',
                    'reports'
                ]
            },
            {
                'title': 'Contratos y ventas',
                'labels': ['contractacio', 'salesforce', 'lead', 'gestio projectes']
            }
        ]
    },
    {
        'title': 'Plataforma y datos',
        'subgroups': [
            {
                'title': 'Plataforma core',
                'labels': [
                    'backend',
                    'core',
                    'db',
                    'postgres',
                    'dependencies',
                    'devtools',
                    'scripts',
                    'Tools',
                    'os',
                    'OSCompat'
                ]
            },
            {
                'title': 'Python y runtime',
                'labels': [
                    'py3',
                    'PY3Migrate',
                    'Compatibilidad PY2'
                ]
            },
            {
                'title': 'Datos e integraciones',
                'labels': [
                    'analytics',
                    'metrics',
                    'dashboard',
                    'autotask',
                    'restapi',
                    'telemedida',
                    'telegestión',
                    'telecos',
                    'GIS',
                    'QGISCE',
                    'QGIS-Styles',
                    'meterapp',
                    'orakwlum',
                    'msgpack',
                    'e-mails'
                ]
            }
        ]
    },
    {
        'title': 'Operaciones y fiabilidad',
        'subgroups': [
            {
                'title': 'Automatizacion y procesos',
                'labels': ['crons', 'sync', 'scripts']
            },
            {
                'title': 'Monitorizacion y observabilidad',
                'labels': ['monitoring', 'sentry', 'postmortem', 'metrics']
            },
            {
                'title': 'Seguridad',
                'labels': ['seguridad']
            }
        ]
    }
]


class ChangelogBuilderV2(object):
    def __init__(self, label_groups=None, ignored_labels=None):
        self.label_groups = label_groups or DEFAULT_LABEL_GROUPS
        self.ignored_labels = set([
            _normalize(label) for label in (ignored_labels or DEFAULT_IGNORED_LABELS)
        ])
        self.prepared_groups = self._prepare_groups(self.label_groups)

    @staticmethod
    def _prepare_groups(groups):
        prepared = []
        for group in groups:
            prepared_subgroups = []
            for subgroup in group['subgroups']:
                prepared_subgroups.append({
                    'title': subgroup['title'],
                    'labels': set([_normalize(label) for label in subgroup['labels']])
                })
            prepared.append({
                'title': group['title'],
                'subgroups': prepared_subgroups
            })
        return prepared

    @staticmethod
    def _sanitize_labels(labels, ignored):
        cleaned = []
        for label in labels:
            normalized = _normalize(label)
            if normalized not in ignored:
                cleaned.append(label)
        return cleaned

    def build(self, pulls, date_since=None):
        cutoff = None
        if date_since:
            cutoff = datetime.strptime(date_since, '%Y-%m-%d')

        grouped = OrderedDict()
        for group in self.prepared_groups:
            grouped[group['title']] = OrderedDict()
            for subgroup in group['subgroups']:
                grouped[group['title']][subgroup['title']] = []

        uncategorized = []
        for pull in pulls:
            status_change_date = pull.get('status_change_date')
            if cutoff and status_change_date:
                status_dt = datetime.strptime(status_change_date, '%Y-%m-%dT%H:%M:%SZ')
                if status_dt < cutoff:
                    continue

            labels = pull.get('labels', [])
            cleaned_labels = self._sanitize_labels(labels, self.ignored_labels)
            normalized_lookup = {}
            for label in cleaned_labels:
                normalized = _normalize(label)
                normalized_lookup.setdefault(normalized, []).append(label)

            entry = {
                'title': pull.get('title'),
                'number': pull.get('number'),
                'url': pull.get('url'),
                'labels': cleaned_labels,
                'status_change_date': status_change_date,
                'merged_at': pull.get('mergedAt')
            }

            matched_any = False
            for group in self.prepared_groups:
                group_title = group['title']
                for subgroup in group['subgroups']:
                    matched_labels = []
                    for candidate in subgroup['labels']:
                        if candidate in normalized_lookup:
                            matched_labels.extend(normalized_lookup[candidate])
                    if matched_labels:
                        matched_any = True
                        grouped[group_title][subgroup['title']].append(dict(entry, matched_labels=sorted(set(matched_labels))))

            if not matched_any:
                uncategorized.append(entry)

        grouped = self._prune_empty_subgroups(grouped)
        return {
            'groups': grouped,
            'uncategorized': uncategorized,
            'generated_at': _utc_timestamp()
        }

    @staticmethod
    def _prune_empty_subgroups(grouped):
        cleaned = OrderedDict()
        for group_title, subgroup_map in grouped.items():
            populated_subgroups = OrderedDict()
            for subgroup_title, items in subgroup_map.items():
                if items:
                    populated_subgroups[subgroup_title] = items
            if populated_subgroups:
                cleaned[group_title] = populated_subgroups
        return cleaned


def format_changelog_v2(changelog_data, project_name, output_format='markdown'):
    if output_format != 'markdown':
        raise ValueError('Unsupported format: {0}'.format(output_format))

    lines = []
    header = '# Cambios {0} (v2) {1}'.format(
        project_name,
        changelog_data.get('generated_at', '')
    ).strip()
    lines.append(header)

    groups = changelog_data.get('groups', OrderedDict())
    for group_title, subgroup_map in groups.items():
        lines.append('## {0}'.format(group_title))
        for subgroup_title, items in subgroup_map.items():
            lines.append('- ### {0}'.format(subgroup_title))
            for item in items:
                focus = ''
                matched = item.get('matched_labels') or []
                if matched:
                    focus = ' _(enfoque: {0})_'.format(', '.join(matched))
                lines.append(
                    '  - {title} [#{number}]({url}){focus}'.format(
                        title=item.get('title'),
                        number=item.get('number'),
                        url=item.get('url'),
                        focus=focus
                    )
                )
                labels = item.get('labels') or []
                if labels:
                    lines.append('    - Etiquetas: {0}'.format(', '.join(labels)))

    uncategorized = changelog_data.get('uncategorized') or []
    if uncategorized:
        lines.append('## Otras actualizaciones')
        for item in uncategorized:
            lines.append(
                '- {title} [#{number}]({url})'.format(
                    title=item.get('title'),
                    number=item.get('number'),
                    url=item.get('url')
                )
            )
            labels = item.get('labels') or []
            if labels:
                lines.append('  - Etiquetas: {0}'.format(', '.join(labels)))

    return '\n'.join(lines) + '\n'
