"""Geotab API client module."""
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import mygeotab
from mygeotab.exceptions import MyGeotabException


class GeotabClient:
    """Client for interacting with Geotab API."""

    def __init__(self, username=None, password=None, database=None, server=None):
        """Initialize the Geotab client with credentials."""
        self.username = username or os.environ.get('GEOTAB_USERNAME')
        self.password = password or os.environ.get('GEOTAB_PASSWORD')
        self.database = database or os.environ.get('GEOTAB_DATABASE')
        self.server = server or os.environ.get('GEOTAB_SERVER', 'my.geotab.com')
        self.client = None
        self.authenticated = False

    def authenticate(self) -> bool:
        """Authenticate with the Geotab API."""
        try:
            self.client = mygeotab.API(
                username=self.username,
                password=self.password,
                database=self.database,
                server=self.server
            )
            self.client.authenticate()
            self.authenticated = True
            return True
        except MyGeotabException as e:
            print(f"Authentication error: {e}")
            self.authenticated = False
            return False

    def ensure_authenticated(self) -> bool:
        """Ensure the client is authenticated."""
        if not self.authenticated or not self.client:
            return self.authenticate()
        return True

    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices in the account."""
        if not self.ensure_authenticated():
            return []
        
        try:
            devices = self.client.get('Device')
            return [
                {
                    'id': device.get('id'),
                    'name': device.get('name'),
                    'serial_number': device.get('serialNumber'),
                    'device_type': device.get('deviceType'),
                    'active': device.get('active', True)
                }
                for device in devices
            ]
        except MyGeotabException as e:
            print(f"Error retrieving devices: {e}")
            return []

    def get_device_location(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get the current location of a device."""
        if not self.ensure_authenticated():
            return None
        
        try:
            # Get the most recent device status data
            device_status_info = self.client.get(
                'DeviceStatusInfo', 
                search={
                    'deviceSearch': {'id': device_id}
                }
            )
            
            if not device_status_info:
                return None
                
            status = device_status_info[0]
            return {
                'device_id': device_id,
                'timestamp': status.get('dateTime'),
                'latitude': status.get('latitude'),
                'longitude': status.get('longitude'),
                'speed': status.get('speed'),
                'bearing': status.get('bearing'),
                'address': self._get_address_from_coordinates(
                    status.get('latitude'), 
                    status.get('longitude')
                )
            }
        except MyGeotabException as e:
            print(f"Error retrieving device location: {e}")
            return None

    def get_trip_data(self, device_id: str, from_date: Optional[datetime] = None, 
                     to_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get trip data for a specific device."""
        if not self.ensure_authenticated():
            return []
        
        # Default to last 24 hours if dates not provided
        if not from_date:
            from_date = datetime.now() - timedelta(days=1)
        if not to_date:
            to_date = datetime.now()
            
        try:
            trips = self.client.get(
                'Trip', 
                search={
                    'deviceSearch': {'id': device_id},
                    'fromDate': from_date,
                    'toDate': to_date
                }
            )
            
            return [
                {
                    'trip_id': trip.get('id'),
                    'device_id': device_id,
                    'start_time': trip.get('start'),
                    'end_time': trip.get('stop'),
                    'distance': trip.get('distance'),
                    'duration': trip.get('duration'),
                    'start_latitude': trip.get('startLatitude'),
                    'start_longitude': trip.get('startLongitude'),
                    'end_latitude': trip.get('endLatitude'),
                    'end_longitude': trip.get('endLongitude'),
                    'max_speed': trip.get('maxSpeed'),
                    'avg_speed': trip.get('averageSpeed'),
                    'idle_time': trip.get('idlingDuration')
                }
                for trip in trips
            ]
        except MyGeotabException as e:
            print(f"Error retrieving trip data: {e}")
            return []

    def get_fault_data(self, device_id: str, from_date: Optional[datetime] = None,
                      to_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get fault codes and diagnostic data for a device."""
        if not self.ensure_authenticated():
            return []
        
        # Default to last 7 days if dates not provided
        if not from_date:
            from_date = datetime.now() - timedelta(days=7)
        if not to_date:
            to_date = datetime.now()
            
        try:
            fault_data = self.client.get(
                'FaultData', 
                search={
                    'deviceSearch': {'id': device_id},
                    'fromDate': from_date,
                    'toDate': to_date
                }
            )
            
            return [
                {
                    'fault_id': fault.get('id'),
                    'device_id': device_id,
                    'diagnostic_id': fault.get('diagnostic', {}).get('id'),
                    'diagnostic_name': fault.get('diagnostic', {}).get('name'),
                    'code': fault.get('code'),
                    'source_address': fault.get('sourceAddress'),
                    'failure_mode': fault.get('failureMode'),
                    'timestamp': fault.get('dateTime'),
                    'controller': fault.get('controller', {}).get('name'),
                    'count': fault.get('count'),
                    'active': fault.get('active', False)
                }
                for fault in fault_data
            ]
        except MyGeotabException as e:
            print(f"Error retrieving fault data: {e}")
            return []

    def _get_address_from_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        """Get address from coordinates using Geotab's reverse geocoding."""
        if not self.ensure_authenticated() or not latitude or not longitude:
            return None
            
        try:
            coordinates = {
                'x': longitude,
                'y': latitude
            }
            
            address = self.client.call('GetAddressForCoordinate', coordinates)
            if address:
                return address
            return None
        except MyGeotabException as e:
            print(f"Error retrieving address: {e}")
            return None
