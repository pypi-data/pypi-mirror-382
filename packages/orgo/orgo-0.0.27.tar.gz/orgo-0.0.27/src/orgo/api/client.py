"""API client for Orgo service"""

import requests
from typing import Dict, Any, Optional, List

from orgo.utils.auth import get_api_key

class ApiClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = get_api_key(api_key)
        self.base_url = base_url or "https://www.orgo.ai/api"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data)
            else:
                response = self.session.request(method, url, json=data)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                error_message = f"API error: {e.response.status_code}"
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_message += f" - {error_data['error']}"
                except ValueError:
                    pass
                raise Exception(error_message) from e
            raise Exception(f"Connection error: {str(e)}") from e
    
    # Project methods
    def create_project(self, name: str) -> Dict[str, Any]:
        """Create a new named project"""
        return self._request("POST", "projects", {"name": name})
    
    def get_project_by_name(self, name: str) -> Dict[str, Any]:
        """Get project details by name"""
        return self._request("GET", f"projects/by-name/{name}")
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details by ID"""
        return self._request("GET", f"projects/{project_id}")
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        response = self._request("GET", "projects")
        return response.get("projects", [])
    
    def start_project(self, project_id: str) -> Dict[str, Any]:
        """Start a project"""
        return self._request("POST", f"projects/{project_id}/start")
    
    def stop_project(self, project_id: str) -> Dict[str, Any]:
        """Stop a project"""
        return self._request("POST", f"projects/{project_id}/stop")
    
    def restart_project(self, project_id: str) -> Dict[str, Any]:
        """Restart a project"""
        return self._request("POST", f"projects/{project_id}/restart")
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project and all its computers"""
        return self._request("POST", f"projects/{project_id}/delete")
    
    # Computer methods
    def create_computer(self, project_name: str, computer_name: str, 
                       os: str = "linux", ram: int = 2, cpu: int = 2, 
                       gpu: str = "none") -> Dict[str, Any]:
        """Create a new computer within a project"""
        return self._request("POST", f"projects/{project_name}/computers", {
            "name": computer_name,
            "os": os,
            "ram": ram,
            "cpu": cpu,
            "gpu": gpu
        })
    
    def list_computers(self, project_name: str) -> List[Dict[str, Any]]:
        """List all computers in a project"""
        response = self._request("GET", f"projects/{project_name}/computers")
        return response.get("computers", [])
    
    def get_computer(self, computer_id: str) -> Dict[str, Any]:
        """Get computer details"""
        return self._request("GET", f"computers/{computer_id}")
    
    def delete_computer(self, computer_id: str) -> Dict[str, Any]:
        """Delete a computer"""
        return self._request("DELETE", f"computers/{computer_id}")
    
    def start_computer(self, computer_id: str) -> Dict[str, Any]:
        """Start a computer"""
        return self._request("POST", f"computers/{computer_id}/start")
    
    def stop_computer(self, computer_id: str) -> Dict[str, Any]:
        """Stop a computer"""
        return self._request("POST", f"computers/{computer_id}/stop")
    
    def restart_computer(self, computer_id: str) -> Dict[str, Any]:
        """Restart a computer"""
        return self._request("POST", f"computers/{computer_id}/restart")
    
    # Computer control methods
    def left_click(self, computer_id: str, x: int, y: int) -> Dict[str, Any]:
        return self._request("POST", f"computers/{computer_id}/click", {
            "button": "left", "x": x, "y": y
        })
    
    def right_click(self, computer_id: str, x: int, y: int) -> Dict[str, Any]:
        return self._request("POST", f"computers/{computer_id}/click", {
            "button": "right", "x": x, "y": y
        })
    
    def double_click(self, computer_id: str, x: int, y: int) -> Dict[str, Any]:
        return self._request("POST", f"computers/{computer_id}/click", {
            "button": "left", "x": x, "y": y, "double": True
        })
    
    def drag(self, computer_id: str, start_x: int, start_y: int, 
             end_x: int, end_y: int, button: str = "left", 
             duration: float = 0.5) -> Dict[str, Any]:
        """Perform a drag operation from start to end coordinates"""
        return self._request("POST", f"computers/{computer_id}/drag", {
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "button": button,
            "duration": duration
        })
    
    def scroll(self, computer_id: str, direction: str, amount: int = 3) -> Dict[str, Any]:
        return self._request("POST", f"computers/{computer_id}/scroll", {
            "direction": direction, "amount": amount
        })
    
    def type_text(self, computer_id: str, text: str) -> Dict[str, Any]:
        return self._request("POST", f"computers/{computer_id}/type", {
            "text": text
        })
    
    def key_press(self, computer_id: str, key: str) -> Dict[str, Any]:
        return self._request("POST", f"computers/{computer_id}/key", {
            "key": key
        })
    
    def get_screenshot(self, computer_id: str) -> Dict[str, Any]:
        return self._request("GET", f"computers/{computer_id}/screenshot")
    
    def execute_bash(self, computer_id: str, command: str) -> Dict[str, Any]:
        return self._request("POST", f"computers/{computer_id}/bash", {
            "command": command
        })
    
    def execute_python(self, computer_id: str, code: str, timeout: int = 10) -> Dict[str, Any]:
        """Execute Python code on the computer"""
        return self._request("POST", f"computers/{computer_id}/exec", {
            "code": code,
            "timeout": timeout
        })
    
    def wait(self, computer_id: str, duration: float) -> Dict[str, Any]:
        return self._request("POST", f"computers/{computer_id}/wait", {
            "duration": duration
        })
    
    # Streaming methods
    def start_stream(self, computer_id: str, connection_name: str) -> Dict[str, Any]:
        """Start streaming to a configured RTMP connection"""
        return self._request("POST", f"computers/{computer_id}/stream/start", {
            "connection_name": connection_name
        })
    
    def stop_stream(self, computer_id: str) -> Dict[str, Any]:
        """Stop the active stream"""
        return self._request("POST", f"computers/{computer_id}/stream/stop")
    
    def get_stream_status(self, computer_id: str) -> Dict[str, Any]:
        """Get current stream status"""
        return self._request("GET", f"computers/{computer_id}/stream/status")