from fastapi import FastAPI, HTTPException
from ldap3 import Server, Connection, ALL
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import ldap3
from rules_engine import RulesEngine

# Connexion PostgreSQL GLOBALE
db_conn = psycopg2.connect(
    host="::1",
    port=5435,
    database="gateway_db",
    user="gateway",
    password="gateway123"
)

# Moteur de règles
rules_engine = RulesEngine()

app = FastAPI()

class ProvisionRequest(BaseModel):
    operation: str
    accountId: str
    attributes: dict

@app.post("/provision/create")
def create_user(req: ProvisionRequest):
    server = Server("ldap://localhost:389", get_info=ALL)
    ldap_conn = Connection(server, "cn=admin,dc=SAE,dc=com", "admin", auto_bind=True)
    firstname = req.attributes["firstname"]
    lastname = req.attributes["lastname"]
    login = f"{firstname.lower()}.{lastname.lower()}"
    dn = f"uid={login},ou=users,dc=SAE,dc=com"
    
    # Ajoute l'utilisateur
    result = ldap_conn.add(dn, ['inetOrgPerson'], {
        'cn': f"{firstname} {lastname}",
        'sn': lastname,
        'mail': req.attributes.get("email", "")
    })
    
    # ← AJOUTE ÇA POUR VOIR L'ERREUR
    print(f"LDAP ADD result: {result}")
    print(f"LDAP response: {ldap_conn.result}")
    
    ldap_conn.unbind()
    
    # Log dans PostgreSQL
    try:
        # 1. Appliquer les règles de calcul
        calculated = rules_engine.apply_rules("ldap", req.attributes)
        
        # 2. Récupérer la config LDAP
        ldap_config = rules_engine.get_server_config("ldap")
        object_classes = rules_engine.get_object_classes("ldap")
        
        # 3. Connexion LDAP (depuis config)
        server = Server(f"ldap://{ldap_config['host']}:{ldap_config['port']}", get_info=ALL)
        ldap_conn = Connection(
            server,
            ldap_config['admin_dn'],
            ldap_config['admin_password'],
            auto_bind=True
        )
        
        # 4. Créer l'utilisateur avec attributs calculés
        dn = calculated['dn']
        result = ldap_conn.add(dn, object_classes, {
            'cn': calculated['cn'],
            'sn': req.attributes['lastname'],
            'mail': calculated['mail']
        })
        
        print(f"LDAP ADD result: {result}")
        print(f"LDAP response: {ldap_conn.result}")
        
        ldap_conn.unbind()
        
        # 5. Log en base
        try:
            now = datetime.now()
            cur = db_conn.cursor()
            cur.execute("""
                INSERT INTO logs (action, descriptif, date)
                VALUES (%s, %s, %s)
            """, ('CREATION', f"User {calculated['login']}", now))
            db_conn.commit()
            cur.close()
        except Exception as e:
            print(f"Error logging: {e}")
        
        return {
            "status": "SUCCESS",
            "calculatedAttributes": calculated,
            "message": f"User {calculated['login']} created"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/provision/update")
def update_user(req: ProvisionRequest):
    """Modifier un utilisateur dans LDAP avec règles dynamiques"""
    try:
        # Connexion LDAP
        server = Server("ldap://localhost:389", get_info=ALL)
        ldap_conn = Connection(server, "cn=admin,dc=SAE,dc=com", "admin", auto_bind=True)
        
        firstname = req.attributes.get("firstname")
        lastname = req.attributes.get("lastname")
        email = req.attributes.get("email")
        login = req.accountId
        dn = f"uid={login},ou=users,dc=SAE,dc=com"
        
        # 3. Connexion LDAP
        server = Server(f"ldap://{ldap_config['host']}:{ldap_config['port']}", get_info=ALL)
        ldap_conn = Connection(
            server,
            ldap_config['admin_dn'],
            ldap_config['admin_password'],
            auto_bind=True
        )
        
        # 4. Construire le DN depuis les règles ou utiliser accountId
        login = calculated.get('login', req.accountId)
        dn = calculated.get('dn', f"uid={login},ou=users,dc=SAE,dc=com")
        
        # 5. Modifier les attributs
        changes = {}
        if 'cn' in calculated:
            changes['cn'] = [(ldap3.MODIFY_REPLACE, [calculated['cn']])]
        if req.attributes.get('lastname'):
            changes['sn'] = [(ldap3.MODIFY_REPLACE, [req.attributes['lastname']])]
        if calculated.get('mail'):
            changes['mail'] = [(ldap3.MODIFY_REPLACE, [calculated['mail']])]
        
        ldap_conn.modify(dn, changes)
        ldap_conn.unbind()
        
        # 6. Log dans PostgreSQL
        try:
            now = datetime.now()
            cur = db_conn.cursor()
            cur.execute("""
                INSERT INTO logs (action, descriptif, date)
                VALUES (%s, %s, %s)
            """, ('UPDATE', f'Updated {login}', now))
            db_conn.commit()
            cur.close()
        except Exception as e:
            print(f"Error while inserting log: {e}")
        
        return {
            "status": "SUCCESS",
            "login": login,
            "action": "updated",
            "calculatedAttributes": calculated
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/provision/delete")
def delete_user(req: ProvisionRequest):
    """Supprimer un utilisateur dans LDAP avec règles dynamiques"""
    try:
        # Connexion LDAP
        server = Server("ldap://localhost:389", get_info=ALL)
        ldap_conn = Connection(server, "cn=admin,dc=SAE,dc=com", "admin", auto_bind=True)
        
        login = req.accountId
        dn = f"uid={login},ou=users,dc=SAE,dc=com"
        
        # 3. Connexion LDAP
        server = Server(f"ldap://{ldap_config['host']}:{ldap_config['port']}", get_info=ALL)
        ldap_conn = Connection(
            server,
            ldap_config['admin_dn'],
            ldap_config['admin_password'],
            auto_bind=True
        )
        
        # 4. Construire le DN
        login = calculated.get('login', req.accountId)
        dn = calculated.get('dn', f"uid={login},ou=users,dc=SAE,dc=com")
        
        # 5. Supprimer l'utilisateur
        ldap_conn.delete(dn)
        ldap_conn.unbind()
        
        # 6. Log dans PostgreSQL
        try:
            now = datetime.now()
            cur = db_conn.cursor()
            cur.execute("""
                INSERT INTO logs (action, descriptif, date)
                VALUES (%s, %s, %s)
            """, ('DELETE', f'Deleted {login}', now))
            db_conn.commit()
            cur.close()
        except Exception as e:
            print(f"Error while inserting log: {e}")
        
        return {
            "status": "SUCCESS",
            "login": login,
            "action": "deleted"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/rules")
def get_rules():
    """Endpoint pour visualiser les règles actuelles"""
    return {
        "ldap_mappings": rules_engine.config.get("ldap", {}).get("mappings", {}),
        "ldap_config": rules_engine.config.get("ldap", {}).get("server", {}),
        "global_config": rules_engine.config.get("global", {})
    }
