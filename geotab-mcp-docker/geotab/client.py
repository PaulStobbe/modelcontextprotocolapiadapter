"""
Geotab API client for interfacing with MyGeotab APIs.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

import mygeotab
from mygeotab.api import API
from mygeotab.exceptions import MyGeotabException

logger = logging.getLogger("geotab.client")

class GeotabClient:
    """Client for interacting with Geotab API."""
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        server: Optional[str] = None
    ):
        """
        Initialize Geotab client with credentials.
        
        Args:
            username: MyGeotab username (default: from env var GEOTAB_USERNAME)
            password: MyGeotab password (default: from env var GEOTAB_PASSWORD)
            database: MyGeotab database (default: from env var GEOTAB_DATABASE)
            server: MyGeotab server (default: from env var GEOTAB_SERVER or "my.geotab.com")
        """
        self.username = username or os.environ.get("GEOTAB_USERNAME")
        self.password = password or os.environ.get("GEOTAB_PASSWORD")
        self.database = database or os.environ.get("GEOTAB_DATABASE")
        self.server = server or os.environ.get("GEOTAB_SERVER", "my.geotab.com")
        
        self.api: Optional[API] = None
        self.session_id: Optional[str] = None
        
        if not all([self.username, self.password, self.database]):
            logger.warning("Geotab credentials not fully configured")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Geotab API.
        
        Returns:
            bool: True if authentication was successful
        """
        try:
            logger.info(f"Authenticating to {self.server} with database {self.database}")
            self.api = mygeotab.API(
                username=self.username,
                password=self.password,
                database=self.database,
                server=self.server
            )
            credentials = self.api.authenticate()
            self.session_id = credentials.session_id
            logger.info("Successfully authenticated to Geotab")
            return True
        except MyGeotabException as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def ensure_authenticated(self) -> bool:
        """
        Ensure API client is authenticated.
        
        Returns:
            bool: True if authenticated
        """
        if not self.api or not self.session_id:
            return self.authenticate()
        return True
    
    def get_devices(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get a list of devices from Geotab.
        
        Args:
            include_inactive: Whether to include inactive devices
            
        Returns:
            List of device objects
        """
        if not self.ensure_authenticated():
            return []
        
        try:
            # Create search criteria
            search = None
            if not include_inactive:
                search = {'active': True}
                
            logger.info(f"Fetching devices (include_inactive={include_inactive})")
            devices = self.api.get('Device', search=search)
            
            # Format device data
            results = []
            for device in devices:
                results.append({
                    'id': device.get('id'),
                    'name': device.get('name'),
                    'serial_number': device.get('serialNumber'),
                    'device_type': device.get('deviceType'),
                    'active': device.get('active', True),
                    'groups': [g.get('id') for g in device.get('groups', [])],
                    'product_id': device.get('productId'),
                    'last_communication_time': device.get('lastCommunicationTime')
                })
            
            logger.info(f"Retrieved {len(results)} devices")
            return results
        except MyGeotabException as e:
            logger.error(f"Error retrieving devices: {e}")
            return []
    
    def get_device_location(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current location for a specific device.
        
        Args:
            device_id: ID of the device
            
        Returns:
            Device location information or None if not found
        """
        if not self.ensure_authenticated():
            return None
        
        try:
            logger.info(f"Fetching location for device {device_id}")
            
            # Get device status info for the specified device
            device_status = self.api.get(
                'DeviceStatusInfo', 
                search={'deviceSearch': {'id': device_id}}
            )
            
            if not device_status:
                logger.warning(f"No status found for device {device_id}")
                return None
            
            status = device_status[0]
            
            # Get address if coordinates are available
            address = None
            if status.get('latitude') and status.get('longitude'):
                try:
                    address_search = {
                        'x': status.get('longitude'),
                        'y': status.get('latitude')
                    }
                    address = self.api.call('GetAddressFromCoordinates', address_search)
                except Exception as e:
                    logger.warning(f"Error getting address: {e}")
            
            # Format the location data
            return {
                'device_id': device_id,
                'timestamp': status.get('dateTime'),
                'latitude': status.get('latitude'),
                'longitude': status.get('longitude'),
                'speed': status.get('speed'),
                'direction': status.get('bearing'),
                'address': address,
                'is_driving': status.get('isDriving', False),
                'is_moving': status.get('isMoving', False)
            }
        except MyGeotabException as e:
            logger.error(f"Error retrieving device location: {e}")
            return None
    
    def get_trips(
        self, 
        device_id: str, 
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        include_non_trip_data: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get trip data for a specific device.
        
        Args:
            device_id: The ID of the device
            from_date: Start date for trip data (default: 24 hours ago)
            to_date: End date for trip data (default: now)
            include_non_trip_data: Whether to include stop information
            
        Returns:
            List of trips
        """
        if not self.ensure_authenticated():
            return []
        
        # Set default date range if not provided
        if not from_date:
            from_date = datetime.now() - timedelta(days=1)
        if not to_date:
            to_date = datetime.now()
        
        try:
            logger.info(f"Fetching trips for device {device_id} from {from_date} to {to_date}")
            
            # Get trip data
            trips = self.api.get(
                'Trip',
                search={
                    'deviceSearch': {'id': device_id},
                    'fromDate': from_date,
                    'toDate': to_date
                }
            )
            
            # Format trip data
            results = []
            for trip in trips:
                trip_data = {
                    'id': trip.get('id'),
                    'device_id': device_id,
                    'start_time': trip.get('start'),
                    'end_time': trip.get('stop'),
                    'duration': trip.get('duration'),
                    'distance': trip.get('distance'),
                    'start_latitude': trip.get('startLatitude'),
                    'start_longitude': trip.get('startLongitude'),
                    'end_latitude': trip.get('endLatitude'),
                    'end_longitude': trip.get('endLongitude'),
                    'max_speed': trip.get('maxSpeed'),
                    'average_speed': trip.get('averageSpeed'),
                    'idle_time': trip.get('idlingDuration'),
                    'stop_time': trip.get('stopDuration')
                }
                
                # Get addresses if coordinates are available
                try:
                    if trip.get('startLatitude') and trip.get('startLongitude'):
                        start_address = self.api.call('GetAddressFromCoordinates', {
                            'x': trip.get('startLongitude'),
                            'y': trip.get('startLatitude')
                        })
                        trip_data['start_address'] = start_address
                        
                    if trip.get('endLatitude') and trip.get('endLongitude'):
                        end_address = self.api.call('GetAddressFromCoordinates', {
                            'x': trip.get('endLongitude'),
                            'y': trip.get('endLatitude')
                        })
                        trip_data['end_address'] = end_address
                except Exception as e:
                    logger.warning(f"Error getting trip addresses: {e}")
                
                results.append(trip_data)
            
            # Get non-trip data (stops) if requested
            if include_non_trip_data:
                try:
                    non_trips = self.api.get(
                        'NonTripActivity',
                        search={
                            'deviceSearch': {'id': device_id},
                            'fromDate': from_date,
                            'toDate': to_date
                        }
                    )
                    
                    for stop in non_trips:
                        stop_data = {
                            'type': 'stop',
                            'id': stop.get('id'),
                            'device_id': device_id,
                            'start_time': stop.get('start'),
                            'end_time': stop.get('stop'),
                            'duration': stop.get('duration'),
                            'latitude': stop.get('latitude'),
                            'longitude': stop.get('longitude')
                        }
                        
                        # Get address if coordinates are available
                        try:
                            if stop.get('latitude') and stop.get('longitude'):
                                address = self.api.call('GetAddressFromCoordinates', {
                                    'x': stop.get('longitude'),
                                    'y': stop.get('latitude')
                                })
                                stop_data['address'] = address
                        except Exception:
                            pass
                        
                        results.append(stop_data)
                except MyGeotabException as e:
                    logger.warning(f"Error retrieving non-trip data: {e}")
            
            logger.info(f"Retrieved {len(results)} trips/stops")
            return results
        except MyGeotabException as e:
            logger.error(f"Error retrieving trip data: {e}")
            return []
    
    def get_fault_data(
        self,
        device_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        include_inactive: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get fault codes and diagnostic data for a device.
        
        Args:
            device_id: ID of the device
            from_date: Start date for fault data (default: 7 days ago)
            to_date: End date for fault data (default: now)
            include_inactive: Whether to include inactive faults
            
        Returns:
            List of faults
        """
        if not self.ensure_authenticated():
            return []
        
        # Set default date range if not provided
        if not from_date:
            from_date = datetime.now() - timedelta(days=7)
        if not to_date:
            to_date = datetime.now()
        
        try:
            logger.info(f"Fetching fault data for device {device_id} from {from_date} to {to_date}")
            
            # Construct search criteria
            search = {
                'deviceSearch': {'id': device_id},
                'fromDate': from_date,
                'toDate': to_date
            }
            
            if not include_inactive:
                search['includeHistoricFaults'] = False
            
            # Get fault data
            faults = self.api.get('FaultData', search=search)
            
            # Format fault data
            results = []
            for fault in faults:
                diagnostic = fault.get('diagnostic', {})
                controller = fault.get('controller', {})
                
                fault_data = {
                    'id': fault.get('id'),
                    'device_id': device_id,
                    'timestamp': fault.get('dateTime'),
                    'diagnostic_id': diagnostic.get('id'),
                    'diagnostic_name': diagnostic.get('name'),
                    'diagnostic_code': diagnostic.get('code'),
                    'controller_id': controller.get('id'),
                    'controller_name': controller.get('name'),
                    'failure_mode': fault.get('failureMode'),
                    'failure_mode_text': fault.get('failureModeText'),
                    'source': fault.get('source'),
                    'count': fault.get('count'),
                    'active': fault.get('activeFault', False),
                    'severity': diagnostic.get('severity')
                }
                
                results.append(fault_data)
            
            logger.info(f"Retrieved {len(results)} faults")
            return results
        except MyGeotabException as e:
            logger.error(f"Error retrieving fault data: {e}")
            return []
    
    def get_status_data(
        self,
        device_id: str,
        diagnostic_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get status data for a device.
        
        Args:
            device_id: ID of the device
            diagnostic_id: ID of the diagnostic to filter by (optional)
            from_date: Start date for status data (default: 1 hour ago)
            to_date: End date for status data (default: now)
            
        Returns:
            List of status data
        """
        if not self.ensure_authenticated():
            return []
        
        # Set default date range if not provided
        if not from_date:
            from_date = datetime.now() - timedelta(hours=1)
        if not to_date:
            to_date = datetime.now()
        
        try:
            # Construct search criteria
            search = {
                'deviceSearch': {'id': device_id},
                'fromDate': from_date,
                'toDate': to_date
            }
            
            if diagnostic_id:
                search['diagnosticSearch'] = {'id': diagnostic_id}
                logger.info(f"Fetching status data for device {device_id} with diagnostic {diagnostic_id}")
            else:
                logger.info(f"Fetching all status data for device {device_id}")
            
            # Get status data
            status_data = self.api.get('StatusData', search=search)
            
            # Format status data
            results = []
            for status in status_data:
                diagnostic = status.get('diagnostic', {})
                
                data_point = {
                    'id': status.get('id'),
                    'device_id': device_id,
                    'timestamp': status.get('dateTime'),
                    'diagnostic_id': diagnostic.get('id'),
                    'diagnostic_name': diagnostic.get('name'),
                    'value': status.get('data'),
                    'units': diagnostic.get('units')
                }
                
                results.append(data_point)
            
            logger.info(f"Retrieved {len(results)} status data points")
            return results
        except MyGeotabException as e:
            logger.error(f"Error retrieving status data: {e}")
            return []
