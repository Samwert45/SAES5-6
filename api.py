from fastapi import FastAPI, HTTPException
from ldap3 import Server, Connection, ALL
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import ldap3

# Connexion PostgreSQL GLOBALE
db_conn = psycopg2.connect(
    host="::1",
    port=5435,
    database="gateway_db",
    user="gateway",
    password="gateway123"
)

app = FastAPI()

class ProvisionRequest(BaseModel):
    operation: str
    accountId: str
    attributes: dict

@app.post("/provision/create")
def create_user(req: ProvisionRequest):
    server = Server("ldap://localhost:389", get_info=ALL)
    ldap_conn = Connection(server, "cn=admin,dc=entreprise,dc=com", "admin", auto_bind=True)
    
    firstname = req.attributes["firstname"]
    lastname = req.attributes["lastname"]
    login = f"{firstname.lower()}.{lastname.lower()}"
    dn = f"uid={login},dc=entreprise,dc=com"
    
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
        now = datetime.now()
        cur = db_conn.cursor()  # ← Maintenant c'est bon
        cur.execute("""
            INSERT INTO logs (action, descriptif, date)
            VALUES (%s, %s, %s)
        """, ('CREATION', f'{firstname} {lastname}', now))
        db_conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error while inserting log: {e}")
        
    return {"status": "SUCCESS", "login": login}
@app.put("/provision/update")
def update_user(req: ProvisionRequest):
    """Modifier un utilisateur dans LDAP"""
    try:
        # Connexion LDAP
        server = Server("ldap://localhost:389", get_info=ALL)
        ldap_conn = Connection(server, "cn=admin,dc=entreprise,dc=com", "admin", auto_bind=True)
        
        firstname = req.attributes.get("firstname")
        lastname = req.attributes.get("lastname")
        email = req.attributes.get("email")
        login = req.accountId
        dn = f"uid={login},dc=entreprise,dc=com"
        
        # Modifier les attributs
        changes = {}
        if firstname and lastname:
            changes['cn'] = [(ldap3.MODIFY_REPLACE, [f"{firstname} {lastname}"])]
        if lastname:
            changes['sn'] = [(ldap3.MODIFY_REPLACE, [lastname])]
        if email:
            changes['mail'] = [(ldap3.MODIFY_REPLACE, [email])]
        
        ldap_conn.modify(dn, changes)
        ldap_conn.unbind()
        
        # Log dans PostgreSQL
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
        
        return {"status": "SUCCESS", "login": login, "action": "updated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/provision/delete")
def delete_user(req: ProvisionRequest):
    """Supprimer un utilisateur dans LDAP"""
    try:
        # Connexion LDAP
        server = Server("ldap://localhost:389", get_info=ALL)
        ldap_conn = Connection(server, "cn=admin,dc=entreprise,dc=com", "admin", auto_bind=True)
        
        login = req.accountId
        dn = f"uid={login},dc=entreprise,dc=com"
        
        # Supprimer l'utilisateur
        ldap_conn.delete(dn)
        ldap_conn.unbind()
        
        # Log dans PostgreSQL
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
        
        return {"status": "SUCCESS", "login": login, "action": "deleted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
def health():
    return {"status": "ok"}