from loguru import logger
from ..client.game_client import GameClient
import json
import re










class Presets(GameClient):
    

    async def get_presets(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("gas", {})
            if sync:
                response = await self.wait_for_response("gas")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        



        
    async def save_new_preset(
        self,
        preset_number: int,
        formation: list,
        sync: bool = True
    ) -> dict | bool:
        
        fprs = preset_number - 1 if preset_number > 0 else 0
        try:
            await self.send_json_message(
                "sas",
                {
                    "S": fprs,
                    "A": formation
                }
            )
            if sync:
                response = await self.wait_for_response("sas")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def rename_preset(
        self,
        preset_number: int,
        new_name: str,
        sync: bool = True    
    ) -> dict | bool:
        
        fprs = preset_number - 1 if preset_number > 0 else 0
        try:
            await self.send_json_message(
                "upan",
                {
                    "S": fprs,
                    "SN": new_name
                }
            )
            if sync:
                response = await self.wait_for_response("upan")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
    
        
    async def select_preset(
        self,
        preset_name: str
    ) -> list | None:
        
        preset_list = await self.get_presets()
        preset_data = preset_list.get("S", [])
        
        target = str(preset_name)
        
        for p in preset_data:
            if str(p.get("SN")) == target:
                a_list = p.get("A", [])
                return json.loads(a_list) if isinstance(a_list, str) else a_list
            
        available = [str(p.get("SN")) for p in preset_data]
        logger.error(f"Unknown preset: {preset_name!r}. Available: {available}")
        return None
    
    
    
    
    def preset_to_wave(self, data: list, targets_pairs = (6, 4, 4, 10, 4, 4)):
        
        def to_pairs(seq):
            if not isinstance(seq, list):
                seq = [int(n) for n in re.findall(r"-?\d+", str(seq))]
            else:
                seq = [int(v) for v in seq]
            return [seq[i:i+2] for i in range(0, len(seq), 2)]
        
        if not isinstance(data, list):
            data = json.loads(data)
        
        if len(data) < 6:
            data = data + [[] for _ in range(6 - len(data))]
        else:
            data = data[:6]
        dat = [to_pairs(ch) for ch in data]
        logger.debug(dat)
        for i, need in enumerate(targets_pairs):
            have = len(dat[i])
            if have == 0:
                continue
            if have < need:
                dat[i] += [[-1, 0]] * (need - have)
            elif have > need:
                dat[i] = dat[i][:need]
        
        return [{
            "L": {"T": dat[1], "U": dat[4]},
            "R": {"T": dat[2], "U": dat[5]},
            "M": {"T": dat[0], "U": dat[3]},
        }]
    
    
    
    
    async def use_preset(self, preset_name: str) -> list:
        
        pdata = await self.select_preset(preset_name = preset_name)
        
        if not isinstance(pdata, list):
            logger.error(f"Preset data should be a list not {type(pdata)}")
            return
        
        wave = self.preset_to_wave(pdata)
        
        return wave
    
    
    def build_final_wave(self, units: list) -> list:
        
        wave = []
        for u in units:
            if isinstance(u, (list, tuple)) and len(u) == 2 and all(isinstance(x, (int, float)) for x in u):
                wave.append(list[u])
        
        while len(wave) < 8:
            wave.append([-1, 0])
            
        wave = wave[:8]
        return [wave]
 
        
            
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    