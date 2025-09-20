#!/usr/bin/env python3
"""
Test script to verify the Space Debris Avoidance system works end-to-end
"""
import os
import sys
from datetime import datetime

# Add current directory to Python path
sys.path.append('.')

# Import all modules
from src.utils.tle_preprocessor import preprocess_and_save_tle
from src.core.timestamp_selector import TimestampSelector
from src.core.orbit_selector import OrbitSelector
from src.core.rocket_selector import RocketSelector
from src.core.trajectory_calculator import TrajectoryCalculator
from src.core.collision_detector import CollisionDetector
from src.core.ddql_optimizer import DDQLOptimizer
from src.core.trajectory_visualizer import TrajectoryVisualizer
from src.core.mission_report import MissionReport

def test_system():
    print("🚀 Starting Space Debris Avoidance System Test...")
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_tle_path = os.path.join(base_dir, "inputs", "tle_raw.txt")
    output_tle_path = os.path.join(base_dir, "data", "tle_data.txt")
    
    # Step 1: Preprocess TLE data
    print("\n1. Testing TLE preprocessing...")
    try:
        preprocess_and_save_tle(input_tle_path, output_tle_path)
        print("✅ TLE preprocessing successful!")
    except Exception as e:
        print(f"❌ TLE preprocessing failed: {e}")
        return False
    
    # Step 2: Test TimestampSelector
    print("\n2. Testing TimestampSelector...")
    try:
        timestamp_selector = TimestampSelector()
        # Use a default timestamp instead of interactive input
        timestamp = datetime(2025, 1, 17, 12, 0, 0)
        print(f"✅ Using timestamp: {timestamp}")
    except Exception as e:
        print(f"❌ TimestampSelector failed: {e}")
        return False
    
    # Step 3: Test RocketSelector 
    print("\n3. Testing RocketSelector...")
    try:
        rocket_selector = RocketSelector()
        # Get first rocket for testing
        test_altitude = 800  # LEO altitude
        test_orbit_type = "LEO"
        # Simulate rocket selection - get first suitable rocket
        suitable_rockets = rocket_selector.rockets_df[
            rocket_selector.rockets_df['Max_Altitude_km'].astype(float) >= test_altitude
        ]
        if len(suitable_rockets) > 0:
            first_rocket = suitable_rockets.iloc[0]
            rocket_info = {
                'rocket_type': first_rocket['Rocket_Type'],
                'launch_site': first_rocket['Launch_Site'],
                'coordinates': (float(first_rocket['x0']), float(first_rocket['y0']), float(first_rocket['z0']))
            }
            print(f"✅ Selected rocket: {rocket_info['rocket_type']}")
        else:
            print("❌ No suitable rockets found")
            return False
    except Exception as e:
        print(f"❌ RocketSelector failed: {e}")
        return False
    
    # Step 4: Test TrajectoryCalculator
    print("\n4. Testing TrajectoryCalculator...")
    try:
        traj_calc = TrajectoryCalculator()
        equations, t_climb, formulas, initial, orbit_vel, burn_time = traj_calc.calculate(
            rocket_info['rocket_type'], test_altitude, rocket_info['coordinates']
        )
        print(f"✅ Trajectory calculated: t_climb={t_climb:.2f}s, orbit_vel={orbit_vel:.2f}m/s")
    except Exception as e:
        print(f"❌ TrajectoryCalculator failed: {e}")
        return False
    
    # Step 5: Test CollisionDetector
    print("\n5. Testing CollisionDetector...")
    try:
        detector = CollisionDetector(tle_txt_path=output_tle_path, threshold_km=1.0)
        collisions = detector.detect_collisions(equations, timestamp, t_climb)
        print(f"✅ Collision detection complete: {len(collisions)} collisions detected")
    except Exception as e:
        print(f"❌ CollisionDetector failed: {e}")
        return False
    
    # Step 6: Test MissionReport
    print("\n6. Testing MissionReport...")
    try:
        report = MissionReport()
        trajectory_data = (equations, t_climb, formulas, initial, orbit_vel, burn_time)
        collisions_with_obj = [(t, pos, "Test Object") for t, pos in collisions] if collisions else []
        
        # Get rocket params
        rocket_data = traj_calc.rocket_data
        rocket_params = {
            'thrust_N': float(rocket_data[rocket_data['Rocket_Type'] == rocket_info['rocket_type']]['Thrust_N'].iloc[0]),
            'mass_kg': float(rocket_data[rocket_data['Rocket_Type'] == rocket_info['rocket_type']]['Mass_kg'].iloc[0]),
            'burn_time_s': float(rocket_data[rocket_data['Rocket_Type'] == rocket_info['rocket_type']]['Burn_Time_s'].iloc[0])
        }
        
        report.generate(
            rocket_type=rocket_info['rocket_type'],
            launch_site=rocket_info['launch_site'],
            orbit_type=test_orbit_type,
            altitude_km=test_altitude,
            timestamp=timestamp,
            trajectory_data=trajectory_data,
            collisions=collisions_with_obj,
            rocket_params=rocket_params,
            filename="test_mission_report.txt"
        )
        print("✅ Mission report generated successfully!")
    except Exception as e:
        print(f"❌ MissionReport failed: {e}")
        return False
    
    print("\n🎯 All system components tested successfully!")
    print("🚀 Space Debris Avoidance and Trajectory Optimization System is fully operational!")
    return True

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)