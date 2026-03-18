# main.py - The Sovereign Hub
from gauges.investment_drag import DragAuditor
from gauges.technology_yield import YieldAuditor
from utils.formatter import ExecutiveDisplay

def calculate_sovereign_direction(current_score, previous_score):
    """
    Analyzes the trend between two time periods.
    This is what moves the leader from inaction to resolution.
    """
    if current_score < previous_score:
        return "⬇️ FRICTION (Action Required)"
    return "⬆️ EFFICIENCY (Maintain Velocity)"

def run_sentinel_strategy():
    display = ExecutiveDisplay()
    display.print_header()

    # 1. Collect Gauge Data
    drag_score = DragAuditor().get_score()   # Gauge 1
    yield_score = YieldAuditor().get_score() # Gauge 2
    
    # 2. Convergence Logic (The Sovereign Formula)
    # Efficiency is Yield minus Drag. Simple. Brutal. Honest.
    sovereign_index = yield_score - drag_score
    
    # 3. Trend Analysis (Simulating a 7-day lookback)
    last_week_index = 0.85 # Mock data for now
    direction = calculate_sovereign_direction(sovereign_index, last_week_index)
    
    display.render_arrow(sovereign_index, direction)

if __name__ == "__main__":
    run_sentinel_strategy()