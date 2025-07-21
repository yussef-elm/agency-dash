"""
Utility functions for data processing and formatting
"""
import unicodedata
import re
from config import BENCHMARKS, COLORS

def strip_accents(s=""):
    """Remove accents from string"""
    return re.sub(r'[\u0300-\u036f]', '', unicodedata.normalize('NFD', s))

def norm(s):
    """Normalize string for comparison"""
    return strip_accents(s).lower().strip()

def canonical(name):
    """Convert stage name to canonical form"""
    n = norm(name)

    # Exclude Database Reactivation explicitly
    if 'database reactivation' in n:
        return 'excluded'

    if 'annule' in n or 'réponse négative' in n:
        return 'annule'
    if 'pas venu' in n or 'pas venus' in n:
        return 'pas_venu'
    if 'concretise' in n or 'concrétisé' in n:
        return 'concretise'
    if 'present' in n or 'présenté cabinet' in n:
        return 'present'
    if 'non confirme' in n or 'message envoye' in n or 'message envoyé' in n:
        return 'non_confirme'
    if 'rdv confirme' in n or 'rendez-vous confirme' in n or 'réponse positive' in n or 'reponse positive (rvd confirme)' in n:
        return 'confirme'
    if 'sans reponse' in n or 'sans réponse' in n or 'without answer' in n or 'voice mail' in n:
        return 'sans_reponse'

    # Additional mappings if needed
    if 'unqualified' in n:
        return 'non_qualifie'
    if 'double' in n:
        return 'double'
    if 'fausse manipulation' in n:
        return 'erreur'
    if 'plus interesse' in n:
        return 'plus_interesse'

    return n

def get_metric_color(value, metric_type):
    """Get color based on benchmark performance"""
    if metric_type not in BENCHMARKS:
        return COLORS['NEUTRAL']

    benchmark = BENCHMARKS[metric_type]
    colors = benchmark['colors']

    # Handle percentage values (remove % and convert to float)
    if isinstance(value, str):
        if '%' in value:
            try:
                value = float(value.replace('%', ''))
            except ValueError:
                return COLORS['NEUTRAL']
        elif ',' in value:
            # Handle comma-separated numbers like "1,234"
            try:
                value = float(value.replace(',', ''))
                # For volume metrics, use neutral color
                return COLORS['NEUTRAL']
            except ValueError:
                return COLORS['NEUTRAL']
        else:
            try:
                value = float(value)
            except ValueError:
                return COLORS['NEUTRAL']

    # For reverse metrics (lower is better)
    if benchmark.get('reverse', False):
        if value < benchmark['excellent']:
            return colors[0]  # Green
        elif value < benchmark['good']:
            return colors[1]  # Yellow
        else:
            return colors[2]  # Red
    else:
        # For normal metrics (higher is better)
        if value >= benchmark['excellent']:
            return colors[0]  # Green
        elif value >= benchmark['good']:
            return colors[1]  # Yellow
        else:
            return colors[2]  # Red

def get_color_class(value, metric_type):
    """Get CSS class based on metric performance"""
    color = get_metric_color(value, metric_type)
    if color == COLORS['GREEN']:
        return 'cell-green'
    elif color == COLORS['YELLOW']:
        return 'cell-yellow'
    elif color == COLORS['RED']:
        return 'cell-red'
    else:
        return 'cell-neutral'

def create_metric_card(title, value, metric_type, delta=None):
    """Create a colored metric card based on performance"""
    color = get_metric_color(value, metric_type)

    if color == COLORS['GREEN']:
        color_class = 'metric-green'
    elif color == COLORS['YELLOW']:
        color_class = 'metric-yellow'
    elif color == COLORS['RED']:
        color_class = 'metric-red'
    else:
        color_class = 'metric-neutral'

    delta_html = f"<small style='color: {color};'>Δ {delta}</small>" if delta else ""

    return f"""
    <div class="metric-card {color_class}">
        <h4 style="margin: 0; color: #333;">{title}</h4>
        <h2 style="margin: 0; color: {color};">{value}</h2>
        {delta_html}
    </div>
    """

def pct(v, d):
    """Calculate percentage"""
    return (v/d)*100 if d else 0

def pct_str(v, d):
    """Calculate percentage as string"""
    return f"{(v/d)*100:.1f}%" if d else "0%"

EXCLUDED_STAGE_CANON = canonical('Database Reactivation')