"""
Tournament Management System - API Test Script

This script tests all the tournament management endpoints.
Run this after starting the Django server to verify everything works.
"""

import requests
import json
from datetime import date, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
TOKEN = "YOUR_TOKEN_HERE"  # Replace with your actual token from localStorage

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if response.status_code < 400:
        print("✅ Success!")
        if response.content:
            print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Error!")
        print(response.text)

def test_tournament_endpoints():
    """Test tournament management endpoints"""
    
    # 1. Create a tournament
    print("\n\n🏆 TESTING TOURNAMENT ENDPOINTS")
    print("="*60)
    
    tournament_data = {
        "name": "Y-Ultimate Championship 2025",
        "description": "Annual ultimate frisbee tournament for youth empowerment",
        "rules": "Standard WFDF rules apply. Spirit of the Game is paramount.",
        "location": "Mumbai, India",
        "start_date": str(date.today() + timedelta(days=30)),
        "end_date": str(date.today() + timedelta(days=32)),
        "registration_deadline": str(date.today() + timedelta(days=20)),
        "status": "registration_open",
        "tournament_format": "round_robin",
        "max_teams": 16,
        "min_players_per_team": 7,
        "max_players_per_team": 15,
        "sponsors": "Y-Ultimate, USAU, Local Sponsors"
    }
    
    response = requests.post(f"{BASE_URL}/tournaments/", headers=headers, json=tournament_data)
    print_response("CREATE TOURNAMENT", response)
    
    if response.status_code >= 400:
        print("\n❌ Tournament creation failed. Please check your token and try again.")
        return
    
    tournament_id = response.json()["id"]
    
    # 2. List tournaments
    response = requests.get(f"{BASE_URL}/tournaments/", headers=headers)
    print_response("LIST TOURNAMENTS", response)
    
    # 3. Get tournament details
    response = requests.get(f"{BASE_URL}/tournaments/{tournament_id}/", headers=headers)
    print_response("GET TOURNAMENT DETAILS", response)
    
    # 4. Register a team
    print("\n\n👥 TESTING TEAM ENDPOINTS")
    print("="*60)
    
    team_data = {
        "tournament": tournament_id,
        "name": "Mumbai Thunderbolts",
        "home_city": "Mumbai, Maharashtra",
        "status": "pending"
    }
    
    response = requests.post(f"{BASE_URL}/teams/", headers=headers, json=team_data)
    print_response("REGISTER TEAM", response)
    
    if response.status_code >= 400:
        print("\n❌ Team registration failed.")
        return
    
    team_id = response.json()["id"]
    
    # 5. Approve team
    response = requests.post(f"{BASE_URL}/teams/{team_id}/approve/", headers=headers)
    print_response("APPROVE TEAM", response)
    
    # 6. Register second team
    team_data2 = {
        "tournament": tournament_id,
        "name": "Delhi Dynamos",
        "home_city": "Delhi",
        "status": "pending"
    }
    
    response = requests.post(f"{BASE_URL}/teams/", headers=headers, json=team_data2)
    team_id_2 = response.json()["id"] if response.status_code < 400 else None
    
    if team_id_2:
        requests.post(f"{BASE_URL}/teams/{team_id_2}/approve/", headers=headers)
    
    # 7. Add players to team
    print("\n\n🏃 TESTING PLAYER ENDPOINTS")
    print("="*60)
    
    players_data = [
        {
            "team": team_id,
            "tournament": tournament_id,
            "full_name": "Rahul Sharma",
            "email": "rahul@example.com",
            "phone": "+91 9876543210",
            "gender": "male",
            "age": 20,
            "jersey_number": 7,
            "position": "Handler",
            "experience_level": "intermediate"
        },
        {
            "team": team_id,
            "tournament": tournament_id,
            "full_name": "Priya Patel",
            "email": "priya@example.com",
            "phone": "+91 9876543211",
            "gender": "female",
            "age": 19,
            "jersey_number": 12,
            "position": "Cutter",
            "experience_level": "intermediate"
        },
        {
            "team": team_id,
            "tournament": tournament_id,
            "full_name": "Arjun Mehta",
            "email": "arjun@example.com",
            "phone": "+91 9876543212",
            "gender": "male",
            "age": 21,
            "jersey_number": 23,
            "position": "Defense",
            "experience_level": "advanced"
        }
    ]
    
    player_ids = []
    for player_data in players_data:
        response = requests.post(f"{BASE_URL}/players/", headers=headers, json=player_data)
        if response.status_code < 400:
            player_ids.append(response.json()["id"])
    
    print_response(f"ADDED {len(player_ids)} PLAYERS", response)
    
    # 8. Create a match
    if team_id_2:
        print("\n\n⚽ TESTING MATCH ENDPOINTS")
        print("="*60)
        
        match_data = {
            "tournament": tournament_id,
            "team_a": team_id,
            "team_b": team_id_2,
            "match_date": str(date.today() + timedelta(days=30)),
            "start_time": "09:00:00",
            "round_number": 1,
            "match_number": 1,
            "status": "scheduled"
        }
        
        response = requests.post(f"{BASE_URL}/matches/", headers=headers, json=match_data)
        print_response("CREATE MATCH", response)
        
        if response.status_code < 400:
            match_id = response.json()["id"]
            
            # 9. Update match score
            score_data = {
                "team_a_score": 13,
                "team_b_score": 11
            }
            
            response = requests.post(f"{BASE_URL}/matches/{match_id}/update_score/", headers=headers, json=score_data)
            print_response("UPDATE MATCH SCORE", response)
            
            # 10. Submit spirit score
            print("\n\n⭐ TESTING SPIRIT SCORE ENDPOINTS")
            print("="*60)
            
            spirit_data = {
                "match": match_id,
                "scoring_team": team_id,
                "receiving_team": team_id_2,
                "rules_knowledge": 3,
                "fouls_and_contact": 4,
                "fair_mindedness": 3,
                "positive_attitude": 4,
                "communication": 3,
                "comments": "Excellent sportsmanship and communication throughout the game!",
                "is_submitted": True
            }
            
            response = requests.post(f"{BASE_URL}/spirit-scores/", headers=headers, json=spirit_data)
            print_response("SUBMIT SPIRIT SCORE", response)
            
            # 11. Get tournament leaderboard
            print("\n\n🏆 TESTING LEADERBOARD ENDPOINTS")
            print("="*60)
            
            response = requests.get(f"{BASE_URL}/tournaments/{tournament_id}/leaderboard/", headers=headers)
            print_response("GET TOURNAMENT LEADERBOARD", response)
            
            # 12. Get spirit rankings
            response = requests.get(f"{BASE_URL}/tournaments/{tournament_id}/spirit_rankings/", headers=headers)
            print_response("GET SPIRIT RANKINGS", response)
            
            # 13. Get tournament schedule
            response = requests.get(f"{BASE_URL}/tournaments/{tournament_id}/schedule/", headers=headers)
            print_response("GET TOURNAMENT SCHEDULE", response)
    
    print("\n\n" + "="*60)
    print("🎉 API TESTING COMPLETE!")
    print("="*60)
    print(f"\n✅ Tournament created with ID: {tournament_id}")
    print(f"✅ Team registered with ID: {team_id}")
    print(f"✅ {len(player_ids)} players added")
    if team_id_2:
        print(f"✅ Match created and scored")
        print(f"✅ Spirit score submitted")
    
    print("\n📱 Next Steps:")
    print("1. Open Django Admin: http://127.0.0.1:8000/admin/")
    print("2. View all tournament data")
    print("3. Start building frontend pages!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏆 TOURNAMENT MANAGEMENT SYSTEM - API TESTER")
    print("="*60)
    print("\n⚠️  IMPORTANT: Update the TOKEN variable with your auth token!")
    print("   Get it from browser localStorage after logging in.\n")
    
    if TOKEN == "YOUR_TOKEN_HERE":
        print("❌ Please update the TOKEN variable in this script first!")
        print("\nHow to get your token:")
        print("1. Login at http://localhost:3000/student/login")
        print("2. Open browser DevTools (F12)")
        print("3. Go to Application → localStorage")
        print("4. Copy the 'token' value")
        print("5. Paste it in this script")
    else:
        try:
            test_tournament_endpoints()
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("\nMake sure:")
            print("1. Django server is running (python manage.py runserver)")
            print("2. Your token is valid")
            print("3. You have Tournament Director permissions")
