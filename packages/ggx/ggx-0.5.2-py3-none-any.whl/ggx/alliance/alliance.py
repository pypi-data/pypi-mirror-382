from ..client.game_client import GameClient
from loguru import logger






class Alliance(GameClient):
    
    
    
    async def get_chat(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("acl", {})
            if sync:
                response = await self.wait_for_response("acl")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    async def write_on_chat(
        self,
        message: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "acm",
                {
                    "M": message
                }
            )
            if sync:
                response = await self.wait_for_response("acm")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
    
    
    
       
        
    async def help_alliance_member(
        self, 
        kingdom: int, 
        help_id: int, 
        sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("ahc", {"LID": help_id, "KID": kingdom})
            if sync:
                response = await self.wait_for_response("ahc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    
       
    async def help_alliance_all(
        self, 
        kingdom: int, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("aha", {"KID": kingdom})
            if sync:
                response = await self.wait_for_response("aha")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False  
        
        
    async def invite_player(
        self,
        user_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "aip",
                {
                    "SV": user_id
                }
            )
            if sync:
                response = await self.wait_for_response("aip")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
        
        
    async def rank_player(
        self,
        account_id: int,
        rank: int,   ## 0-8 leader to member
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "arm",
                {
                    "PID": account_id,
                    "R": rank
                }  
            )
            if sync:
                response = await self.wait_for_response("arm")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
      
      
        
        
    async def mass_message(
        self,
        text: str,
        title: str = None,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "anl",
                {
                    "SJ": title,
                    "TXT": text
                }
            )
            if sync:
                response = await self.wait_for_response("anl")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
        
        
    async def leave_alliance(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("aqi", {})
            if sync:
                response = await self.wait_for_response("aqi")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
        
        
    async def create_alliance(
        self,
        alliance_name: str,
        allinace_state: int,
        description: str,
        lang: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "afo",
                {
                    "PO":-1,
                    "PWR":0,
                    "IA": allinace_state,
                    "N": alliance_name,
                    "D": description,
                    "ALL": lang
                }
            )
            if sync:
                response = await self.wait_for_response("afo")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
        
    async def alliance_info(
        self,
        alliance_id: int,
        sync: bool = True
        ) -> dict | bool:
        
        try:
            await self.send_json_message("ain", {"AID": alliance_id})
            if sync:
                response = await self.wait_for_response("ain")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
    
    
    async def get_alliance(
        self,
        sync: bool = True
        ) -> dict | bool:
        
        try:
            await self.send_json_message("all", {})
            if sync:
                response = await self.wait_for_response("all")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
    
    
    
    
        
    async def get_alliance_discussions_panel(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("gat", {})
            if sync:
                response = await self.wait_for_response("gat")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
      
      
      
        
    async def post_alliance_announce(
        self,
        announce_text: str, 
        sync: bool = True
        ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "acd",
                {
                    "T": 0,
                    "TXT": announce_text
                }
            )
            if sync:
                response = await self.wait_for_response("gat")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
       
     
     
        
    async def postin_alliance_discussions_panel(
        self,
        title: str,
        text: str,
        rank_list: list = [0, 1, 2],
        sync: bool = True
        ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "atc",
                {
                    "N": title,
                    "RG": rank_list,
                    "R": text
                }
            )
            if sync:
                response = await self.wait_for_response("gat")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False 
        
    
        
    async def get_online_members(self) -> list:
    
        get_all = await self.get_alliance()
        alliance_id = get_all.get("AID", None)
        main_all_info = await self.alliance_info(alliance_id = alliance_id)
        
        all_resp = main_all_info.get("A", {})
        user_data = all_resp.get("AMI", {})
        online_members = [member[0] for member in user_data if member[4] == 0]
        
        return online_members
        

        