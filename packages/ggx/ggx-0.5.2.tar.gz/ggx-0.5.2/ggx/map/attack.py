from ..client.game_client import GameClient
from ..utils.utils import Utils
from loguru import logger
import json






class Attack(GameClient):
    
    
    
    
    async def send_attack(
        self,
        kingdom: int,
        sx: int,
        sy: int,
        tx: int,
        ty: int,
        army: list,
        lord_id: int = 0,
        horses_type: int = -1,
        feathers: int = 0,
        slowdown: int = 0,
        boosters: list = [],
        support_tools: list = [],
        final_wave: list = [],
        sync: bool = True
    ) -> dict | bool:
        
        try:
            
            await self.send_json_message(
                "cra",
                {
                    "SX": sx,
                    "SY": sy,
                    "TX": tx,
                    "TY": ty,
                    "KID": kingdom,
                    "LID": lord_id,
                    "WT": 0,
                    "HBW": horses_type,
                    "BPC": 0,
                    "ATT": 0,
                    "AV": 0,
                    "LP": 0,
                    "FC": 0,
                    "PTT": feathers,
                    "SD": slowdown,
                    "ICA": 0,
                    "CD": 99,
                    "A": army,
                    "BKS": boosters,
                    "AST": support_tools,
                    "RW": final_wave,
                    "ASCT": 0, 
                }
            )
            if sync:
                response = await self.wait_for_response("cra")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    async def send_conquer(
        self,
        kingdom: int,
        sx: int,
        sy: int,
        tx: int,
        ty: int,
        army: list,
        castellan_id: int = 0,
        horses_type: int = -1,
        feathers: int = 0,
        slowdown: int = 0,
        boosters: list = [],
        support_tools: list = [],
        final_wave: list = [],
        sync: bool = True
    ) -> dict | bool:
        
        try:
            
            await self.send_json_message(
                "cra",
                {
                    "SX": sx,
                    "SY": sy,
                    "TX": tx,
                    "TY": ty,
                    "KID": kingdom,
                    "LID": castellan_id,
                    "WT": 0,
                    "HBW": horses_type,
                    "BPC": 0,
                    "ATT": 7,
                    "AV": 0,
                    "LP": 0,
                    "FC": 0,
                    "PTT": feathers,
                    "SD": slowdown,
                    "ICA": 0,
                    "CD": 99,
                    "A": army,
                    "BKS": boosters,
                    "AST": support_tools,
                    "RW": final_wave,
                    "ASCT": 0, 
                }
            )
            if sync:
                response = await self.wait_for_response("cra")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
     
     
        
        
    async def time_skip_npc_cooldown(
        self,
        kingdom: int,
        tx: int,
        ty: int,
        time_skip: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "msd",
                {
                    "X": tx,
                    "Y": ty,
                    "MID": -1,
                    "NID": -1,
                    "MST": time_skip,
                    "KID": str(kingdom)
                }
            )
            if sync:
                response = await self.wait_for_response("msd")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    
    
    async def autoskip_npc_cooldown(
        self,
        kingdom: int,
        tx: int,
        ty: int,
        cooldown_time: int,
        skips: list = None
    ) -> None:
        
        utils = Utils()
        if cooldown_time > 0:
            
            skips_list = utils.skip_calculator(cooldown_time, skips)
            for skip in skips_list:
                await self.time_skip_npc_cooldown(kingdom, tx, ty, skip, sync=False)
        
        
               
                
    
    
    
    def attack_units_sum(
        self,
        waves: list[dict],
        final_wave: list
    ) -> dict:
        
        per_wave = []
        total_waves = 0
        
        if not isinstance(waves, list):
            waves = json.loads(waves)
            
        if not isinstance(final_wave, list):
            final_wave = json.loads(final_wave)
            
        for w in waves:
            wave_sum = 0
            if not isinstance(w, dict):
                continue
            
            for side in ("L", "R", "M"):
                part = w.get(side, {})
                units = part.get("U", [])
                for u in units:
                    if isinstance(u, (list, tuple)) and len(u) >= 2 and isinstance(u[1], (int, float)) and u[1] > 0:
                        wave_sum += int(u[1])
            
            per_wave.append(wave_sum)
            total_waves += wave_sum
        
        final_total = 0  
        if isinstance(final_wave, list):
            for item in final_wave:
                if isinstance(item, (list, tuple)) and len(item) >= 2 and isinstance(item[1], (int, float)) and item[1] > 0:
                    final_total += int(item[1])
        
        grand_total = total_waves + final_total
        
        return {
            
            "per_wave": per_wave,
            "total_waves": total_waves,
            "final_total": final_total,
            "grand_total": grand_total
            
        }
                      
       
            




