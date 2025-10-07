#!/usr/bin/env python3
"""
Ejemplo de uso del nuevo método login() que devuelve tokens
"""

import os
from schwab_sdk import Client, AsyncClient

def ejemplo_sync():
    """Ejemplo con cliente síncrono"""
    print("=== Cliente Síncrono ===")
    
    client = Client(
        os.environ['SCHWAB_CLIENT_ID'],
        os.environ['SCHWAB_CLIENT_SECRET'],
        save_token=True
    )
    
    # Login devuelve (success, tokens)
    success, tokens = client.login()
    
    if success:
        print("✅ Login exitoso!")
        print("\n📋 Datos de tokens recibidos:")
        print(f"  - access_token: {tokens.get('access_token', 'N/A')[:20]}...")
        print(f"  - refresh_token: {tokens.get('refresh_token', 'N/A')[:20]}...")
        print(f"  - expires_in: {tokens.get('expires_in', 'N/A')} segundos")
        print(f"  - token_type: {tokens.get('token_type', 'N/A')}")
        print(f"  - scope: {tokens.get('scope', 'N/A')}")
        
        # Ahora puedes usar el cliente normalmente
        print("\n🔍 Obteniendo cuentas...")
        accounts = client.account.get_accounts()
        print(f"  - Cuentas encontradas: {len(accounts)}")
        
    else:
        print("❌ Login falló")

async def ejemplo_async():
    """Ejemplo con cliente asíncrono"""
    print("\n=== Cliente Asíncrono ===")
    
    async with AsyncClient(
        os.environ['SCHWAB_CLIENT_ID'],
        os.environ['SCHWAB_CLIENT_SECRET'],
        save_token=True
    ) as client:
        
        # Login devuelve (success, tokens)
        success, tokens = await client.login()
        
        if success:
            print("✅ Async login exitoso!")
            print("\n📋 Datos de tokens recibidos:")
            print(f"  - access_token: {tokens.get('access_token', 'N/A')[:20]}...")
            print(f"  - refresh_token: {tokens.get('refresh_token', 'N/A')[:20]}...")
            print(f"  - expires_in: {tokens.get('expires_in', 'N/A')} segundos")
            print(f"  - token_type: {tokens.get('token_type', 'N/A')}")
            print(f"  - scope: {tokens.get('scope', 'N/A')}")
            
            # Ahora puedes usar el cliente normalmente
            print("\n🔍 Obteniendo cuentas...")
            accounts = await client.account.get_accounts()
            print(f"  - Cuentas encontradas: {len(accounts)}")
            
        else:
            print("❌ Async login falló")

def ejemplo_token_data():
    """Ejemplo usando token_data para inicializar"""
    print("\n=== Inicialización con token_data ===")
    
    # Simular tokens existentes (en la práctica vendrían de tu sistema)
    token_data = {
        'access_token': 'tu_access_token_aqui',
        'refresh_token': 'tu_refresh_token_aqui',
        'expires_in': 1800,  # 30 minutos
        'token_type': 'Bearer',
        'scope': 'readonly'
    }
    
    client = Client(
        os.environ['SCHWAB_CLIENT_ID'],
        os.environ['SCHWAB_CLIENT_SECRET'],
        save_token=False,  # Solo en memoria
        token_data=token_data
    )
    
    # Verificar tokens actuales
    current_tokens = client.token_handler.get_token_payload()
    print("📋 Tokens actuales en memoria:")
    print(f"  - access_token: {current_tokens.get('access_token', 'N/A')[:20]}...")
    print(f"  - refresh_token: {current_tokens.get('refresh_token', 'N/A')[:20]}...")
    print(f"  - expires_in: {current_tokens.get('expires_in', 'N/A')} segundos")

if __name__ == "__main__":
    import asyncio
    
    # Verificar variables de entorno
    required_vars = ['SCHWAB_CLIENT_ID', 'SCHWAB_CLIENT_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Faltan variables de entorno: {missing_vars}")
        print("Configura las variables antes de ejecutar este ejemplo.")
        exit(1)
    
    print("🚀 Ejecutando ejemplos de login con tokens...")
    
    # Ejemplo síncrono
    ejemplo_sync()
    
    # Ejemplo asíncrono
    asyncio.run(ejemplo_async())
    
    # Ejemplo con token_data
    ejemplo_token_data()
    
    print("\n✅ Ejemplos completados!")
