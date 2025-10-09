import asyncio
from csfloat_inspector import CSFloatInspector

inspector = CSFloatInspector()

async def main():
    print("[*] Inspecting item...")
    try:
        data = await inspector.inspect("steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20S76561198309889674A45731137503D190491363065250641")
        print(f"[*] Successfully retrieved data: {data}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[!] An error occurred: {e}")
        
    print("[*] Fetching item image URL...")
    try:
        img_url = await inspector.getimg("steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20S76561198309889674A45731137503D190491363065250641")
        print(f"[*] Successfully retrieved image URL: {img_url}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[!] An error occurred: {e}")
        
if __name__ == "__main__":
    asyncio.run(main())
