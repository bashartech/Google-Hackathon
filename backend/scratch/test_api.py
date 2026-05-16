
import requests
import json

def test_api():
    url = "http://localhost:8001/api/service-request"
    data = {
        "message": "Hi, I need AC repair in G-13. My number is 0300-1112223.",
        "session_id": "test_session"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if "workflow_steps" in result:
            print(f"Workflow steps found: {len(result['workflow_steps'])}")
        else:
            print("Workflow steps MISSING from response!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
