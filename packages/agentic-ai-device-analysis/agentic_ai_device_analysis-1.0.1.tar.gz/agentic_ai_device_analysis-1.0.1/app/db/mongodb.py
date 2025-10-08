from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional, Any
from datetime import datetime
from bson import ObjectId
from app.core.device_fingerprint import DeviceFingerprint
from app.core.behavior_analysis import UserBehavior

class MongoDB:
    def __init__(self, connection_string: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.device_analytics
        self.device_profiles = self.db.device_profiles
        self.behaviors = self.db.behaviors
        self.agentic_analysis = self.db.agentic_analysis
        self.context_data = self.db.context_data
    
    async def store_device_profile(self, fingerprint: DeviceFingerprint) -> str:
        """Store device fingerprint and return profile ID."""
        profile_data = fingerprint.to_dict()
        profile_data['created_at'] = datetime.utcnow()
        profile_data['updated_at'] = datetime.utcnow()
        
        # Check if a profile with this fingerprint hash already exists
        existing_profile = await self.device_profiles.find_one({
            'fingerprint_hash': profile_data.get('fingerprint_hash')
        })
        
        if existing_profile:
            # Update existing profile
            await self.device_profiles.update_one(
                {'_id': existing_profile['_id']},
                {'$set': {
                    'updated_at': datetime.utcnow(),
                    'last_seen': datetime.utcnow(),
                    'session_id': fingerprint.session_id
                }}
            )
            return str(existing_profile['_id'])
        else:
            # Create new profile
            profile_data['first_seen'] = datetime.utcnow()
            profile_data['last_seen'] = datetime.utcnow()
            result = await self.device_profiles.insert_one(profile_data)
            return str(result.inserted_id)
    
    async def update_device_profile(self, profile_id: str, fingerprint: DeviceFingerprint):
        """Update existing device profile."""
        profile_data = fingerprint.to_dict()
        profile_data['updated_at'] = datetime.utcnow()
        profile_data['last_seen'] = datetime.utcnow()
        
        await self.device_profiles.update_one(
            {'_id': ObjectId(profile_id)},
            {'$set': profile_data}
        )
    
    async def store_behavior(self, behavior: UserBehavior) -> str:
        """Store user behavior data and return behavior ID."""
        behavior_data = behavior.model_dump()
        behavior_data['created_at'] = datetime.utcnow()
        
        result = await self.behaviors.insert_one(behavior_data)
        return str(result.inserted_id)
    
    async def get_device_behaviors(self, session_id: str) -> List[Dict]:
        """Retrieve behavior history for a device."""
        cursor = self.behaviors.find({'session_id': session_id})
        return await cursor.to_list(length=None)
    
    async def get_latest_behavior(self, session_id: str) -> Optional[Dict]:
        """Get the most recent behavior data for a session."""
        cursor = self.behaviors.find({'session_id': session_id}).sort('created_at', -1).limit(1)
        behaviors = await cursor.to_list(length=1)
        return behaviors[0] if behaviors else None
    
    async def get_device_profile(self, profile_id: str) -> Optional[Dict]:
        """Retrieve device profile by ID."""
        try:
            return await self.device_profiles.find_one({'_id': ObjectId(profile_id)})
        except:
            return None
    
    async def get_device_fingerprint_by_session(self, session_id: str) -> Optional[DeviceFingerprint]:
        """Get device fingerprint by session ID."""
        profile = await self.device_profiles.find_one({'session_id': session_id})
        if profile:
            # Convert MongoDB document to DeviceFingerprint object
            # Remove MongoDB-specific fields
            profile.pop('_id', None)
            profile.pop('created_at', None)
            profile.pop('updated_at', None)
            profile.pop('parsed_user_agent', None)
            profile.pop('fingerprint_hash', None)
            profile.pop('uniqueness_score', None)
            profile.pop('first_seen', None)
            profile.pop('last_seen', None)
            
            # Create DeviceFingerprint object
            return DeviceFingerprint(**profile)
        return None
    
    async def get_similar_profiles(self, fingerprint: DeviceFingerprint, limit: int = 5) -> List[Dict]:
        """Find similar device profiles based on fingerprint attributes."""
        parsed_ua = fingerprint.parse_user_agent()
        fingerprint_hash = fingerprint.generate_fingerprint_hash()
        
        # Enhanced query with more attributes
        query = {
            '$or': [
                {'fingerprint_hash': fingerprint_hash},
                {'ip_address': fingerprint.ip_address},
                {'parsed_user_agent.browser.family': parsed_ua['browser']['family']},
                {'parsed_user_agent.os.family': parsed_ua['os']['family']},
                {'screen_resolution': fingerprint.screen_resolution},
                {'hardware_concurrency': fingerprint.hardware_concurrency},
                {'device_memory': fingerprint.device_memory}
            ]
        }
        
        cursor = self.device_profiles.find(query).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def store_agentic_analysis(self, profile_id: str, analysis_result: Dict) -> str:
        """Store agentic analysis result."""
        analysis_data = {
            'profile_id': profile_id,
            'result': analysis_result,
            'created_at': datetime.utcnow()
        }
        
        result = await self.agentic_analysis.insert_one(analysis_data)
        return str(result.inserted_id)
    
    async def get_agentic_analysis_history(self, profile_id: str, limit: int = 10) -> List[Dict]:
        """Get agentic analysis history for a profile."""
        cursor = self.agentic_analysis.find({'profile_id': profile_id}).sort('created_at', -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_device_context(self, fingerprint: Optional[DeviceFingerprint]) -> Dict[str, Any]:
        """Get context data for a device fingerprint."""
        if not fingerprint:
            return {}
            
        # Get historical browsers
        browser_cursor = self.device_profiles.find({
            'ip_address': fingerprint.ip_address
        }).sort('created_at', -1).limit(10)
        
        browser_history = await browser_cursor.to_list(length=10)
        historical_browsers = []
        historical_ips = []
        
        for profile in browser_history:
            ua_info = profile.get('parsed_user_agent', {}).get('browser', {})
            browser = f"{ua_info.get('family')} {ua_info.get('version')}"
            if browser not in historical_browsers:
                historical_browsers.append(browser)
            
            ip = profile.get('ip_address')
            if ip and ip not in historical_ips:
                historical_ips.append(ip)
        
        # Get session history
        session_cursor = self.behaviors.aggregate([
            {'$match': {'session_id': fingerprint.session_id}},
            {'$group': {
                '_id': '$session_id',
                'count': {'$sum': 1},
                'first_seen': {'$min': '$timestamp'},
                'last_seen': {'$max': '$timestamp'}
            }}
        ])
        
        session_history = {}
        async for session in session_cursor:
            session_id = session['_id']
            count = session['count']
            first_seen = session['first_seen']
            last_seen = session['last_seen']
            
            # Calculate frequency score based on activity count
            frequency = min(1.0, count / 20)  # Cap at 1.0
            
            session_history[session_id] = {
                'count': count,
                'first_seen': first_seen,
                'last_seen': last_seen,
                'frequency': frequency
            }
        
        return {
            'historical_browsers': historical_browsers,
            'historical_ips': historical_ips,
            'session_history': session_history
        }